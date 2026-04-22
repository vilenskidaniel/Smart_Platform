(function () {
  const STYLE_ID = "smart-platform-compact-bar-style";
  const HOST_ID = "smart-platform-compact-bar-host";
  const TOOLTIP_ID = "smart-platform-compact-bar-tooltip";
  const STORAGE_KEY = "smart-platform.desktop-controls.enabled";
  const VIEWER_STORAGE_KEY = "smart-platform.viewer.id";
  const DEFAULT_TOOLTIP = "Status details are loading.";
  const REFRESH_MS = 5000;
  const VIEWER_HEARTBEAT_MS = 5000;
  const TOUCH_TOOLTIP_HIDE_MS = 2000;
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
  let globalListenersInstalled = false;
  let barLayoutFrame = 0;
  let viewerSessionId = "";
  let viewerHeartbeatTimer = 0;
  let viewerHeartbeatInFlight = false;
  let tooltipHideTimer = 0;

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
      .sp-bar[data-density="phone-portrait"] {
        display: grid;
        grid-template-columns: minmax(0, 1fr);
        align-items: stretch;
        justify-content: stretch;
        overflow: hidden;
        gap: 6px;
      }

      .sp-bar[data-density="narrow"] .sp-row,
      .sp-bar[data-density="phone-portrait"] .sp-row {
        min-width: 0;
      }

      .sp-bar[data-density="narrow"] .sp-row[data-row="top"] {
        display: flex;
        gap: 6px;
        align-items: center;
        min-width: 0;
      }

      .sp-bar[data-density="narrow"] .sp-row[data-row="bottom"] {
        display: flex;
        gap: 6px;
        align-items: center;
        min-width: 0;
      }

      .sp-bar[data-density="phone-portrait"] .sp-row[data-row="top"] {
        display: grid;
        grid-template-columns: auto minmax(0, 1fr) auto;
        gap: 6px;
        align-items: center;
      }

      .sp-bar[data-density="phone-portrait"] .sp-row[data-row="bottom"] {
        display: flex;
        gap: 6px;
        align-items: center;
        min-width: 0;
      }

      .sp-bar[data-density="phone-landscape"] {
        display: flex;
        align-items: center;
        gap: 6px;
        overflow: hidden;
      }

      .sp-bar[data-density="narrow"] .sp-row-cluster,
      .sp-bar[data-density="phone-portrait"] .sp-row-cluster,
      .sp-bar[data-density="phone-landscape"] .sp-row-cluster {
        min-width: 0;
        display: flex;
        align-items: center;
        gap: 4px;
      }

      .sp-bar[data-density="narrow"] .sp-row-cluster[data-cluster="controls"],
      .sp-bar[data-density="phone-portrait"] .sp-row-cluster[data-cluster="controls"],
      .sp-bar[data-density="phone-landscape"] .sp-row-cluster[data-cluster="controls"] {
        flex: 0 0 auto;
        justify-content: flex-start;
      }

      .sp-bar[data-density="narrow"] .sp-row-cluster[data-cluster="devices"],
      .sp-bar[data-density="narrow"] .sp-row-cluster[data-cluster="irrigation"],
      .sp-bar[data-density="phone-portrait"] .sp-row-cluster[data-cluster="devices"],
      .sp-bar[data-density="phone-portrait"] .sp-row-cluster[data-cluster="summary"],
      .sp-bar[data-density="phone-landscape"] .sp-row-cluster[data-cluster="center"] {
        overflow-x: auto;
        scrollbar-width: none;
      }

      .sp-bar[data-density="narrow"] .sp-row-cluster[data-cluster="devices"]::-webkit-scrollbar,
      .sp-bar[data-density="narrow"] .sp-row-cluster[data-cluster="irrigation"]::-webkit-scrollbar,
      .sp-bar[data-density="phone-portrait"] .sp-row-cluster[data-cluster="devices"]::-webkit-scrollbar,
      .sp-bar[data-density="phone-portrait"] .sp-row-cluster[data-cluster="summary"]::-webkit-scrollbar,
      .sp-bar[data-density="phone-landscape"] .sp-row-cluster[data-cluster="center"]::-webkit-scrollbar {
        display: none;
      }

      .sp-bar[data-density="narrow"] .sp-row-cluster[data-cluster="devices"] {
        flex: 1 1 auto;
      }

      .sp-bar[data-density="narrow"] .sp-row-cluster[data-cluster="sensors"] {
        flex: 0 0 auto;
      }

      .sp-bar[data-density="narrow"] .sp-row-cluster[data-cluster="system"],
      .sp-bar[data-density="phone-portrait"] .sp-row-cluster[data-cluster="system"],
      .sp-bar[data-density="phone-landscape"] .sp-row-cluster[data-cluster="system"] {
        flex: 0 0 auto;
        margin-left: auto;
        justify-content: flex-end;
      }

      .sp-bar[data-density="phone-landscape"] .sp-row-cluster[data-cluster="center"] {
        flex: 1 1 auto;
      }

      .sp-bar[data-density="narrow"] .sp-token,
      .sp-bar[data-density="narrow"] .sp-control,
      .sp-bar[data-density="phone-portrait"] .sp-token,
      .sp-bar[data-density="phone-portrait"] .sp-control,
      .sp-bar[data-density="phone-landscape"] .sp-token,
      .sp-bar[data-density="phone-landscape"] .sp-control {
        min-height: 28px;
        padding-inline: 6px;
        gap: 4px;
      }

      .sp-bar[data-density="narrow"] .sp-control,
      .sp-bar[data-density="phone-portrait"] .sp-control,
      .sp-bar[data-density="phone-landscape"] .sp-control {
        width: 28px;
        padding-inline: 0;
      }

      .sp-bar[data-density="narrow"] .sp-icon,
      .sp-bar[data-density="narrow"] .sp-icon svg,
      .sp-bar[data-density="phone-portrait"] .sp-icon,
      .sp-bar[data-density="phone-portrait"] .sp-icon svg,
      .sp-bar[data-density="phone-landscape"] .sp-icon,
      .sp-bar[data-density="phone-landscape"] .sp-icon svg {
        width: 14px;
        height: 14px;
      }

      .sp-bar[data-density="narrow"] .sp-value,
      .sp-bar[data-density="phone-portrait"] .sp-value,
      .sp-bar[data-density="phone-landscape"] .sp-value {
        font-size: 11px;
      }

      .sp-bar[data-density="narrow"] .sp-row[data-row="bottom"] .sp-token,
      .sp-bar[data-density="phone-portrait"] .sp-row[data-row="bottom"] .sp-token,
      .sp-bar[data-density="phone-landscape"] .sp-row-cluster[data-cluster="center"] .sp-token {
        min-width: 0;
        justify-content: center;
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
        max-width: min(360px, calc(100vw - 20px));
        padding: 12px 13px;
        border-radius: 16px;
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
        margin: 0 0 8px;
        color: rgba(231, 241, 233, 0.76);
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
    return host;
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
          state: "attention",
          blink: true,
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

  function zonePreviewRows() {
    return Array.from({ length: 5 }, (_, index) => ({
      id: `zone-${index + 1}`,
      title: `Zone ${index + 1}`,
      mode: "Manual",
      targetSoil: "60%",
      targetTemp: "24C",
      targetLight: "60%",
      targetPh: "5.8",
      liveSoil: "--%",
      liveTemp: "--°",
      liveLight: "--",
      livePh: "--"
    }));
  }

  function environmentPreviewRows() {
    const hour = new Date().getHours();
    const night = hour >= 20 || hour < 6;
    return [
      {
        id: "sensor-air",
        icon: "humidity",
        value: "--",
        title: "Air Humidity",
        state: "neutral",
        detail: "Live ambient humidity is not published to the shell snapshot yet.",
        tooltip: {
          title: "Air Humidity",
          subtitle: "Environment preview",
          description: "Humidity still uses a preview target until the real ambient feed is published.",
          sections: [
            {
              title: "Readout",
              rows: [
                { label: "Live", value: "--" },
                { label: "Preview target", value: "60%" }
              ]
            }
          ]
        }
      },
      {
        id: "sensor-temp",
        icon: "temperature",
        iconOptions: { fill: 0 },
        value: "--°",
        title: "Temperature",
        state: "neutral",
        detail: "Live ambient temperature is not published to the shell snapshot yet.",
        tooltip: {
          title: "Temperature",
          subtitle: "Environment preview",
          description: "The thermometer stays neutral until a truthful temperature feed is linked.",
          sections: [
            {
              title: "Readout",
              rows: [
                { label: "Live", value: "--°" },
                { label: "Comfort target", value: "24C" }
              ]
            }
          ]
        }
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
          : "Day-phase icon is derived from the current local time until a truthful light sensor value is published.",
        tooltip: {
          title: "Light / Day Cycle",
          subtitle: "Environment preview",
          description: "The icon already switches between day and night, but the bar is still waiting for a real light reading.",
          sections: [
            {
              title: "Readout",
              rows: [
                { label: "Live", value: "--" },
                { label: "Derived phase", value: night ? "Night" : "Day" }
              ]
            }
          ]
        }
      }
    ];
  }

  function systemState(snapshot) {
    const smokeRuntime = isSmokeRuntime(snapshot);
    const current = ((snapshot || {}).nodes || {}).current || {};
    const diagnostics = (((snapshot || {}).summaries || {}).diagnostics || {});
    const syncState = String(diagnostics.sync_state || "unknown");
    const locale = navigator.language || "en";
    const now = new Date();
    return {
      smokeRuntime,
      current,
      diagnostics,
      syncState,
      locale,
      now,
      wifiReady: !smokeRuntime && Boolean(current.wifi_ready),
      syncReady: !smokeRuntime && syncState === "ready",
      syncPending: !smokeRuntime && syncState === "pending"
    };
  }

  function wirelessToken(state, showValue) {
    return {
      id: "system-wifi",
      icon: "wifi",
      iconOptions: { variant: state.wifiReady ? "online" : "offline" },
      value: showValue ? (state.smokeRuntime ? "PRE" : state.wifiReady ? "ON" : "OFF") : "",
      title: "Wi-Fi",
      state: state.smokeRuntime ? "neutral" : state.wifiReady ? "online" : "attention",
      detail: state.smokeRuntime
        ? "Smoke runtime keeps wireless status in preview mode."
        : state.wifiReady
        ? "The active owner reports network readiness."
        : "The active owner is not currently reporting Wi-Fi readiness.",
      tooltip: {
        title: "Wireless Link",
        subtitle: state.smokeRuntime ? "Smoke preview" : "Owner-reported connectivity",
        description: state.smokeRuntime
          ? "Desktop smoke does not prove board-level radio readiness."
          : "This compact view keeps the connection story short and prioritised.",
        sections: [
          {
            title: "Connectivity",
            rows: [
              { label: "Wi-Fi", value: state.smokeRuntime ? "Preview only" : state.wifiReady ? "Ready" : "Waiting" },
              { label: "Sync", value: state.smokeRuntime ? "Preview" : state.syncReady ? `Ready (${state.syncState})` : state.syncPending ? `Pending (${state.syncState})` : state.syncState }
            ]
          }
        ]
      }
    };
  }

  function syncToken(state) {
    return {
      id: "system-sync",
      icon: "sync",
      iconOptions: { variant: state.smokeRuntime ? "pending" : state.syncReady ? "online" : state.syncPending ? "pending" : "offline" },
      value: "",
      title: "Sync",
      state: state.smokeRuntime ? "neutral" : state.syncReady ? "online" : "attention",
      detail: state.smokeRuntime
        ? "Smoke runtime keeps sync in preview mode."
        : state.syncReady
        ? `Sync stack is ready. Current state: ${state.syncState}.`
        : state.syncPending
        ? "Peer link is visible, but sync is still pending."
        : `Sync is not ready. Current state: ${state.syncState}.`,
      tooltip: {
        title: "Sync",
        subtitle: state.smokeRuntime ? "Smoke preview" : "Peer status",
        description: state.smokeRuntime
          ? "Real peer readiness must come from hardware-linked owners."
          : "This token is narrowed to the peer-handshake state that matters for the current shell.",
        sections: [
          {
            title: "Readout",
            rows: [
              { label: "State", value: state.smokeRuntime ? "Preview" : state.syncState },
              { label: "Peer readiness", value: state.syncReady ? "Ready" : state.syncPending ? "Pending" : "Waiting" }
            ]
          }
        ]
      }
    };
  }

  function volumeToken(showValue) {
    return {
      id: "system-volume",
      icon: "volume",
      iconOptions: { level: null },
      value: showValue ? "--" : "",
      title: "Volume",
      state: "neutral",
      detail: "System volume is not exposed as a truthful browser-side signal yet.",
      tooltip: {
        title: "Volume",
        subtitle: "Client-side only",
        description: "The browser does not publish a reliable system volume level yet, so this control stays neutral instead of inventing one.",
        sections: [
          {
            title: "Readout",
            rows: [
              { label: "Level", value: "--" },
              { label: "Source", value: "Client browser" }
            ]
          }
        ]
      }
    };
  }

  function localeToken(state) {
    return {
      id: "system-language",
      icon: "language",
      value: String(state.locale).slice(0, 2).toUpperCase(),
      title: "Language",
      state: "neutral",
      detail: `Current browser locale: ${state.locale}. Language switching belongs in Settings.`,
      tooltip: {
        title: "Language",
        subtitle: "Client locale",
        sections: [
          {
            title: "Readout",
            rows: [
              { label: "Locale", value: state.locale },
              { label: "Switching", value: "Settings" }
            ]
          }
        ]
      }
    };
  }

  function timeToken(state) {
    const timeValue = state.now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    const dateValue = state.now.toLocaleDateString([], { month: "short", day: "2-digit" });
    return {
      id: "system-time",
      icon: "time",
      value: timeValue,
      title: "Time",
      state: "neutral",
      detail: "Client local time.",
      tooltip: {
        title: "Local Clock",
        subtitle: "Client-side system time",
        sections: [
          {
            title: "Readout",
            rows: [
              { label: "Time", value: timeValue },
              { label: "Date", value: dateValue },
              { label: "Locale", value: state.locale }
            ]
          }
        ]
      }
    };
  }

  function dateToken(state) {
    return {
      id: "system-date",
      icon: "date",
      value: state.now.toLocaleDateString([], { month: "short", day: "2-digit" }),
      title: "Date",
      state: "neutral",
      detail: "Client local date."
    };
  }

  function compactSystemTokens(snapshot) {
    const state = systemState(snapshot);
    return [wirelessToken(state, false), volumeToken(false), batteryToken(), timeToken(state)];
  }

  function phoneSystemTokens(snapshot) {
    const state = systemState(snapshot);
    return [wirelessToken(state, false), volumeToken(false), batteryToken(), timeToken(state)];
  }

  function zoneTokens() {
    return zonePreviewRows().map((zone) => ({
      id: zone.id,
      icon: "water",
      value: zone.liveSoil,
      title: zone.title,
      state: "neutral",
      detail: `${zone.title}. Live irrigation telemetry is not linked to the shell snapshot yet.`,
      tooltip: {
        title: zone.title,
        subtitle: "Compact irrigation preview",
        description: "Live telemetry is still pending, so the tooltip keeps the plant-profile targets visible instead of showing an empty shell.",
        sections: [
          {
            title: "Profile",
            rows: [
              { label: "Mode", value: zone.mode },
              { label: "Target soil", value: zone.targetSoil },
              { label: "Target temp", value: zone.targetTemp },
              { label: "Target light", value: zone.targetLight },
              { label: "Target pH", value: zone.targetPh }
            ]
          },
          {
            title: "Live feed",
            rows: [
              { label: "Soil", value: zone.liveSoil },
              { label: "Temp", value: zone.liveTemp },
              { label: "Light", value: zone.liveLight },
              { label: "pH", value: zone.livePh }
            ]
          }
        ]
      }
    }));
  }

  function sensorTokens(snapshot) {
    return environmentPreviewRows(snapshot);
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
        detail: "Battery state is not available in this browser session.",
        tooltip: {
          title: "Battery",
          subtitle: "Client-side power state",
          sections: [
            {
              title: "Readout",
              rows: [
                { label: "Level", value: "--" },
                { label: "Status", value: "Unavailable" }
              ]
            }
          ]
        }
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
        : `Client battery level: ${percent}%.`,
      tooltip: {
        title: "Battery",
        subtitle: batterySnapshot.charging ? "Charging" : "Client-side power state",
        sections: [
          {
            title: "Readout",
            rows: [
              { label: "Level", value: `${percent}%` },
              { label: "Status", value: batterySnapshot.charging ? "Charging" : saver ? "Low power" : "Stable" }
            ]
          }
        ]
      }
    };
  }

  function systemTokens(snapshot) {
    const state = systemState(snapshot);
    return [wirelessToken(state, false), syncToken(state), volumeToken(true), batteryToken(), localeToken(state), timeToken(state), dateToken(state)];
  }

  function controlMarkup(item) {
    const detail = esc(item.detail || DEFAULT_TOOLTIP);
    const payload = tooltipPayloadAttr(item);
    if (item.href) {
      return `
        <a class="sp-control" href="${esc(item.href)}" data-tooltip-title="${esc(item.title)}" data-tooltip-detail="${detail}" data-tooltip-payload="${payload}" title="${esc(item.title)}. ${detail}">
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
        data-tooltip-payload="${payload}"
        data-active="${item.active ? "true" : "false"}"
        data-blink="${item.blink ? "true" : "false"}"
        title="${esc(item.title)}. ${detail}">
        <span class="sp-icon">${icon(item.icon, item.iconOptions)}</span>
      </button>
    `;
  }

  function tokenMarkup(item) {
    const detail = esc(item.detail || DEFAULT_TOOLTIP);
    const payload = tooltipPayloadAttr(item);
    return `
      <button
        type="button"
        class="sp-token"
        data-token-id="${esc(item.id || "")}"
        data-tooltip-title="${esc(item.title || "")}"
        data-tooltip-detail="${detail}"
        data-tooltip-payload="${payload}"
        data-state="${esc(item.state || "neutral")}"
        data-blink="${item.blink ? "true" : "false"}"
        title="${esc(item.title || "")}. ${detail}">
        <span class="sp-icon">${icon(item.icon || "raspberry_pi", item.iconOptions)}</span>
        <span class="sp-value">${esc(item.value || "")}</span>
      </button>
    `;
  }

  function groupMarkup(groupName, items, renderer) {
    return `<div class="sp-group" data-group="${esc(groupName)}">${items.map(renderer).join("")}</div>`;
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

  function irrigationSummaryToken(snapshot) {
    const rows = zonePreviewRows();
    return {
      id: "summary-irrigation",
      icon: "water",
      value: `${rows.length}Z`,
      title: "Irrigation",
      state: "neutral",
      detail: "Compact irrigation zone matrix.",
      tooltip: {
        title: "Irrigation Overview",
        subtitle: "Compact zone matrix",
        description: "Profile targets stay visible even before live irrigation telemetry is linked into the shell snapshot.",
        sections: [
          {
            title: "Zones",
            rows: rows.map((zone) => ({
              label: zone.title,
              value: `${zone.targetSoil} soil • ${zone.targetTemp} temp • ${zone.targetLight} light • pH ${zone.targetPh}`
            }))
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
      title: "Environment",
      state: summarizeState(items),
      detail: "Compact environment matrix.",
      tooltip: {
        title: "Environment Overview",
        subtitle: "Compact sensor matrix",
        description: "The bar keeps one compact sensor summary here and moves the detailed values into a small table.",
        sections: [
          {
            title: "Sensors",
            rows: items.map((item) => ({
              label: item.title,
              value: item.value || "--"
            }))
          }
        ]
      }
    };
  }

  function systemSummaryToken(snapshot) {
    const state = systemState(snapshot);
    return {
      id: "summary-system",
      icon: "sync",
      value: "SYS",
      title: "System Summary",
      state: state.smokeRuntime ? "neutral" : state.wifiReady ? "online" : "attention",
      detail: "Prioritized system overview.",
      tooltip: {
        title: "System Overview",
        subtitle: "Prioritized compact status",
        sections: [
          {
            title: "Connectivity",
            rows: [
              { label: "Wi-Fi", value: state.smokeRuntime ? "Preview" : state.wifiReady ? "Ready" : "Waiting" },
              { label: "Sync", value: state.smokeRuntime ? "Preview" : state.syncState }
            ]
          },
          {
            title: "Client",
            rows: [
              { label: "Battery", value: batterySnapshot.available ? `${Math.round((batterySnapshot.level || 0) * 100)}%` : "--" },
              { label: "Locale", value: state.locale },
              { label: "Time", value: state.now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) }
            ]
          }
        ]
      }
    };
  }

  function controlTokens(snapshot, density) {
    const localViewer = detectClient(snapshot);
    const controls = [
      { id: "home", href: "/", icon: "home", title: "Smart Platform Home", detail: "Return to the Smart Platform launcher." },
      { id: "input", icon: "keyboard", title: "Input Helpers", detail: desktopControlsEnabled ? "Desktop keyboard shortcuts and hover helpers are enabled." : "Desktop keyboard shortcuts and hover helpers are disabled.", active: desktopControlsEnabled },
      { id: "fullscreen", icon: "fullscreen", title: "Fullscreen", detail: document.fullscreenElement ? "Leave fullscreen mode." : "Enter fullscreen mode." }
    ];

    if ((density === "phone-portrait" || density === "phone-landscape") && localViewer.kind !== "desktop") {
      return controls.filter((item) => item.id !== "input");
    }

    return controls;
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

  function clusterMarkup(clusterName, items, renderer) {
    return `<div class="sp-row-cluster" data-cluster="${esc(clusterName)}">${items.map(renderer).join("")}</div>`;
  }

  function narrowDesktopBarMarkup(snapshot, view, controls, deviceTokens) {
    const sensorItems = view.width < 1160 ? [sensorSummaryToken(snapshot)] : sensorTokens(snapshot);
    const irrigationItems = view.width < 1080 ? [irrigationSummaryToken(snapshot)] : zoneTokens(snapshot);
    const systemItems = compactSystemTokens(snapshot);

    return [
      `<div class="sp-row" data-row="top">${clusterMarkup("controls", controls, controlMarkup)}${clusterMarkup("devices", deviceTokens, tokenMarkup)}${clusterMarkup("sensors", sensorItems, tokenMarkup)}${clusterMarkup("system", systemItems, tokenMarkup)}</div>`,
      `<div class="sp-row" data-row="bottom">${clusterMarkup("irrigation", irrigationItems, tokenMarkup)}</div>`
    ].join("");
  }

  function phonePortraitBarMarkup(snapshot, controls, deviceTokens) {
    const systemItems = phoneSystemTokens(snapshot);
    const summaryItems = [irrigationSummaryToken(snapshot), sensorSummaryToken(snapshot)];

    return [
      `<div class="sp-row" data-row="top">${clusterMarkup("controls", controls, controlMarkup)}${clusterMarkup("devices", deviceTokens, tokenMarkup)}${clusterMarkup("system", systemItems, tokenMarkup)}</div>`,
      `<div class="sp-row" data-row="bottom">${clusterMarkup("summary", summaryItems, tokenMarkup)}</div>`
    ].join("");
  }

  function phoneLandscapeBarMarkup(snapshot, controls, deviceTokens) {
    const systemItems = phoneSystemTokens(snapshot);
    const middleItems = [...deviceTokens, irrigationSummaryToken(snapshot), sensorSummaryToken(snapshot)];
    return `${clusterMarkup("controls", controls, controlMarkup)}${clusterMarkup("middle", middleItems, tokenMarkup)}${clusterMarkup("system", systemItems, tokenMarkup)}`;
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

  function chooseBarDensity(view) {
    if (view.coarse) {
      return view.landscape ? "phone-landscape" : "phone-portrait";
    }

    if (view.width >= 1680) {
      return "full";
    }

    if (view.width >= 1320) {
      return "compact";
    }

    return "narrow";
  }

  function applyBarLayout(bar, density) {
    if (barLayoutFrame) {
      cancelAnimationFrame(barLayoutFrame);
    }

    barLayoutFrame = requestAnimationFrame(() => {
      barLayoutFrame = 0;
      bar.dataset.density = density;
      bar.dataset.fit = density === "full" || density === "compact" ? "true" : "false";
    });
  }

  function renderBar(snapshot) {
    const view = viewportInfo();
    const density = chooseBarDensity(view);
    const controls = controlTokens(snapshot, density);
    const deviceTokens = [...viewerTokens(snapshot), ...boardTokens(snapshot), ...modeTokens(snapshot)];

    const bar = document.getElementById("sp-compact-bar");
    if (!bar) {
      return;
    }

    if (density === "phone-landscape") {
      bar.innerHTML = phoneLandscapeBarMarkup(snapshot, controls, deviceTokens);
    } else if (density === "phone-portrait") {
      bar.innerHTML = phonePortraitBarMarkup(snapshot, controls, deviceTokens);
    } else if (density === "narrow") {
      bar.innerHTML = narrowDesktopBarMarkup(snapshot, view, controls, deviceTokens);
    } else {
      bar.innerHTML = [
        groupMarkup("controls", controls, controlMarkup),
        groupMarkup("devices", deviceTokens, tokenMarkup),
        groupMarkup("irrigation", zoneTokens(snapshot), tokenMarkup),
        groupMarkup("sensors", sensorTokens(snapshot), tokenMarkup),
        groupMarkup("system", systemTokens(snapshot), tokenMarkup)
      ].join("");
    }

    applyBarLayout(bar, density);
    bindInteractions();
  }

  function clearTooltipHideTimer() {
    if (!tooltipHideTimer) {
      return;
    }
    window.clearTimeout(tooltipHideTimer);
    tooltipHideTimer = 0;
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
    if (!isCoarsePointer()) {
      return;
    }

    const ownerId = tooltipOwnerId;
    tooltipHideTimer = window.setTimeout(() => {
      if (tooltipOwnerId === ownerId) {
        hideTooltip(true);
      }
    }, TOUCH_TOOLTIP_HIDE_MS);
  }

  function showTooltip(target, pinned) {
    const tooltip = ensureTooltip();
    const payload = readTooltipPayload(target);
    const rect = target.getBoundingClientRect();

    tooltip.innerHTML = renderTooltipMarkup(payload);
    tooltip.setAttribute("data-visible", "true");
    tooltipOwnerId = target.getAttribute("data-token-id") || target.getAttribute("data-control-id") || "";
    tooltipPinned = Boolean(pinned);
    scheduleTooltipAutoHide();

    requestAnimationFrame(() => {
      const tipRect = tooltip.getBoundingClientRect();
      const left = Math.min(Math.max(12, rect.left + (rect.width / 2) - (tipRect.width / 2)), window.innerWidth - tipRect.width - 12);
      const showAbove = rect.bottom + tipRect.height + 16 > window.innerHeight;
      const top = showAbove ? rect.top - tipRect.height - 8 : rect.bottom + 8;
      tooltip.style.left = `${left}px`;
      tooltip.style.top = `${Math.max(12, top)}px`;
    });
  }

  function hideTooltip(force) {
    if (tooltipPinned && !force) {
      return;
    }
    clearTooltipHideTimer();
    const tooltip = ensureTooltip();
    tooltip.setAttribute("data-visible", "false");
    tooltipOwnerId = "";
    if (force) {
      tooltipPinned = false;
    }
  }

  function bindInteractions() {
    const tokens = document.querySelectorAll(".sp-token, .sp-control");
    for (const token of tokens) {
      token.onmouseenter = () => showTooltip(token, tooltipPinned && tooltipOwnerId === (token.getAttribute("data-token-id") || token.getAttribute("data-control-id") || ""));
      token.onfocus = () => showTooltip(token, tooltipPinned && tooltipOwnerId === (token.getAttribute("data-token-id") || token.getAttribute("data-control-id") || ""));
      token.onmouseleave = () => hideTooltip(false);
      token.onblur = () => hideTooltip(false);
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
        showTooltip(token, true);
      };
    }

    const inputToggle = document.querySelector('.sp-control[data-control-id="input"]');
    const fullscreenToggle = document.querySelector('.sp-control[data-control-id="fullscreen"]');

    if (inputToggle) {
      inputToggle.onclick = (event) => {
        event.preventDefault();
        desktopControlsEnabled = !desktopControlsEnabled;
        writeStorage(STORAGE_KEY, desktopControlsEnabled ? "1" : "0");
        renderBar(currentSnapshot);
        const nextToggle = document.querySelector('.sp-control[data-control-id="input"]');
        if (nextToggle) {
          showTooltip(nextToggle, true);
        }
      };
    }

    if (fullscreenToggle) {
      fullscreenToggle.onclick = async (event) => {
        event.preventDefault();
        try {
          if (document.fullscreenElement && document.exitFullscreen) {
            await document.exitFullscreen();
          } else if (document.documentElement.requestFullscreen) {
            await document.documentElement.requestFullscreen();
          }
        } catch (_error) {
          // Ignore browser fullscreen rejections; the tooltip already explains the action.
        }
        renderBar(currentSnapshot);
        const nextToggle = document.querySelector('.sp-control[data-control-id="fullscreen"]');
        if (nextToggle) {
          showTooltip(nextToggle, true);
        }
      };
    }

    if (!globalListenersInstalled) {
      globalListenersInstalled = true;

      document.addEventListener("click", (event) => {
        const target = event.target;
        if (target instanceof HTMLElement && target.closest(".sp-token, .sp-control, .sp-tooltip")) {
          return;
        }
        hideTooltip(true);
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

        const destination = ROUTES[event.code];
        if (!destination) {
          return;
        }

        event.preventDefault();
        window.location.href = destination;
      });

      document.addEventListener("fullscreenchange", () => {
        renderBar(currentSnapshot);
      });

      window.addEventListener("resize", () => {
        renderBar(currentSnapshot);
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
    if (viewerHeartbeatTimer) {
      return;
    }

    sendViewerHeartbeat().catch(() => {});
    viewerHeartbeatTimer = window.setInterval(() => {
      sendViewerHeartbeat().catch(() => {});
    }, VIEWER_HEARTBEAT_MS);
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

  injectStyles();
  ensureHost();
  ensureTooltip();
  renderBar(currentSnapshot);
  ensureBatteryWatcher().catch(() => {});
  ensureViewerHeartbeat();
  refresh().catch(() => {});
  setInterval(() => {
    refresh().catch(() => {});
  }, REFRESH_MS);
  setInterval(() => {
    renderBar(currentSnapshot);
  }, CLOCK_MS);
})();