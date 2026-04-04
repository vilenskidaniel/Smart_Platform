# Shell LittleFS Stage

Этот документ фиксирует завершение этапа переноса `ESP32 shell` в `LittleFS`.

## Что изменилось

Раньше shell-страницы жили внутри прошивки как большие строковые литералы.

Теперь:

- основные страницы лежат в `firmware_esp32/data/`;
- `WebShellServer` сначала пытается отдать страницы из `LittleFS`;
- если файловая система еще не загружена, открывается безопасный fallback-экран из прошивки.

## Зачем это было нужно

- уменьшить архитектурный долг перед ростом UI;
- перестать держать большие HTML-страницы в `.cpp`;
- упростить редактирование интерфейса;
- подготовить платформу к следующему этапу, где будет расти shell и добавляться `irrigation`.

## Какие файлы теперь являются источником shell

- [index.html](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/ESP32_COB_Strobe_Bench/Smart_Platform/firmware_esp32/data/index.html)
- [strobe.html](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/ESP32_COB_Strobe_Bench/Smart_Platform/firmware_esp32/data/service/strobe.html)

## Что осталось в прошивке

В прошивке остаются только:

- маленькие fallback-страницы;
- API;
- логика модулей;
- логика безопасного старта и маршрутизации.

Это намеренно.

## Как теперь пользоваться

Для полного запуска shell теперь нужны два шага:

1. Залить прошивку.
2. Залить файловую систему `LittleFS`.

Типовой цикл:

```powershell
pio run -t upload
pio run -t uploadfs
```

## Что уже проверено

- `pio run` успешно;
- `pio run -t buildfs` успешно.

## Что еще не проверено

- живое открытие страниц на реальной плате;
- `uploadfs` на конкретное устройство;
- поведение fallback-страниц на незалитой файловой системе.
