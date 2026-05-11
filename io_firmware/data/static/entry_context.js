(function () {
  const STYLE_ID = "smart-platform-entry-context-style";
  const PANEL_SELECTOR = "[data-sp-entry-panel]";
  const HERO_SELECTOR = ".hero";
  const INSERT_BEFORE_SELECTORS = [
    "nav",
    ".tab-row",
    ".control-strip",
    ".actions",
    ".hero-actions",
    ".device-ribbon",
    ".summary-grid",
  ];
  const SHORTCUTS = [
    { code: "KeyH", key: "H", label: "Home", path: "/" },
    { code: "KeyI", key: "I", label: "Irrigation", path: "/irrigation" },
    { code: "KeyT", key: "T", label: "Turret", path: "/turret" },
    { code: "KeyG", key: "G", label: "Gallery", path: "/gallery" },
    { code: "KeyR", key: "R", label: "Reports", path: "/gallery?tab=reports" },
    { code: "KeyL", key: "L", label: "Laboratory", path: "/service" },
    { code: "KeyS", key: "S", label: "Settings", path: "/settings" },
  ];

  function injectStyles() {
    if (document.getElementById(STYLE_ID)) {
      return;
    }

    const style = document.createElement("style");
    style.id = STYLE_ID;
    style.textContent = `
      .sp-entry-panel {
        margin-top: 16px;
        display: grid;
        gap: 10px;
      }

      .sp-entry-panel[data-sp-mounted="false"] {
        opacity: 0.72;
      }

      .sp-entry-title {
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: rgba(245, 251, 246, 0.82);
      }

      .sp-entry-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
      }

      .sp-entry-chip {
        appearance: none;
        border: 1px solid rgba(255, 255, 255, 0.16);
        background: rgba(255, 255, 255, 0.12);
        color: inherit;
        border-radius: 999px;
        padding: 9px 13px;
        display: inline-flex;
        align-items: center;
        gap: 9px;
        font: inherit;
        font-size: 13px;
        cursor: pointer;
        transition: transform 140ms ease, box-shadow 140ms ease, background 140ms ease;
      }

      .sp-entry-chip:hover,
      .sp-entry-chip:focus-visible {
        transform: translateY(-1px);
        box-shadow: 0 12px 24px rgba(19, 31, 23, 0.16);
        background: rgba(255, 255, 255, 0.18);
        outline: none;
      }

      .sp-entry-chip[data-sp-clickable="true"] {
        border-color: rgba(173, 213, 236, 0.32);
      }

      .sp-entry-icon {
        width: 18px;
        height: 18px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        flex: 0 0 auto;
      }

      .sp-entry-icon svg {
        width: 18px;
        height: 18px;
        display: block;
        stroke: currentColor;
        fill: none;
        stroke-width: 1.8;
        stroke-linecap: round;
        stroke-linejoin: round;
      }

      .sp-entry-label {
        white-space: nowrap;
        font-weight: 600;
      }

      .sp-entry-hint {
        margin: 0;
        min-height: 20px;
        color: rgba(245, 251, 246, 0.84);
        font-size: 13px;
        line-height: 1.45;
      }

      @media (max-width: 760px) {
        .sp-entry-bar {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
        }

        .sp-entry-chip {
          justify-content: flex-start;
          width: 100%;
        }
      }
    `;
    document.head.appendChild(style);
  }

  function matchMediaSafe(query) {
    if (!window.matchMedia) {
      return false;
    }
    return window.matchMedia(query).matches;
  }

  function isLoopbackHost(hostname) {
    return hostname === "127.0.0.1" || hostname === "localhost";
  }

  function shellBaseUrl(snapshot) {
    const shell = (snapshot && snapshot.current_shell) || {};
    return shell.shell_base_url || "";
  }

  function resolveLoopbackRuntime(snapshot) {
    if (isLoopbackHost(window.location.hostname)) {
      return true;
    }

    const baseUrl = shellBaseUrl(snapshot);
    if (!baseUrl) {
      return false;
    }

    try {
      return isLoopbackHost(new URL(baseUrl, window.location.href).hostname);
    } catch (_error) {
      return false;
    }
  }

  async function fetchShellSnapshot() {
    const response = await fetch("/api/v1/shell/snapshot", { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`shell snapshot unavailable: ${response.status}`);
    }
    return response.json();
  }

  function detectContext(snapshot) {
    const currentShell = (snapshot && snapshot.current_shell) || {};
    const nodes = (snapshot && snapshot.nodes) || {};
    const peerNode = nodes.peer || {};
    const userAgent = String(navigator.userAgent || "").toLowerCase();
    const maxTouchPoints = navigator.maxTouchPoints || 0;
    const width = Math.max(window.innerWidth || 0, (window.screen && window.screen.width) || 0);
    const hasCoarsePointer = matchMediaSafe("(pointer: coarse)");
    const hasFinePointer = matchMediaSafe("(pointer: fine)");
    const hasHover = matchMediaSafe("(hover: hover)");
    const touchCapable = maxTouchPoints > 0 || hasCoarsePointer;
    const mobilePhone = /iphone|ipod|android.+mobile|windows phone|mobile/.test(userAgent);
    const tabletDevice = /ipad|tablet/.test(userAgent) || (!mobilePhone && touchCapable && width <= 1366 && !hasFinePointer);
    const armLinuxBrowser = /linux arm|linux aarch64|armv7l|armv8l|raspbian/.test(userAgent);
    const hostType = String(currentShell.node_type || "unknown");
    const runtime = resolveLoopbackRuntime(snapshot)
      ? "laptop_smoke"
      : hostType === "esp32"
      ? "esp32_shell"
      : hostType === "raspberry_pi"
      ? "raspberry_pi_shell"
      : "browser_shell";

    let clientProfile = "desktop";
    if (mobilePhone) {
      clientProfile = "phone";
    } else if (hostType === "raspberry_pi" && armLinuxBrowser) {
      clientProfile = "embedded_display";
    } else if (tabletDevice) {
      clientProfile = "tablet";
    }

    const peerReachable = Boolean(peerNode.reachable);
    const topology = peerReachable
      ? "dual_board"
      : runtime === "laptop_smoke"
      ? "laptop_only"
      : "single_board";
    const keyboardMouse = hasFinePointer || hasHover;
    const inputProfile = keyboardMouse ? (touchCapable ? "touch_keyboard_mouse" : "keyboard_mouse") : "touch";
    const fullscreenSupported = Boolean(document.documentElement && document.documentElement.requestFullscreen);
    const orientationLockSupported = Boolean(
      (clientProfile === "phone" || clientProfile === "tablet") &&
        window.screen &&
        screen.orientation &&
        typeof screen.orientation.lock === "function"
    );

    return {
      runtime,
      hostType,
      clientProfile,
      topology,
      inputProfile,
      keyboardMouse,
      fullscreenSupported,
      orientationLockSupported,
      peerReachable,
      currentNodeTitle: String(((nodes.current || {}).title) || currentShell.node_type || "Current node"),
      peerNodeTitle: String(peerNode.title || "Peer node"),
    };
  }

  function iconSvg(name) {
    switch (name) {
      case "board":
        return '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="5" width="14" height="14" rx="2"></rect><rect x="9" y="9" width="6" height="6" rx="1"></rect><path d="M3 8h2M3 12h2M3 16h2M19 8h2M19 12h2M19 16h2M8 3v2M12 3v2M16 3v2M8 19v2M12 19v2M16 19v2"></path></svg>';
      case "phone":
        return '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="7" y="2.5" width="10" height="19" rx="2.5"></rect><path d="M10 6h4"></path><circle cx="12" cy="18.2" r="0.9" fill="currentColor" stroke="none"></circle></svg>';
      case "tablet":
        return '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="3.5" width="14" height="17" rx="2.5"></rect><circle cx="12" cy="17.2" r="0.9" fill="currentColor" stroke="none"></circle></svg>';
      case "desktop":
        return '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="5" width="16" height="10" rx="1.8"></rect><path d="M10 19h4M12 15v4"></path></svg>';
      case "display":
        return '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3.5" y="4.5" width="17" height="11" rx="1.8"></rect><path d="M9 19h6"></path></svg>';
      case "topology":
        return '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="7" cy="12" r="3"></circle><circle cx="17" cy="8" r="3"></circle><circle cx="17" cy="16" r="3"></circle><path d="M9.7 10.5 14.4 8.8M9.7 13.5l4.7 1.7"></path></svg>';
      case "touch":
        return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M10 21V9.2a1.8 1.8 0 0 1 3.6 0V13"></path><path d="M13.6 11.7a1.7 1.7 0 0 1 3.3.3V15"></path><path d="M16.9 12.8a1.7 1.7 0 0 1 3.1 1V18"></path><path d="M8.2 13.2 6.8 12a1.8 1.8 0 0 0-2.8 2.1l3.2 4.8A4 4 0 0 0 10.6 21H17"></path></svg>';
      case "keyboard":
        return '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3.5" y="6.5" width="17" height="10" rx="1.8"></rect><path d="M6.5 10.5h.01M9.5 10.5h.01M12.5 10.5h.01M15.5 10.5h.01M6.5 13.5h7M16.5 13.5h.01"></path></svg>';
      case "rotate":
        return '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="8" y="4" width="8" height="16" rx="2"></rect><path d="M6 8 3.5 10.5 6 13"></path><path d="M3.5 10.5h8"></path><path d="M18 16l2.5-2.5L18 11"></path><path d="M20.5 13.5h-8"></path></svg>';
      case "fullscreen":
        return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 4H4v4M16 4h4v4M8 20H4v-4M16 20h4v-4"></path></svg>';
      default:
        return iconSvg("board");
    }
  }

  function runtimeItem(context) {
    if (context.runtime === "laptop_smoke") {
      return {
        id: "runtime",
        icon: "desktop",
        label: "Laptop Smoke Runtime",
        detail: "Loopback shell detected. This browser session is being served by the local smoke runtime. It helps test UI and routing, but it does not replace physical host, viewer, or node truth.",
      };
    }

    if (context.hostType === "esp32") {
      return {
        id: "runtime",
        icon: "board",
        label: "ESP32 Runtime Host",
        detail: "This shell surface is currently served by the ESP32 runtime host. Browser viewers can still be phones, tablets, desktops, or attached displays. Irrigation and local service slices stay local here, while turret-owned routes hand off to Raspberry Pi when it is present.",
      };
    }

    if (context.hostType === "raspberry_pi") {
      return {
        id: "runtime",
        icon: "board",
        label: "Raspberry Pi Runtime Host",
        detail: "This shell surface is currently served by the Raspberry Pi runtime host. Browser viewers can still be separate participants from the host itself. Turret, display qualification, Gallery, Laboratory, and Settings stay local here, while ESP32-owned irrigation routes should hand off or explain the missing owner.",
      };
    }

    return {
      id: "runtime",
      icon: "board",
      label: "Shell Runtime Host",
      detail: "The shell surface is active, but the runtime host could not be identified precisely.",
    };
  }

  function clientItem(context) {
    if (context.clientProfile === "phone") {
      return {
        id: "client",
        icon: "phone",
        label: "Phone",
        detail: "Phone browser detected. Touch-first behavior is expected here. Use the layout chip to request fullscreen landscape when the browser allows it.",
      };
    }

    if (context.clientProfile === "tablet") {
      return {
        id: "client",
        icon: "tablet",
        label: "Tablet Touch",
        detail: "Tablet-like touch device detected. The shell should stay readable without hover-only affordances, and fullscreen remains a normal testing mode.",
      };
    }

    if (context.clientProfile === "embedded_display") {
      return {
        id: "client",
        icon: "display",
        label: "Pi Display",
        detail: "An embedded Raspberry Pi display profile is likely active. Touch, fullscreen density, and owner-side panel checks should stay visible without pretending this is a generic desktop browser.",
      };
    }

    return {
      id: "client",
      icon: "desktop",
      label: "Desktop",
      detail: "Desktop or laptop browser detected. Keyboard and mouse input are expected, and hover hints plus shortcut navigation should stay available.",
    };
  }

  function topologyItem(context) {
    if (context.topology === "dual_board") {
      return {
        id: "topology",
        icon: "topology",
        label: "Dual Board",
        detail: `${context.currentNodeTitle} can see ${context.peerNodeTitle}. Owner-aware handoff should be available instead of blocked single-node explanations.`,
      };
    }

    if (context.topology === "laptop_only") {
      return {
        id: "topology",
        icon: "topology",
        label: "Laptop Only",
        detail: "Single-node laptop review is active. This path is meant for local smoke, route discovery, and UI review without pretending the missing board is online.",
      };
    }

    return {
      id: "topology",
      icon: "topology",
      label: "Single Board",
      detail: `${context.currentNodeTitle} is currently alone. Peer-owned routes should stay visible, but they must explain the missing owner instead of failing silently.`,
    };
  }

  function inputItem(context) {
    if (context.inputProfile === "touch_keyboard_mouse") {
      return {
        id: "input",
        icon: "keyboard",
        label: "Touch + Keys",
        detail: "The browser reports both touch and keyboard or mouse input. Keyboard shortcuts are enabled: H Home, I Irrigation, T Turret, G Gallery, R Reports, L Laboratory, S Settings.",
      };
    }

    if (context.inputProfile === "keyboard_mouse") {
      return {
        id: "input",
        icon: "keyboard",
        label: "Keys + Mouse",
        detail: "Keyboard and mouse input are available. Shortcut navigation is enabled: H Home, I Irrigation, T Turret, G Gallery, R Reports, L Laboratory, S Settings.",
      };
    }

    return {
      id: "input",
      icon: "touch",
      label: "Touch",
      detail: "Touch-first input is active. Controls should stay readable without hover, and blocked states need tap-visible explanations.",
    };
  }

  function layoutItem(context) {
    if (context.clientProfile === "phone" || context.clientProfile === "tablet") {
      if (context.orientationLockSupported) {
        return {
          id: "layout",
          icon: "rotate",
          label: "Rotate",
          clickable: true,
          detail: "Tap to request fullscreen landscape. Browsers require a user gesture and may still refuse orientation lock, so this helper stays honest about that limitation.",
        };
      }

      return {
        id: "layout",
        icon: "rotate",
        label: "Landscape",
        clickable: true,
        detail: "This browser does not expose orientation lock. Tap for a reminder to rotate the device manually before dense laboratory or panel work.",
      };
    }

    if (context.fullscreenSupported) {
      return {
        id: "layout",
        icon: "fullscreen",
        label: "Fullscreen",
        clickable: true,
        detail: "Tap to toggle fullscreen. Desktop and owner-display reviews should keep context visible in both windowed and fullscreen modes.",
      };
    }

    return {
      id: "layout",
      icon: "fullscreen",
      label: "Browser",
      detail: "Fullscreen is not available from this browser context, so the page stays in normal browser mode.",
    };
  }

  function buildItems(context) {
    return [runtimeItem(context), clientItem(context), topologyItem(context), inputItem(context), layoutItem(context)];
  }

  function setHint(panel, message) {
    const hint = panel.querySelector("[data-sp-entry-hint]");
    if (hint) {
      hint.textContent = message;
    }
  }

  function removeManagedBodyClasses() {
    const prefixes = ["sp-runtime-", "sp-client-", "sp-topology-", "sp-input-"];
    const current = Array.from(document.body.classList);
    for (const className of current) {
      if (prefixes.some((prefix) => className.indexOf(prefix) === 0)) {
        document.body.classList.remove(className);
      }
    }
  }

  function updateBodyClasses(context) {
    removeManagedBodyClasses();
    document.body.classList.add(`sp-runtime-${context.runtime}`);
    document.body.classList.add(`sp-client-${context.clientProfile}`);
    document.body.classList.add(`sp-topology-${context.topology}`);
    document.body.classList.add(`sp-input-${context.inputProfile}`);
  }

  function ignoreShortcutTarget(target) {
    if (!target || !(target instanceof HTMLElement)) {
      return false;
    }

    const tagName = target.tagName.toLowerCase();
    return tagName === "input" || tagName === "textarea" || tagName === "select" || target.isContentEditable;
  }

  function installKeyboardShortcuts(context, panel) {
    if (!context.keyboardMouse || window.__smartPlatformEntryShortcutsInstalled) {
      return;
    }

    window.__smartPlatformEntryShortcutsInstalled = true;
    document.addEventListener("keydown", (event) => {
      if (event.defaultPrevented || event.metaKey || event.ctrlKey || event.altKey) {
        return;
      }
      if (ignoreShortcutTarget(event.target)) {
        return;
      }

      const shortcut = SHORTCUTS.find((item) => item.code === event.code);
      if (!shortcut) {
        return;
      }

      event.preventDefault();
      setHint(panel, `Keyboard shortcut ${shortcut.key} -> ${shortcut.label}`);
      window.location.href = shortcut.path;
    });
  }

  async function runLayoutAction(context, panel) {
    if (context.clientProfile === "phone" || context.clientProfile === "tablet") {
      if (context.fullscreenSupported && !document.fullscreenElement) {
        try {
          await document.documentElement.requestFullscreen();
        } catch (_error) {
          // Keep going. Orientation lock may still be unavailable or blocked.
        }
      }

      if (context.orientationLockSupported) {
        try {
          await screen.orientation.lock("landscape");
          setHint(panel, "Landscape request sent. If the browser accepts it, the shell should stay denser without losing owner and status context.");
          return;
        } catch (_error) {
          setHint(panel, "Landscape lock was requested, but this browser refused it. Rotate the device manually and keep the page in fullscreen when possible.");
          return;
        }
      }

      setHint(panel, "Rotate the device manually to landscape. This browser does not expose orientation lock for the current session.");
      return;
    }

    if (!context.fullscreenSupported) {
      setHint(panel, "Fullscreen is not available from this browser context.");
      return;
    }

    try {
      if (document.fullscreenElement && document.exitFullscreen) {
        await document.exitFullscreen();
        setHint(panel, "Returned to windowed mode.");
        return;
      }

      await document.documentElement.requestFullscreen();
      setHint(panel, "Fullscreen requested for denser shell or laboratory review.");
    } catch (_error) {
      setHint(panel, "Fullscreen request was rejected by the browser.");
    }
  }

  function buildPanel(hero) {
    const panel = document.createElement("div");
    panel.className = "sp-entry-panel";
    panel.dataset.spEntryPanel = "true";
    panel.dataset.spMounted = "false";
    panel.innerHTML = [
      '<div class="sp-entry-title">Entry Context</div>',
      '<div class="sp-entry-bar" data-sp-entry-bar></div>',
      '<p class="sp-entry-hint" data-sp-entry-hint>Loading runtime, device, and input profile...</p>',
    ].join("");

    const insertBefore = INSERT_BEFORE_SELECTORS
      .map((selector) => hero.querySelector(selector))
      .find((candidate) => candidate instanceof HTMLElement);

    if (insertBefore) {
      hero.insertBefore(panel, insertBefore);
    } else {
      hero.appendChild(panel);
    }

    return panel;
  }

  function renderPanel(panel, context) {
    const bar = panel.querySelector("[data-sp-entry-bar]");
    if (!bar) {
      return;
    }

    const items = buildItems(context);
    bar.innerHTML = items
      .map((item) => {
        const detail = item.detail.replace(/"/g, "&quot;");
        return `
          <button class="sp-entry-chip" type="button" data-sp-entry-id="${item.id}" data-sp-clickable="${item.clickable ? "true" : "false"}" title="${detail}" aria-label="${detail}">
            <span class="sp-entry-icon">${iconSvg(item.icon)}</span>
            <span class="sp-entry-label">${item.label}</span>
          </button>
        `;
      })
      .join("");

    const defaultItem = items[0];
    setHint(panel, defaultItem ? defaultItem.detail : "Entry context is active.");

    for (const button of bar.querySelectorAll(".sp-entry-chip")) {
      const item = items.find((entry) => entry.id === button.dataset.spEntryId);
      if (!item) {
        continue;
      }

      const showHint = () => setHint(panel, item.detail);
      button.addEventListener("mouseenter", showHint);
      button.addEventListener("focus", showHint);
      button.addEventListener("click", async () => {
        if (item.id === "layout") {
          await runLayoutAction(context, panel);
          return;
        }
        showHint();
      });
    }

    panel.dataset.spMounted = "true";
  }

  async function mount() {
    injectStyles();

    const hero = document.querySelector(HERO_SELECTOR);
    if (!hero) {
      return null;
    }

    let panel = hero.querySelector(PANEL_SELECTOR);
    if (!panel) {
      panel = buildPanel(hero);
    }

    let snapshot = null;
    try {
      snapshot = await fetchShellSnapshot();
    } catch (_error) {
      snapshot = null;
    }

    let context = detectContext(snapshot);
    panel._spSnapshot = snapshot;
    panel._spContext = context;
    updateBodyClasses(context);
    renderPanel(panel, context);
    installKeyboardShortcuts(context, panel);

    if (!panel._spRefreshTimer) {
      panel._spRefreshTimer = window.setInterval(async () => {
        try {
          panel._spSnapshot = await fetchShellSnapshot();
        } catch (_error) {
          panel._spSnapshot = panel._spSnapshot || null;
        }

        panel._spContext = detectContext(panel._spSnapshot);
        updateBodyClasses(panel._spContext);
        renderPanel(panel, panel._spContext);
      }, 9000);
    }

    if (!panel._spResizeBound) {
      panel._spResizeBound = true;
      window.addEventListener("resize", () => {
        const latestSnapshot = panel._spSnapshot || null;
        const latestContext = detectContext(latestSnapshot);
        panel._spContext = latestContext;
        updateBodyClasses(latestContext);
        renderPanel(panel, latestContext);
      }, { passive: true });

      document.addEventListener("fullscreenchange", () => {
        const latestSnapshot = panel._spSnapshot || null;
        const latestContext = detectContext(latestSnapshot);
        panel._spContext = latestContext;
        updateBodyClasses(latestContext);
        renderPanel(panel, latestContext);
      });
    }

    return context;
  }

  window.SmartPlatformEntryContext = {
    mount,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
      mount().catch(() => {});
    });
  } else {
    mount().catch(() => {});
  }
})();