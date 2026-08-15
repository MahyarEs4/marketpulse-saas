import os
from decimal import Decimal


class Settings:
    TELEGRAM_BOT_TOKEN: str | None = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID: str | None = os.getenv("TELEGRAM_CHAT_ID")

    PRICE_CHANGE_ALERT_THRESHOLD_PERCENT: Decimal = Decimal(
        os.getenv("PRICE_CHANGE_ALERT_THRESHOLD_PERCENT", "5.0")
    )

    ALERT_CHANNEL_TELEGRAM: str = "telegram"


settings = Settings()
