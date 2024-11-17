use super::_entities::documents::{ActiveModel, Entity};
use sea_orm::entity::prelude::*;
pub type Documents = Entity;

impl ActiveModelBehavior for ActiveModel {
    // extend activemodel below (keep comment for generators)
}
