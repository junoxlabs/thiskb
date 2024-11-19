#![allow(clippy::missing_errors_doc)]
#![allow(clippy::unnecessary_struct_initialization)]
#![allow(clippy::unused_async)]
use axum::debug_handler;
use loco_rs::prelude::*;

#[debug_handler]
async fn index(ViewEngine(v): ViewEngine<TeraView>) -> Result<Response> {
    format::render().view(&v, "home/index.html", data!({}))
}

pub fn routes() -> Routes {
    Routes::new().prefix("/").add("/", get(index))
}
