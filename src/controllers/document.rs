#![allow(clippy::missing_errors_doc)]
#![allow(clippy::unnecessary_struct_initialization)]
#![allow(clippy::unused_async)]
use loco_rs::prelude::*;

// use axum::debug_handler;
use std::collections::HashMap;
use std::sync::OnceLock;
use tracing::error;


// !### ### route configuration ### ### //
const PREFIX: &str = "documents";

fn get_routes() -> &'static HashMap<&'static str, &'static str> {
    static ROUTES: OnceLock<HashMap<&'static str, &'static str>> = OnceLock::new();

    ROUTES.get_or_init(|| {
        // define routes here, and reference everywhere you need it.
        HashMap::from([
            ("index", "/"),
            ("upload", "/upload"),
            ("upload_status", "/upload/status"),
            ("get_all", "/get/all"),
            ("get", "/get"),
            ("delete", "/delete"),
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


pub fn routes() -> Routes {
    let r = get_routes();

    Routes::new().prefix(PREFIX)
}
