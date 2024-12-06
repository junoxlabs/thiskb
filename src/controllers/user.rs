#![allow(clippy::missing_errors_doc)]
#![allow(clippy::unnecessary_struct_initialization)]
#![allow(clippy::unused_async)]
use auth::JWTWithUser;
use axum::{debug_handler, http::StatusCode, Form};

use loco_rs::prelude::*;
use std::collections::HashMap;
use std::sync::OnceLock;
use tracing::error;

use crate::{
    mailers::auth::AuthMailer,
    models::users::{self, LoginParams, RegisterParams},
};

// !### ### route configuration ### ### //
const PREFIX: &str = "users";

fn get_routes() -> &'static HashMap<&'static str, &'static str> {
    static ROUTES: OnceLock<HashMap<&'static str, &'static str>> = OnceLock::new();

    ROUTES.get_or_init(|| {
        // define routes here, and reference everywhere you need it.
        HashMap::from([
            ("index", "/"),
            ("login", "/auth/login"),
            ("register", "/auth/register"),
            ("verify", "/auth/verify"),
            ("forgot_password", "/auth/forgot-password"),
            ("logout", "/auth/logout"),
            ("profile", "/profile"),
            ("settings", "/settings"),
        ])
    })
}

fn get_routes_with_prefix(key: &str) -> String {
    let route = match get_routes().get(key) {
        Some(route) => route,
        None => {
            error!("get_routes({}) not found", key);
            return "".to_string();
        }
    };
    format!("/{}{}", &PREFIX, route)
}
// !### ### end route configuration ### ### //

// !### --- index routes --- ### //

// index page
#[debug_handler]
pub async fn index(ViewEngine(v): ViewEngine<TeraView>) -> Result<Response> {
    format::render().view(&v, "user/index.html", data!({}))
}

// !### --- end index routes --- ### //

// !### --- profile routes --- ### //

// profile page route
#[debug_handler]
pub async fn profile(
    auth: JWTWithUser<users::Model>,
    ViewEngine(v): ViewEngine<TeraView>,
    State(_ctx): State<AppContext>,
) -> Result<Response> {
    tracing::info!("{}", &auth.user.pid);
    format::render().view(&v, "user/index.html", data!({}))
}

// !### end profile routes ### //

// !### --- auth routes --- ### //

// !GET login page route
#[debug_handler]
pub async fn login(ViewEngine(v): ViewEngine<TeraView>) -> Result<Response> {
    format::render().view(
        &v,
        "user/login.html",
        data!(
            {
                "post_url": get_routes_with_prefix("login")
            }
        ),
    )
}

// !POST login response
#[debug_handler]
pub async fn do_login(
    ViewEngine(v): ViewEngine<TeraView>,
    State(ctx): State<AppContext>,
    Form(params): Form<LoginParams>,
) -> Result<Response> {
    // get user by email from db
    let user = match users::Model::find_by_email(&ctx.db, &params.email).await {
        Ok(user) => user,
        Err(err) => {
            // debug tracing
            tracing::debug!(message = &err.to_string(), "could not find user");

            // render error page for htmx
            return format::render().view(
                &v,
                "user/errors/form_error.html",
                data!({
                    "message": err.to_string() // !TODO: do better error message handling
                }),
            );
        }
    };

    // verify user password using the given password
    match user.verify_password(&params.password) {
        true => {
            let jwt_secret = ctx.config.get_jwt_config()?;

            let token = match user.generate_jwt(&jwt_secret.secret, &jwt_secret.expiration) {
                Ok(token) => token,
                Err(err) => {
                    // debug tracing
                    tracing::error!(message = &err.to_string(), "could not generate token");

                    // render error page for htmx
                    return format::render().view(
                        &v,
                        "user/errors/form_error.html",
                        data!({
                            "message": err.to_string()
                        }),
                    );
                }
            };

            // !TODO: get cookie name from config file automatically
            let cookie = cookie::Cookie::build(("jwt", token))
                .http_only(true)
                .path("/")
                .same_site(cookie::SameSite::Strict)
                .max_age(time::Duration::minutes(60));

            Ok((
                StatusCode::SEE_OTHER, // 303 See Other
                [
                    // set auth jwt cookie
                    ("Set-Cookie", cookie.to_string()),
                    // redirect to login page using htmx redirect header
                    ("HX-Redirect", get_routes_with_prefix("profile")),
                ],
            )
                .into_response())
        }
        false => {
            // debug tracing
            tracing::debug!("invalid login credentials");

            // render error page for htmx
            format::render().view(
                &v,
                "user/errors/form_error.html",
                data!({
                    "message": "invalid login credentials"
                }),
            )
        }
    }
}

// !GET register page route
#[debug_handler]
pub async fn register(ViewEngine(v): ViewEngine<TeraView>) -> Result<Response> {
    format::render().view(
        &v,
        "user/register.html",
        data!({
            "post_url": get_routes_with_prefix("register")
        }),
    )
}

// !POST register response
#[debug_handler]
pub async fn do_register(
    ViewEngine(v): ViewEngine<TeraView>,
    State(ctx): State<AppContext>,
    Form(params): Form<RegisterParams>,
) -> Result<Response> {
    let res = users::Model::create_with_password(&ctx.db, &params).await;

    let user = match res {
        Ok(user) => user,
        Err(err) => {
            // debug tracing
            tracing::debug!(message = &err.to_string(), "could not register user",);

            // render error page for htmx
            return format::render().view(
                &v,
                "user/errors/form_error.html",
                data!({
                    "message": err.to_string()
                }),
            );
        }
    };

    let user = user
        .into_active_model()
        .set_email_verification_sent(&ctx.db)
        .await?;

    AuthMailer::send_welcome(&ctx, &user).await?;

    Ok((
        StatusCode::SEE_OTHER, // 303 See Other
        // redirect to login page using htmx redirect header
        [("HX-Redirect", get_routes_with_prefix("login"))],
    )
        .into_response())
}

// !GET verify page route
#[debug_handler]
pub async fn verify(ViewEngine(v): ViewEngine<TeraView>) -> Result<Response> {
    format::render().view(
        &v,
        "user/index.html",
        data!({
            "post_url": get_routes_with_prefix("verify")
        }),
    )
}

// !GET forgot password page route
#[debug_handler]
pub async fn forgot_password(ViewEngine(v): ViewEngine<TeraView>) -> Result<Response> {
    format::render().view(
        &v,
        "user/forgot_password.html",
        data!({
            "post_url": get_routes_with_prefix("forgot_password")
        }),
    )
}

// !GET logout page route
#[debug_handler]
pub async fn logout(
    _auth: JWTWithUser<users::Model>,
    State(_ctx): State<AppContext>,
) -> Result<Response> {
    let cookie = cookie::Cookie::build(("jwt", ""))
        .http_only(true)
        .path("/")
        .same_site(cookie::SameSite::Strict)
        .max_age(time::Duration::minutes(0));

    Ok((
        StatusCode::TEMPORARY_REDIRECT, // 307 Temporary Redirect
        [
            // set auth jwt cookie
            ("Set-Cookie", cookie.to_string()),
            // redirect to login page using htmx redirect header
            ("Location", get_routes_with_prefix("login")),
        ],
    )
        .into_response())
}

// !### --- end auth routes --- ### //

// routes declaration for app.rs
pub fn routes() -> Routes {
    let r = get_routes();

    Routes::new()
        .prefix(PREFIX)
        .add(r.get("index").unwrap(), get(index))
        .add(r.get("login").unwrap(), get(login))
        .add(r.get("login").unwrap(), post(do_login))
        .add(r.get("register").unwrap(), get(register))
        .add(r.get("register").unwrap(), post(do_register))
        .add(r.get("verify").unwrap(), get(verify))
        .add(r.get("forgot_password").unwrap(), get(forgot_password))
        .add(r.get("logout").unwrap(), get(logout))
        .add(r.get("profile").unwrap(), get(profile))
}
