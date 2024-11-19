#![allow(clippy::missing_errors_doc)]
#![allow(clippy::unnecessary_struct_initialization)]
#![allow(clippy::unused_async)]
use axum::debug_handler;
use loco_rs::prelude::*;

// index page
#[debug_handler]
pub async fn index(ViewEngine(v): ViewEngine<TeraView>) -> Result<Response> {
    format::render().view(&v, "user/index.html", data!({}))
}

// ### --- auth routes --- ### //

// login page route
#[debug_handler]
pub async fn login(ViewEngine(v): ViewEngine<TeraView>) -> Result<Response> {
    format::render().view(&v, "user/login.html", data!({}))
}

// register page route
#[debug_handler]
pub async fn register(ViewEngine(v): ViewEngine<TeraView>) -> Result<Response> {
    format::render().view(&v, "user/index.html", data!({}))
}

// verify page route
#[debug_handler]
pub async fn verify(ViewEngine(v): ViewEngine<TeraView>) -> Result<Response> {
    format::render().view(&v, "user/index.html", data!({}))
}

// logout page route
#[debug_handler]
pub async fn logout(ViewEngine(v): ViewEngine<TeraView>) -> Result<Response> {
    format::render().view(&v, "user/index.html", data!({}))
}

// forgot password page route
#[debug_handler]
pub async fn forgot_password(ViewEngine(v): ViewEngine<TeraView>) -> Result<Response> {
    format::render().view(&v, "user/index.html", data!({}))
}

// ### --- end auth routes --- ### //

// ### --- profile routes --- ### //

// profile page route
#[debug_handler]
pub async fn profile(ViewEngine(v): ViewEngine<TeraView>) -> Result<Response> {
    format::render().view(&v, "user/index.html", data!({}))
}

// ### end profile routes ### //


// routes declaration for app.rs
pub fn routes() -> Routes {
    Routes::new()
        .prefix("users")
        .add("/", get(index))
        .add("/auth/login", get(login))
        .add("/auth/register", get(register))
        .add("/auth/verify", get(verify))
        .add("/auth/forgot-password", get(forgot_password))
        .add("/auth/logout", get(logout))
        .add("/profile", get(profile))
}
