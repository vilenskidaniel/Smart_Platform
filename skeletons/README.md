# Smart Platform Skeletons

Здесь лежат не боевые runtime-файлы, а архитектурные skeleton-файлы.

Их задача:

- показать крупные сущности;
- зафиксировать роли и ownership;
- не дать проекту снова расползтись в глубину раньше времени.

Что важно:

- эти файлы не являются production-реализацией;
- они не должны подменять собой реальные runtime-классы;
- они нужны как карта проектирования перед глубокой разработкой.

Текущие skeleton-файлы:

- `esp32_blueprint.h`
- `raspberry_pi_blueprint.py`
- `platform_shell_esp32_blueprint.h`
- `platform_shell_raspberry_pi_blueprint.py`
- `shell_snapshot_facade_esp32_blueprint.h`
- `shell_snapshot_facade_raspberry_pi_blueprint.py`

Специализированные карты по продуктовым блокам:

- `Platform Shell`:
  - [31_platform_shell_class_map.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/docs/31_platform_shell_class_map.md)
  - [33_shell_snapshot_schema.md](/c:/Users/vilen/OneDrive/Dokumentumok/PlatformIO/Projects/Smart_Platform/docs/33_shell_snapshot_schema.md)
  - `platform_shell_esp32_blueprint.h`
  - `platform_shell_raspberry_pi_blueprint.py`
  - `shell_snapshot_facade_esp32_blueprint.h`
  - `shell_snapshot_facade_raspberry_pi_blueprint.py`

Следующее правило работы:

1. сначала обсуждаем и правим skeleton;
2. потом переносим согласованные сущности в реальные runtime-ветки;
3. только затем пишем глубокую реализацию.
