"""
Этот файл не является production runtime.
Он нужен как planning-skeleton для ShellSnapshotFacade на стороне Raspberry Pi.
"""


class ShellSnapshotFacadeRaspberryPiBlueprint:
    """Собирает shell-level snapshot из локальных источников Raspberry Pi.

    Позже сюда логично стянуть:
    - BridgeState
    - platform log summary
    - sync summary
    - content root readiness
    - owner-aware module cards

    Важно:
    facade не должен быть HTTP server и не должен рисовать HTML.
    """
