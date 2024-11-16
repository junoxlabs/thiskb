#![allow(elided_lifetimes_in_paths)]
#![allow(clippy::wildcard_imports)]
pub use sea_orm_migration::prelude::*;

mod m20220101_000001_users;

mod m20241116_185457_tenants;
mod m20241116_192348_user_tenant_memberships;
mod m20241116_200701_knowledge_bases;
pub struct Migrator;

#[async_trait::async_trait]
impl MigratorTrait for Migrator {
    fn migrations() -> Vec<Box<dyn MigrationTrait>> {
        vec![
            // inject-below (do not remove this comment)
            Box::new(m20241116_200701_knowledge_bases::Migration),
            Box::new(m20241116_192348_user_tenant_memberships::Migration),
            Box::new(m20241116_185457_tenants::Migration),
            Box::new(m20220101_000001_users::Migration),
            // inject-above (do not remove this comment)
        ]
    }
}