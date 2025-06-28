from mongodb_migrations.base import BaseMigration
from pymongo import IndexModel, ASCENDING


class Migration(BaseMigration):

    IDX_CATALOGO_SELLERID_SKU = "idx_sellerid_sku"

    def upgrade(self):
        indexes = [
            IndexModel(
                [("seller_id", ASCENDING), ("sku", ASCENDING)],
                name=self.IDX_CATALOGO_SELLERID_SKU,
            )
        ]
        self.db.catalogo.create_indexes(indexes)

    def downgrade(self):
        self.db.catalogo.drop_index(self.IDX_CATALOGO_SELLERID_SKU)
    