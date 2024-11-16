use sea_orm::entity::prelude::*;
use super::_entities::knowledge_bases::{ActiveModel, Entity};
pub type KnowledgeBases = Entity;

impl ActiveModelBehavior for ActiveModel {
    // extend activemodel below (keep comment for generators)
}
