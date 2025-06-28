import pytest
import pymongo

@pytest.fixture(autouse=True)
def clean_catalogo_collection():
    client = pymongo.MongoClient("mongodb://admin:admin@localhost:27018/test_db?authSource=admin")
    db = client.get_default_database()
    db["catalogo"].delete_many({})
    yield
    db["catalogo"].delete_many({})
    client.close()