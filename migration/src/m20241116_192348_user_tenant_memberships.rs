use loco_rs::schema::table_auto_tz;
use sea_orm_migration::{prelude::*, schema::*};

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .create_table(
                table_auto_tz(UserTenantMemberships::Table)
                    .primary_key(
                        Index::create()
                            .name("idx-user_tenant_memberships-refs-pk")
                            .table(UserTenantMemberships::Table)
                            .col(UserTenantMemberships::TenantId)
                            .col(UserTenantMemberships::UserId)
                            ,
                    )
                    .col(uuid(UserTenantMemberships::TenantId))
                    .col(integer(UserTenantMemberships::UserId))
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-user_tenant_memberships-tenants")
                            .from(UserTenantMemberships::Table, UserTenantMemberships::TenantId)
                            .to(Tenants::Table, Tenants::Id)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-user_tenant_memberships-users")
                            .from(UserTenantMemberships::Table, UserTenantMemberships::UserId)
                            .to(Users::Table, Users::Id)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .to_owned(),
            )
            .await
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .drop_table(Table::drop().table(UserTenantMemberships::Table).to_owned())
            .await
    }
}

#[derive(DeriveIden)]
enum UserTenantMemberships {
    Table,
    TenantId,
    UserId,
    
}


#[derive(DeriveIden)]
enum Tenants {
    Table,
    Id,
}
#[derive(DeriveIden)]
enum Users {
    Table,
    Id,
}
