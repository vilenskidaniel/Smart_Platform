#pragma once

#include <stddef.h>

#include "core/SystemCoreTypes.h"

namespace smart_platform::core {

class ModuleRegistry {
public:
    static constexpr size_t kMaxModules = 16;

    ModuleRegistry();

    void clear();
    bool add(const ModuleDescriptor& descriptor);
    size_t count() const;

    const ModuleDescriptor* at(size_t index) const;
    const ModuleDescriptor* find(const char* moduleId) const;
    ModuleDescriptor* findMutable(const char* moduleId);

    bool updateState(const char* moduleId, ModuleState state, BlockReason reason);

private:
    ModuleDescriptor modules_[kMaxModules];
    size_t count_;
};

}  // namespace smart_platform::core
