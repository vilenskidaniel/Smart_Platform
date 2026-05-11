#pragma once

#include <Arduino.h>
#include <WiFi.h>

namespace smart_platform::net {

class WiFiBootstrap {
public:
    WiFiBootstrap();

    bool begin();
    void update();

    bool isReady() const;
    const char* accessPointSsid() const;
    IPAddress accessPointIp() const;
    String buildSummary() const;

private:
    bool ready_;
};

}  // namespace smart_platform::net
