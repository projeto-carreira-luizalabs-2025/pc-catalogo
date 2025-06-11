import asyncio

from bson.binary import UuidRepresentation
from bson.codec_options import CodecOptions, TypeCodec, TypeRegistry
from motor.core import AgnosticClient, AgnosticCollection, AgnosticDatabase
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import MongoDsn


class SetCodec(TypeCodec):
    python_type = set
    bson_type = 4

    def transform_python(self, value: list) -> list:
        return list(value)

    def transform_bson(self, value: set) -> list:
        return list(value)


class MongoDB:
    def __init__(self, db: AgnosticDatabase):
        self.db = db

    def __getitem__(self, name: str) -> AgnosticCollection:
        return self.db[name]


class MongoClient:
    def __init__(self, mongo_url: MongoDsn):
        self.mongo_url = mongo_url
        self.motor_client: AgnosticClient = AsyncIOMotorClient(str(mongo_url))
        self.motor_client.get_io_loop = asyncio.get_event_loop

    def close(self):
        self.motor_client.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            ...

    def get_default_database(self) -> MongoDB:
        type_registry = TypeRegistry([SetCodec()])
        codec_options: CodecOptions = CodecOptions(
            type_registry=type_registry, uuid_representation=UuidRepresentation.STANDARD, tz_aware=True
        )
        return MongoDB(self.motor_client.get_default_database(codec_options=codec_options))

    def __getitem__(self, name: str) -> MongoDB:
        return MongoDB(self.motor_client[name])

    def get_collection(self, name: str) -> AgnosticCollection:
        collection = self.get_default_database()[name]
        return collection
