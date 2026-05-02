# Архивный слой `docs/archive`

Этот каталог хранит historical snapshots, которые уже не входят в активный reading order,
но остаются полезными как след подтвержденных migration-stage и bootstrap-stage решений.

Правила для этого слоя:

- файлы отсюда не считаются primary или supporting truth для нового implementation-чата;
- если исторический смысл все еще нужен, он должен быть уже коротко зафиксирован в canonical core,
  deep-docs или supporting-docs активного слоя;
- compatibility-stub на старом пути допустим, если он помогает не рвать старые ссылки и чужие заметки;
- новые product-решения нельзя обосновывать только ссылкой на архивный snapshot.

Сейчас в архивный слой вынесены:

- `12_esp32_shell_bootstrap.md`
- `18_rpi_turret_bridge_bootstrap.md`
- `24_federated_owner_routing_stage.md`
- `25_federated_handoff_stage.md`

Если со временем compatibility-stub на старом пути перестанут быть нужны, их можно удалить,
оставив только архивные копии в этом каталоге.
