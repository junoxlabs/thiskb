use sea_orm::entity::prelude::*;
use super::_entities::documents::{ActiveModel, Entity};
pub type Documents = Entity;

impl ActiveModelBehavior for ActiveModel {
    // extend activemodel below (keep comment for generators)
}
