use sea_orm_migration::sea_query::types::Iden;
use std::fmt;

// default vector size
pub const DEFAULT_VECTOR_SIZE: usize = 1536;

// define a vector type with a fixed size
pub type VectorEmbedding = Vec<f32>;

// SeaORM vector type definition with default size
pub struct PGVectorType<const SIZE: usize>;

// implement Iden for SeaORM
impl<const SIZE: usize> Iden for PGVectorType<SIZE> {
    fn unquoted(&self, s: &mut dyn fmt::Write) {
        write!(s, "VECTOR({})", SIZE).unwrap(); // Dynamically set the dimension, default is 1536
    }
}
