from __future__ import annotations

from bridge_config import load_config
from bridge_state import BridgeState
from server import build_server
from sync_client import SyncClient


def main() -> None:
    config = load_config()
    state = BridgeState(
        node_id=config.node_id,
        shell_version=config.shell_version,
        local_shell_base_url=config.public_base_url,
        peer_shell_base_url=config.esp32_base_url,
        content_root=config.content_root,
    )
    sync_client = SyncClient(config=config, state=state)
    server = build_server(config=config, state=state, sync_client=sync_client)

    print("=== Smart Platform / Host Runtime ===")
    print(f"Shell node ID: {config.node_id}")
    print(f"Listen: http://{config.bind_host}:{config.bind_port}/")
    print(f"Public shell URL: {config.public_base_url}")
    print(f"Turret: http://{config.bind_host}:{config.bind_port}/turret")
    print(f"ESP32 peer base URL: {config.esp32_base_url}")
    print(f"Background sync enabled: {config.sync_enabled}")

    sync_client.start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        sync_client.stop()
        server.server_close()


if __name__ == "__main__":
    main()
