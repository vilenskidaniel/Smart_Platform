#include "storage/StorageManager.h"

#include <FS.h>
#include <SD.h>

#ifndef SMART_PLATFORM_SD_CS_PIN
#define SMART_PLATFORM_SD_CS_PIN 5
#endif

namespace smart_platform::storage {

StorageManager::StorageManager()
    : sdReady_(false),
      assetsReady_(false),
      audioReady_(false),
      animationsReady_(false),
      librariesReady_(false),
      csPin_(SMART_PLATFORM_SD_CS_PIN) {
}

bool StorageManager::begin() {
#if defined(SMART_PLATFORM_SD_ENABLED) && SMART_PLATFORM_SD_ENABLED
    sdReady_ = SD.begin(csPin_);
    if (!sdReady_) {
        assetsReady_ = false;
        audioReady_ = false;
        animationsReady_ = false;
        librariesReady_ = false;
        return false;
    }

    // На SD держим только тяжелый контент и крупные библиотеки данных.
    // Сам shell по-прежнему может жить в LittleFS как легкий fallback/entrypoint.
    assetsReady_ = directoryExists("/assets");
    audioReady_ = directoryExists("/audio");
    animationsReady_ = directoryExists("/animations");
    librariesReady_ = directoryExists("/libraries");
    return true;
#else
    sdReady_ = false;
    assetsReady_ = false;
    audioReady_ = false;
    animationsReady_ = false;
    librariesReady_ = false;
    return false;
#endif
}

bool StorageManager::sdReady() const {
    return sdReady_;
}

bool StorageManager::assetsReady() const {
    return assetsReady_;
}

bool StorageManager::audioReady() const {
    return audioReady_;
}

bool StorageManager::animationsReady() const {
    return animationsReady_;
}

bool StorageManager::librariesReady() const {
    return librariesReady_;
}

uint8_t StorageManager::csPin() const {
    return csPin_;
}

bool StorageManager::isManagedContentPath(const String& path) const {
    if (path.indexOf("..") >= 0) {
        return false;
    }

    return hasPrefix(path, "/assets/") || path == "/assets" || hasPrefix(path, "/audio/") ||
           path == "/audio" || hasPrefix(path, "/animations/") || path == "/animations" ||
           hasPrefix(path, "/libraries/") || path == "/libraries";
}

bool StorageManager::hasManagedContent() const {
    return assetsReady_ || audioReady_ || animationsReady_ || librariesReady_;
}

bool StorageManager::streamManagedContent(WebServer& server, const String& path) const {
    if (!sdReady_ || !isManagedContentPath(path) || !SD.exists(path.c_str())) {
        return false;
    }

    File file = SD.open(path.c_str(), FILE_READ);
    if (!file) {
        return false;
    }

    server.streamFile(file, contentTypeForPath(path));
    file.close();
    return true;
}

String StorageManager::buildContentStatusJson() const {
    String json;
    json.reserve(256);
    json += "{";
    json += "\"storage\":\"sd\",";
    json += "\"sd_ready\":";
    json += sdReady_ ? "true" : "false";
    json += ",\"cs_pin\":";
    json += String(csPin_);
    json += ",\"assets_ready\":";
    json += assetsReady_ ? "true" : "false";
    json += ",\"audio_ready\":";
    json += audioReady_ ? "true" : "false";
    json += ",\"animations_ready\":";
    json += animationsReady_ ? "true" : "false";
    json += ",\"libraries_ready\":";
    json += librariesReady_ ? "true" : "false";
    json += "}";
    return json;
}

bool StorageManager::directoryExists(const char* path) const {
    if (path == nullptr || !SD.exists(path)) {
        return false;
    }

    File entry = SD.open(path);
    if (!entry) {
        return false;
    }

    const bool result = entry.isDirectory();
    entry.close();
    return result;
}

bool StorageManager::hasPrefix(const String& path, const char* prefix) {
    if (prefix == nullptr) {
        return false;
    }
    return path.startsWith(prefix);
}

String StorageManager::contentTypeForPath(const String& path) {
    const String lowerPath = String(path);
    if (lowerPath.endsWith(".html")) {
        return "text/html; charset=utf-8";
    }
    if (lowerPath.endsWith(".css")) {
        return "text/css; charset=utf-8";
    }
    if (lowerPath.endsWith(".js")) {
        return "application/javascript; charset=utf-8";
    }
    if (lowerPath.endsWith(".json")) {
        return "application/json; charset=utf-8";
    }
    if (lowerPath.endsWith(".svg")) {
        return "image/svg+xml";
    }
    if (lowerPath.endsWith(".png")) {
        return "image/png";
    }
    if (lowerPath.endsWith(".jpg") || lowerPath.endsWith(".jpeg")) {
        return "image/jpeg";
    }
    if (lowerPath.endsWith(".gif")) {
        return "image/gif";
    }
    if (lowerPath.endsWith(".webp")) {
        return "image/webp";
    }
    if (lowerPath.endsWith(".mp3")) {
        return "audio/mpeg";
    }
    if (lowerPath.endsWith(".wav")) {
        return "audio/wav";
    }
    if (lowerPath.endsWith(".ogg")) {
        return "audio/ogg";
    }
    if (lowerPath.endsWith(".webm")) {
        return "video/webm";
    }
    return "application/octet-stream";
}

}  // namespace smart_platform::storage
