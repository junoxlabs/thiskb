//! `SeaORM` Entity, @generated by sea-orm-codegen 1.1.1

use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, PartialEq, DeriveEntityModel, Eq, Serialize, Deserialize)]
#[sea_orm(table_name = "tenants")]
pub struct Model {
    pub created_at: DateTimeWithTimeZone,
    pub updated_at: DateTimeWithTimeZone,
    #[sea_orm(primary_key, auto_increment = false)]
    pub id: Uuid,
    pub name: String,
    #[sea_orm(column_type = "JsonBinary")]
    pub metadata: Json,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {
    #[sea_orm(has_many = "super::user_tenant_memberships::Entity")]
    UserTenantMemberships,
}

impl Related<super::user_tenant_memberships::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::UserTenantMemberships.def()
    }
}

impl Related<super::users::Entity> for Entity {
    fn to() -> RelationDef {
        super::user_tenant_memberships::Relation::Users.def()
    }
    fn via() -> Option<RelationDef> {
        Some(
            super::user_tenant_memberships::Relation::Tenants
                .def()
                .rev(),
        )
    }
}
