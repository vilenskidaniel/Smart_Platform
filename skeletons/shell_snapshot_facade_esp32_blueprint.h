#pragma once

// Этот файл не входит в production build.
// Он нужен как planning-skeleton для ShellSnapshotFacade на стороне ESP32.

namespace smart_platform::skeletons {

class ShellSnapshotFacadeEsp32Blueprint {
    // Собирает shell-level snapshot из локальных источников ESP32.
    //
    // В этот слой позже логично стянуть:
    // - SystemCore
    // - PlatformEventLog
    // - StorageManager
    // - owner-aware summary локальных и peer-owned модулей
    //
    // Важно:
    // facade не должен знать про HTML и не должен сам принимать HTTP-запросы.
};

}  // namespace smart_platform::skeletons
