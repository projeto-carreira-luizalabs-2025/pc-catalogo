from mongodb_migrations.base import BaseMigration
from pymongo import IndexModel, ASCENDING


class Migration(BaseMigration):

    IDX_SOMETHING_SELLERID_SKU = "idx_sellerid_sku"

    def upgrade(self):
        indexes = [
            IndexModel(
                [("seller_id", ASCENDING), ("sku", ASCENDING)],
                name=self.IDX_SOMETHING_SELLERID_SKU,
            )
        ]
        self.db.something.create_indexes(indexes)

    def downgrade(self):
        self.db.something.drop_index(self.IDX_SOMETHING_SELLERID_SKU)
