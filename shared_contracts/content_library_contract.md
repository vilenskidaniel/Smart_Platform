# Content Library Contract

Этот документ описывает не пользовательский модуль, а технический contract для библиотек данных,
которые живут в mirrored content storage:

- `ESP32 SD`
- `Raspberry Pi content_root`

## 1. Общие правила

Каждая библиотека:

- хранится как `JSON`;
- имеет `schema_version`;
- имеет `library_type`;
- имеет `entries`;
- может безопасно читаться без выполнения кода.

## 2. Plant Profiles

Файл:

- `/libraries/plant_profiles.v1.json`

Назначение:

- хранит профили растений и базовые целевые параметры ухода.

Минимальная форма:

```json
{
  "schema_version": "1.0",
  "library_type": "plant_profiles",
  "entries": [
    {
      "plant_id": "tomato_balcony",
      "title": "Tomato / Balcony",
      "zone_binding": "zone_1",
      "soil_target_percent": 62,
      "soil_warning_low_percent": 45,
      "soil_warning_high_percent": 78,
      "air_temp_min_c": 16,
      "air_temp_max_c": 29,
      "light_target_lux": 22000,
      "default_state_rule_id": "tomato_standard_rules",
      "default_care_scenario_id": "tomato_daily_care"
    }
  ]
}
```

## 3. Plant State Rules

Файл:

- `/libraries/plant_state_rules.v1.json`

Назначение:

- хранит правила, по которым система понимает состояние растения.

Минимальная форма:

```json
{
  "schema_version": "1.0",
  "library_type": "plant_state_rules",
  "entries": [
    {
      "rule_id": "tomato_standard_rules",
      "title": "Tomato Standard Rules",
      "states": [
        {
          "state_id": "dry",
          "soil_below_percent": 46,
          "priority": 90,
          "recommended_care_scenario_id": "tomato_daily_care"
        },
        {
          "state_id": "healthy",
          "soil_min_percent": 46,
          "soil_max_percent": 74,
          "priority": 20
        }
      ]
    }
  ]
}
```

## 4. Care Scenarios

Файл:

- `/libraries/care_scenarios.v1.json`

Назначение:

- хранит сценарии действий для полива и опрыскивания через турель.

Минимальная форма:

```json
{
  "schema_version": "1.0",
  "library_type": "care_scenarios",
  "entries": [
    {
      "scenario_id": "tomato_daily_care",
      "title": "Tomato Daily Care",
      "manual_allowed": true,
      "automatic_allowed": true,
      "steps": [
        {
          "action": "water_zone",
          "owner_module": "irrigation",
          "zone_binding": "zone_1",
          "duration_ms": 12000
        },
        {
          "action": "spray_burst",
          "owner_module": "turret",
          "duration_ms": 350,
          "requires_peer_owner": true
        }
      ]
    }
  ]
}
```

## 5. Что важно для `v1`

- библиотеки читаются, но не обязательно редактируются через UI;
- contract должен быть достаточно простым для ручного редактирования;
- тяжелые библиотеки не должны переезжать в `LittleFS`;
- одни и те же имена файлов должны работать на обоих узлах.
