#pragma once

// Этот файл не подключается в production build.
// Он нужен как верхнеуровневая карта крупных сущностей стороны ESP32.

namespace smart_platform::skeletons {

class Esp32DutyNodeBlueprint {
    // Главный дежурный узел платформы на стороне ESP32.
    // Собирает локальные блоки полива, сервиса, хранения и пробуждения peer-узла.
};

class LocalTriggerHubBlueprint {
    // Агрегирует дешевые по энергии локальные триггеры.
    // Сюда потом входят PIR, расписания, датчики среды и простые условия пробуждения turret-owner.
};

class PeerWakeCoordinatorBlueprint {
    // Решает, когда нужно будить Raspberry Pi.
    // Не анализирует vision сам, а только переводит cheap-trigger в wake-request.
};

class PowerSupervisorBlueprint {
    // Следит за состоянием питания, безопасным включением/отключением узлов и режимами энергосбережения.
    // В будущем именно здесь должен учитываться сценарий "почти мгновенного" пробуждения turret-owner.
};

class IrrigationCoordinatorBlueprint {
    // Верхний координационный слой локального Irrigation v1.
    // Объединяет зоны, датчики, сценарии ухода и локальную автоматику без привязки к UI.
};

class ServiceTestCoordinatorBlueprint {
    // Собирает локальные service/test профили стороны ESP32.
    // Сюда относится strobe_bench, локальная диагностика полива и ручные сервисные проверки.
};

class ContentStorageCoordinatorBlueprint {
    // Отвечает за mirrored content storage на стороне ESP32.
    // Легкий shell остается в LittleFS, тяжелый контент и библиотеки живут на SD.
};

class PeerShellClientBlueprint {
    // Держит peer-awareness для federated shell.
    // Не владеет чужими модулями, а только знает, где их canonical owner page.
};

}  // namespace smart_platform::skeletons
