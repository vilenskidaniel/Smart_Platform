#pragma once

#include <Arduino.h>
#include <WebServer.h>

namespace smart_platform::storage {

class StorageManager {
public:
    StorageManager();

    bool begin();

    bool sdReady() const;
    bool assetsReady() const;
    bool audioReady() const;
    bool animationsReady() const;
    bool librariesReady() const;
    uint8_t csPin() const;

    bool isManagedContentPath(const String& path) const;
    bool hasManagedContent() const;
    bool streamManagedContent(WebServer& server, const String& path) const;
    String buildContentStatusJson() const;

private:
    bool directoryExists(const char* path) const;
    static bool hasPrefix(const String& path, const char* prefix);
    static String contentTypeForPath(const String& path);

    bool sdReady_;
    bool assetsReady_;
    bool audioReady_;
    bool animationsReady_;
    bool librariesReady_;
    uint8_t csPin_;
};

}  // namespace smart_platform::storage
