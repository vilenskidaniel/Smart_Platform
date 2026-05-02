(function () {
  const STYLE_ID = "smart-platform-compact-bar-style";
  const HOST_ID = "smart-platform-compact-bar-host";
  const TOOLTIP_ID = "smart-platform-compact-bar-tooltip";
  const STORAGE_KEY = "smart-platform.desktop-controls.enabled";
  const SETTINGS_CACHE_KEY = "smart-platform.settings.cache";
  const SETTINGS_LANGUAGE_KEY = "smart-platform.settings.language";
  const SETTINGS_THEME_KEY = "smart-platform.settings.theme";
  const SETTINGS_DENSITY_KEY = "smart-platform.settings.density";
  const VIEWER_STORAGE_KEY = "smart-platform.viewer.id";
  const FULLSCREEN_STORAGE_KEY = "smart-platform.fullscreen.enabled";
  const FULLSCREEN_PENDING_KEY = "smart-platform.fullscreen.pending";
  const SETTINGS_ENDPOINT = "/api/v1/settings";
  const DEFAULT_TOOLTIP = "Status details are loading.";
  const TOOLTIP_HIDE_MS = 6000;
  const TOOLTIP_SHOW_DELAY_MS = 500;
  const TOOLTIP_MOVE_TOLERANCE_PX = 3;
  const REFRESH_MS = 5000;
  const VIEWER_HEARTBEAT_MS = 5000;
  const CLOCK_MS = 30000;
  const ROUTES = {
    KeyH: "/",
    KeyI: "/irrigation",
    KeyT: "/turret",
    KeyG: "/gallery",
    KeyL: "/service",
    KeyS: "/settings"
  };

  let currentSnapshot = null;
  let batterySnapshot = { available: false };
  let desktopControlsEnabled = readStorage(STORAGE_KEY) !== "0";
  let tooltipPinned = false;
  let tooltipOwnerId = "";
  let tooltipShowTimer = 0;
  let tooltipHoverTarget = null;
  let tooltipPointerX = 0;
  let tooltipPointerY = 0;
  let tooltipFocusSuppressedUntil = 0;
  let tooltipHideTimer = 0;
  let globalListenersInstalled = false;
  let barLayoutFrame = 0;
  let viewerSessionId = "";
  let viewerHeartbeatTimer = 0;
  let viewerHeartbeatInFlight = false;
  let refreshTimer = 0;
  let clockTimer = 0;
  let fullscreenToggleIntent = null;
  let fullscreenResumeListenersInstalled = false;
  let fullscreenPendingHintPage = "";
  let barSettings = {
    language: "",
    theme: "meadow",
    density: "comfortable",
    fullscreenEnabled: false,
    desktopControlsEnabled: desktopControlsEnabled,
    preferPeerContinuity: true,
    pollIntervalSeconds: 30
  };

  function esc(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function readStorage(key) {
    try {
      return window.localStorage.getItem(key);
    } catch (_error) {
      return null;
    }
  }

  function writeStorage(key, value) {
    try {
      window.localStorage.setItem(key, value);
    } catch (_error) {
      return;
    }
  }

  function normalizeBarLanguage(value) {
    const normalized = String(value || "").trim().toLowerCase();
    return ["en", "ru", "he", "de", "fr", "es", "zh", "ar"].includes(normalized) ? normalized : "";
  }

  function normalizeBarTheme(value) {
    const normalized = String(value || "").trim().toLowerCase();
    return ["meadow", "dawn", "studio", "midnight", "sunlit", "night", "minimal", "contrast"].includes(normalized)
      ? normalized
      : "";
  }

  function normalizeBarDensity(value) {
    const normalized = String(value || "").trim().toLowerCase();
    return ["comfortable", "compact"].includes(normalized) ? normalized : "";
  }

  function clampInt(value, fallback, min, max) {
    const parsed = Number(value);
    if (!Number.isFinite(parsed)) {
      return fallback;
    }
    return Math.min(max, Math.max(min, Math.round(parsed)));
  }

  function readCachedSettings() {
    const raw = readStorage(SETTINGS_CACHE_KEY);
    if (!raw) {
      return null;
    }

    try {
      return JSON.parse(raw);
    } catch (_error) {
      return null;
    }
  }

  function boolPreference(value, fallback) {
    if (typeof value === "boolean") {
      return value;
    }
    if (typeof value === "string") {
      return ["1", "true", "yes", "on"].includes(value.trim().toLowerCase());
    }
    return fallback;
  }

  function normalizeBarSettings(raw) {
    const payload = raw && typeof raw === "object" ? raw : {};
    const interfaceSettings = payload.interface && typeof payload.interface === "object" ? payload.interface : payload;
    const styleSettings = payload.style && typeof payload.style === "object" ? payload.style : payload;
    const syncSettings = payload.synchronization && typeof payload.synchronization === "object" ? payload.synchronization : payload;
    const storedLanguage = normalizeBarLanguage(readStorage(SETTINGS_LANGUAGE_KEY));
    const storedTheme = normalizeBarTheme(readStorage(SETTINGS_THEME_KEY));
    const storedDensity = normalizeBarDensity(readStorage(SETTINGS_DENSITY_KEY));
    const storedFullscreen = readStorage(FULLSCREEN_STORAGE_KEY);
    const storedDesktopControls = readStorage(STORAGE_KEY);
    return {
      language: normalizeBarLanguage(interfaceSettings.language) || storedLanguage,
      theme: normalizeBarTheme(styleSettings.theme) || storedTheme || "meadow",
      density: normalizeBarDensity(styleSettings.density) || storedDensity || "comfortable",
      fullscreenEnabled: storedFullscreen === null
        ? boolPreference(interfaceSettings.fullscreen_enabled, fullscreenPreferenceEnabled())
        : storedFullscreen === "1",
      desktopControlsEnabled: storedDesktopControls === null
        ? boolPreference(interfaceSettings.desktop_controls_enabled, desktopControlsEnabled)
        : storedDesktopControls !== "0",
      preferPeerContinuity: boolPreference(syncSettings.prefer_peer_continuity, true),
      pollIntervalSeconds: clampInt(syncSettings.poll_interval_seconds, 30, 5, 300)
    };
  }

  function preferredLocale() {
    return barSettings.language || normalizeBarLanguage(readStorage(SETTINGS_LANGUAGE_KEY)) || navigator.language || "en";
  }

  function settingsPageActive() {
    const pathname = String(window.location.pathname || "/").replace(/\/+$/, "") || "/";
    return pathname === "/settings";
  }

  function applyShellAppearance() {
    if (!(document.body instanceof HTMLBodyElement) || settingsPageActive()) {
      return;
    }
    document.body.dataset.shellTheme = normalizeBarTheme(barSettings.theme) || "meadow";
    document.body.dataset.shellDensity = normalizeBarDensity(barSettings.density) || "comfortable";
  }

  function effectiveRefreshMs() {
    if (barSettings.preferPeerContinuity !== false) {
      return REFRESH_MS;
    }
    return clampInt(barSettings.pollIntervalSeconds, 30, 5, 300) * 1000;
  }

  function restartRefreshLoop() {
    if (refreshTimer) {
      window.clearInterval(refreshTimer);
      refreshTimer = 0;
    }
    refreshTimer = window.setInterval(() => {
      refresh().catch(() => {});
    }, effectiveRefreshMs());
  }

  function restartViewerHeartbeatLoop() {
    if (viewerHeartbeatTimer) {
      window.clearInterval(viewerHeartbeatTimer);
      viewerHeartbeatTimer = 0;
    }
    sendViewerHeartbeat().catch(() => {});
    viewerHeartbeatTimer = window.setInterval(() => {
      sendViewerHeartbeat().catch(() => {});
    }, effectiveRefreshMs());
  }

  function ensureClockLoop() {
    if (clockTimer) {
      return;
    }
    clockTimer = window.setInterval(() => {
      renderBar(currentSnapshot);
    }, CLOCK_MS);
  }

  function applyBarSettings(raw) {
    barSettings = normalizeBarSettings(raw);
    desktopControlsEnabled = barSettings.desktopControlsEnabled;
    writeStorage(STORAGE_KEY, desktopControlsEnabled ? "1" : "0");
    if (barSettings.language) {
      writeStorage(SETTINGS_LANGUAGE_KEY, barSettings.language);
    }
    writeStorage(SETTINGS_THEME_KEY, barSettings.theme);
    writeStorage(SETTINGS_DENSITY_KEY, barSettings.density);
    setFullscreenPreference(barSettings.fullscreenEnabled);
    ensureFullscreenPreference();
    applyShellAppearance();
    restartRefreshLoop();
    restartViewerHeartbeatLoop();
    renderBar(currentSnapshot);
  }

  async function loadBarSettings() {
    try {
      const response = await fetch(SETTINGS_ENDPOINT, { cache: "no-store" });
      if (!response.ok) {
        throw new Error(`Settings request failed: ${response.status}`);
      }

      const payload = await response.json();
      writeStorage(SETTINGS_CACHE_KEY, JSON.stringify(payload));
      applyBarSettings(payload);
      return;
    } catch (_error) {
      const cached = readCachedSettings();
      applyBarSettings(cached || {});
    }
  }

  function fullscreenPreferenceEnabled() {
    return readStorage(FULLSCREEN_STORAGE_KEY) === "1";
  }

  function setFullscreenPreference(enabled) {
    writeStorage(FULLSCREEN_STORAGE_KEY, enabled ? "1" : "0");
    if (!enabled) {
      writeStorage(FULLSCREEN_PENDING_KEY, "0");
    }
  }

  async function persistFullscreenPreference(enabled) {
    try {
      const current = await fetch(SETTINGS_ENDPOINT, { cache: "no-store" });
      const payload = current.ok ? await current.json() : {};
      const next = {
        ...(payload && typeof payload === "object" ? payload : {}),
        interface: {
          ...(((payload || {}).interface) || {}),
          fullscreen_enabled: Boolean(enabled)
        }
      };
      const saved = await fetch(SETTINGS_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(next)
      });
      const savedPayload = saved.ok ? await saved.json() : next;
      writeStorage(SETTINGS_CACHE_KEY, JSON.stringify(savedPayload));
      window.dispatchEvent(new CustomEvent("smart-platform:settings-updated", { detail: savedPayload }));
    } catch (_error) {
      window.dispatchEvent(new CustomEvent("smart-platform:fullscreen-updated", {
        detail: { fullscreen_enabled: Boolean(enabled) }
      }));
    }
  }

  function fullscreenNavigationPending() {
    return readStorage(FULLSCREEN_PENDING_KEY) === "1";
  }

  function keyboardNavigationShortcutsEnabled() {
    return false;
  }

  function setFullscreenNavigationPending(pending) {
    writeStorage(FULLSCREEN_PENDING_KEY, pending ? "1" : "0");
  }

  function fullscreenRestorePending() {
    return fullscreenPreferenceEnabled() && !document.fullscreenElement;
  }

  function clearTooltipHideTimer() {
    if (!tooltipHideTimer) {
      return;
    }
    window.clearTimeout(tooltipHideTimer);
    tooltipHideTimer = 0;
  }

  function clearTooltipShowTimer() {
    if (!tooltipShowTimer) {
      return;
    }
    window.clearTimeout(tooltipShowTimer);
    tooltipShowTimer = 0;
  }

  function setTooltipPointerOrigin(event) {
    const isPointerEvent = typeof PointerEvent !== "undefined" && event instanceof PointerEvent;
    if (!(event instanceof MouseEvent || isPointerEvent)) {
      return;
    }
    tooltipPointerX = event.clientX;
    tooltipPointerY = event.clientY;
  }

  function tooltipMovedPastTolerance(event) {
    const isPointerEvent = typeof PointerEvent !== "undefined" && event instanceof PointerEvent;
    if (!(event instanceof MouseEvent || isPointerEvent)) {
      return false;
    }
    const dx = Math.abs(event.clientX - tooltipPointerX);
    const dy = Math.abs(event.clientY - tooltipPointerY);
    return Math.max(dx, dy) > TOOLTIP_MOVE_TOLERANCE_PX;
  }

  async function requestStoredFullscreen() {
    if (!fullscreenPreferenceEnabled() || document.fullscreenElement || !document.fullscreenEnabled || !document.documentElement.requestFullscreen) {
      if (fullscreenPreferenceEnabled() && !document.fullscreenElement) {
        setFullscreenNavigationPending(true);
      }
      return false;
    }

    try {
      await document.documentElement.requestFullscreen();
      setFullscreenNavigationPending(false);
      clearFullscreenResumeListeners();
      return true;
    } catch (_error) {
      setFullscreenNavigationPending(true);
      return false;
    }
  }

  async function handleFullscreenResumeInteraction(event) {
    if (!fullscreenPreferenceEnabled()) {
      clearFullscreenResumeListeners();
      return;
    }

    if (event instanceof MouseEvent) {
      if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
        return;
      }
    }

    const resumed = await requestStoredFullscreen();
    if (resumed || !fullscreenPreferenceEnabled()) {
      clearFullscreenResumeListeners();
    }
  }

  function clearFullscreenResumeListeners() {
    if (!fullscreenResumeListenersInstalled) {
      return;
    }

    document.removeEventListener("click", handleFullscreenResumeInteraction, true);
    document.removeEventListener("keydown", handleFullscreenResumeInteraction, true);
    fullscreenResumeListenersInstalled = false;
  }

  function installFullscreenResumeListeners() {
    fullscreenResumeListenersInstalled = false;
  }

  function ensureFullscreenPreference() {
    if (!fullscreenPreferenceEnabled() || document.fullscreenElement) {
      return;
    }
    setFullscreenNavigationPending(true);

    requestStoredFullscreen().then((resumed) => {
      if (!resumed && fullscreenPreferenceEnabled()) {
        installFullscreenResumeListeners();
        renderBar(currentSnapshot);
      }
    }).catch(() => {
      if (fullscreenPreferenceEnabled()) {
        installFullscreenResumeListeners();
        renderBar(currentSnapshot);
      }
    });
  }

  function markFullscreenResumeOnInternalNavigation(destination) {
    if (!(fullscreenPreferenceEnabled() || document.fullscreenElement)) {
      return;
    }

    try {
      const targetUrl = new URL(destination, window.location.href);
      if (targetUrl.origin === window.location.origin) {
        setFullscreenNavigationPending(true);
      }
    } catch (_error) {
      return;
    }
  }

  function createViewerId() {
    if (window.crypto && typeof window.crypto.randomUUID === "function") {
      return window.crypto.randomUUID();
    }
    return `viewer-${Math.random().toString(36).slice(2, 10)}${Date.now().toString(36)}`;
  }

  function ensureViewerId() {
    if (viewerSessionId) {
      return viewerSessionId;
    }

    const existing = readStorage(VIEWER_STORAGE_KEY);
    if (existing) {
      viewerSessionId = existing;
      return viewerSessionId;
    }

    viewerSessionId = createViewerId();
    writeStorage(VIEWER_STORAGE_KEY, viewerSessionId);
    return viewerSessionId;
  }

  function injectStyles() {
    if (document.getElementById(STYLE_ID)) {
      return;
    }

    const style = document.createElement("style");
    style.id = STYLE_ID;
    style.textContent = `
      :root {
        --sp-bar-edge: clamp(6px, 0.7vw, 12px);
        --sp-bar-bg: rgba(247, 250, 244, 0.88);
        --sp-bar-line: rgba(53, 88, 63, 0.12);
        --sp-bar-shadow: 0 14px 36px rgba(21, 36, 26, 0.12);
        --sp-bar-ink: #243329;
        --sp-bar-muted: #607164;
        --sp-bar-neutral-bg: rgba(109, 118, 112, 0.12);
        --sp-bar-neutral-line: rgba(100, 112, 104, 0.14);
        --sp-bar-neutral-ink: #66736a;
        --sp-bar-online-bg: rgba(46, 125, 78, 0.14);
        --sp-bar-online-line: rgba(47, 125, 77, 0.18);
        --sp-bar-online-ink: #2f7d4d;
        --sp-bar-attention-bg: rgba(202, 142, 28, 0.16);
        --sp-bar-attention-line: rgba(146, 96, 20, 0.18);
        --sp-bar-attention-ink: #926014;
        --sp-bar-fault-bg: rgba(184, 56, 56, 0.14);
        --sp-bar-fault-line: rgba(159, 52, 52, 0.18);
        --sp-bar-fault-ink: #9f3434;
        --sp-bar-active-bg: rgba(37, 95, 151, 0.16);
        --sp-bar-active-line: rgba(37, 95, 151, 0.22);
        --sp-bar-active-ink: #255f97;
      }

      body[data-shell-theme="meadow"] {
        --bg: #dce5dd;
        --panel: rgba(251, 252, 248, 0.92);
        --panel-strong: #f9fcf6;
        --ink: #1a2620;
        --muted: #657469;
        --line: rgba(52, 79, 61, 0.14);
        --accent: #2f5d43;
        --accent-soft: rgba(47, 93, 67, 0.12);
        --button-bg: rgba(47, 93, 67, 0.08);
        --button-line: rgba(47, 93, 67, 0.18);
        --shadow: 0 24px 54px rgba(21, 33, 25, 0.12);
        --ok-bg: rgba(47, 125, 77, 0.14);
        --ok-ink: #2f7d4d;
        --warn-bg: rgba(155, 102, 25, 0.14);
        --warn-ink: #9b6619;
        --fault-bg: rgba(164, 58, 58, 0.14);
        --fault-ink: #a43a3a;
        --idle-bg: rgba(101, 116, 105, 0.12);
        --idle-ink: #657469;
        --shell-hero-a: rgba(30, 61, 43, 0.98);
        --shell-hero-b: rgba(71, 108, 79, 0.96);
        --shell-hero-ink: #f3fbf2;
        --shell-glow-a: rgba(77, 119, 85, 0.18);
        --shell-glow-b: rgba(44, 106, 111, 0.08);
        --shell-wash: #f2f7f1;
      }

      body[data-shell-theme="dawn"] {
        --bg: #e7ddd1;
        --panel: rgba(255, 249, 239, 0.92);
        --panel-strong: #fffbf3;
        --ink: #302217;
        --muted: #7c6956;
        --line: rgba(120, 86, 54, 0.15);
        --accent: #8b5d2b;
        --accent-soft: rgba(139, 93, 43, 0.12);
        --button-bg: rgba(139, 93, 43, 0.08);
        --button-line: rgba(139, 93, 43, 0.18);
        --shadow: 0 24px 54px rgba(60, 37, 17, 0.12);
        --ok-bg: rgba(104, 132, 59, 0.14);
        --ok-ink: #68843b;
        --warn-bg: rgba(157, 100, 24, 0.14);
        --warn-ink: #9d6418;
        --fault-bg: rgba(162, 66, 57, 0.14);
        --fault-ink: #a24239;
        --idle-bg: rgba(124, 105, 86, 0.12);
        --idle-ink: #7c6956;
        --shell-hero-a: rgba(98, 60, 24, 0.98);
        --shell-hero-b: rgba(153, 105, 52, 0.96);
        --shell-hero-ink: #fff8ef;
        --shell-glow-a: rgba(179, 123, 67, 0.18);
        --shell-glow-b: rgba(213, 168, 118, 0.12);
        --shell-wash: #fff6ec;
      }

      body[data-shell-theme="studio"] {
        --bg: #dce2e7;
        --panel: rgba(248, 251, 253, 0.92);
        --panel-strong: #fcfdfe;
        --ink: #18232a;
        --muted: #62717a;
        --line: rgba(57, 84, 103, 0.15);
        --accent: #31546b;
        --accent-soft: rgba(49, 84, 107, 0.12);
        --button-bg: rgba(49, 84, 107, 0.08);
        --button-line: rgba(49, 84, 107, 0.18);
        --shadow: 0 24px 54px rgba(18, 34, 43, 0.12);
        --ok-bg: rgba(50, 111, 96, 0.14);
        --ok-ink: #326f60;
        --warn-bg: rgba(147, 102, 43, 0.14);
        --warn-ink: #93662b;
        --fault-bg: rgba(156, 65, 65, 0.14);
        --fault-ink: #9c4141;
        --idle-bg: rgba(98, 113, 122, 0.12);
        --idle-ink: #62717a;
        --shell-hero-a: rgba(25, 48, 61, 0.98);
        --shell-hero-b: rgba(68, 97, 118, 0.96);
        --shell-hero-ink: #f5fbfe;
        --shell-glow-a: rgba(91, 130, 158, 0.18);
        --shell-glow-b: rgba(158, 184, 198, 0.12);
        --shell-wash: #f1f6fa;
      }

      body[data-shell-theme="midnight"] {
        --bg: #101820;
        --panel: rgba(24, 35, 43, 0.92);
        --panel-strong: #16212a;
        --ink: #edf6f8;
        --muted: #9fb2b9;
        --line: rgba(160, 190, 198, 0.16);
        --accent: #6eb6c5;
        --accent-soft: rgba(110, 182, 197, 0.14);
        --button-bg: rgba(110, 182, 197, 0.12);
        --button-line: rgba(110, 182, 197, 0.2);
        --shadow: 0 24px 54px rgba(3, 9, 13, 0.34);
        --ok-bg: rgba(122, 215, 163, 0.14);
        --ok-ink: #7ad7a3;
        --warn-bg: rgba(241, 193, 111, 0.16);
        --warn-ink: #f1c16f;
        --fault-bg: rgba(242, 139, 130, 0.16);
        --fault-ink: #f28b82;
        --idle-bg: rgba(159, 178, 185, 0.14);
        --idle-ink: #9fb2b9;
        --shell-hero-a: rgba(14, 25, 34, 0.98);
        --shell-hero-b: rgba(34, 66, 78, 0.96);
        --shell-hero-ink: #f4fbfd;
        --shell-glow-a: rgba(67, 130, 151, 0.22);
        --shell-glow-b: rgba(110, 182, 197, 0.14);
        --shell-wash: #16242d;
      }

      body[data-shell-theme="sunlit"] {
        --bg: #f1e7bf;
        --panel: rgba(255, 253, 238, 0.92);
        --panel-strong: #fff9df;
        --ink: #2b2a18;
        --muted: #7d744e;
        --line: rgba(143, 122, 46, 0.18);
        --accent: #9b7a16;
        --accent-soft: rgba(155, 122, 22, 0.13);
        --button-bg: rgba(155, 122, 22, 0.08);
        --button-line: rgba(155, 122, 22, 0.18);
        --shadow: 0 24px 54px rgba(75, 58, 12, 0.13);
        --ok-bg: rgba(89, 125, 47, 0.14);
        --ok-ink: #597d2f;
        --warn-bg: rgba(169, 103, 18, 0.15);
        --warn-ink: #a96712;
        --fault-bg: rgba(161, 62, 50, 0.15);
        --fault-ink: #a13e32;
        --idle-bg: rgba(125, 116, 78, 0.12);
        --idle-ink: #7d744e;
        --shell-hero-a: rgba(116, 89, 13, 0.98);
        --shell-hero-b: rgba(191, 148, 37, 0.95);
        --shell-hero-ink: #fffbe8;
        --shell-glow-a: rgba(248, 213, 94, 0.24);
        --shell-glow-b: rgba(212, 168, 47, 0.14);
        --shell-wash: #fff7dc;
      }

      body[data-shell-theme="night"] {
        --bg: #17171d;
        --panel: rgba(31, 31, 40, 0.92);
        --panel-strong: #20212b;
        --ink: #f2f0ea;
        --muted: #aaa7bd;
        --line: rgba(186, 181, 208, 0.15);
        --accent: #b8a7ff;
        --accent-soft: rgba(184, 167, 255, 0.13);
        --button-bg: rgba(184, 167, 255, 0.12);
        --button-line: rgba(184, 167, 255, 0.2);
        --shadow: 0 24px 54px rgba(5, 5, 10, 0.35);
        --ok-bg: rgba(143, 212, 156, 0.14);
        --ok-ink: #8fd49c;
        --warn-bg: rgba(231, 189, 116, 0.15);
        --warn-ink: #e7bd74;
        --fault-bg: rgba(236, 141, 154, 0.16);
        --fault-ink: #ec8d9a;
        --idle-bg: rgba(170, 167, 189, 0.14);
        --idle-ink: #aaa7bd;
        --shell-hero-a: rgba(28, 25, 43, 0.98);
        --shell-hero-b: rgba(67, 57, 103, 0.96);
        --shell-hero-ink: #fbf9ff;
        --shell-glow-a: rgba(122, 105, 199, 0.2);
        --shell-glow-b: rgba(184, 167, 255, 0.14);
        --shell-wash: #211f2e;
      }

      body[data-shell-theme="minimal"] {
        --bg: #eeeeea;
        --panel: rgba(252, 252, 248, 0.94);
        --panel-strong: #ffffff;
        --ink: #20231f;
        --muted: #6c7068;
        --line: rgba(65, 69, 62, 0.14);
        --accent: #4b5a4b;
        --accent-soft: rgba(75, 90, 75, 0.1);
        --button-bg: rgba(75, 90, 75, 0.08);
        --button-line: rgba(75, 90, 75, 0.18);
        --shadow: 0 18px 42px rgba(28, 30, 28, 0.08);
        --ok-bg: rgba(63, 115, 82, 0.12);
        --ok-ink: #3f7352;
        --warn-bg: rgba(140, 107, 40, 0.12);
        --warn-ink: #8c6b28;
        --fault-bg: rgba(148, 67, 64, 0.13);
        --fault-ink: #944340;
        --idle-bg: rgba(108, 112, 104, 0.12);
        --idle-ink: #6c7068;
        --shell-hero-a: rgba(54, 61, 55, 0.98);
        --shell-hero-b: rgba(91, 101, 90, 0.94);
        --shell-hero-ink: #fbfbf8;
        --shell-glow-a: rgba(170, 176, 166, 0.18);
        --shell-glow-b: rgba(108, 112, 104, 0.08);
        --shell-wash: #f8f8f3;
      }

      body[data-shell-theme="contrast"] {
        --bg: #ffffff;
        --panel: #ffffff;
        --panel-strong: #ffffff;
        --ink: #000000;
        --muted: #343434;
        --line: rgba(0, 0, 0, 0.24);
        --accent: #003f8f;
        --accent-soft: rgba(0, 63, 143, 0.12);
        --button-bg: rgba(0, 63, 143, 0.08);
        --button-line: rgba(0, 63, 143, 0.24);
        --shadow: 0 14px 28px rgba(0, 0, 0, 0.12);
        --ok-bg: rgba(0, 107, 45, 0.12);
        --ok-ink: #006b2d;
        --warn-bg: rgba(138, 82, 0, 0.13);
        --warn-ink: #8a5200;
        --fault-bg: rgba(176, 0, 32, 0.12);
        --fault-ink: #b00020;
        --idle-bg: rgba(52, 52, 52, 0.08);
        --idle-ink: #343434;
        --shell-hero-a: #000000;
        --shell-hero-b: #1d1d1d;
        --shell-hero-ink: #ffffff;
        --shell-glow-a: rgba(0, 63, 143, 0.12);
        --shell-glow-b: rgba(0, 0, 0, 0.04);
        --shell-wash: #ffffff;
      }

      body[data-shell-theme] {
        color: var(--ink);
        background:
          radial-gradient(circle at top left, var(--shell-glow-a, rgba(77, 119, 85, 0.18)), transparent 32%),
          radial-gradient(circle at bottom right, var(--shell-glow-b, rgba(44, 106, 111, 0.08)), transparent 28%),
          linear-gradient(180deg, var(--shell-wash, #f3f7ef) 0%, var(--bg) 100%) !important;
      }

      body[data-shell-theme] .hero {
        background: linear-gradient(135deg, var(--shell-hero-a), var(--shell-hero-b)) !important;
        color: var(--shell-hero-ink) !important;
      }

      body[data-shell-theme] .hero p {
        color: color-mix(in srgb, var(--shell-hero-ink) 84%, transparent) !important;
      }

      body[data-shell-theme] .hero,
      body[data-shell-theme] .card,
      body[data-shell-theme] .module,
      body[data-shell-theme] .tile,
      body[data-shell-theme] .topbar,
      body[data-shell-theme] .launcher-card,
      body[data-shell-theme] .check,
      body[data-shell-theme] .report,
      body[data-shell-theme] .field input,
      body[data-shell-theme] .field select,
      body[data-shell-theme] .field textarea {
        border-color: var(--line) !important;
        box-shadow: var(--shadow);
      }

      body[data-shell-theme] .card,
      body[data-shell-theme] .module,
      body[data-shell-theme] .tile,
      body[data-shell-theme] .report,
      body[data-shell-theme] .check,
      body[data-shell-theme] .topbar,
      body[data-shell-theme] .launcher-card {
        background: var(--panel) !important;
      }

      body[data-shell-theme] .token,
      body[data-shell-theme] .moisture-lane,
      body[data-shell-theme] .home-button,
      body[data-shell-theme] .control-button,
      body[data-shell-theme] .primary,
      body[data-shell-theme] .secondary,
      body[data-shell-theme] .button.primary,
      body[data-shell-theme] .button.secondary,
      body[data-shell-theme] .card-action {
        color: var(--ink);
      }

      body[data-shell-theme] .home-button,
      body[data-shell-theme] .control-button,
      body[data-shell-theme] .secondary,
      body[data-shell-theme] .button.secondary,
      body[data-shell-theme] .card-action {
        background: var(--button-bg) !important;
        border-color: var(--button-line) !important;
      }

      body[data-shell-theme] .primary,
      body[data-shell-theme] .button.primary {
        background: var(--accent) !important;
        border-color: color-mix(in srgb, var(--accent) 72%, black) !important;
        color: var(--shell-hero-ink) !important;
      }

      body[data-shell-density="comfortable"] .app-shell,
      body[data-shell-density="comfortable"] .page,
      body[data-shell-density="comfortable"] .shell {
        padding: 18px 14px 44px !important;
      }

      body[data-shell-density="comfortable"] .hero,
      body[data-shell-density="comfortable"] .card,
      body[data-shell-density="comfortable"] .module,
      body[data-shell-density="comfortable"] .tile,
      body[data-shell-density="comfortable"] .topbar,
      body[data-shell-density="comfortable"] .launcher-card,
      body[data-shell-density="comfortable"] .report,
      body[data-shell-density="comfortable"] .check {
        padding: 22px !important;
        border-radius: 24px !important;
      }

      body[data-shell-density="compact"] .app-shell,
      body[data-shell-density="compact"] .page,
      body[data-shell-density="compact"] .shell {
        padding: 10px 10px 24px !important;
      }

      body[data-shell-density="compact"] .hero,
      body[data-shell-density="compact"] .card,
      body[data-shell-density="compact"] .module,
      body[data-shell-density="compact"] .tile,
      body[data-shell-density="compact"] .topbar,
      body[data-shell-density="compact"] .launcher-card,
      body[data-shell-density="compact"] .report,
      body[data-shell-density="compact"] .check {
        padding: 14px !important;
        border-radius: 16px !important;
      }

      body[data-shell-density="compact"] .hero h1 {
        font-size: clamp(24px, 4vw, 36px) !important;
      }

      body[data-shell-density="compact"] .hero p,
      body[data-shell-density="compact"] .meta,
      body[data-shell-density="compact"] .module p,
      body[data-shell-density="compact"] .tile p,
      body[data-shell-density="compact"] .check p,
      body[data-shell-density="compact"] .report-note,
      body[data-shell-density="compact"] .report-message {
        font-size: 13px !important;
      }

      body[data-shell-density="compact"] .home-button,
      body[data-shell-density="compact"] .control-button,
      body[data-shell-density="compact"] .primary,
      body[data-shell-density="compact"] .secondary,
      body[data-shell-density="compact"] .button.primary,
      body[data-shell-density="compact"] .button.secondary,
      body[data-shell-density="compact"] .token,
      body[data-shell-density="compact"] .moisture-lane,
      body[data-shell-density="compact"] .card-action,
      body[data-shell-density="compact"] input,
      body[data-shell-density="compact"] select,
      body[data-shell-density="compact"] textarea {
        min-height: 38px !important;
        padding: 8px 10px !important;
      }

      body[data-sp-bar-mounted="true"] {
        min-height: 100vh;
      }

      .sp-bar-host {
        position: sticky;
        top: 8px;
        z-index: 50;
        width: calc(100% - (var(--sp-bar-edge) * 2));
        margin: 8px auto 0;
      }

      .sp-bar {
        display: flex;
        align-items: center;
        gap: 8px;
        overflow-x: auto;
        padding: 8px 10px;
        border-radius: 20px;
        border: 1px solid var(--sp-bar-line);
        background: var(--sp-bar-bg);
        box-shadow: var(--sp-bar-shadow);
        backdrop-filter: blur(16px);
        scrollbar-width: thin;
        justify-content: flex-start;
        scrollbar-color: rgba(96, 113, 100, 0.36) transparent;
        width: 100%;
      }

      .sp-bar::-webkit-scrollbar {
        height: 6px;
      }

      .sp-bar::-webkit-scrollbar-thumb {
        background: rgba(96, 113, 100, 0.32);
        border-radius: 999px;
      }

      .sp-group {
        flex: 0 0 auto;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding-right: 8px;
        border-right: 1px solid rgba(96, 113, 100, 0.12);
      }

      .sp-group:last-child {
        padding-right: 0;
        border-right: 0;
      }

      .sp-bar[data-fit="true"] {
        justify-content: space-between;
        overflow-x: hidden;
      }

      .sp-bar[data-fit="true"] .sp-group {
        flex: 0 1 auto;
      }

      .sp-bar[data-density="compact"] {
        gap: 6px;
        padding: 6px 8px;
      }

      .sp-bar[data-density="compact"] .sp-group {
        gap: 3px;
        padding-right: 6px;
      }

      .sp-bar[data-density="compact"] .sp-token,
      .sp-bar[data-density="compact"] .sp-control {
        min-height: 30px;
        padding-inline: 7px;
        gap: 5px;
      }

      .sp-bar[data-density="compact"] .sp-control {
        width: 30px;
        padding-inline: 0;
      }

      .sp-bar[data-density="compact"] .sp-icon,
      .sp-bar[data-density="compact"] .sp-icon svg {
        width: 14px;
        height: 14px;
      }

      .sp-bar[data-density="compact"] .sp-value {
        font-size: 11px;
      }

      .sp-bar[data-density="compact"] .sp-group[data-group="sensors"] .sp-value,
      .sp-bar[data-density="compact"] .sp-token[data-token-id="system-volume"] .sp-value {
        display: none;
      }

      .sp-bar[data-density="narrow"],
      .sp-bar[data-density="phone"] {
        display: grid;
        grid-template-columns: minmax(0, 1fr);
        align-items: stretch;
        justify-content: stretch;
        overflow: hidden;
        gap: 8px;
      }

      .sp-bar[data-density="narrow"] .sp-row,
      .sp-bar[data-density="phone"] .sp-row {
        min-width: 0;
      }

      .sp-bar[data-density="narrow"] .sp-row[data-row="top"],
      .sp-bar[data-density="phone"] .sp-row[data-row="top"] {
        display: grid;
        grid-template-columns: auto minmax(0, 1fr);
        gap: 8px;
        align-items: center;
      }

      .sp-bar[data-density="narrow"] .sp-row[data-row="bottom"],
      .sp-bar[data-density="phone"] .sp-row[data-row="bottom"] {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 6px;
        align-items: center;
      }

      .sp-bar[data-density="narrow"] .sp-row-cluster,
      .sp-bar[data-density="phone"] .sp-row-cluster {
        min-width: 0;
        display: flex;
        align-items: center;
        gap: 4px;
      }

      .sp-bar[data-density="narrow"] .sp-row-cluster[data-cluster="controls"],
      .sp-bar[data-density="phone"] .sp-row-cluster[data-cluster="controls"] {
        justify-content: flex-start;
      }

      .sp-bar[data-density="narrow"] .sp-row-cluster[data-cluster="devices"],
      .sp-bar[data-density="phone"] .sp-row-cluster[data-cluster="devices"] {
        justify-content: flex-end;
        overflow-x: auto;
        scrollbar-width: none;
      }

      .sp-bar[data-density="narrow"] .sp-row-cluster[data-cluster="devices"]::-webkit-scrollbar,
      .sp-bar[data-density="phone"] .sp-row-cluster[data-cluster="devices"]::-webkit-scrollbar {
        display: none;
      }

      .sp-bar[data-density="narrow"] .sp-token,
      .sp-bar[data-density="narrow"] .sp-control,
      .sp-bar[data-density="phone"] .sp-token,
      .sp-bar[data-density="phone"] .sp-control {
        min-height: 28px;
        padding-inline: 6px;
        gap: 4px;
      }

      .sp-bar[data-density="narrow"] .sp-control,
      .sp-bar[data-density="phone"] .sp-control {
        width: 28px;
        padding-inline: 0;
      }

      .sp-bar[data-density="narrow"] .sp-icon,
      .sp-bar[data-density="narrow"] .sp-icon svg,
      .sp-bar[data-density="phone"] .sp-icon,
      .sp-bar[data-density="phone"] .sp-icon svg {
        width: 14px;
        height: 14px;
      }

      .sp-bar[data-density="narrow"] .sp-value,
      .sp-bar[data-density="phone"] .sp-value {
        font-size: 11px;
      }

      .sp-bar[data-density="narrow"] .sp-row[data-row="bottom"] .sp-token,
      .sp-bar[data-density="phone"] .sp-row[data-row="bottom"] .sp-token {
        width: 100%;
        min-width: 0;
        justify-content: center;
      }

      .sp-bar[data-density="stacked"] {
        display: grid;
        grid-template-columns: minmax(0, 0.95fr) minmax(0, 1.35fr);
        grid-template-areas:
          "controls devices"
          "irrigation irrigation"
          "sensors system";
        align-items: start;
        justify-content: stretch;
        overflow-x: visible;
        gap: 8px 10px;
      }

      .sp-bar[data-density="stacked"] .sp-group {
        min-width: 0;
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
        padding-right: 0;
        border-right: 0;
      }

      .sp-bar[data-density="stacked"] .sp-group[data-group="controls"] {
        grid-area: controls;
        justify-content: flex-start;
      }

      .sp-bar[data-density="stacked"] .sp-group[data-group="devices"] {
        grid-area: devices;
        justify-content: flex-end;
      }

      .sp-bar[data-density="stacked"] .sp-group[data-group="irrigation"] {
        grid-area: irrigation;
        justify-content: space-between;
      }

      .sp-bar[data-density="stacked"] .sp-group[data-group="sensors"] {
        grid-area: sensors;
        justify-content: flex-start;
      }

      .sp-bar[data-density="stacked"] .sp-group[data-group="system"] {
        grid-area: system;
        justify-content: flex-end;
      }

      .sp-bar[data-density="stacked"] .sp-token,
      .sp-bar[data-density="stacked"] .sp-control {
        min-height: 28px;
        padding-inline: 6px;
        gap: 4px;
      }

      .sp-bar[data-density="stacked"] .sp-control {
        width: 28px;
        padding-inline: 0;
      }

      .sp-bar[data-density="stacked"] .sp-icon,
      .sp-bar[data-density="stacked"] .sp-icon svg {
        width: 14px;
        height: 14px;
      }

      .sp-bar[data-density="stacked"] .sp-value {
        font-size: 11px;
      }

      .sp-bar[data-density="stacked"] .sp-group[data-group="sensors"] .sp-value,
      .sp-bar[data-density="stacked"] .sp-token[data-token-id="system-volume"] .sp-value {
        display: none;
      }

      .sp-bar[data-density="stacked"] .sp-group[data-group="irrigation"] .sp-token {
        flex: 1 1 calc(20% - 8px);
        justify-content: center;
        min-width: 0;
      }

      @media (max-width: 540px) {
        .sp-bar[data-density="stacked"] {
          grid-template-columns: 1fr;
          grid-template-areas:
            "controls"
            "devices"
            "irrigation"
            "sensors"
            "system";
        }

        .sp-bar[data-density="stacked"] .sp-group[data-group="controls"],
        .sp-bar[data-density="stacked"] .sp-group[data-group="devices"],
        .sp-bar[data-density="stacked"] .sp-group[data-group="sensors"],
        .sp-bar[data-density="stacked"] .sp-group[data-group="system"] {
          justify-content: flex-start;
        }

        .sp-bar[data-density="stacked"] .sp-group[data-group="irrigation"] .sp-token {
          flex-basis: calc(50% - 6px);
        }
      }

      .sp-token,
      .sp-control {
        appearance: none;
        flex: 0 0 auto;
        min-height: 32px;
        border: 1px solid transparent;
        border-radius: 999px;
        padding: 0 8px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        color: var(--sp-bar-ink);
        background: rgba(255, 255, 255, 0.7);
        text-decoration: none;
        cursor: pointer;
        font: inherit;
        white-space: nowrap;
        transition: transform 140ms ease, box-shadow 140ms ease, border-color 140ms ease, background 140ms ease;
      }

      .sp-token:hover,
      .sp-token:focus-visible,
      .sp-control:hover,
      .sp-control:focus-visible {
        transform: translateY(-1px);
        box-shadow: 0 10px 22px rgba(21, 36, 26, 0.12);
        outline: none;
      }

      .sp-control {
        padding: 0;
        width: 32px;
        background: rgba(45, 93, 67, 0.08);
        border-color: rgba(45, 93, 67, 0.18);
      }

      .sp-control[data-active="true"] {
        background: var(--sp-bar-active-bg);
        color: var(--sp-bar-active-ink);
        border-color: var(--sp-bar-active-line);
      }

      .sp-token[data-state="neutral"] {
        background: var(--sp-bar-neutral-bg);
        color: var(--sp-bar-neutral-ink);
        border-color: var(--sp-bar-neutral-line);
      }

      .sp-token[data-state="online"] {
        background: var(--sp-bar-online-bg);
        color: var(--sp-bar-online-ink);
        border-color: var(--sp-bar-online-line);
      }

      .sp-token[data-state="attention"] {
        background: var(--sp-bar-attention-bg);
        color: var(--sp-bar-attention-ink);
        border-color: var(--sp-bar-attention-line);
      }

      .sp-token[data-state="fault"] {
        background: var(--sp-bar-fault-bg);
        color: var(--sp-bar-fault-ink);
        border-color: var(--sp-bar-fault-line);
      }

      .sp-token[data-state="active"] {
        background: var(--sp-bar-active-bg);
        color: var(--sp-bar-active-ink);
        border-color: var(--sp-bar-active-line);
      }

      .sp-token[data-blink="true"],
      .sp-control[data-blink="true"] {
        animation: sp-bar-pulse 1.2s ease-in-out infinite;
      }

      .sp-token[data-state="active"][data-blink="true"],
      .sp-control[data-active="true"][data-blink="true"] {
        animation-name: sp-bar-pulse-active;
      }

      @keyframes sp-bar-pulse {
        0%,
        100% {
          box-shadow: 0 0 0 0 rgba(202, 142, 28, 0.22);
        }
        50% {
          box-shadow: 0 0 0 7px rgba(202, 142, 28, 0);
        }
      }

      @keyframes sp-bar-pulse-active {
        0%,
        100% {
          box-shadow: 0 0 0 0 rgba(37, 95, 151, 0.24);
        }
        50% {
          box-shadow: 0 0 0 7px rgba(37, 95, 151, 0);
        }
      }

      .sp-icon {
        width: 16px;
        height: 16px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        flex: 0 0 auto;
      }

      .sp-icon svg {
        width: 16px;
        height: 16px;
        display: block;
        stroke: currentColor;
        fill: none;
        stroke-width: 1.8;
        stroke-linecap: round;
        stroke-linejoin: round;
      }

      .sp-value {
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.01em;
      }

      .sp-value:empty {
        display: none;
      }

      .sp-tooltip {
        position: fixed;
        z-index: 80;
        max-width: min(320px, calc(100vw - 24px));
        padding: 10px 12px;
        border-radius: 14px;
        border: 1px solid rgba(53, 88, 63, 0.12);
        background: rgba(33, 44, 36, 0.94);
        color: #eff8f0;
        box-shadow: 0 16px 36px rgba(16, 26, 20, 0.28);
        font: 13px/1.45 "Segoe UI", "Trebuchet MS", sans-serif;
        pointer-events: none;
        opacity: 0;
        transform: translateY(4px);
        transition: opacity 120ms ease, transform 120ms ease;
      }

      .sp-tooltip[data-visible="true"] {
        opacity: 1;
        transform: translateY(0);
      }

      .sp-tooltip-title {
        display: block;
        margin-bottom: 4px;
        font-weight: 700;
        color: #ffffff;
      }

      .sp-tooltip-subtitle {
        display: block;
        margin-bottom: 8px;
        color: rgba(199, 223, 205, 0.84);
        font-size: 12px;
      }

      .sp-tooltip-body {
        display: grid;
        gap: 8px;
      }

      .sp-tooltip-description {
        margin: 0;
        color: rgba(239, 248, 240, 0.9);
      }

      .sp-tooltip-section {
        display: grid;
        gap: 6px;
        padding-top: 8px;
        border-top: 1px solid rgba(216, 232, 218, 0.14);
      }

      .sp-tooltip-section:first-of-type {
        padding-top: 0;
        border-top: 0;
      }

      .sp-tooltip-section-title {
        font-size: 11px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: rgba(196, 220, 201, 0.84);
      }

      .sp-tooltip-row {
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto;
        gap: 10px;
        align-items: start;
      }

      .sp-tooltip-row-label {
        min-width: 0;
        color: #ffffff;
        font-weight: 600;
      }

      .sp-tooltip-row-value {
        white-space: nowrap;
        text-align: right;
        color: #d5f0db;
        font-weight: 700;
      }

      @media (max-width: 760px) {
        .sp-bar-host {
          width: calc(100% - 12px);
          margin-top: 6px;
        }

        .sp-bar {
          padding: 7px 8px;
        }

        .sp-group {
          gap: 4px;
          padding-right: 6px;
        }

        .sp-token,
        .sp-control {
          min-height: 30px;
          padding-inline: 7px;
        }

        .sp-control {
          width: 30px;
          padding-inline: 0;
        }

        .sp-tooltip {
          max-width: min(340px, calc(100vw - 16px));
        }
      }
    `;
    document.head.appendChild(style);
  }

  function ensureHost() {
    let host = document.getElementById(HOST_ID);
    if (host) {
      applyPageOffset(host);
      return host;
    }

    host = document.createElement("header");
    host.id = HOST_ID;
    host.className = "sp-bar-host";
    host.innerHTML = '<div class="sp-bar" id="sp-compact-bar" role="toolbar" aria-label="Smart Platform status bar"></div>';

    const existingTopbar = document.querySelector(".topbar");
    if (existingTopbar) {
      existingTopbar.remove();
    }

    document.body.insertBefore(host, document.body.firstChild);
    document.body.setAttribute("data-sp-bar-mounted", "true");
    applyPageOffset(host);
    return host;
  }

  function applyPageOffset(host) {
    const target = host || document.getElementById(HOST_ID);
    const height = target ? Math.ceil(target.getBoundingClientRect().height || 0) : 0;
    document.documentElement.style.setProperty("--smart-platform-bar-height", `${Math.max(0, height)}px`);
  }

  function ensureTooltip() {
    let tooltip = document.getElementById(TOOLTIP_ID);
    if (tooltip) {
      return tooltip;
    }

    tooltip = document.createElement("div");
    tooltip.id = TOOLTIP_ID;
    tooltip.className = "sp-tooltip";
    tooltip.setAttribute("data-visible", "false");
    document.body.appendChild(tooltip);
    return tooltip;
  }

  function icon(name, options) {
    const opts = options || {};
    switch (name) {
      case "home":
        return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 10.5 12 4l7 6.5"></path><path d="M7.5 9.8V20h9V9.8"></path></svg>';
      case "keyboard":
        return '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3.5" y="6.5" width="17" height="10" rx="2"></rect><path d="M6.5 10.5h.01M9.5 10.5h.01M12.5 10.5h.01M15.5 10.5h.01M6.5 13.5h7"></path></svg>';
      case "fullscreen":
        return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 4H4v4M16 4h4v4M8 20H4v-4M16 20h4v-4"></path></svg>';
      case "desktop":
        return '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="5" width="16" height="10" rx="2"></rect><path d="M10 19h4M12 15v4"></path></svg>';
      case "phone":
        return '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="7" y="2.5" width="10" height="19" rx="2.5"></rect><path d="M10 6h4"></path><circle cx="12" cy="18.3" r="0.8" fill="currentColor" stroke="none"></circle></svg>';
      case "tablet":
        return '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="3.5" width="14" height="17" rx="2.5"></rect><circle cx="12" cy="17.5" r="0.8" fill="currentColor" stroke="none"></circle></svg>';
      case "display":
        return '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3.5" y="4.5" width="17" height="11" rx="2"></rect><path d="M9 19h6"></path></svg>';
      case "raspberry_pi":
        return '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4.5" y="5.5" width="15" height="13" rx="2"></rect><rect x="7.8" y="8.8" width="5.4" height="5.4" rx="1"></rect><circle cx="16.4" cy="9.2" r="1"></circle><path d="M3 8h1.5M3 11h1.5M3 14h1.5M3 17h1.5M19.5 8H21M19.5 11H21M19.5 14H21M7 4v1.5M10 4v1.5M13 4v1.5M16 4v1.5"></path></svg>';
      case "esp32":
        return '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="6.5" y="5.5" width="11" height="13" rx="1.8"></rect><rect x="9.2" y="8.6" width="5.6" height="3.8" rx="0.8"></rect><path d="M5 8h1.5M5 11h1.5M5 14h1.5M17.5 8H19M17.5 11H19M17.5 14H19M8.5 19.5v-1.8M11 19.5v-1.8M13.5 19.5v-1.8M16 19.5v-1.8"></path></svg>';
      case "manual":
        return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M10 21V9.4a1.7 1.7 0 0 1 3.4 0V13"></path><path d="M13.4 11.6a1.7 1.7 0 0 1 3.2.3V15"></path><path d="M16.6 12.8a1.6 1.6 0 0 1 3 1V18"></path><path d="M8.2 13.2 6.9 12a1.8 1.8 0 0 0-2.9 2.1l3.1 4.8A4 4 0 0 0 10.5 21H17"></path></svg>';
      case "automatic":
        return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3.5c-3.7 0-6.7 3-6.7 6.7S8.3 17 12 17s6.7-3 6.7-6.8S15.7 3.5 12 3.5Z"></path><path d="M12 1.5v2M12 20.5v2M4.8 4.8l1.4 1.4M17.8 17.8l1.4 1.4M1.5 12h2M20.5 12h2M4.8 19.2l1.4-1.4M17.8 6.2l1.4-1.4"></path><circle cx="12" cy="10.2" r="1.6"></circle></svg>';
      case "water":
        return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3.4c2.7 3.5 5.2 6.2 5.2 9.2a5.2 5.2 0 1 1-10.4 0c0-3 2.5-5.7 5.2-9.2Z"></path></svg>';
      case "humidity":
        return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3.7c2.4 3.2 4.6 5.5 4.6 8a4.6 4.6 0 1 1-9.2 0c0-2.5 2.2-4.8 4.6-8Z"></path><path d="M15.5 16.2a3.6 3.6 0 0 1-5.8 0"></path><circle cx="12" cy="11.8" r="0.8" fill="currentColor" stroke="none"></circle></svg>';
      case "temperature": {
        const fill = Math.max(0, Math.min(1, Number(opts.fill || 0)));
        const top = 15 - (fill * 6);
        return `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M10 5a2 2 0 0 1 4 0v8.2a4 4 0 1 1-4 0V5"></path><path d="M12 8.2v6"></path><path d="M10.9 ${top.toFixed(1)}h2.2"></path></svg>`;
      }
      case "light":
        if (opts.variant === "moon") {
          return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15.5 3.8a8.3 8.3 0 1 0 4.7 14.9A8.8 8.8 0 0 1 15.5 3.8Z"></path><path d="M16.8 8.2h.01M18.8 11.4h.01"></path></svg>';
        }
        return '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"></circle><path d="M12 2v2.2M12 19.8V22M4.9 4.9l1.6 1.6M17.5 17.5l1.6 1.6M2 12h2.2M19.8 12H22M4.9 19.1l1.6-1.6M17.5 6.5l1.6-1.6"></path></svg>';
      case "alert":
        return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4.2 20 19H4z"></path><path d="M12 9v4.6"></path><circle cx="12" cy="16.8" r="0.9" fill="currentColor" stroke="none"></circle></svg>';
      case "wifi":
        if (opts.variant === "offline") {
          return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4.5 9.5a11 11 0 0 1 15 0"></path><path d="M7.5 12.5a7 7 0 0 1 9 0"></path><path d="M10.5 15.5a3 3 0 0 1 3 0"></path><circle cx="12" cy="19" r="1" fill="currentColor" stroke="none"></circle><path d="M4 4l16 16"></path></svg>';
        }
        return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4.5 9.5a11 11 0 0 1 15 0"></path><path d="M7.5 12.5a7 7 0 0 1 9 0"></path><path d="M10.5 15.5a3 3 0 0 1 3 0"></path><circle cx="12" cy="19" r="1" fill="currentColor" stroke="none"></circle></svg>';
      case "sync":
        if (opts.variant === "offline") {
          return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 7v5h-5"></path><path d="M4 17v-5h5"></path><path d="M6.5 11A6 6 0 0 1 17 8"></path><path d="M17.5 13A6 6 0 0 1 7 16"></path><path d="M5 5 19 19"></path></svg>';
        }
        if (opts.variant === "pending") {
          return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 7v5h-5"></path><path d="M4 17v-5h5"></path><path d="M6.5 11A6 6 0 0 1 17 8l3 4"></path><path d="M17.5 13A6 6 0 0 1 7 16l-3-4"></path><circle cx="12" cy="12" r="1.1" fill="currentColor" stroke="none"></circle></svg>';
        }
        return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 7v5h-5"></path><path d="M4 17v-5h5"></path><path d="M6.5 11A6 6 0 0 1 17 8l3 4"></path><path d="M17.5 13A6 6 0 0 1 7 16l-3-4"></path></svg>';
      case "volume": {
        const level = opts.level;
        if (level == null) {
          return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 14h4l5 4V6l-5 4H5z"></path><path d="M17.5 9.5a3.5 3.5 0 0 1 0 5"></path><path d="M19.5 6.5v0"></path></svg>';
        }
        if (level <= 0) {
          return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 14h4l5 4V6l-5 4H5z"></path><path d="M17 9 21 15"></path><path d="M21 9 17 15"></path></svg>';
        }
        if (level < 0.34) {
          return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 14h4l5 4V6l-5 4H5z"></path><path d="M17 10.5a2.5 2.5 0 0 1 0 3"></path></svg>';
        }
        if (level < 0.67) {
          return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 14h4l5 4V6l-5 4H5z"></path><path d="M17 10a3 3 0 0 1 0 4"></path><path d="M19.3 8.2a5.5 5.5 0 0 1 0 7.6"></path></svg>';
        }
        return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 14h4l5 4V6l-5 4H5z"></path><path d="M17 10a3 3 0 0 1 0 4"></path><path d="M19.3 8.2a5.5 5.5 0 0 1 0 7.6"></path><path d="M21.3 6a8.5 8.5 0 0 1 0 12"></path></svg>';
      }
      case "battery": {
        const fill = Math.max(0, Math.min(1, Number(opts.fill || 0)));
        const width = Math.max(0, Math.min(11, Math.round(fill * 11)));
        const fillColor = opts.saver ? "currentColor" : "none";
        const overlay = opts.charging
          ? '<path d="m12 8.2-1.8 3.5H13l-1 4.1 3-4.7h-2.6L14 8.2"></path>'
          : opts.saver
          ? '<path d="M11.2 10.1c1.4-1.3 3.4-1.6 4.9-1.4-1.2.8-1.8 2-1.9 3.1-.1 1.1.3 2.3 1.2 3.2-1.9.1-3.8-.4-5-1.9-1-1.3-1.1-2.3-.9-3Z"></path>'
          : "";
        return `<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="7" width="17" height="10" rx="2"></rect><path d="M20 10h1.5v4H20"></path><rect x="5.2" y="9.2" width="${width}" height="5.6" rx="1.1" fill="${fillColor}" stroke="none"></rect>${overlay}</svg>`;
      }
      case "language":
        return '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"></circle><path d="M3.5 12h17"></path><path d="M12 3a14 14 0 0 1 0 18"></path><path d="M12 3a14 14 0 0 0 0 18"></path></svg>';
      case "time":
        return '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8.5"></circle><path d="M12 7.5v5l3 2"></path></svg>';
      case "date":
        return '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="5" width="16" height="15" rx="2"></rect><path d="M8 3.5v3M16 3.5v3M4 9h16"></path></svg>';
      default:
        return icon("raspberry_pi");
    }
  }

  function isLoopbackHost(hostname) {
    return hostname === "127.0.0.1" || hostname === "localhost";
  }

  function currentShell(snapshot) {
    return (snapshot && snapshot.current_shell) || {};
  }

  function runtimeProfile(snapshot) {
    return String(currentShell(snapshot).runtime_profile || "").toLowerCase();
  }

  function isSmokeRuntime(snapshot) {
    const profile = runtimeProfile(snapshot);
    if (profile) {
      return profile !== "owner_device";
    }

    if (isLoopbackHost(window.location.hostname)) {
      return true;
    }

    const baseUrl = currentShell(snapshot).shell_base_url;
    if (!baseUrl) {
      return false;
    }

    try {
      return isLoopbackHost(new URL(baseUrl, window.location.href).hostname);
    } catch (_error) {
      return false;
    }
  }

  function isLaptopSmoke(snapshot) {
    return isSmokeRuntime(snapshot);
  }

  function viewerKindOrder(kind) {
    const order = {
      phone: 0,
      desktop: 1,
      tablet: 2,
      display: 3
    };
    return order[kind] ?? 9;
  }

  function normalizeViewerKind(kind) {
    const normalized = String(kind || "desktop").toLowerCase();
    if (normalized === "phone" || normalized === "tablet" || normalized === "display" || normalized === "desktop") {
      return normalized;
    }
    return "desktop";
  }

  function viewerIcon(kind) {
    const icons = {
      phone: "phone",
      tablet: "tablet",
      display: "display",
      desktop: "desktop"
    };
    return icons[normalizeViewerKind(kind)] || "desktop";
  }

  function defaultViewerLabel(kind) {
    const labels = {
      phone: { title: "Phone", value: "PH" },
      tablet: { title: "Tablet", value: "TB" },
      display: { title: "Pi Display", value: "Pi" },
      desktop: { title: "Desktop", value: "PC" }
    };
    return labels[normalizeViewerKind(kind)] || labels.desktop;
  }

  function detectClient(snapshot) {
    const userAgent = String(navigator.userAgent || "").toLowerCase();
    const width = Math.max(window.innerWidth || 0, (window.screen && window.screen.width) || 0);
    const touchCapable = (navigator.maxTouchPoints || 0) > 0 || (window.matchMedia && window.matchMedia("(pointer: coarse)").matches);
    const mobilePhone = /iphone|ipod|android.+mobile|windows phone|mobile/.test(userAgent);
    const tabletDevice = /ipad|tablet/.test(userAgent) || (!mobilePhone && touchCapable && width <= 1366);
    const shellType = String(currentShell(snapshot).node_type || "").toLowerCase();
    const armLinuxBrowser = /linux arm|linux aarch64|armv7l|armv8l|raspbian/.test(userAgent);
    const smokeRuntime = isSmokeRuntime(snapshot);

    if (mobilePhone) {
      return { kind: "phone", icon: "phone", value: "PH", title: "Phone", detail: "Phone client detected. Touch-first hints stay active here.", state: "active", blink: smokeRuntime };
    }
    if (shellType === "raspberry_pi" && armLinuxBrowser) {
      return { kind: "display", icon: "display", value: "Pi", title: "Pi Display", detail: "Embedded Raspberry Pi display profile detected.", state: "active", blink: smokeRuntime };
    }
    if (tabletDevice) {
      return { kind: "tablet", icon: "tablet", value: "TB", title: "Tablet", detail: "Tablet client detected. Compact tap-first hints stay available.", state: "active", blink: smokeRuntime };
    }

    return {
      kind: "desktop",
      icon: "desktop",
      value: "PC",
      title: "Desktop",
      detail: smokeRuntime
        ? "Smoke runtime is active. This browser is a viewer, and the compact bar is showing preview-only board states."
        : "Desktop client detected. Hover and keyboard helpers can be toggled from the input control.",
      state: "active",
      blink: smokeRuntime
    };
  }

  function viewerTokens(snapshot) {
    const localViewer = detectClient(snapshot);
    const localViewerId = ensureViewerId();
    const smokeRuntime = isSmokeRuntime(snapshot);
    const provided = Array.isArray((snapshot || {}).viewers) ? snapshot.viewers : [];
    const viewers = provided.length
      ? provided.map((viewer) => {
          const kind = normalizeViewerKind(viewer.viewer_kind);
          const labels = defaultViewerLabel(kind);
          return {
            viewer_id: String(viewer.viewer_id || ""),
            viewer_kind: kind,
            title: String(viewer.title || labels.title),
            value: String(viewer.value || labels.value),
            page: String(viewer.page || "/")
          };
        })
      : [{ viewer_id: localViewerId, viewer_kind: localViewer.kind, title: localViewer.title, value: localViewer.value, page: window.location.pathname || "/" }];

    viewers.sort((left, right) => {
      if (left.viewer_id === localViewerId && right.viewer_id !== localViewerId) {
        return -1;
      }
      if (right.viewer_id === localViewerId && left.viewer_id !== localViewerId) {
        return 1;
      }
      const orderDiff = viewerKindOrder(left.viewer_kind) - viewerKindOrder(right.viewer_kind);
      if (orderDiff !== 0) {
        return orderDiff;
      }
      return left.value.localeCompare(right.value);
    });

    return viewers.map((viewer) => {
      const currentDevice = viewer.viewer_id === localViewerId;
      const labels = defaultViewerLabel(viewer.viewer_kind);
      const page = viewer.page && viewer.page !== "/" ? ` Current page: ${viewer.page}.` : "";
      return {
        id: `viewer-${viewer.viewer_id || viewer.viewer_kind}`,
        icon: viewerIcon(viewer.viewer_kind),
        value: viewer.value || labels.value,
        title: viewer.title || labels.title,
        state: "active",
        blink: smokeRuntime,
        detail: currentDevice
          ? `This ${labels.title.toLowerCase()} is an active Smart Platform viewer.${page}`
          : `${viewer.title || labels.title} is also viewing the current Smart Platform shell.${page}`
      };
    });
  }

  function resolveModule(snapshot, id) {
    return ((snapshot || {}).module_cards || []).find((module) => module.id === id) || null;
  }

  function boardTokens(snapshot) {
    const current = ((snapshot || {}).nodes || {}).current || {};
    const peer = ((snapshot || {}).nodes || {}).peer || {};
    const smokeRuntime = isSmokeRuntime(snapshot);
    const shellType = String(currentShell(snapshot).node_type || "raspberry_pi").toLowerCase();

    if (smokeRuntime) {
      return [
        {
          id: "board-rpi",
          icon: "raspberry_pi",
          value: "RPi",
          title: "Raspberry Pi",
          state: "neutral",
          detail: shellType === "raspberry_pi"
            ? "Smoke runtime is serving the Raspberry Pi shell from a desktop host. The physical Raspberry Pi board is not attached right now. To test the real board, run the shell from the device itself."
            : "Raspberry Pi owner is not attached in this smoke runtime. To test turret-side hardware, power the Raspberry Pi board and open its shell directly."
        },
        {
          id: "board-esp",
          icon: "esp32",
          value: "ESP",
          title: "ESP32",
          state: "neutral",
          detail: "ESP32 owner is currently absent in this smoke runtime. Power the ESP32 board and restore the peer link to unlock irrigation-owned slices."
        }
      ];
    }

    const defs = [
      { id: "board-rpi", icon: "raspberry_pi", value: "RPi", title: "Raspberry Pi", node: shellType === "raspberry_pi" ? current : peer, local: shellType === "raspberry_pi" },
      { id: "board-esp", icon: "esp32", value: "ESP", title: "ESP32", node: shellType === "esp32" ? current : peer, local: shellType === "esp32" }
    ];

    return defs.map((item) => {
      const node = item.node || {};
      const reachable = item.local ? true : Boolean(node.reachable);
      const health = String(node.health || "offline").toLowerCase();

      if (!reachable) {
        return {
          id: item.id,
          icon: item.icon,
          value: item.value,
          title: item.title,
          state: "neutral",
          blink: false,
          detail: `${item.title} is expected by the platform but is not connected yet.`
        };
      }

      if (health === "degraded") {
        return {
          id: item.id,
          icon: item.icon,
          value: item.value,
          title: item.title,
          state: "attention",
          detail: `${item.title} is visible, but one or more owner services are degraded.`
        };
      }

      return {
        id: item.id,
        icon: item.icon,
        value: item.value,
        title: item.title,
        state: "online",
        detail: `${item.title} is connected and its owner-side shell is reachable.`
      };
    });
  }

  function modeTokens(snapshot) {
    if (isSmokeRuntime(snapshot)) {
      return [];
    }

    const shell = currentShell(snapshot);
    const turret = resolveModule(snapshot, "turret_bridge");
    const irrigation = resolveModule(snapshot, "irrigation");
    const tokens = [];

    if (turret && turret.owner_available) {
      const automatic = shell.active_mode === "automatic";
      tokens.push({
        id: "mode-turret",
        icon: automatic ? "automatic" : "manual",
        value: automatic ? "T:A" : "T:M",
        title: automatic ? "Turret Automatic" : "Turret Manual",
        state: "online",
        detail: automatic
          ? "Turret owner is available and the selected turret mode is automatic."
          : "Turret owner is available and the selected turret mode is manual."
      });
    }

    if (irrigation && irrigation.owner_available) {
      tokens.push({
        id: "mode-irrigation",
        icon: "manual",
        value: "I:M",
        title: "Irrigation Manual",
        state: "online",
        detail: "Irrigation owner is available. Manual mode stays visible until an explicit automatic policy is selected."
      });
    }

    return tokens;
  }

  function zoneTokens() {
    return Array.from({ length: 5 }, (_, index) => ({
      id: `zone-${index + 1}`,
      icon: "water",
      value: "--%",
      title: `Zone ${index + 1}`,
      state: "neutral",
      detail: `Zone ${index + 1}. Live soil moisture is not published in the shell snapshot yet. Later this tooltip can also show the linked plant profile from Gallery, Settings, or Irrigation.`
    }));
  }

  function sensorTokens(snapshot) {
    const hour = new Date().getHours();
    const night = hour >= 20 || hour < 6;
    return [
      {
        id: "sensor-air",
        icon: "humidity",
        value: "--",
        title: "Air Humidity",
        state: "neutral",
        detail: "Ambient humidity is not published in the current shell snapshot yet. The icon stays humidity-specific so it does not collide with future wind-speed indicators."
      },
      {
        id: "sensor-temp",
        icon: "temperature",
        iconOptions: { fill: 0 },
        value: "--°",
        title: "Temperature",
        state: "neutral",
        detail: "Ambient temperature is not published in the current shell snapshot yet. When a real value appears, this thermometer can fill proportionally instead of staying empty."
      },
      {
        id: "sensor-light",
        icon: "light",
        iconOptions: { variant: night ? "moon" : "sun" },
        value: "--",
        title: "Light / Day Cycle",
        state: "neutral",
        detail: night
          ? "Night-phase icon is derived from the current local time until a truthful light sensor value is published."
          : "Day-phase icon is derived from the current local time until a truthful light sensor value is published."
      }
    ];
  }

  function batteryToken() {
    if (!batterySnapshot.available) {
      return {
        id: "system-battery",
        icon: "battery",
        iconOptions: { fill: 0 },
        value: "--",
        title: "Battery",
        state: "neutral",
        detail: "Battery state is not available in this browser session."
      };
    }

    const fill = Math.max(0, Math.min(1, Number(batterySnapshot.level || 0)));
    const percent = Math.round(fill * 100);
    const saver = !batterySnapshot.charging && percent <= 20;
    return {
      id: "system-battery",
      icon: "battery",
      iconOptions: { fill, charging: batterySnapshot.charging, saver },
      value: `${percent}%`,
      title: "Battery",
      state: saver ? "attention" : batterySnapshot.charging ? "active" : "online",
      detail: batterySnapshot.charging
        ? `Client battery is charging. Current level: ${percent}%.`
        : saver
        ? `Client battery is low at ${percent}%. Compact saver styling is active.`
        : `Client battery level: ${percent}%.`
    };
  }

  function failureTitle(rawId) {
    return String(rawId || "unknown")
      .split(/[_-]+/)
      .filter(Boolean)
      .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
      .join(" ");
  }

  function failureReason(rawReason) {
    return String(rawReason || "none").replace(/[_-]+/g, " ");
  }

  function failureStateLabel(rawState) {
    const state = String(rawState || "").trim().toLowerCase();
    if (state === "locked") {
      return "Locked";
    }
    if (state === "degraded") {
      return "Degraded";
    }
    if (state === "fault") {
      return "Fault";
    }
    return "Attention";
  }

  function shellFailuresToken(snapshot) {
    const faults = (((snapshot || {}).summaries || {}).faults || {});
    const activeFailures = Array.isArray(faults.active_failures)
      ? faults.active_failures.filter((item) => item && typeof item === "object")
      : [];

    if (!activeFailures.length) {
      const legacyState = faults.has_fault ? "fault" : faults.has_degraded ? "attention" : "";
      if (!legacyState) {
        return null;
      }

      return {
        id: "system-failures",
        icon: "alert",
        value: "!",
        title: "Active Failures",
        state: legacyState,
        detail: String(faults.message || "The shell reports active failures without per-item details yet.")
      };
    }

    const hasFault = activeFailures.some((item) => String(item.shell_state || "").trim().toLowerCase() === "fault");
    const hasAttention = activeFailures.some((item) => {
      const state = String(item.shell_state || "").trim().toLowerCase();
      return state === "locked" || state === "degraded";
    });
    const detail = activeFailures
      .slice(0, 2)
      .map((item) => `${failureTitle(item.id)}: ${failureReason(item.reason)}.`)
      .join(" ");

    return {
      id: "system-failures",
      icon: "alert",
      value: String(activeFailures.length),
      title: "Active Failures",
      state: hasFault ? "fault" : hasAttention ? "attention" : "online",
      detail: detail || String(faults.message || "Shell-level failures currently affect routing or readiness."),
      tooltip: {
        title: "Active Failures",
        subtitle: activeFailures.length === 1 ? "1 shell-level issue" : `${activeFailures.length} shell-level issues`,
        description: String(faults.message || "Shell-level failures currently affect routing or readiness."),
        sections: [
          {
            title: "Failures",
            rows: activeFailures.slice(0, 6).map((item) => ({
              label: failureTitle(item.id),
              value: `${failureStateLabel(item.shell_state)} / ${failureReason(item.reason)}`
            }))
          }
        ]
      }
    };
  }

  function systemTokens(snapshot) {
    const smokeRuntime = isSmokeRuntime(snapshot);
    const current = ((snapshot || {}).nodes || {}).current || {};
    const diagnostics = (((snapshot || {}).summaries || {}).diagnostics || {});
    const failuresToken = shellFailuresToken(snapshot);
    const syncState = String(diagnostics.sync_state || "unknown");
    const locale = preferredLocale();
    const now = new Date();
    const wifiReady = !smokeRuntime && Boolean(current.wifi_ready);
    const syncReady = !smokeRuntime && syncState === "ready";
    const syncPending = !smokeRuntime && (syncState === "pending" || syncState === "never_synced");
    const syncLocalOnly = !smokeRuntime && syncState === "local_only";
    const syncRemoteUnavailable = !smokeRuntime && syncState === "remote_unavailable";
    const syncError = !smokeRuntime && syncState === "error";

    const items = [
      {
        id: "system-wifi",
        icon: "wifi",
        iconOptions: { variant: wifiReady ? "online" : "offline" },
        value: "",
        title: "Wi-Fi",
        state: smokeRuntime ? "neutral" : wifiReady ? "online" : "neutral",
        detail: smokeRuntime
          ? "Smoke runtime does not prove board-level Wi-Fi readiness."
          : wifiReady
          ? "The active owner reports network readiness."
          : "The active owner is not currently reporting Wi-Fi readiness."
      },
      {
        id: "system-sync",
        icon: "sync",
        iconOptions: {
          variant: smokeRuntime
            ? "pending"
            : syncReady
            ? "online"
            : syncPending || syncLocalOnly
            ? "pending"
            : "offline"
        },
        value: "",
        title: "Sync",
        state: smokeRuntime ? "neutral" : syncReady ? "online" : syncError ? "fault" : (syncPending ? "attention" : "neutral"),
        detail: smokeRuntime
          ? "Smoke runtime keeps sync in preview mode. Real peer readiness must come from hardware-linked owners."
          : syncReady
          ? `Sync stack is ready. Current state: ${syncState}.`
          : syncLocalOnly
          ? "Background sync is disabled. This host is currently operating in local-only mode."
          : syncRemoteUnavailable
          ? "Base node connectivity is unavailable because the remote node is offline."
          : syncPending
          ? syncState === "never_synced"
            ? "Sync is enabled, but the first successful exchange has not completed yet."
            : "Peer link is visible, but sync is still pending."
          : syncError
          ? `Sync reported an error. Current state: ${syncState}.`
          : `Sync is not ready. Current state: ${syncState}.`
      }
    ];

    if (failuresToken) {
      items.push(failuresToken);
    }

    items.push(
      {
        id: "system-volume",
        icon: "volume",
        iconOptions: { level: null },
        value: "--",
        title: "Volume",
        state: "neutral",
        detail: "System volume is not exposed as a truthful browser-side signal yet, so the compact bar keeps it neutral instead of inventing a level."
      },
      batteryToken(),
      {
        id: "system-language",
        icon: "language",
        value: String(locale).slice(0, 2).toUpperCase(),
        title: "Language",
        state: "neutral",
        detail: `Current shell locale: ${locale}. Language switching belongs in Settings.`
      },
      {
        id: "system-time",
        icon: "time",
        value: now.toLocaleTimeString(locale, { hour: "2-digit", minute: "2-digit" }),
        title: "Time",
        state: "neutral",
        detail: `Client local time rendered for ${locale}.`
      },
      {
        id: "system-date",
        icon: "date",
        value: now.toLocaleDateString(locale, { month: "short", day: "2-digit" }),
        title: "Date",
        state: "neutral",
        detail: `Client local date rendered for ${locale}.`
      }
    );

    return items;
  }

  function tooltipPayloadForItem(item) {
    return item.tooltip || {
      title: item.title || "",
      description: item.detail || DEFAULT_TOOLTIP
    };
  }

  function tooltipPayloadAttr(item) {
    try {
      return esc(encodeURIComponent(JSON.stringify(tooltipPayloadForItem(item))));
    } catch (_error) {
      return "";
    }
  }

  function controlMarkup(item) {
    const detail = esc(item.detail || DEFAULT_TOOLTIP);
    const tooltipPayload = tooltipPayloadAttr(item);
    if (item.href) {
      return `
        <a class="sp-control" href="${esc(item.href)}" data-tooltip-title="${esc(item.title)}" data-tooltip-detail="${detail}" data-tooltip-payload="${tooltipPayload}">
          <span class="sp-icon">${icon(item.icon, item.iconOptions)}</span>
        </a>
      `;
    }

    return `
      <button
        type="button"
        class="sp-control"
        data-control-id="${esc(item.id)}"
        data-tooltip-title="${esc(item.title)}"
        data-tooltip-detail="${detail}"
        data-tooltip-payload="${tooltipPayload}"
        data-active="${item.active ? "true" : "false"}"
        data-blink="${item.blink ? "true" : "false"}">
        <span class="sp-icon">${icon(item.icon, item.iconOptions)}</span>
      </button>
    `;
  }

  function tokenMarkup(item) {
    const detail = esc(item.detail || DEFAULT_TOOLTIP);
    const tooltipPayload = tooltipPayloadAttr(item);
    return `
      <button
        type="button"
        class="sp-token"
        data-token-id="${esc(item.id || "")}"
        data-tooltip-title="${esc(item.title || "")}"
        data-tooltip-detail="${detail}"
        data-tooltip-payload="${tooltipPayload}"
        data-state="${esc(item.state || "neutral")}"
        data-blink="${item.blink ? "true" : "false"}">
        <span class="sp-icon">${icon(item.icon || "raspberry_pi", item.iconOptions)}</span>
        <span class="sp-value">${esc(item.value || "")}</span>
      </button>
    `;
  }

  function groupMarkup(groupName, items, renderer) {
    return `<div class="sp-group" data-group="${esc(groupName)}">${items.map(renderer).join("")}</div>`;
  }

  function clusterMarkup(clusterName, items, renderer) {
    return `<div class="sp-row-cluster" data-cluster="${esc(clusterName)}">${items.map(renderer).join("")}</div>`;
  }

  function summarizeState(items) {
    if (items.some((item) => item.state === "fault")) {
      return "fault";
    }
    if (items.some((item) => item.state === "attention")) {
      return "attention";
    }
    if (items.some((item) => item.state === "active")) {
      return "active";
    }
    if (items.some((item) => item.state === "online")) {
      return "online";
    }
    return "neutral";
  }

  function summarizeDetail(items) {
    return items.map((item) => `${item.title}: ${item.value || "--"}. ${item.detail || ""}`.trim()).join(" ");
  }

  function summaryTooltipValue(item) {
    if (item.value) {
      return item.value;
    }

    switch (item.state) {
      case "online":
        return "Ready";
      case "active":
        return "Active";
      case "attention":
        return "Waiting";
      case "fault":
        return "Fault";
      default:
        return "Preview";
    }
  }

  function summaryTooltipRows(items) {
    return items.map((item) => ({
      label: item.title || "",
      value: summaryTooltipValue(item)
    }));
  }

  function irrigationSummaryToken(snapshot) {
    const items = zoneTokens(snapshot);
    return {
      id: "summary-irrigation",
      icon: "water",
      value: `${items.length}Z`,
      title: "Irrigation Summary",
      state: summarizeState(items),
      detail: "Compact irrigation overview.",
      tooltip: {
        title: "Irrigation Summary",
        subtitle: "Compact zone overview",
        description: "The narrow desktop bar keeps irrigation compressed into one readable summary token.",
        sections: [
          {
            title: "Zones",
            rows: summaryTooltipRows(items)
          }
        ]
      }
    };
  }

  function sensorSummaryToken(snapshot) {
    const items = sensorTokens(snapshot);
    return {
      id: "summary-sensors",
      icon: "humidity",
      value: "ENV",
      title: "Sensor Summary",
      state: summarizeState(items),
      detail: "Compact environment overview.",
      tooltip: {
        title: "Sensor Summary",
        subtitle: "Compact environment overview",
        description: "Grouped environment readouts stay short in the bar and expand into rows here.",
        sections: [
          {
            title: "Sensors",
            rows: summaryTooltipRows(items)
          }
        ]
      }
    };
  }

  function systemSummaryToken(snapshot) {
    const items = systemTokens(snapshot);
    return {
      id: "summary-system",
      icon: "sync",
      value: "SYS",
      title: "System Summary",
      state: summarizeState(items),
      detail: "Prioritized platform overview.",
      tooltip: {
        title: "System Summary",
        subtitle: "Prioritized platform status",
        description: "The compact bar keeps only the platform signals that matter most and expands them into a readable matrix here.",
        sections: [
          {
            title: "System",
            rows: summaryTooltipRows(items)
          }
        ]
      }
    };
  }

  function controlTokens(snapshot, phoneDensity) {
    const localViewer = detectClient(snapshot);
    const fullscreenPending = fullscreenRestorePending();
    const controls = [
      { id: "home", href: `${window.location.origin}/`, icon: "home", title: "Smart Platform Home", detail: "Return to the Smart Platform launcher." },
      { id: "input", icon: "keyboard", title: "Input Helpers", detail: desktopControlsEnabled ? "Turret Manual action keys and hover helpers are enabled. Text fields keep normal typing behavior." : "Turret Manual action keys and hover helpers are disabled.", active: desktopControlsEnabled },
      {
        id: "fullscreen",
        icon: "fullscreen",
        title: "Fullscreen",
        detail: document.fullscreenElement
          ? "Leave fullscreen mode."
          : fullscreenPending
          ? "Browser fullscreen ended during page navigation. Use this control to restore fullscreen."
          : "Enter fullscreen mode.",
        active: document.fullscreenElement || fullscreenPending,
        blink: fullscreenPending
      }
    ];

    if (phoneDensity && localViewer.kind !== "desktop") {
      return controls.filter((item) => item.id !== "input");
    }

    return controls;
  }

  function phoneBarMarkup(controls, deviceTokens, summaryTokens) {
    return [
      `<div class="sp-row" data-row="top">${clusterMarkup("controls", controls, controlMarkup)}${clusterMarkup("devices", deviceTokens, tokenMarkup)}</div>`,
      `<div class="sp-row" data-row="bottom">${summaryTokens.map(tokenMarkup).join("")}</div>`
    ].join("");
  }

  function shouldUseNarrowDesktopDensity(snapshot, viewportWidth) {
    if (shouldUsePhoneDensity(snapshot, viewportWidth)) {
      return false;
    }

    return viewportWidth <= 1120;
  }

  function shouldUsePhoneDensity(snapshot, viewportWidth) {
    if (viewportWidth > 900) {
      return false;
    }

    return detectClient(snapshot).kind !== "desktop";
  }

  function measureBarFits(bar, density) {
    const host = bar.parentElement || document.body;
    const probe = bar.cloneNode(true);
    probe.style.position = "absolute";
    probe.style.visibility = "hidden";
    probe.style.pointerEvents = "none";
    probe.style.left = "0";
    probe.style.top = "-10000px";
    probe.style.width = `${bar.clientWidth}px`;
    probe.dataset.density = density;
    probe.dataset.fit = "false";
    host.appendChild(probe);
    const fits = probe.scrollWidth <= (probe.clientWidth + 1);
    probe.remove();
    return fits;
  }

  function chooseBarDensity(bar, viewportWidth, phoneDensity, narrowDesktopDensity) {
    if (phoneDensity) {
      return "phone";
    }

    if (narrowDesktopDensity) {
      return "narrow";
    }

    if (viewportWidth > 1320 && measureBarFits(bar, "full")) {
      return "full";
    }

    if (measureBarFits(bar, "compact")) {
      return "compact";
    }

    return "stacked";
  }

  function applyBarLayout(bar, snapshot, forcedDensity) {
    if (barLayoutFrame) {
      cancelAnimationFrame(barLayoutFrame);
    }

    barLayoutFrame = requestAnimationFrame(() => {
      barLayoutFrame = 0;
      const density = forcedDensity || (() => {
        const viewportWidth = Math.max(window.innerWidth || 0, document.documentElement.clientWidth || 0);
        const phoneDensity = shouldUsePhoneDensity(snapshot, viewportWidth);
        const narrowDesktopDensity = shouldUseNarrowDesktopDensity(snapshot, viewportWidth);
        return chooseBarDensity(bar, viewportWidth, phoneDensity, narrowDesktopDensity);
      })();
      bar.dataset.density = density;
      bar.dataset.fit = density === "full" || density === "compact" ? "true" : "false";
      applyPageOffset(bar.parentElement || undefined);
    });
  }

  function renderBar(snapshot) {
    const viewportWidth = Math.max(window.innerWidth || 0, document.documentElement.clientWidth || 0);
    const phoneDensity = shouldUsePhoneDensity(snapshot, viewportWidth);
    const narrowDesktopDensity = shouldUseNarrowDesktopDensity(snapshot, viewportWidth);
    const controls = controlTokens(snapshot, phoneDensity);
    const deviceTokens = [...viewerTokens(snapshot), ...boardTokens(snapshot), ...modeTokens(snapshot)];
    const summaryTokens = [irrigationSummaryToken(snapshot), sensorSummaryToken(snapshot), systemSummaryToken(snapshot)];

    const bar = document.getElementById("sp-compact-bar");
    if (!bar) {
      return;
    }

    const density = phoneDensity ? "phone" : narrowDesktopDensity ? "narrow" : null;

    if (density) {
      bar.innerHTML = phoneBarMarkup(controls, deviceTokens, summaryTokens);
    } else {
      bar.innerHTML = [
        groupMarkup("controls", controls, controlMarkup),
        groupMarkup("devices", deviceTokens, tokenMarkup),
        groupMarkup("irrigation", zoneTokens(snapshot), tokenMarkup),
        groupMarkup("sensors", sensorTokens(snapshot), tokenMarkup),
        groupMarkup("system", systemTokens(snapshot), tokenMarkup)
      ].join("");
    }

    applyBarLayout(bar, snapshot, density || undefined);
    bindInteractions();
    maybeShowFullscreenRestoreHint();
    applyPageOffset(bar.parentElement || undefined);
  }

  function maybeShowFullscreenRestoreHint() {
    if (!fullscreenRestorePending()) {
      fullscreenPendingHintPage = "";
      return;
    }

    const pageKey = `${window.location.pathname || "/"}${window.location.search || ""}`;
    if (fullscreenPendingHintPage === pageKey) {
      return;
    }

    const toggle = document.querySelector('.sp-control[data-control-id="fullscreen"]');
    if (!(toggle instanceof HTMLElement)) {
      return;
    }

    fullscreenPendingHintPage = pageKey;
    showTooltip(toggle, false);
  }

  function readTooltipPayload(target) {
    const encoded = target.getAttribute("data-tooltip-payload") || "";
    if (encoded) {
      try {
        return JSON.parse(decodeURIComponent(encoded));
      } catch (_error) {
        // Fall through to the plain-text tooltip fallback below.
      }
    }

    return {
      title: target.getAttribute("data-tooltip-title") || "",
      description: target.getAttribute("data-tooltip-detail") || DEFAULT_TOOLTIP
    };
  }

  function renderTooltipMarkup(payload) {
    const sections = Array.isArray(payload.sections) ? payload.sections : [];
    const description = payload.description
      ? `<p class="sp-tooltip-description">${esc(payload.description)}</p>`
      : "";
    const sectionMarkup = sections.map((section) => {
      const rows = Array.isArray(section.rows) ? section.rows : [];
      return `
        <section class="sp-tooltip-section">
          ${section.title ? `<div class="sp-tooltip-section-title">${esc(section.title)}</div>` : ""}
          <div class="sp-tooltip-table">
            ${rows.map((row) => `
              <div class="sp-tooltip-row">
                <span class="sp-tooltip-row-label">${esc(row.label || "")}</span>
                <span class="sp-tooltip-row-value">${esc(row.value || "")}</span>
              </div>
            `).join("")}
          </div>
        </section>
      `;
    }).join("");

    return `
      <span class="sp-tooltip-title">${esc(payload.title || "")}</span>
      ${payload.subtitle ? `<span class="sp-tooltip-subtitle">${esc(payload.subtitle)}</span>` : ""}
      <div class="sp-tooltip-body">${description}${sectionMarkup}</div>
    `;
  }

  function scheduleTooltipAutoHide() {
    clearTooltipHideTimer();
    const ownerId = tooltipOwnerId;
    tooltipHideTimer = window.setTimeout(() => {
      if (tooltipOwnerId === ownerId) {
        hideTooltip(true);
      }
    }, TOOLTIP_HIDE_MS);
  }

  function positionTooltipNearPointer(tooltip, target) {
    requestAnimationFrame(() => {
      const tipRect = tooltip.getBoundingClientRect();
      const rect = target.getBoundingClientRect();
      const hasPointer = tooltipPointerX > 0 || tooltipPointerY > 0;
      const anchorX = hasPointer ? tooltipPointerX : rect.left + (rect.width / 2);
      const anchorY = hasPointer ? tooltipPointerY : rect.bottom;
      const gap = 14;
      const preferredLeft = anchorX + gap;
      const left = preferredLeft + tipRect.width + 12 > window.innerWidth
        ? anchorX - tipRect.width - gap
        : preferredLeft;
      const preferredTop = anchorY + gap;
      const top = preferredTop + tipRect.height + 12 > window.innerHeight
        ? anchorY - tipRect.height - gap
        : preferredTop;
      tooltip.style.left = `${Math.min(Math.max(12, left), window.innerWidth - tipRect.width - 12)}px`;
      tooltip.style.top = `${Math.min(Math.max(12, top), window.innerHeight - tipRect.height - 12)}px`;
    });
  }

  function scheduleTooltipShow(target, pinned, event) {
    if (!(target instanceof HTMLElement)) {
      return;
    }
    if (tooltipPinned && !pinned) {
      return;
    }
    if (tooltipHoverTarget === target && tooltipShowTimer) {
      return;
    }
    clearTooltipShowTimer();
    setTooltipPointerOrigin(event);
    tooltipHoverTarget = target;
    tooltipShowTimer = window.setTimeout(() => {
      tooltipShowTimer = 0;
      if (tooltipHoverTarget === target) {
        showTooltip(target, pinned);
      }
    }, pinned ? 0 : TOOLTIP_SHOW_DELAY_MS);
  }

  function showTooltip(target, pinned) {
    const tooltip = ensureTooltip();
    const payload = readTooltipPayload(target);

    tooltip.innerHTML = renderTooltipMarkup(payload);
    tooltip.setAttribute("data-visible", "true");
    tooltipOwnerId = target.getAttribute("data-token-id") || target.getAttribute("data-control-id") || "";
    tooltipPinned = Boolean(pinned);
    scheduleTooltipAutoHide();
    positionTooltipNearPointer(tooltip, target);
  }

  function hideTooltip(force) {
    if (tooltipPinned && !force) {
      return;
    }
    clearTooltipShowTimer();
    clearTooltipHideTimer();
    const tooltip = ensureTooltip();
    tooltip.setAttribute("data-visible", "false");
    tooltipOwnerId = "";
    tooltipHoverTarget = null;
    if (force) {
      tooltipPinned = false;
    }
  }

  function normalizeShellNavigationHref(rawHref) {
    try {
      const url = new URL(rawHref, window.location.href);
      if (url.protocol === window.location.protocol && url.hostname === window.location.hostname && !url.port && window.location.port) {
        url.port = window.location.port;
        return url.href;
      }
      return rawHref;
    } catch (_error) {
      return rawHref;
    }
  }

  function bindInteractions() {
    const tokens = document.querySelectorAll(".sp-token, .sp-control");
    for (const token of tokens) {
      token.onpointerdown = () => {
        tooltipFocusSuppressedUntil = Date.now() + 700;
        hideTooltip(true);
      };
      token.onmouseenter = (event) => scheduleTooltipShow(token, tooltipPinned && tooltipOwnerId === (token.getAttribute("data-token-id") || token.getAttribute("data-control-id") || ""), event);
      token.onmousemove = (event) => {
        if (!tooltipHoverTarget && !tooltipOwnerId) {
          return;
        }
        if (tooltipMovedPastTolerance(event)) {
          hideTooltip(true);
        }
      };
      token.onfocus = () => {
        if (Date.now() < tooltipFocusSuppressedUntil) {
          return;
        }
        showTooltip(token, tooltipPinned && tooltipOwnerId === (token.getAttribute("data-token-id") || token.getAttribute("data-control-id") || ""));
      };
      token.onmouseleave = () => hideTooltip(true);
      token.onblur = () => hideTooltip(true);
    }

    const statusTokens = document.querySelectorAll(".sp-token");
    for (const token of statusTokens) {
      token.onclick = (event) => {
        event.preventDefault();
        const tokenId = token.getAttribute("data-token-id") || "";
        if (tooltipPinned && tooltipOwnerId === tokenId) {
          hideTooltip(true);
          return;
        }
        setTooltipPointerOrigin(event);
        showTooltip(token, false);
      };
    }

    const inputToggle = document.querySelector('.sp-control[data-control-id="input"]');
    const fullscreenToggle = document.querySelector('.sp-control[data-control-id="fullscreen"]');

    if (inputToggle) {
      inputToggle.onclick = (event) => {
        event.preventDefault();
        setTooltipPointerOrigin(event);
        desktopControlsEnabled = !desktopControlsEnabled;
        writeStorage(STORAGE_KEY, desktopControlsEnabled ? "1" : "0");
        window.dispatchEvent(new CustomEvent("smart-platform:desktop-controls-updated", {
          detail: { desktop_controls_enabled: desktopControlsEnabled }
        }));
        renderBar(currentSnapshot);
        const nextToggle = document.querySelector('.sp-control[data-control-id="input"]');
        if (nextToggle) {
          showTooltip(nextToggle, false);
        }
      };
    }

    if (fullscreenToggle) {
      fullscreenToggle.onclick = async (event) => {
        event.preventDefault();
        setTooltipPointerOrigin(event);
        const wantsFullscreen = !document.fullscreenElement;
        fullscreenToggleIntent = wantsFullscreen ? "enter" : "exit";
        setFullscreenPreference(wantsFullscreen);
        setFullscreenNavigationPending(wantsFullscreen);
        clearFullscreenResumeListeners();
        try {
          if (document.fullscreenElement && document.exitFullscreen) {
            await document.exitFullscreen();
          } else if (document.documentElement.requestFullscreen) {
            await document.documentElement.requestFullscreen();
          }
        } catch (_error) {
          // Ignore browser fullscreen rejections; the tooltip already explains the action.
          setFullscreenPreference(wantsFullscreen);
          setFullscreenNavigationPending(wantsFullscreen && !document.fullscreenElement);
          fullscreenToggleIntent = null;
        }
        const nextPreference = fullscreenToggleIntent === "exit" ? false : (wantsFullscreen || Boolean(document.fullscreenElement));
        setFullscreenPreference(nextPreference);
        setFullscreenNavigationPending(nextPreference && !document.fullscreenElement);
        persistFullscreenPreference(nextPreference).catch(() => {});
        renderBar(currentSnapshot);
        const nextToggle = document.querySelector('.sp-control[data-control-id="fullscreen"]');
        if (nextToggle) {
          showTooltip(nextToggle, false);
        }
      };
    }

    if (!globalListenersInstalled) {
      globalListenersInstalled = true;

      document.addEventListener("click", (event) => {
        const target = event.target;
        if (!event.defaultPrevented && event.button === 0 && !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey && target instanceof HTMLElement) {
          const anchor = target.closest("a[href]");
          if (anchor instanceof HTMLAnchorElement) {
            const normalizedHref = normalizeShellNavigationHref(anchor.href);
            markFullscreenResumeOnInternalNavigation(normalizedHref);
            if (normalizedHref !== anchor.href) {
              event.preventDefault();
              window.location.href = normalizedHref;
              return;
            }
          }
        }
        if (target instanceof HTMLElement && target.closest(".sp-token, .sp-control, .sp-tooltip")) {
          return;
        }
        hideTooltip(true);
      });

      document.addEventListener("mousemove", (event) => {
        if (!tooltipHoverTarget && !tooltipOwnerId) {
          return;
        }
        if (tooltipMovedPastTolerance(event)) {
          hideTooltip(true);
        }
      });

      document.addEventListener("keydown", (event) => {
        if (!desktopControlsEnabled || event.defaultPrevented || event.metaKey || event.ctrlKey || event.altKey) {
          return;
        }

        const target = event.target;
        if (target instanceof HTMLElement) {
          const tagName = target.tagName.toLowerCase();
          if (tagName === "input" || tagName === "textarea" || tagName === "select" || target.isContentEditable) {
            return;
          }
        }

        if (!keyboardNavigationShortcutsEnabled()) {
          return;
        }

        const destination = ROUTES[event.code];
        if (!destination) {
          return;
        }

        event.preventDefault();
        markFullscreenResumeOnInternalNavigation(destination);
        window.location.href = destination;
      });

      document.addEventListener("fullscreenchange", () => {
        if (document.fullscreenElement) {
          setFullscreenPreference(true);
          setFullscreenNavigationPending(false);
          clearFullscreenResumeListeners();
        } else if (fullscreenNavigationPending()) {
          setFullscreenPreference(true);
          setFullscreenNavigationPending(true);
          clearFullscreenResumeListeners();
        } else if (fullscreenToggleIntent === "exit") {
          setFullscreenPreference(false);
          setFullscreenNavigationPending(false);
          clearFullscreenResumeListeners();
        } else if (fullscreenPreferenceEnabled()) {
          setFullscreenPreference(true);
          setFullscreenNavigationPending(true);
          clearFullscreenResumeListeners();
        }
        fullscreenToggleIntent = null;
        renderBar(currentSnapshot);
      });

      window.addEventListener("resize", () => {
        renderBar(currentSnapshot);
      });

      window.addEventListener("pageshow", () => {
        ensureFullscreenPreference();
      });

      window.addEventListener("smart-platform:settings-updated", (event) => {
        const detail = event instanceof CustomEvent ? event.detail : null;
        applyBarSettings(detail || {});
      });

      window.addEventListener("storage", (event) => {
        if (!event.key || ![
          STORAGE_KEY,
          FULLSCREEN_STORAGE_KEY,
          SETTINGS_LANGUAGE_KEY,
          SETTINGS_THEME_KEY,
          SETTINGS_DENSITY_KEY,
          SETTINGS_CACHE_KEY
        ].includes(event.key)) {
          return;
        }

        if (event.key === SETTINGS_CACHE_KEY && event.newValue) {
          try {
            applyBarSettings(JSON.parse(event.newValue));
            return;
          } catch (_error) {
            return;
          }
        }

        applyBarSettings(readCachedSettings() || {});
      });
    }
  }

  async function fetchSnapshot() {
    const response = await fetch("/api/v1/shell/snapshot", { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`Snapshot request failed: ${response.status}`);
    }
    return response.json();
  }

  async function sendViewerHeartbeat() {
    if (viewerHeartbeatInFlight) {
      return;
    }

    viewerHeartbeatInFlight = true;
    const client = detectClient(currentSnapshot);
    const params = new URLSearchParams({
      viewer_id: ensureViewerId(),
      viewer_kind: client.kind,
      title: client.title,
      value: client.value,
      page: `${window.location.pathname || "/"}${window.location.search || ""}`
    });

    try {
      const response = await fetch(`/api/v1/shell/viewer-heartbeat?${params.toString()}`, {
        method: "POST",
        cache: "no-store",
        keepalive: true
      });
      if (!response.ok) {
        return;
      }

      const payload = await response.json();
      currentSnapshot = {
        ...(currentSnapshot || {}),
        current_shell: {
          ...(currentShell(currentSnapshot)),
          ...(payload.runtime_profile ? { runtime_profile: payload.runtime_profile } : {})
        },
        viewers: Array.isArray(payload.viewers) ? payload.viewers : ((currentSnapshot || {}).viewers || [])
      };
      renderBar(currentSnapshot);
    } catch (_error) {
      // Heartbeats are optional on static mirrors; ignore transport failures.
    } finally {
      viewerHeartbeatInFlight = false;
    }
  }

  function ensureViewerHeartbeat() {
    restartViewerHeartbeatLoop();
  }

  async function ensureBatteryWatcher() {
    if (!navigator.getBattery || batterySnapshot.available) {
      return;
    }

    try {
      const battery = await navigator.getBattery();
      const update = () => {
        batterySnapshot = {
          available: true,
          level: battery.level,
          charging: battery.charging
        };
        renderBar(currentSnapshot);
      };
      battery.addEventListener("levelchange", update);
      battery.addEventListener("chargingchange", update);
      update();
    } catch (_error) {
      batterySnapshot = { available: false };
    }
  }

  async function refresh() {
    currentSnapshot = await fetchSnapshot();
    renderBar(currentSnapshot);
    sendViewerHeartbeat().catch(() => {});
  }

  async function boot() {
    injectStyles();
    ensureHost();
    ensureTooltip();
    applyBarSettings(readCachedSettings() || {});
    await loadBarSettings();
    ensureFullscreenPreference();
    renderBar(currentSnapshot);
    ensureBatteryWatcher().catch(() => {});
    ensureViewerHeartbeat();
    refresh().catch(() => {});
    ensureClockLoop();
  }

  boot().catch(() => {
    injectStyles();
    ensureHost();
    ensureTooltip();
    applyBarSettings(readCachedSettings() || {});
    ensureFullscreenPreference();
    renderBar(currentSnapshot);
    ensureBatteryWatcher().catch(() => {});
    ensureViewerHeartbeat();
    refresh().catch(() => {});
    ensureClockLoop();
  });
})();
