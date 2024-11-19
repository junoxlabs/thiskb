use axum::{async_trait, Extension, Router};
use loco_rs::{
    app::{AppContext, Initializer},
    controller::views::{engines::TeraView, ViewEngine},
    Result,
};
use tracing::info;

pub struct TemplateEngineInitializer;

const TEMPLATES_DIR: &str = "src/templates";

#[async_trait]
impl Initializer for TemplateEngineInitializer {
    fn name(&self) -> String {
        "Tera Template Engine".to_string()
    }

    async fn after_routes(&self, router: Router, _ctx: &AppContext) -> Result<Router> {
        // initialize tera engine
        let tera_engine: TeraView = TeraView::from_custom_dir(&TEMPLATES_DIR)?;

        // INFO: log tera engine initialization
        info!("{} Initialized", &self.name().as_str());

        // return with the router wrapped with
        // an extension containing the view engine.
        Ok(router.layer(Extension(ViewEngine::from(tera_engine))))
    }
}
