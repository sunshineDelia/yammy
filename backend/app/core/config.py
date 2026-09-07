from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "南昌旅游美食推荐平台"
    database_url: str = (
        "mysql+pymysql://root:password@localhost:3306/nanchang_travel?charset=utf8mb4"
    )
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"


settings = Settings()
