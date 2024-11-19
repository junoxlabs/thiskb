#![allow(clippy::missing_errors_doc)]
#![allow(clippy::unnecessary_struct_initialization)]
#![allow(clippy::unused_async)]
use axum::debug_handler;
use loco_rs::prelude::*;

#[debug_handler]
async fn index() -> Result<Response> {
    // format::template("home/index", )
    format::empty_json()
}

pub fn routes() -> Routes {
    Routes::new().prefix("/").add("/", get(index))
}
