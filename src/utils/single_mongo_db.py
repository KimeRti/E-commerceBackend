from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from src.settings import config

from src.complaint.models import Complaint

_mongo_client = None

async def init_mongo_db():
    global _mongo_client
    try:
        if not _mongo_client:
            print(f"MongoDB URI: {config.mongo_uri}")  # Debug için
            _mongo_client = AsyncIOMotorClient(config.mongo_uri)
            print("MongoDB bağlantısı kuruldu")  # Debug için
        db = _mongo_client[config.mongo_db]
        print(f"MongoDB veritabanı seçildi: {config.mongo_db}")  # Debug için
        return db
    except Exception as e:
        print(f"MongoDB bağlantı hatası: {str(e)}")  # Debug için
        return None
