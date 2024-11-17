use common::utils::pg_vector::{PGVectorType, DEFAULT_VECTOR_SIZE};
use loco_rs::schema::table_auto_tz;
use sea_orm_migration::{prelude::*, schema::*};

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .create_table(
                table_auto_tz(Chunks::Table)
                    .col(
                        ColumnDef::new(Chunks::Id)
                            .uuid()
                            .extra("DEFAULT gen_random_uuid()")
                            .not_null()
                            .primary_key(),
                    )
                    .col(uuid(Chunks::TenantId))
                    .col(uuid(Chunks::KnowledgeBaseId))
                    .col(uuid(Chunks::DocumentId))
                    .col(text(Chunks::Content))
                    .col(
                        ColumnDef::new(Chunks::Embedding)
                            .custom(PGVectorType::<DEFAULT_VECTOR_SIZE>) // entity type VectorEmbedding
                            .not_null(),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-chunks-tenants")
                            .from(Chunks::Table, Chunks::TenantId)
                            .to(Tenants::Table, Tenants::Id)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-chunks-knowledge_bases")
                            .from(Chunks::Table, Chunks::KnowledgeBaseId)
                            .to(KnowledgeBases::Table, KnowledgeBases::Id)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-chunks-documents")
                            .from(Chunks::Table, Chunks::DocumentId)
                            .to(Documents::Table, Documents::Id)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .to_owned(),
            )
            .await
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .drop_table(Table::drop().table(Chunks::Table).to_owned())
            .await
    }
}

#[derive(DeriveIden)]
enum Chunks {
    Table,
    Id,
    TenantId,
    KnowledgeBaseId,
    DocumentId,
    Content,
    Embedding,
}

#[derive(DeriveIden)]
enum Tenants {
    Table,
    Id,
}
#[derive(DeriveIden)]
enum KnowledgeBases {
    Table,
    Id,
}
#[derive(DeriveIden)]
enum Documents {
    Table,
    Id,
}
