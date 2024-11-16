use loco_rs::schema::table_auto_tz;
use sea_orm_migration::{prelude::*, schema::*};

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .create_table(
                table_auto_tz(KnowledgeBases::Table)
                    .col(
                        ColumnDef::new(KnowledgeBases::Id)
                            .uuid()
                            .extra("DEFAULT gen_random_uuid()")
                            .not_null()
                            .primary_key(),
                    )
                    .col(uuid(KnowledgeBases::TenantId))
                    .col(string(KnowledgeBases::Name))
                    .col(text_null(KnowledgeBases::Description))
                    .col(json_binary_null(KnowledgeBases::Metadata))
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-knowledge_bases-tenants")
                            .from(KnowledgeBases::Table, KnowledgeBases::TenantId)
                            .to(Tenants::Table, Tenants::Id)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .to_owned(),
            )
            .await
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .drop_table(Table::drop().table(KnowledgeBases::Table).to_owned())
            .await
    }
}

#[derive(DeriveIden)]
enum KnowledgeBases {
    Table,
    Id,
    TenantId,
    Name,
    Description,
    Metadata,
    
}


#[derive(DeriveIden)]
enum Tenants {
    Table,
    Id,
}
