from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class BridgeConfig:
    bind_host: str
    bind_port: int
    public_base_url: str
    content_root: str
    node_id: str
    shell_version: str
    esp32_base_url: str
    sync_interval_sec: float
    sync_enabled: bool


def load_config() -> BridgeConfig:
    # Этот bootstrap пока специально остается без тяжелых зависимостей.
    # Поэтому конфигурацию берем из простых переменных окружения.
    bind_port = int(os.getenv("SMART_PLATFORM_RPI_PORT", "8080"))
    public_base_url = os.getenv(
        "SMART_PLATFORM_RPI_PUBLIC_BASE_URL",
        f"http://raspberrypi.local:{bind_port}",
    ).rstrip("/")
    default_content_root = str(Path(__file__).resolve().parent / "content")
    return BridgeConfig(
        bind_host=os.getenv("SMART_PLATFORM_RPI_HOST", "0.0.0.0"),
        bind_port=bind_port,
        public_base_url=public_base_url,
        content_root=os.getenv("SMART_PLATFORM_RPI_CONTENT_ROOT", default_content_root),
        node_id=os.getenv("SMART_PLATFORM_RPI_NODE_ID", "rpi-turret"),
        shell_version=os.getenv("SMART_PLATFORM_UI_VERSION", "0.1.0"),
        esp32_base_url=os.getenv("SMART_PLATFORM_ESP32_BASE_URL", "http://192.168.4.1").rstrip("/"),
        sync_interval_sec=float(os.getenv("SMART_PLATFORM_SYNC_INTERVAL_SEC", "2.0")),
        sync_enabled=_env_bool("SMART_PLATFORM_SYNC_ENABLED", True),
    )
