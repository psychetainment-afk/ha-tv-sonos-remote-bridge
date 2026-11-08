# Licence and third-party notices

TV Sonos Remote Bridge project sources, examples, documentation, generated project icon and companion app are distributed under **GNU GPL version 3 only (SPDX: GPL-3.0-only)**; the complete text is in [LICENSE](LICENSE). Copyright (C) 2026 TV Sonos Remote Bridge contributors. No warranty; see LICENSE.

The bundled APK corresponds to android/app/src/main at this release. The preferred source, resource XML, build script and build instructions are included. Signing keys are not distributed. Android SDK/JDK tools and platform implementation are not included. The APK build compiles the project Java sources against Android platform APIs without bundling third-party app libraries.

Runtime dependencies are installed separately by Home Assistant, not vendored in this repository or APK:

| Component | Role | Upstream licence/source |
|---|---|---|
| adb-shell >=0.4.4 (async extra; tested with 0.4.4) | ADB connection in HA | [Apache-2.0](https://github.com/JeffLIrion/adb_shell/blob/v0.4.4/LICENSE) |
| Home Assistant | Host application/API | [Apache-2.0](https://github.com/home-assistant/core/blob/dev/LICENSE.md) |

Transitive dependencies retain their upstream licences. Development-only tools (pytest, PyYAML, Jinja2 and Pillow for icon generation) are separately installed; their implementations are not included in the release. No third-party source files were identified in the reviewed Android sources. This records the checked distribution scope, not an independent legal audit.

Sonos, Xiaomi, Android and Home Assistant names identify compatible/related products. This independent project does not imply endorsement or affiliation.
