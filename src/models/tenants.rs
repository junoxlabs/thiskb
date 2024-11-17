use super::_entities::tenants::{ActiveModel, Entity};
use sea_orm::entity::prelude::*;
pub type Tenants = Entity;

impl ActiveModelBehavior for ActiveModel {
    // extend activemodel below (keep comment for generators)
}
