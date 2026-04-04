#pragma once

#include <Arduino.h>
#include <stddef.h>
#include <stdint.h>

namespace smart_platform::core {

constexpr size_t kPlatformLogSourceMaxLength = 24;
constexpr size_t kPlatformLogLevelMaxLength = 12;
constexpr size_t kPlatformLogTypeMaxLength = 32;
constexpr size_t kPlatformLogMessageMaxLength = 80;
constexpr size_t kPlatformLogDetailMaxLength = 128;
constexpr size_t kPlatformLogOriginNodeMaxLength = 24;
constexpr size_t kPlatformLogOriginEventIdMaxLength = 24;
constexpr size_t kPlatformLogEntryCount = 64;

struct PlatformLogEntry {
    uint32_t localIndex;
    uint32_t timestampMs;
    bool mirrored;
    char localEventId[kPlatformLogOriginEventIdMaxLength];
    char originNode[kPlatformLogOriginNodeMaxLength];
    char originEventId[kPlatformLogOriginEventIdMaxLength];
    char source[kPlatformLogSourceMaxLength];
    char level[kPlatformLogLevelMaxLength];
    char type[kPlatformLogTypeMaxLength];
    char message[kPlatformLogMessageMaxLength];
    char details[kPlatformLogDetailMaxLength];
};

class PlatformEventLog {
public:
    PlatformEventLog();

    void begin(const char* localNodeId);
    void addLocal(const char* source,
                  const char* level,
                  const char* type,
                  const char* message,
                  const char* details = nullptr);
    bool ingestRemote(const char* originNode,
                      const char* originEventId,
                      const char* source,
                      const char* level,
                      const char* type,
                      const char* message,
                      const char* details = nullptr);

    size_t count() const;
    size_t countLevel(const char* level) const;
    String buildSnapshotJson(size_t limit) const;
    String buildReportsJson(size_t limit) const;

private:
    void writeEntry(const PlatformLogEntry& entry);
    bool hasRemoteEntry(const char* originNode, const char* originEventId) const;
    void copyText(char* destination, size_t destinationSize, const char* source) const;
    void appendJsonEscaped(String& target, const char* text) const;

    char localNodeId_[kPlatformLogOriginNodeMaxLength];
    PlatformLogEntry entries_[kPlatformLogEntryCount];
    uint32_t nextLocalIndex_;
    size_t count_;
    size_t head_;
};

}  // namespace smart_platform::core
