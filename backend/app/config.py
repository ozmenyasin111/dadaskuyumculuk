from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    env: str = "dev"

    database_url: str = "postgresql+asyncpg://dadas:dadas_dev@localhost:5432/dadaskuyumculuk"

    finansveri_api_key: str = ""
    finansveri_base_url: str = "https://api.finansveri.com"

    jwt_secret: str = "dev_change_me_super_secret_jwt_signing_key_at_least_32_chars"
    jwt_expires_hours: int = 168
    jwt_algorithm: str = "HS256"

    admin_bootstrap_username: str = "admin"
    admin_bootstrap_password: str = "admin123"

    poll_interval_seconds: float = 1.0

    # Bayatlık (staleness) eşikleri: bir sembolün son güncellemesi bu süreden eskiyse
    # "donuk" sayılıp alternatif kaynağa geçilir. Altın/sarrafiye saniyede tıkladığı
    # için 3 dk; döviz çiftleri daha seyrek geldiği için 5 dk (boşuna geçiş olmasın).
    stale_threshold_gold_seconds: float = 180.0
    stale_threshold_doviz_seconds: float = 300.0

    # "Toptan donma" alarmı: ana + alternatif TÜM kaynakların en tazesi bile bu süreden
    # eskiyse (yani failover'ın geçebileceği canlı bir kaynak kalmadıysa) Telegram'a
    # tek seferlik uyarı atılır. Sabahki gibi finansveri'nin komple durduğu durumu yakalar.
    total_freeze_threshold_seconds: float = 600.0

    cors_origins: str = "http://localhost:3000"

    # Telegram bildirimi (finansveri eksik/0 veri başladı-düzeldi). Boşsa devre dışı.
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
