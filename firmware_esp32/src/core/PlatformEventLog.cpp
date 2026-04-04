#include "core/PlatformEventLog.h"

#include <stdio.h>
#include <string.h>

namespace smart_platform::core {

PlatformEventLog::PlatformEventLog()
    : nextLocalIndex_(1),
      count_(0),
      head_(0) {
    memset(localNodeId_, 0, sizeof(localNodeId_));
    memset(entries_, 0, sizeof(entries_));
}

void PlatformEventLog::begin(const char* localNodeId) {
    copyText(localNodeId_, sizeof(localNodeId_), localNodeId);
}

void PlatformEventLog::addLocal(const char* source,
                                const char* level,
                                const char* type,
                                const char* message,
                                const char* details) {
    PlatformLogEntry entry {};
    entry.localIndex = nextLocalIndex_++;
    entry.timestampMs = millis();
    entry.mirrored = false;
    snprintf(entry.localEventId, sizeof(entry.localEventId), "esp32-%05lu",
             static_cast<unsigned long>(entry.localIndex));
    copyText(entry.originNode, sizeof(entry.originNode), localNodeId_);
    copyText(entry.originEventId, sizeof(entry.originEventId), entry.localEventId);
    copyText(entry.source, sizeof(entry.source), source);
    copyText(entry.level, sizeof(entry.level), level);
    copyText(entry.type, sizeof(entry.type), type);
    copyText(entry.message, sizeof(entry.message), message);
    copyText(entry.details, sizeof(entry.details), details);
    writeEntry(entry);
}

bool PlatformEventLog::ingestRemote(const char* originNode,
                                    const char* originEventId,
                                    const char* source,
                                    const char* level,
                                    const char* type,
                                    const char* message,
                                    const char* details) {
    if (originNode == nullptr || originNode[0] == '\0' || originEventId == nullptr ||
        originEventId[0] == '\0') {
        return false;
    }

    if (hasRemoteEntry(originNode, originEventId)) {
        return false;
    }

    PlatformLogEntry entry {};
    entry.localIndex = nextLocalIndex_++;
    entry.timestampMs = millis();
    entry.mirrored = true;
    snprintf(entry.localEventId, sizeof(entry.localEventId), "esp32-%05lu",
             static_cast<unsigned long>(entry.localIndex));
    copyText(entry.originNode, sizeof(entry.originNode), originNode);
    copyText(entry.originEventId, sizeof(entry.originEventId), originEventId);
    copyText(entry.source, sizeof(entry.source), source);
    copyText(entry.level, sizeof(entry.level), level);
    copyText(entry.type, sizeof(entry.type), type);
    copyText(entry.message, sizeof(entry.message), message);
    copyText(entry.details, sizeof(entry.details), details);
    writeEntry(entry);
    return true;
}

size_t PlatformEventLog::count() const {
    return count_;
}

size_t PlatformEventLog::countLevel(const char* level) const {
    if (level == nullptr || level[0] == '\0') {
        return 0;
    }

    size_t matches = 0;
    for (size_t index = 0; index < count_; ++index) {
        const size_t logicalIndex = (head_ + kPlatformLogEntryCount - 1 - index) % kPlatformLogEntryCount;
        const PlatformLogEntry& entry = entries_[logicalIndex];
        if (strcmp(entry.level, level) == 0) {
            ++matches;
        }
    }

    return matches;
}

String PlatformEventLog::buildSnapshotJson(size_t limit) const {
    const size_t clampedLimit = limit == 0 ? 1 : limit;
    const size_t actualCount = count_ < clampedLimit ? count_ : clampedLimit;

    String json;
    json.reserve(2048);
    json += "{";
    json += "\"count\":";
    json += String(count_);
    json += ",\"limit\":";
    json += String(clampedLimit);
    json += ",\"entries\":[";

    bool first = true;
    for (size_t offset = 0; offset < actualCount; ++offset) {
        const size_t logicalIndex = (head_ + kPlatformLogEntryCount - 1 - offset) % kPlatformLogEntryCount;
        const PlatformLogEntry& entry = entries_[logicalIndex];

        if (!first) {
            json += ",";
        }

        json += "{";
        json += "\"event_id\":";
        appendJsonEscaped(json, entry.localEventId);
        json += ",\"timestamp_ms\":";
        json += String(entry.timestampMs);
        json += ",\"origin_node\":";
        appendJsonEscaped(json, entry.originNode);
        json += ",\"origin_event_id\":";
        appendJsonEscaped(json, entry.originEventId);
        json += ",\"mirrored\":";
        json += entry.mirrored ? "true" : "false";
        json += ",\"source\":";
        appendJsonEscaped(json, entry.source);
        json += ",\"level\":";
        appendJsonEscaped(json, entry.level);
        json += ",\"type\":";
        appendJsonEscaped(json, entry.type);
        json += ",\"message\":";
        appendJsonEscaped(json, entry.message);
        json += ",\"details\":";
        appendJsonEscaped(json, entry.details);
        json += "}";
        first = false;
    }

    json += "]}";
    return json;
}

void PlatformEventLog::writeEntry(const PlatformLogEntry& entry) {
    entries_[head_] = entry;
    head_ = (head_ + 1) % kPlatformLogEntryCount;
    if (count_ < kPlatformLogEntryCount) {
        ++count_;
    }
}

bool PlatformEventLog::hasRemoteEntry(const char* originNode, const char* originEventId) const {
    for (size_t index = 0; index < count_; ++index) {
        const size_t logicalIndex = (head_ + kPlatformLogEntryCount - 1 - index) % kPlatformLogEntryCount;
        const PlatformLogEntry& entry = entries_[logicalIndex];
        if (strcmp(entry.originNode, originNode) == 0 && strcmp(entry.originEventId, originEventId) == 0) {
            return true;
        }
    }
    return false;
}

void PlatformEventLog::copyText(char* destination, size_t destinationSize, const char* source) const {
    if (destination == nullptr || destinationSize == 0) {
        return;
    }

    if (source == nullptr) {
        destination[0] = '\0';
        return;
    }

    snprintf(destination, destinationSize, "%s", source);
}

void PlatformEventLog::appendJsonEscaped(String& target, const char* text) const {
    target += "\"";
    if (text != nullptr) {
        target += text;
    }
    target += "\"";
}

}  // namespace smart_platform::core
