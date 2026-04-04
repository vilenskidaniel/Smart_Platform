"""
Этот файл не является production runtime.
Он нужен как верхнеуровневая карта крупных сущностей стороны Raspberry Pi.
"""


class RaspberryPiTurretNodeBlueprint:
    """Главный turret-owner узел.

    Собирает turret runtime, vision-ветку, heavy-content mirror и federated shell стороны Raspberry Pi.
    """


class TurretStandbyManagerBlueprint:
    """Управляет быстрым к жизни состоянием turret-owner.

    С учетом требования почти мгновенного пробуждения этот слой важнее полного cold-start power gating.
    """


class VisionSessionManagerBlueprint:
    """Владеет жизненным циклом vision-сессии.

    Подготавливает запуск камеры, обработку кадра и завершение анализа без смешивания с UI.
    """


class TargetDecisionEngineBlueprint:
    """Превращает события наблюдения в решение.

    Здесь потом живут правила: ложное срабатывание, сопровождение цели, разрешение действия, отказ от действия.
    """


class TurretActionCoordinatorBlueprint:
    """Координирует turret actions.

    Соединяет motion, water, audio и combat strobe без прямой привязки к transport/UI.
    """


class TurretServiceCoordinatorBlueprint:
    """Собирает service/test контур turret-owner.

    Отвечает за локальные сервисные сценарии, диагностику и безопасные тестовые профили.
    """


class ContentMirrorCoordinatorBlueprint:
    """Ведет mirrored content storage стороны Raspberry Pi.

    Держит локальный content root с тем же layout, что и SD на ESP32.
    """


class PeerStateBridgeBlueprint:
    """Держит federated связь с ESP32.

    Сюда позже логично поместить ownership-aware sync, handoff context и обмен состояниями узлов.
    """
