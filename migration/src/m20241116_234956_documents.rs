use loco_rs::schema::table_auto_tz;
use sea_orm_migration::{prelude::*, schema::*};

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .create_table(
                table_auto_tz(Documents::Table)
                    .col(
                        ColumnDef::new(Documents::Id)
                            .uuid()
                            .extra("DEFAULT gen_random_uuid()")
                            .not_null()
                            .primary_key(),
                    )
                    .col(uuid(Documents::TenantId))
                    .col(uuid(Documents::KnowledgeBaseId))
                    .col(string(Documents::Name))
                    .col(string(Documents::ContentType))
                    .col(big_integer_null(Documents::FileSize))
                    .col(json_binary_null(Documents::Metadata))
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-documents-tenants")
                            .from(Documents::Table, Documents::TenantId)
                            .to(Tenants::Table, Tenants::Id)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-documents-knowledge_bases")
                            .from(Documents::Table, Documents::KnowledgeBaseId)
                            .to(KnowledgeBases::Table, KnowledgeBases::Id)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .to_owned(),
            )
            .await
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .drop_table(Table::drop().table(Documents::Table).to_owned())
            .await
    }
}

#[derive(DeriveIden)]
enum Documents {
    Table,
    Id,
    TenantId,
    KnowledgeBaseId,
    Name,
    ContentType,
    FileSize,
    Metadata,
    
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
