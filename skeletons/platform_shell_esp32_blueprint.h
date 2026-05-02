#pragma once

// Этот файл не входит в production build.
// Он нужен как skeleton-карта крупных ролей Platform Shell на стороне ESP32.
// Методы намеренно не расписываются глубоко, чтобы сначала согласовать
// границы ответственности, а не плодить случайные детали реализации.

namespace smart_platform::skeletons {

class ShellSnapshotFacadeBlueprint {
    // Собирает shell-friendly snapshot из SystemCore, логов, статуса контента
    // и краткой диагностики текущего узла.
};

class ShellNavigationCoordinatorBlueprint {
    // Отвечает за owner-aware навигацию: локальный переход, handoff,
    // canonical URL и доступность peer-owned разделов.
};

class ShellHomePresenterBlueprint {
    // Описывает главную страницу shell: карточки узлов, быстрые входы,
    // предупреждения и понятное объяснение, что сейчас доступно.
};

class ShellSettingsPresenterBlueprint {
    // Описывает страницу настроек shell-уровня: язык, тема, базовые адреса,
    // сетевые параметры и задел под будущую авторизацию.
};

class ShellDiagnosticsPresenterBlueprint {
    // Описывает страницу диагностики: heartbeat, sync, ownership, faults,
    // degraded-причины и готовность storage/content слоя.
};

class ShellLogPresenterBlueprint {
    // Описывает страницу логов: локальные события, синхронизированные записи
    // и ручные действия пользователя.
};

class ShellContentPresenterBlueprint {
    // Описывает страницу Content Storage: LittleFS, SD, mirrored content,
    // readiness библиотек и доступность тяжелого контента.
};

class ShellHttpAdapterBlueprint {
    // Тонкий HTTP-адаптер shell.
    // Его задача — маршруты и склейка, а не хранение всей shell-логики
    // внутри одного гигантского класса.
};

}  // namespace smart_platform::skeletons
