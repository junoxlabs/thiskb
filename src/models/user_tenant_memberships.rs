use sea_orm::entity::prelude::*;
use super::_entities::user_tenant_memberships::{ActiveModel, Entity};
pub type UserTenantMemberships = Entity;

impl ActiveModelBehavior for ActiveModel {
    // extend activemodel below (keep comment for generators)
}
