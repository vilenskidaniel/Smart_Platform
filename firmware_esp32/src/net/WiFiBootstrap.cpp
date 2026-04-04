#include "net/WiFiBootstrap.h"

namespace smart_platform::net {

namespace {

#ifndef SMART_PLATFORM_AP_SSID
#define SMART_PLATFORM_AP_SSID "SmartPlatform-ESP32"
#endif

#ifndef SMART_PLATFORM_AP_PASSWORD
#define SMART_PLATFORM_AP_PASSWORD "smartplat"
#endif

}  // namespace

WiFiBootstrap::WiFiBootstrap() : ready_(false) {
}

bool WiFiBootstrap::begin() {
    // Для первого web shell выбираем максимально автономный режим:
    // ESP32 сама поднимает точку доступа, чтобы к системе можно было зайти без проводов и без роутера.
    WiFi.mode(WIFI_AP);
    ready_ = WiFi.softAP(SMART_PLATFORM_AP_SSID, SMART_PLATFORM_AP_PASSWORD);

    return ready_;
}

void WiFiBootstrap::update() {
    // TODO(stage-shell-wifi):
    // Позже здесь появятся:
    // - STA режим
    // - поиск соседа Raspberry Pi
    // - heartbeat
    // - автоматическое переключение сетевых профилей
}

bool WiFiBootstrap::isReady() const {
    return ready_;
}

const char* WiFiBootstrap::accessPointSsid() const {
    return SMART_PLATFORM_AP_SSID;
}

IPAddress WiFiBootstrap::accessPointIp() const {
    return WiFi.softAPIP();
}

String WiFiBootstrap::buildSummary() const {
    String text;
    text.reserve(128);

    text += "Wi-Fi AP: ";
    text += accessPointSsid();
    text += " / ready=";
    text += ready_ ? "true" : "false";
    text += " / ip=";
    text += accessPointIp().toString();
    return text;
}

}  // namespace smart_platform::net
