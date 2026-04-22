# Browser Entry And Host Launch

Этот документ фиксирует каноническую стартовую точку для `Smart Platform` без путаницы между:

- запуском host-side shell;
- входом клиентов через браузер;
- распознаванием разных viewers внутри системы.

## 1. Главное правило

У платформы нет и не должно быть одного "магического ярлыка для всех устройств".

Нужны два разных слоя:

1. **Host launch**: кто-то должен поднять shell-server.
2. **Browser entry**: все остальные устройства просто открывают URL этого shell в браузере.

Именно так сохраняется browser-first модель для `Windows`, `Linux`, `Android`, `Raspberry Pi display` и других клиентов.

## 2. Что такое ярлык и нужен ли он

Windows shortcut или `.cmd`-файл полезен только как **host convenience layer**.

Он нужен не всей системе, а только машине, которая прямо сейчас выступает host для `Raspberry Pi` shell smoke/runtime entry.

Shortcut не является cross-device точкой входа, потому что:

- `Android` не запускает локальный `PowerShell`;
- `Linux` не использует Windows shortcut;
- `ESP32` вообще не открывает локальный браузер сам у себя как пользовательское устройство;
- остальные клиенты должны просто открыть уже опубликованный URL.

Вывод:

- **Да**, shortcut может и должен существовать на `Windows` как удобный старт host-side shell.
- **Нет**, shortcut не может быть универсальной стартовой точкой для всех клиентов.

## 3. Как это должно работать правильно

### 3.1 Host layer

Один из узлов или один из host-компьютеров поднимает shell:

- `Raspberry Pi` как owner-side shell;
- `ESP32` как свой локальный shell;
- `Windows laptop` как smoke-host для `Raspberry Pi` shell.

### 3.2 Browser entry layer

После этого любой клиент заходит через браузер:

- `Windows PC`;
- `Linux laptop`;
- `Android phone`;
- `tablet`;
- встроенный `Pi display`.

Клиенту нужен только URL, а не локальный запускной файл.

### 3.3 Viewer detection layer

Система уже умеет определять активных viewers.

Текущий механизм:

- браузер получает локальный `viewer_id`;
- bar отправляет heartbeat на `/api/v1/shell/viewer-heartbeat`;
- сервер хранит `viewer_id`, `viewer_kind`, `page`, `address` и `last_seen`;
- snapshot возвращает актуальный список viewers.

Это уже реализовано в:

- [raspberry_pi/web/static/smart_bar.js](../raspberry_pi/web/static/smart_bar.js)
- [raspberry_pi/server.py](../raspberry_pi/server.py)
- [raspberry_pi/shell_viewer_presence.py](../raspberry_pi/shell_viewer_presence.py)

То есть система уже отличает `phone`, `desktop`, `tablet`, `display` и видит, кто зашел и взаимодействует.

## 4. Практическая стартовая точка для Windows

Для Windows host в репозитории есть launcher:

- [tools/Launch-SmartPlatformShell.vbs](../tools/Launch-SmartPlatformShell.vbs)
- [tools/Launch-SmartPlatformShell.cmd](../tools/Launch-SmartPlatformShell.cmd)
- [tools/Launch-SmartPlatformShell.ps1](../tools/Launch-SmartPlatformShell.ps1)

Что делает launcher по умолчанию:

- находит `python`;
- выставляет `SMART_PLATFORM_RPI_HOST`, `SMART_PLATFORM_RPI_PORT`, `SMART_PLATFORM_RPI_PUBLIC_BASE_URL`, `SMART_PLATFORM_SYNC_ENABLED`;
- стартует `raspberry_pi/app.py` как скрытый host-side background process;
- останавливает старый listener на том же порту;
- открывает браузер на опубликованный URL в app-like окне;
- пишет host log в `tools/runtime/rpi-shell-host.log`.

### 4.1 Самый простой запуск

Двойной клик по:

- [tools/Launch-SmartPlatformShell.vbs](../tools/Launch-SmartPlatformShell.vbs)

или, если нужен совместимый wrapper:

- [tools/Launch-SmartPlatformShell.cmd](../tools/Launch-SmartPlatformShell.cmd)

По умолчанию он запускает `LAN`-режим:

- `bind_host = 0.0.0.0`
- `port = 8091`
- `public_base_url = http://<local-lan-ip>:8091`

Это лучший режим, если к shell должны подключаться:

- этот же Windows-host;
- телефон в той же сети;
- другой ноутбук;
- любой браузерный клиент в локальной сети.

Для PC testing это теперь и есть основная стартовая точка.

### 4.2 Локальный smoke-only запуск

Если нужен только локальный desktop smoke path:

```powershell
& ".\tools\Launch-SmartPlatformShell.ps1" -EntryMode Loopback
```

В этом режиме launcher соберет:

- `bind_host = 127.0.0.1`
- `public_base_url = http://127.0.0.1:8091`

### 4.3 Явный LAN URL

Если автоопределение адреса не подходит, URL можно задать явно:

```powershell
& ".\tools\Launch-SmartPlatformShell.ps1" -PublicBaseUrl "http://192.168.1.227:8091"
```

### 4.4 Проверка без запуска

Если нужно только увидеть, что именно launcher собирается сделать:

```powershell
& ".\tools\Launch-SmartPlatformShell.ps1" -EntryMode Lan -PrintOnly
```

## 5. Нужен ли shortcut, который открывает PowerShell

Да, на `Windows` это нормальный и полезный слой.

Правильная модель такая:

- `VBS`/`CMD` launcher тихо поднимает background host process;
- постоянное окно терминала не остается висеть на рабочем столе;
- после этого автоматически открывается браузер в app-like desktop window;
- остальные устройства заходят по LAN URL уже без всяких shortcut.

Иными словами:

- shortcut нужен `host operator`;
- URL нужен всем viewer-клиентам.

## 5.1 Smartphone Entry Popup

Когда desktop-клиент впервые открывает shell по не-loopback URL, `Home` теперь показывает popup `Open On Smartphone`.

Что делает popup:

- показывает QR-код на текущую shell page;
- позволяет открыть тот же shell с телефона камерой;
- закрывается крестиком в правом верхнем углу;
- после закрытия не навязывается заново на каждом refresh в том же browser-origin;
- может быть открыт повторно через кнопку `Open On Smartphone` под заголовком `Smart Platform`.

Если shell запущен только в `Loopback`-режиме, popup не показывается, потому что `127.0.0.1` не является валидной phone entry точкой.

## 6. Как входить с разных устройств

### 6.1 Windows host

Запускает launcher и получает открытый браузер автоматически.

### 6.2 Другой Windows или Linux клиент

Ничего не запускает локально.

Просто открывает в браузере:

- `http://<host-ip>:8091/`

### 6.3 Android phone

Тоже ничего не запускает локально.

Открывает тот же URL в браузере телефона:

- `http://<host-ip>:8091/`

Дальше shell уже сам определяет viewer как `phone`.

### 6.4 ESP32 side

`ESP32` не использует Windows launcher.

Если нужен вход в `ESP32` shell, клиент открывает URL самого `ESP32`-узла, а не пытается локально запускать PowerShell.

## 7. Что можно добавить позже

Следующие удобные слои логично добавлять уже поверх этой модели:

1. QR-код с `LAN` URL для первого mobile entry.
2. Маленькую entry-page с явными ссылками `This device`, `LAN`, `owner shell`, `peer shell`.
3. Launcher для `Linux`, если Linux-машина тоже будет выступать host-side smoke/server entry.

Но базовая архитектура уже сейчас должна оставаться именно такой:

- host поднимает shell;
- клиенты открывают URL;
- система распознает viewers heartbeat-механизмом.