from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    env: str = "dev"

    database_url: str = "postgresql+asyncpg://dadas:dadas_dev@localhost:5432/dadaskuyumculuk"

    finansveri_api_key: str = ""
    finansveri_base_url: str = "https://api.finansveri.com"

    # Yedek sağlayıcı: altinapi.com (finansveri çökünce/donunca otomatik geçilir).
    # Anahtar Railway env ALTINAPI_API_KEY ile ezilebilir; default canlı uptime için.
    altinapi_base_url: str = "https://altinapi.com/api/v1"
    altinapi_api_key: str = "hapi_121fc19abbd04900aa7ab95720932227"

    # finansveri TAMAMEN donuk sayılma eşiği: ana kaynaklarımız + alternatiflerinin
    # hiçbiri bu süreden daha taze değilse (finansveri bize tek taze sayı veremiyor)
    # tüm sistem altinapi'ye geçer. 10 dk (kısa duraklamalarda gereksiz geçiş/bildirim
    # olmasın diye 5 dk → 10 dk).
    provider_stale_seconds: float = 600.0

    jwt_secret: str = "dev_change_me_super_secret_jwt_signing_key_at_least_32_chars"
    jwt_expires_hours: int = 168
    jwt_algorithm: str = "HS256"

    admin_bootstrap_username: str = "admin"
    admin_bootstrap_password: str = "admin123"

    # Poll aralığı aktif sağlayıcıya göre dinamik: finansveri sınırsız → 1 sn (gerçek
    # zamanlı); altinapi Starter 30/dk → 3 sn (20/dk, 429 marjı). Worker active_provider'a
    # bakıp seçer.
    poll_interval_seconds: float = 1.0
    altinapi_poll_interval_seconds: float = 3.0

    # Bayatlık (staleness) eşikleri: bir sembolün son güncellemesi bu süreden eskiyse
    # "donuk" sayılıp alternatif kaynağa geçilir. Altın/sarrafiye ve döviz için 10 dk
    # (ana değerler 20-100 sn duraklayıp canlandığında gereksiz geçiş/bildirim olmasın
    # diye 5 dk → 10 dk). Belirli yavaş semboller için failover.PER_SYMBOL_THRESHOLD_SECONDS
    # ile özel (daha uzun) eşik verilebilir.
    stale_threshold_gold_seconds: float = 600.0
    stale_threshold_doviz_seconds: float = 600.0

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
