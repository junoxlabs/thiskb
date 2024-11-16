use sea_orm::entity::prelude::*;
use super::_entities::tenants::{ActiveModel, Entity};
pub type Tenants = Entity;

impl ActiveModelBehavior for ActiveModel {
    // extend activemodel below (keep comment for generators)
}
