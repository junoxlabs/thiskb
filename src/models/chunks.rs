use super::_entities::chunks::{ActiveModel, Entity};
use sea_orm::entity::prelude::*;
pub type Chunks = Entity;

impl ActiveModelBehavior for ActiveModel {
    // extend activemodel below (keep comment for generators)
}
