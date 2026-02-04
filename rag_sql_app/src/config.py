from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    OPENAI_API_KEY: str

    pg_host: str = Field(alias="pg_host")
    pg_port: int = Field(alias="pg_port")
    pg_db: str = Field(alias="pg_db")
    pg_user: str = Field(alias="pg_user")
    pg_password: str = Field(alias="pg_password")

    CHROMA_PATH: str = "rag_sql_app/embeddings/chroma_store"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.pg_user}:{self.pg_password}"
            f"@{self.pg_host}:{self.pg_port}/{self.pg_db}"
        )

    class Config:
        env_file = ".env"
        extra = "forbid"   # catches typos early

settings = Settings()