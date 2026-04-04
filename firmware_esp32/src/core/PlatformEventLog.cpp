#include "core/PlatformEventLog.h"

#include <ctype.h>
#include <stdio.h>
#include <string.h>

namespace smart_platform::core {

namespace {

bool textEquals(const char* left, const char* right) {
    if (left == nullptr || right == nullptr) {
        return false;
    }
    return strcmp(left, right) == 0;
}

bool textEndsWith(const char* text, const char* suffix) {
    if (text == nullptr || suffix == nullptr) {
        return false;
    }

    const size_t textLength = strlen(text);
    const size_t suffixLength = strlen(suffix);
    if (suffixLength > textLength) {
        return false;
    }

    return strcmp(text + textLength - suffixLength, suffix) == 0;
}

String trimCopy(String value) {
    value.trim();
    return value;
}

bool isJsonObjectString(const String& value) {
    return value.startsWith("{") && value.endsWith("}");
}

void appendQuotedJson(String& target, const String& text) {
    target += "\"";
    for (size_t index = 0; index < text.length(); ++index) {
        const char current = text[index];
        switch (current) {
            case '\\':
            case '"':
                target += "\\";
                target += current;
                break;
            case '\n':
                target += "\\n";
                break;
            case '\r':
                target += "\\r";
                break;
            case '\t':
                target += "\\t";
                break;
            default:
                target += current;
                break;
        }
    }
    target += "\"";
}

void appendQuotedJson(String& target, const char* text) {
    appendQuotedJson(target, String(text != nullptr ? text : ""));
}

bool isIntegerValue(const String& value) {
    if (value.length() == 0) {
        return false;
    }

    size_t index = 0;
    if (value[0] == '-') {
        if (value.length() == 1) {
            return false;
        }
        index = 1;
    }

    for (; index < value.length(); ++index) {
        if (!isdigit(static_cast<unsigned char>(value[index]))) {
            return false;
        }
    }

    return true;
}

void appendScalarJson(String& target, String value) {
    value = trimCopy(value);
    if ((value.startsWith("\"") && value.endsWith("\"")) ||
        (value.startsWith("'") && value.endsWith("'"))) {
        value = value.substring(1, value.length() - 1);
    }

    if (value.equalsIgnoreCase("true")) {
        target += "true";
        return;
    }
    if (value.equalsIgnoreCase("false")) {
        target += "false";
        return;
    }
    if (isIntegerValue(value)) {
        target += value;
        return;
    }

    appendQuotedJson(target, value);
}

String extractJsonLikeValue(const String& details, const char* key) {
    if (key == nullptr || key[0] == '\0') {
        return "";
    }

    const String keyPattern = String("\"") + key + "\"";
    const int keyIndex = details.indexOf(keyPattern);
    if (keyIndex < 0) {
        return "";
    }

    int cursor = details.indexOf(':', keyIndex + static_cast<int>(keyPattern.length()));
    if (cursor < 0) {
        return "";
    }
    cursor += 1;
    while (cursor < static_cast<int>(details.length()) &&
           isspace(static_cast<unsigned char>(details[cursor]))) {
        cursor += 1;
    }
    if (cursor >= static_cast<int>(details.length())) {
        return "";
    }

    if (details[cursor] == '"') {
        cursor += 1;
        String value;
        while (cursor < static_cast<int>(details.length())) {
            const char current = details[cursor];
            if (current == '"' && details[cursor - 1] != '\\') {
                break;
            }
            value += current;
            cursor += 1;
        }
        return value;
    }

    int end = cursor;
    while (end < static_cast<int>(details.length()) && details[end] != ',' && details[end] != '}') {
        end += 1;
    }
    return trimCopy(details.substring(cursor, end));
}

String extractKeyValueValue(const String& details, const char* key) {
    if (key == nullptr || key[0] == '\0') {
        return "";
    }

    const String pattern = String(key) + "=";
    int cursor = details.indexOf(pattern);
    if (cursor < 0) {
        return "";
    }

    cursor += static_cast<int>(pattern.length());
    int end = details.indexOf(',', cursor);
    if (end < 0) {
        end = static_cast<int>(details.length());
    }
    return trimCopy(details.substring(cursor, end));
}

String extractDetailValue(const char* details, const char* key) {
    String detailText = trimCopy(String(details != nullptr ? details : ""));
    if (detailText.length() == 0) {
        return "";
    }

    const String jsonValue = extractJsonLikeValue(detailText, key);
    if (jsonValue.length() > 0) {
        return jsonValue;
    }
    return extractKeyValueValue(detailText, key);
}

String extractAliasedDetailValue(const char* details, const char* primaryKey, const char* alternateKey) {
    const String primary = extractDetailValue(details, primaryKey);
    if (primary.length() > 0) {
        return primary;
    }
    if (alternateKey == nullptr || alternateKey[0] == '\0') {
        return "";
    }
    return extractDetailValue(details, alternateKey);
}

bool extractDetailBool(const char* details, const char* key, bool& outValue) {
    const String value = extractDetailValue(details, key);
    if (value.length() == 0) {
        return false;
    }

    if (value.equalsIgnoreCase("true") || value == "1") {
        outValue = true;
        return true;
    }
    if (value.equalsIgnoreCase("false") || value == "0") {
        outValue = false;
        return true;
    }
    return false;
}

bool extractDetailLong(const char* details, const char* key, long& outValue) {
    const String value = extractDetailValue(details, key);
    if (!isIntegerValue(value)) {
        return false;
    }

    outValue = value.toInt();
    return true;
}

String buildParametersJson(const char* details) {
    String detailText = trimCopy(String(details != nullptr ? details : ""));
    if (detailText.length() == 0) {
        return "{}";
    }
    if (isJsonObjectString(detailText)) {
        return detailText;
    }

    String json = "{";
    bool appended = false;
    int cursor = 0;
    while (cursor < static_cast<int>(detailText.length())) {
        int comma = detailText.indexOf(',', cursor);
        if (comma < 0) {
            comma = static_cast<int>(detailText.length());
        }
        String chunk = trimCopy(detailText.substring(cursor, comma));
        cursor = comma + 1;

        const int separator = chunk.indexOf('=');
        if (separator <= 0) {
            if (!appended) {
                String fallback = "{\"raw\":";
                appendQuotedJson(fallback, detailText);
                fallback += "}";
                return fallback;
            }
            continue;
        }

        const String key = trimCopy(chunk.substring(0, separator));
        const String value = trimCopy(chunk.substring(separator + 1));
        if (key.length() == 0) {
            continue;
        }

        String canonicalKey = key;
        if (canonicalKey == "case") {
            canonicalKey = "case_id";
        } else if (canonicalKey == "module") {
            canonicalKey = "module_id";
        } else if (canonicalKey == "result") {
            canonicalKey = "test_result";
        }

        if (appended) {
            json += ",";
        }
        appendQuotedJson(json, canonicalKey);
        json += ":";
        appendScalarJson(json, value);
        appended = true;
    }

    if (!appended) {
        String fallback = "{\"raw\":";
        appendQuotedJson(fallback, detailText);
        fallback += "}";
        return fallback;
    }

    json += "}";
    return json;
}

const char* inferSurface(const char* source) {
    if (textEquals(source, "turret_scenarios") || textEquals(source, "strobe_bench") ||
        textEquals(source, "irrigation_service") || textEquals(source, "service_mode")) {
        return "laboratory";
    }
    if (textEquals(source, "turret_runtime") || textEquals(source, "turret_driver_layer") ||
        textEquals(source, "turret_bridge") || textEquals(source, "strobe")) {
        return "turret";
    }
    if (textEquals(source, "irrigation")) {
        return "irrigation";
    }
    if (textEquals(source, "system_shell") || textEquals(source, "sync_core")) {
        return "system";
    }
    return "unknown";
}

const char* inferDefaultMode(const char* surface) {
    if (textEquals(surface, "laboratory")) {
        return "service_test";
    }
    if (textEquals(surface, "turret") || textEquals(surface, "irrigation")) {
        return "product_runtime";
    }
    if (textEquals(surface, "system")) {
        return "system";
    }
    return "unknown";
}

String inferSourceMode(const char* surface, const char* details) {
    const String mode = extractDetailValue(details, "mode");
    if (mode.length() > 0) {
        return mode;
    }
    const String activeMode = extractDetailValue(details, "active_mode");
    if (activeMode.length() > 0) {
        return activeMode;
    }
    const String reportedMode = extractDetailValue(details, "reported_mode");
    if (reportedMode.length() > 0) {
        return reportedMode;
    }
    return inferDefaultMode(surface);
}

String inferModuleId(const char* source, const char* details) {
    const String explicitModule = extractAliasedDetailValue(details, "module_id", "module");
    if (explicitModule.length() > 0) {
        return explicitModule;
    }
    if (textEquals(source, "turret_runtime") || textEquals(source, "turret_scenarios") ||
        textEquals(source, "turret_driver_layer") || textEquals(source, "turret_bridge")) {
        return "turret_bridge";
    }
    if (textEquals(source, "strobe") || textEquals(source, "strobe_bench") ||
        textEquals(source, "irrigation") || textEquals(source, "irrigation_service") ||
        textEquals(source, "system_shell") || textEquals(source, "sync_core") ||
        textEquals(source, "service_mode")) {
        return String(source);
    }
    return (source != nullptr && source[0] != '\0') ? String(source) : String("unknown");
}

const char* inferEntryType(const char* source, const char* rawType, const char* details) {
    if ((rawType != nullptr && strncmp(rawType, "testcase_", 9) == 0) ||
        (extractAliasedDetailValue(details, "case_id", "case").length() > 0 &&
         extractAliasedDetailValue(details, "test_result", "result").length() > 0)) {
        return "testcase";
    }
    if (textEquals(rawType, "operator_note")) {
        return "operator_note";
    }
    if (rawType != nullptr && strncmp(rawType, "scenario_", 9) == 0) {
        return "scenario";
    }
    if (rawType != nullptr && strstr(rawType, "interlock") != nullptr) {
        return "interlock";
    }
    if (rawType != nullptr && strstr(rawType, "mode") != nullptr) {
        return "mode_change";
    }
    if (textEquals(source, "sync_core")) {
        return "sync";
    }
    if (rawType != nullptr &&
        (strstr(rawType, "subsystem") != nullptr || strstr(rawType, "flag") != nullptr ||
         strstr(rawType, "strobe_") != nullptr || strstr(rawType, "irrigation_") != nullptr ||
         strstr(rawType, "driver_") != nullptr)) {
        return "action";
    }
    return "event";
}

bool failedStepsPresent(const char* details) {
    const String detailText = trimCopy(String(details != nullptr ? details : ""));
    if (detailText.length() == 0 || detailText.indexOf("failed_steps") < 0) {
        return false;
    }
    return detailText.indexOf("failed_steps=[]") < 0 &&
           detailText.indexOf("\"failed_steps\":[]") < 0 &&
           detailText.indexOf("\"failed_steps\": []") < 0;
}

const char* inferResult(const PlatformLogEntry& entry) {
    const String testcaseResult = extractAliasedDetailValue(entry.details, "test_result", "result");
    if (testcaseResult.equalsIgnoreCase("pass")) {
        return "pass";
    }
    if (testcaseResult.equalsIgnoreCase("fail")) {
        return "fail";
    }
    if (testcaseResult.equalsIgnoreCase("warn")) {
        return "warn";
    }

    bool accepted = false;
    if (extractDetailBool(entry.details, "accepted", accepted)) {
        return accepted ? "accepted" : "rejected";
    }
    if (textEndsWith(entry.type, "_rejected")) {
        return "rejected";
    }
    if (textEndsWith(entry.type, "_started")) {
        return "started";
    }
    if (textEndsWith(entry.type, "_finished")) {
        return failedStepsPresent(entry.details) ? "completed_with_warnings" : "completed";
    }
    if (textEquals(entry.level, "error")) {
        return "failed";
    }
    if (textEquals(entry.level, "warning") || textEquals(entry.level, "warn")) {
        return "attention";
    }
    return "recorded";
}

bool inferDurationMs(const char* details, long& outValue) {
    return extractDetailLong(details, "duration_ms", outValue) ||
           extractDetailLong(details, "runtime_ms", outValue) ||
           extractDetailLong(details, "active_time_ms", outValue);
}

String humanizeType(const char* rawType, const char* details) {
    String text = rawType != nullptr ? rawType : "";
    if (text.length() == 0) {
        return "Event";
    }
    if (text == "testcase_result_recorded") {
        const String caseId = extractAliasedDetailValue(details, "case_id", "case");
        if (caseId.length() > 0) {
            return String("Testcase ") + caseId;
        }
        return "Testcase Result";
    }

    String result;
    result.reserve(text.length() + 4);
    bool capitalizeNext = true;
    for (size_t index = 0; index < text.length(); ++index) {
        const char current = text[index];
        if (current == '_') {
            result += ' ';
            capitalizeNext = true;
            continue;
        }
        result += capitalizeNext ? static_cast<char>(toupper(static_cast<unsigned char>(current))) : current;
        capitalizeNext = false;
    }
    return result;
}

void appendSummaryCount(String& json, const char* key, size_t value, bool& first) {
    if (value == 0) {
        return;
    }
    if (!first) {
        json += ",";
    }
    appendQuotedJson(json, key);
    json += ":";
    json += String(value);
    first = false;
}

String normalizeFilterValue(const char* value) {
    String text = trimCopy(String(value != nullptr ? value : ""));
    text.toLowerCase();
    if (text == "all") {
        return "";
    }
    return text;
}

bool matchesFilterValue(const String& actual, const String& filter) {
    return filter.length() == 0 || actual.equalsIgnoreCase(filter);
}

}  // namespace

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

String PlatformEventLog::buildReportsJson(size_t limit,
                                          const char* surfaceFilter,
                                          const char* entryTypeFilter,
                                          const char* severityFilter,
                                          const char* originNodeFilter) const {
    const size_t clampedLimit = limit == 0 ? 1 : limit;
    const String normalizedSurfaceFilter = normalizeFilterValue(surfaceFilter);
    const String normalizedEntryTypeFilter = normalizeFilterValue(entryTypeFilter);
    const String normalizedSeverityFilter = normalizeFilterValue(severityFilter);
    const String normalizedOriginNodeFilter = normalizeFilterValue(originNodeFilter);

    size_t warningCount = 0;
    size_t errorCount = 0;
    size_t surfaceLaboratory = 0;
    size_t surfaceTurret = 0;
    size_t surfaceIrrigation = 0;
    size_t surfaceSystem = 0;
    size_t surfaceUnknown = 0;
    size_t typeOperatorNote = 0;
    size_t typeTestcase = 0;
    size_t typeScenario = 0;
    size_t typeInterlock = 0;
    size_t typeModeChange = 0;
    size_t typeSync = 0;
    size_t typeAction = 0;
    size_t typeEvent = 0;
    size_t originLocal = 0;
    size_t originPeer = 0;
    size_t originOther = 0;
    size_t matchedCount = 0;
    size_t visibleCount = 0;

    String json;
    json.reserve(4096);
    json += "{";
    json += "\"schema_version\":\"reports-feed.v1\",";
    json += "\"source_kind\":\"platform_log_baseline\",";
    json += "\"count\":0";
    json += ",\"limit\":";
    json += String(clampedLimit);
    json += ",\"filters\":{";
    bool firstFilter = true;
    if (normalizedSurfaceFilter.length() > 0) {
        appendQuotedJson(json, "surface");
        json += ":";
        appendQuotedJson(json, normalizedSurfaceFilter);
        firstFilter = false;
    }
    if (normalizedEntryTypeFilter.length() > 0) {
        if (!firstFilter) {
            json += ",";
        }
        appendQuotedJson(json, "entry_type");
        json += ":";
        appendQuotedJson(json, normalizedEntryTypeFilter);
        firstFilter = false;
    }
    if (normalizedSeverityFilter.length() > 0) {
        if (!firstFilter) {
            json += ",";
        }
        appendQuotedJson(json, "severity");
        json += ":";
        appendQuotedJson(json, normalizedSeverityFilter);
        firstFilter = false;
    }
    if (normalizedOriginNodeFilter.length() > 0) {
        if (!firstFilter) {
            json += ",";
        }
        appendQuotedJson(json, "origin_node");
        json += ":";
        appendQuotedJson(json, normalizedOriginNodeFilter);
    }
    json += "}";
    json += ",\"entries\":[";

    bool firstEntry = true;
    for (size_t offset = 0; offset < count_; ++offset) {
        const size_t logicalIndex = (head_ + kPlatformLogEntryCount - 1 - offset) % kPlatformLogEntryCount;
        const PlatformLogEntry& entry = entries_[logicalIndex];
        const char* surface = inferSurface(entry.source);
        const String moduleId = inferModuleId(entry.source, entry.details);
        const char* entryType = inferEntryType(entry.source, entry.type, entry.details);
        const char* result = inferResult(entry);
        const String sourceMode = inferSourceMode(surface, entry.details);
        const String parametersJson = buildParametersJson(entry.details);
        const String title = humanizeType(entry.type, entry.details);
        if (!matchesFilterValue(String(surface), normalizedSurfaceFilter) ||
            !matchesFilterValue(String(entryType), normalizedEntryTypeFilter) ||
            !matchesFilterValue(String(entry.level), normalizedSeverityFilter) ||
            !matchesFilterValue(String(entry.originNode), normalizedOriginNodeFilter)) {
            continue;
        }

        matchedCount += 1;
        if (visibleCount >= clampedLimit) {
            continue;
        }

        if (!firstEntry) {
            json += ",";
        }

        json += "{";
        json += "\"report_id\":\"report-";
        json += entry.localEventId;
        json += "\",\"event_id\":";
        appendQuotedJson(json, entry.localEventId);
        json += ",\"timestamp_ms\":";
        json += String(entry.timestampMs);
        json += ",\"origin_node\":";
        appendQuotedJson(json, entry.originNode);
        json += ",\"mirrored\":";
        json += entry.mirrored ? "true" : "false";
        json += ",\"source\":";
        appendQuotedJson(json, entry.source);
        json += ",\"entry_type\":";
        appendQuotedJson(json, entryType);
        json += ",\"source_surface\":";
        appendQuotedJson(json, surface);
        json += ",\"source_mode\":";
        appendQuotedJson(json, sourceMode);
        json += ",\"module_id\":";
        appendQuotedJson(json, moduleId);
        json += ",\"title\":";
        appendQuotedJson(json, title);
        json += ",\"message\":";
        appendQuotedJson(json, entry.message);
        json += ",\"severity\":";
        appendQuotedJson(json, entry.level);
        json += ",\"result\":";
        appendQuotedJson(json, result);

        long durationMs = 0;
        json += ",\"duration_ms\":";
        if (inferDurationMs(entry.details, durationMs)) {
            json += String(durationMs);
        } else {
            json += "null";
        }

        json += ",\"parameters\":";
        json += parametersJson;
        json += ",\"raw_type\":";
        appendQuotedJson(json, entry.type);
        json += "}";
        firstEntry = false;
        visibleCount += 1;

        if (textEquals(entry.level, "warning") || textEquals(entry.level, "warn")) {
            ++warningCount;
        } else if (textEquals(entry.level, "error")) {
            ++errorCount;
        }

        if (textEquals(surface, "laboratory")) {
            ++surfaceLaboratory;
        } else if (textEquals(surface, "turret")) {
            ++surfaceTurret;
        } else if (textEquals(surface, "irrigation")) {
            ++surfaceIrrigation;
        } else if (textEquals(surface, "system")) {
            ++surfaceSystem;
        } else {
            ++surfaceUnknown;
        }

        if (textEquals(entryType, "operator_note")) {
            ++typeOperatorNote;
        } else if (textEquals(entryType, "testcase")) {
            ++typeTestcase;
        } else if (textEquals(entryType, "scenario")) {
            ++typeScenario;
        } else if (textEquals(entryType, "interlock")) {
            ++typeInterlock;
        } else if (textEquals(entryType, "mode_change")) {
            ++typeModeChange;
        } else if (textEquals(entryType, "sync")) {
            ++typeSync;
        } else if (textEquals(entryType, "action")) {
            ++typeAction;
        } else {
            ++typeEvent;
        }

        if (textEquals(entry.originNode, localNodeId_)) {
            ++originLocal;
        } else if (textEquals(entry.originNode, "rpi-turret") || textEquals(entry.originNode, "esp32-main")) {
            ++originPeer;
        } else {
            ++originOther;
        }
    }

    json += "],\"summary\":{";
    json += "\"warning_count\":";
    json += String(warningCount);
    json += ",\"error_count\":";
    json += String(errorCount);
    json += ",\"surfaces\":{";
    bool firstSurface = true;
    appendSummaryCount(json, "laboratory", surfaceLaboratory, firstSurface);
    appendSummaryCount(json, "turret", surfaceTurret, firstSurface);
    appendSummaryCount(json, "irrigation", surfaceIrrigation, firstSurface);
    appendSummaryCount(json, "system", surfaceSystem, firstSurface);
    appendSummaryCount(json, "unknown", surfaceUnknown, firstSurface);
    json += "},\"entry_types\":{";
    bool firstEntryType = true;
    appendSummaryCount(json, "operator_note", typeOperatorNote, firstEntryType);
    appendSummaryCount(json, "testcase", typeTestcase, firstEntryType);
    appendSummaryCount(json, "scenario", typeScenario, firstEntryType);
    appendSummaryCount(json, "interlock", typeInterlock, firstEntryType);
    appendSummaryCount(json, "mode_change", typeModeChange, firstEntryType);
    appendSummaryCount(json, "sync", typeSync, firstEntryType);
    appendSummaryCount(json, "action", typeAction, firstEntryType);
    appendSummaryCount(json, "event", typeEvent, firstEntryType);
    json += "},\"origin_nodes\":{";
    bool firstOrigin = true;
    appendSummaryCount(json, localNodeId_, originLocal, firstOrigin);
    appendSummaryCount(json, "peer", originPeer, firstOrigin);
    appendSummaryCount(json, "other", originOther, firstOrigin);
    json += "}}";
    json += "}";

    const String countPattern = "\"count\":0";
    const int countIndex = json.indexOf(countPattern);
    if (countIndex >= 0) {
        json.remove(countIndex, static_cast<unsigned int>(countPattern.length()));
        json = json.substring(0, countIndex) + "\"count\":" + String(matchedCount) + json.substring(countIndex);
    }
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
