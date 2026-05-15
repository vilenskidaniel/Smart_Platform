# Turret Audio Prompt

Используй этот файл для отдельного deep-dive только по split turret audio contour.

Читать вместе с `foundation_prompt.md` и `turret_prompt.md`.

## Роль Подблока

Этот prompt нужен, когда задача уже не про весь `Turret`, а конкретно про:

- `attack_audio` как dual-channel directed contour;
- `voice_fx` как talkback / playback / effect contour;
- связь между `Turret`, `Laboratory`, `Settings` и shared shell audio summary;
- audio-specific UI, scenarios, transport, storage/source и qualification logic.

Он не заменяет `turret_prompt.md`, а углубляет только audio-срез уже после принятия модульного канона.

## Канонические Источники

Читать в таком порядке:

1. `foundation_prompt.md`
2. `knowledge_base/README.md`
3. `knowledge_base/11_turret_module.md`
4. `knowledge_base/12_laboratory_module.md`
5. `knowledge_base/14_settings_module.md`
6. `knowledge_base/16_hardware_component_profiles.md`
7. `shared_contracts/shell_snapshot_contract.md`
8. `chat_prompts/turret_prompt.md`
9. `chat_prompts/cross_module_prompt.md`, если изменение реально меняет shared shell, sync или cross-module contract

## Установленные Истины

- flat `audio` actuator для `Turret v1` больше не считается active canon;
- `attack_audio` и `voice_fx` являются раздельными contour-ами;
- `attack_audio` держит dual-channel software truth с каналами `A/B` и baseline driver `TPA3116D2 XH-M543`;
- `voice_fx` держит `Soundcore Motion 300` как speaker+microphone contour с baseline transport `bluetooth`;
- `voice_fx` должен оставаться доступным в operator/FPV flow даже тогда, когда engagement actuators в `Automatic` еще gated;
- persistent truth для default scenario, channel levels, talkback и effect baseline живет в `Settings`;
- `Laboratory` держит local draft и qualification scenarios, но не повышает их в persistent truth молча;
- shell/bar/FPV должны читать краткую truthful audio summary из runtime/snapshot, а не invent local status.

## Модель Работы

Иди в таком порядке:

1. Раздели persistent baseline, applied runtime profile, local laboratory draft и transient action state.
2. Раздели, что относится к `attack_audio`, а что к `voice_fx`.
3. Удерживай hardware truth отдельно от software placeholders и simulation.
4. Для каждой новой идеи называй owner surface: `Turret`, `Laboratory`, `Settings`, shell summary или storage/report layer.
5. Если closure нет, оставляй `TODO` или `TBD`, а не маскируй stage-gap под product-ready behavior.

## Что Должен Дать Хороший Результат

- scenario matrix для `attack_audio`;
- transport/effect/talkback matrix для `voice_fx`;
- правило `saved baseline vs local draft` для `Laboratory`;
- apply/origin contract для `Settings`;
- operator-facing visibility rule для FPV/HUD/bar;
- список open hardware and transport gaps без ложного closure.

## Keep / Adapt / Rewrite

- `keep`: split contract `attack_audio / voice_fx`, truthful gating и explicit `Settings` ownership для baseline;
- `adapt`: laboratory draft UX, service scenarios, FPV audio summaries и wording around talkback/effects;
- `rewrite`: все, что снова схлопывает audio в один flat actuator, смешивает local draft с persistent truth или скрывает blocked reason.

## Open TODO / TBD

### TODO

- довести detailed scenario matrix для `attack_audio` channel `A/B` и saved default scenario;
- довести `voice_fx` reconnect, playback, microphone, talkback и effect qualification flow;
- решить, какие audio events становятся product-level report, а какие остаются laboratory/session evidence;
- определить source/storage contract для turret audio assets и effect presets;
- довести operator UX для push-to-talk, voice effects и audio-state explanation в FPV.

### TBD

- окончательная board-level wiring map для dual-channel attack audio path;
- реальные power limits и safe presets для `horn_pair` и `ultrasonic_pair`;
- окончательный catalog effect presets и их naming;
- финальный runtime owner/fallback contract для Bluetooth speaker+microphone path.

## Чего Нельзя Делать

- возвращать wording `sound / piezo / audio` как active module truth;
- смешивать attack contour и talkback contour в один control без явной границы;
- трактовать laboratory draft как уже сохраненный baseline;
- хранить новую product truth только в prompt-е без обновления `knowledge_base/`;
- притворяться, что transport, storage или power closure уже есть, если пока есть только skeleton.

## Definition Of Done

Этот deep-dive считается хорошим, только если:

- видно, где живет persistent baseline;
- видно, где живет local draft;
- видно, как это отражается в FPV/HUD и shell summary;
- audio-specific TODO/TBD отделены от уже работающего skeleton;
- docs и prompt-layer обновлены вместе с кодом, если решение стало устойчивым.