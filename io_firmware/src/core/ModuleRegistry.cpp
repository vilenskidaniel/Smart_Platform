#include "core/ModuleRegistry.h"

#include <string.h>

namespace smart_platform::core {

namespace {

bool sameText(const char* left, const char* right) {
    if (left == nullptr || right == nullptr) {
        return false;
    }

    return strcmp(left, right) == 0;
}

}  // namespace

ModuleRegistry::ModuleRegistry() : count_(0) {
    clear();
}

void ModuleRegistry::clear() {
    memset(modules_, 0, sizeof(modules_));
    count_ = 0;
}

bool ModuleRegistry::add(const ModuleDescriptor& descriptor) {
    if (count_ >= kMaxModules) {
        return false;
    }

    modules_[count_] = descriptor;
    ++count_;
    return true;
}

size_t ModuleRegistry::count() const {
    return count_;
}

const ModuleDescriptor* ModuleRegistry::at(size_t index) const {
    if (index >= count_) {
        return nullptr;
    }

    return &modules_[index];
}

const ModuleDescriptor* ModuleRegistry::find(const char* moduleId) const {
    for (size_t index = 0; index < count_; ++index) {
        if (sameText(modules_[index].id, moduleId)) {
            return &modules_[index];
        }
    }

    return nullptr;
}

ModuleDescriptor* ModuleRegistry::findMutable(const char* moduleId) {
    for (size_t index = 0; index < count_; ++index) {
        if (sameText(modules_[index].id, moduleId)) {
            return &modules_[index];
        }
    }

    return nullptr;
}

bool ModuleRegistry::updateState(const char* moduleId, ModuleState state, BlockReason reason) {
    ModuleDescriptor* descriptor = findMutable(moduleId);
    if (descriptor == nullptr) {
        return false;
    }

    descriptor->state = state;
    descriptor->blockReason = reason;
    return true;
}

}  // namespace smart_platform::core
