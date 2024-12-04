from pydantic_settings import BaseSettings
from pydantic import Field


class Config(BaseSettings):
    sql_uri: str = Field(default="postgresql+asyncpg://postgres:cyc@192.168.1.102:5432/valshosting",
                         alias="DEF_SQL_URI")
    mongo_uri: str = Field(default="mongodb://localhost:27017")
    mongo_db: str = Field(default="valshosting")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    JWT_SECRET_KEY: str = Field(default="TvXrIhF1Abs5g7xTvXrIhF1Abs5g7xPzVsq46hpsPQuiX7PzVsq46hpsPQuiX7",
                                alias="DEF_JWT_SECRET_KEY")
    BASE_URL: str = Field(default="http://192.168.1.102:8000")


config: Config = Config()