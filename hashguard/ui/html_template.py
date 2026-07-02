HTML_CONTENT = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>HashGuard — Hashing Hub</title>
  <style>
    :root {
      --bg: #070b14;
      --panel: rgba(18, 25, 42, 0.82);
      --panel-2: rgba(23, 33, 54, 0.9);
      --border: rgba(255,255,255,0.08);
      --text: #ecf2fb;
      --muted: #8a96ad;
      --cyan: #1ac7ff;
      --purple: #a24cff;
      --brand-mid: #6aa7ff;
      --brand-end: #b883ff;
      --glow-cyan: rgba(26,199,255,.18);
      --glow-purple: rgba(162,76,255,.12);
      --surface-cyan: rgba(17,183,223,.18);
      --surface-purple: rgba(162,76,255,.16);
      --surface-cyan-strong: rgba(17,183,223,.24);
      --surface-purple-strong: rgba(162,76,255,.22);
      --green: #22c76e;
      --red: #ff5b57;
      --yellow: #ffb347;
      --shadow: 0 20px 60px rgba(0,0,0,.38);
      --radius: 18px;
      --app-font-stack: 'Segoe UI', Inter, system-ui, -apple-system, sans-serif;
    }

    * { box-sizing: border-box; outline: none; }
    html, body { height: 100%; margin: 0; padding: 0; }

    body {
      color: var(--text);
      font-family: var(--app-font-stack);
      background:
        radial-gradient(900px 500px at 50% 40%, rgba(84,25,166,0.12), transparent 70%),
        radial-gradient(700px 500px at 50% 20%, rgba(24,163,211,0.08), transparent 75%),
        linear-gradient(180deg, #08101b 0%, #070b14 100%);
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }

    /* GHP Styled Background Grid Overlay */
    body::before {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background-image:
        linear-gradient(rgba(32, 54, 88, 0.12) 1px, transparent 1px),
        linear-gradient(90deg, rgba(32, 54, 88, 0.12) 1px, transparent 1px);
      background-size: 80px 80px;
      mask-image: linear-gradient(to bottom, rgba(255,255,255,.85), rgba(255,255,255,.35));
    }

    /* Custom Theme Mode values */
    body[data-theme="midnight"] {
      --cyan: #4fb9ff;
      --purple: #6f8dff;
      --brand-mid: #7ea8ff;
      --brand-end: #9cb4ff;
      --glow-cyan: rgba(79,185,255,.18);
      --glow-purple: rgba(111,141,255,.12);
      --surface-cyan: rgba(79,185,255,.16);
      --surface-purple: rgba(111,141,255,.14);
      --surface-cyan-strong: rgba(79,185,255,.24);
      --surface-purple-strong: rgba(111,141,255,.22);
      background:
        radial-gradient(900px 500px at 50% 40%, rgba(44,81,165,0.16), transparent 70%),
        radial-gradient(700px 500px at 50% 20%, rgba(45,130,188,0.10), transparent 75%),
        linear-gradient(180deg, #081019 0%, #09111d 100%);
    }

    body[data-theme="rubellite"] {
      --cyan: #ff4b75;
      --purple: #b3133b;
      --brand-mid: #a30f32;
      --brand-end: #ff4b75;
      --glow-cyan: rgba(255,75,117,.30);
      --glow-purple: rgba(179,19,59,.18);
      --surface-cyan: rgba(255,75,117,.22);
      --surface-purple: rgba(179,19,59,.18);
      --surface-cyan-strong: rgba(255,75,117,.32);
      --surface-purple-strong: rgba(179,19,59,.28);
      background:
        radial-gradient(900px 500px at 50% 40%, rgba(102,0,17,0.26), transparent 70%),
        radial-gradient(700px 500px at 50% 20%, rgba(179,19,59,0.12), transparent 75%),
        linear-gradient(180deg, #110817 0%, #090712 100%);
    }

    body[data-theme="ember"] {
      --cyan: #ff8a3d;
      --purple: #ff4d6d;
      --brand-mid: #ff9a52;
      --brand-end: #ff6884;
      --glow-cyan: rgba(255,138,61,.18);
      --glow-purple: rgba(255,77,109,.12);
      --surface-cyan: rgba(255,138,61,.16);
      --surface-purple: rgba(255,77,109,.14);
      --surface-cyan-strong: rgba(255,138,61,.24);
      --surface-purple-strong: rgba(255,77,109,.22);
      background:
        radial-gradient(900px 500px at 50% 40%, rgba(150,39,53,0.15), transparent 70%),
        radial-gradient(700px 500px at 50% 20%, rgba(201,102,29,0.10), transparent 75%),
        linear-gradient(180deg, #120b0c 0%, #0c0b13 100%);
    }

    body[data-theme="emerald"] {
      --cyan: #1fd0a6;
      --purple: #3fbf7c;
      --brand-mid: #6ef8d6;
      --brand-end: #66dd9b;
      --glow-cyan: rgba(31,208,166,.18);
      --glow-purple: rgba(63,191,124,.12);
      --surface-cyan: rgba(31,208,166,.16);
      --surface-purple: rgba(63,191,124,.14);
      --surface-cyan-strong: rgba(31,208,166,.24);
      --surface-purple-strong: rgba(63,191,124,.22);
      background:
        radial-gradient(900px 500px at 50% 40%, rgba(27,123,91,0.14), transparent 70%),
        radial-gradient(700px 500px at 50% 20%, rgba(33,181,126,0.08), transparent 75%),
        linear-gradient(180deg, #07130f 0%, #07100d 100%);
    }

    body[data-theme="custom"] {
      --cyan: var(--custom-accent, #1ac7ff);
      --purple: var(--custom-accent-2, #a24cff);
      --brand-mid: var(--custom-accent, #1ac7ff);
      --brand-end: var(--custom-accent-2, #a24cff);
      --glow-cyan: color-mix(in srgb, var(--custom-accent, #1ac7ff) 22%, transparent);
      --glow-purple: color-mix(in srgb, var(--custom-accent-2, #a24cff) 16%, transparent);
      --surface-cyan: color-mix(in srgb, var(--custom-accent, #1ac7ff) 17%, transparent);
      --surface-purple: color-mix(in srgb, var(--custom-accent-2, #a24cff) 15%, transparent);
      --surface-cyan-strong: color-mix(in srgb, var(--custom-accent, #1ac7ff) 26%, transparent);
      --surface-purple-strong: color-mix(in srgb, var(--custom-accent-2, #a24cff) 22%, transparent);
      background:
        radial-gradient(900px 500px at 50% 40%, color-mix(in srgb, var(--custom-accent, #1ac7ff) 16%, transparent), transparent 70%),
        radial-gradient(700px 500px at 50% 20%, color-mix(in srgb, var(--custom-accent-2, #a24cff) 10%, transparent), transparent 75%),
        linear-gradient(180deg, #080b14 0%, #070812 100%);
    }

    /* Scrollbars */
    * {
      scrollbar-width: thin;
      scrollbar-color: rgba(106, 131, 170, .7) rgba(255,255,255,.04);
    }
    *::-webkit-scrollbar { width: 8px; height: 8px; }
    *::-webkit-scrollbar-track { background: rgba(255,255,255,.02); border-radius: 99px; }
    *::-webkit-scrollbar-thumb {
      background: linear-gradient(180deg, rgba(108,128,161,.6), rgba(80,98,128,.6));
      border-radius: 99px;
    }
    *::-webkit-scrollbar-thumb:hover {
      background: linear-gradient(180deg, rgba(108,128,161,.9), rgba(80,98,128,.9));
    }

    /* Layout Elements */
    .app {
      position: relative;
      height: 100%;
      display: flex;
      flex-direction: column;
      z-index: 2;
    }

    /* Topbar matching GHP */
    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 16px 28px 10px;
      flex: 0 0 auto;
    }

    .brand {
      display: flex;
      gap: 12px;
      align-items: center;
    }

    .brand-icon {
      font-size: 24px;
      text-shadow: 0 0 12px rgba(26,199,255,.55);
    }

    .brand-title {
      font-size: 20px;
      font-weight: 900;
      letter-spacing: .2px;
      background: linear-gradient(90deg, var(--cyan), var(--brand-mid) 55%, var(--brand-end) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }

    .brand-sub {
      font-size: 11px;
      color: var(--muted);
      margin-top: 2px;
      font-weight: bold;
    }

    .brand-sub .desktop {
      color: var(--cyan);
    }

    .tabs {
      display: inline-flex;
      gap: 8px;
      padding: 6px;
      background: rgba(255,255,255,.04);
      border: 1px solid rgba(255,255,255,.07);
      border-radius: 16px;
      backdrop-filter: blur(12px);
    }

    .tab {
      appearance: none;
      border: 0;
      background: transparent;
      color: var(--muted);
      font-weight: 800;
      font-size: 14px;
      padding: 10px 18px;
      border-radius: 12px;
      cursor: pointer;
      transition: .2s ease;
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }

    .tab.active {
      background: linear-gradient(90deg, var(--surface-cyan-strong), var(--surface-purple-strong));
      color: var(--text);
      box-shadow: inset 0 0 0 1px rgba(255,255,255,.06), 0 0 18px var(--glow-cyan);
    }

    .view-wrap {
      flex: 1 1 auto;
      min-height: 0;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    .view {
      display: none;
      flex: 1 1 auto;
      min-height: 0;
      overflow: auto;
      padding: 8px 28px 16px;
    }

    .view.active { display: block; }

    /* Cards */
    .card {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      backdrop-filter: blur(16px);
      padding: 16px 20px;
      margin-bottom: 0px; /* Managed by grid gap */
      position: relative;
    }

    .section-title {
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: .12em;
      color: var(--cyan);
      margin: 0px 2px 12px;
    }

    /* GHP Styled Side-by-Side Dashboard Grid to fit window without scrolling */
    .hashing-dashboard {
      display: grid;
      grid-template-columns: 11fr 10fr;
      gap: 16px;
      height: 100%;
      min-height: 0;
    }

    .dashboard-col {
      display: flex;
      flex-direction: column;
      gap: 16px;
      min-height: 0;
      overflow-y: auto;
    }

    /* Beautiful custom buttons */
    .btn {
      appearance: none;
      border: 1px solid var(--border);
      border-radius: 12px;
      background: rgba(255,255,255,.04);
      color: var(--text);
      font-weight: 800;
      font-size: 13px;
      padding: 10px 18px;
      cursor: pointer;
      transition: .2s ease;
      box-shadow: 0 6px 18px rgba(0,0,0,.15);
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
    }

    .btn:hover:not(:disabled) {
      transform: translateY(-1px);
      background: rgba(255,255,255,.07);
      border-color: rgba(255,255,255,.15);
    }

    .btn.primary {
      border: 0;
      color: #ffffff;
      background: linear-gradient(90deg, var(--cyan), var(--purple));
      box-shadow: 0 8px 24px var(--glow-cyan);
    }

    .btn.primary:hover:not(:disabled) {
      box-shadow: 0 8px 30px var(--glow-cyan), 0 0 16px var(--glow-purple);
    }

    .btn:disabled { opacity: .4; cursor: not-allowed; }

    /* Inputs & Entries */
    .input-shell {
      width: 100%;
      height: 40px;
      border: 1px solid rgba(255,255,255,.09);
      border-radius: 10px;
      background: rgba(0,0,0,.2);
      color: var(--text);
      padding: 0 12px;
      outline: none;
      font-size: 13px;
      font-weight: 600;
      transition: .15s ease;
    }

    .input-shell:focus {
      border-color: var(--cyan);
      box-shadow: 0 0 12px var(--glow-cyan);
    }

    .input-shell.readonly { cursor: default; }

    /* Checkboxes */
    .checkbox-row {
      display: flex;
      gap: 16px;
      flex-wrap: wrap;
    }

    .check-container {
      display: flex;
      align-items: center;
      position: relative;
      padding-left: 26px;
      cursor: pointer;
      font-size: 13px;
      font-weight: 700;
      user-select: none;
    }

    .check-container input {
      position: absolute;
      opacity: 0;
      cursor: pointer;
      height: 0;
      width: 0;
    }

    .checkmark {
      position: absolute;
      top: 0;
      left: 0;
      height: 18px;
      width: 18px;
      background-color: rgba(255,255,255,.05);
      border: 1px solid rgba(255,255,255,.1);
      border-radius: 5px;
      transition: .15s ease;
    }

    .check-container:hover input ~ .checkmark {
      background-color: rgba(255,255,255,.08);
      border-color: rgba(255,255,255,.2);
    }

    .check-container input:checked ~ .checkmark {
      background-color: var(--cyan);
      border-color: var(--cyan);
      box-shadow: 0 0 10px var(--glow-cyan);
    }

    .checkmark:after {
      content: "";
      position: absolute;
      display: none;
    }

    .check-container input:checked ~ .checkmark:after {
      display: block;
    }

    .check-container .checkmark:after {
      left: 5px;
      top: 2px;
      width: 4px;
      height: 8px;
      border: solid #000;
      border-width: 0 2px 2.5px 0;
      transform: rotate(45deg);
    }

    /* Drag & Drop Overlay style */
    .drop-box {
      border: 2.2px dashed rgba(255,255,255,.1);
      border-radius: 10px;
      padding: 16px;
      text-align: center;
      background: rgba(0,0,0,.15);
      cursor: pointer;
      transition: .2s ease;
      color: var(--muted);
      font-size: 13px;
      font-weight: 600;
    }

    .drop-box:hover, .drop-box.dragover {
      border-color: var(--cyan);
      background: var(--surface-cyan);
      color: var(--text);
      box-shadow: 0 0 16px var(--glow-cyan);
    }

    /* Hashing List row */
    .hash-row {
      display: grid;
      grid-template-columns: 82px 1fr auto;
      gap: 10px;
      align-items: center;
      margin-bottom: 10px;
    }

    .hash-row label {
      font-size: 11px;
      font-weight: 800;
      color: var(--muted);
      text-align: right;
    }

    .hash-row input {
      font-family: 'JetBrains Mono', ui-monospace, monospace;
      font-weight: 700;
      font-size: 11.5px;
      letter-spacing: .02em;
    }

    /* Verification Results Panel */
    .result-panel {
      padding: 12px 16px;
      border-radius: 10px;
      margin-top: 12px;
      font-size: 13.5px;
      font-weight: bold;
      line-height: 1.5;
      white-space: pre-wrap;
      display: none;
    }

    .result-panel.success {
      display: block;
      background: rgba(34, 199, 110, .12);
      border: 1px solid rgba(34, 199, 110, .22);
      color: var(--green);
    }

    .result-panel.error {
      display: block;
      background: rgba(255, 91, 87, .12);
      border: 1px solid rgba(255, 91, 87, .22);
      color: var(--red);
    }

    .result-panel.warning {
      display: block;
      background: rgba(255, 179, 71, .12);
      border: 1px solid rgba(255, 179, 71, .22);
      color: var(--yellow);
    }

    /* Progress bar */
    .progress-wrap {
      width: 100%;
      height: 5px;
      background: rgba(255,255,255,.05);
      border-radius: 99px;
      overflow: hidden;
      margin-top: 10px;
      display: none;
    }

    .progress-bar {
      height: 100%;
      width: 0%;
      background: linear-gradient(90deg, var(--cyan), var(--purple));
      box-shadow: 0 0 10px var(--glow-cyan);
      transition: width .1s ease;
    }

    /* Settings tabbed columns */
    .settings-grid {
      display: grid;
      grid-template-columns: 160px 1fr;
      gap: 20px;
      height: 100%;
    }

    .settings-nav-sidebar {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .settings-nav-btn {
      appearance: none;
      border: 0;
      background: transparent;
      color: var(--muted);
      font-weight: 800;
      font-size: 13.5px;
      padding: 10px 14px;
      border-radius: 10px;
      cursor: pointer;
      text-align: left;
      transition: .15s ease;
    }

    .settings-nav-btn:hover {
      background: rgba(255,255,255,.04);
      color: var(--text);
    }

    .settings-nav-btn.active {
      background: var(--panel-2);
      color: var(--cyan);
      box-shadow: inset 0 0 0 1px rgba(255,255,255,.05);
    }

    .settings-content-pane {
      overflow-y: auto;
      padding-right: 4px;
    }

    .settings-pane {
      display: none;
    }

    .settings-pane.active {
      display: block;
    }

    /* Grid of theme selection cards - MATCHING GHP */
    .theme-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
      gap: 12px;
      margin-bottom: 20px;
    }

    .theme-card {
      border: 1px solid rgba(255,255,255,.06);
      border-radius: 14px;
      padding: 10px;
      background: rgba(255,255,255,.03);
      color: var(--text);
      text-align: left;
      cursor: default;
      transition: .15s ease;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }

    .theme-card-main {
      appearance: none;
      border: 0;
      background: transparent;
      color: inherit;
      text-align: left;
      padding: 0;
      width: 100%;
      cursor: pointer;
      display: block;
      font: inherit;
    }

    .theme-card:hover {
      transform: translateY(-1px);
      border-color: rgba(255,255,255,.12);
    }

    .theme-card.active {
      border-color: var(--cyan);
      box-shadow: 0 0 18px var(--glow-cyan);
      background: linear-gradient(90deg, color-mix(in srgb, var(--surface-cyan) 65%, transparent), color-mix(in srgb, var(--surface-purple) 60%, transparent));
    }

    .theme-swatch-preview {
      height: 52px;
      border-radius: 10px;
      margin-bottom: 8px;
      border: 1px solid rgba(255,255,255,.08);
      background-clip: padding-box;
      box-shadow: inset 0 0 0 1px rgba(255,255,255,.035);
    }

    .theme-swatch-preview.glow { background: linear-gradient(135deg, #070b14, #12192a 60%, #1ac7ff); }
    .theme-swatch-preview.blue { background: linear-gradient(135deg, #081019, #121c2c 60%, #4fb9ff); }
    .theme-swatch-preview.ruby { background: linear-gradient(135deg, #110817, #1e0e24 60%, #ff4b75); }
    .theme-swatch-preview.ember { background: linear-gradient(135deg, #120b0c, #231215 60%, #ff8a3d); }
    .theme-swatch-preview.mint { background: linear-gradient(135deg, #07130f, #0f221c 60%, #1fd0a6); }
    .theme-swatch-preview.custom { background: linear-gradient(135deg, #080b14, var(--custom-accent, #1ac7ff) 60%, var(--custom-accent-2, #a24cff)); }

    .theme-card-title {
      font-size: 13px;
      font-weight: 800;
      margin-bottom: 3px;
    }

    .theme-card-sub {
      color: var(--muted);
      font-size: 11px;
      line-height: 1.4;
    }

    /* Modal overlay matching GHP scale-up animations */
    .modal-overlay {
      position: fixed;
      inset: 0;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 24px;
      background: rgba(5, 8, 15, .65);
      backdrop-filter: blur(12px);
      z-index: 999;
    }

    .modal-overlay.show {
      display: flex;
    }

    .custom-theme-modal-card {
      width: min(520px, 100%);
      background: rgba(11, 16, 28, .97);
      border: 1px solid rgba(255,255,255,.09);
      border-radius: 22px;
      box-shadow: 0 32px 90px rgba(0,0,0,.46), 0 0 24px var(--glow-cyan);
      animation: tvOpen .24s ease-out;
    }

    .custom-theme-modal-head {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 16px;
      padding: 16px 20px;
      border-bottom: 1px solid rgba(255,255,255,.06);
    }

    .custom-theme-modal-body {
      padding: 20px;
    }

    .custom-theme-modal-preview {
      width: 100%;
      height: 48px;
      border-radius: 12px;
      border: 1px solid rgba(255,255,255,.08);
      background: linear-gradient(90deg, var(--custom-accent, #1ac7ff), var(--custom-accent-2, #a24cff));
      margin-bottom: 16px;
      box-shadow: 0 0 16px var(--glow-cyan);
    }

    .modal-close {
      appearance: none;
      border: 0;
      background: rgba(255,255,255,.06);
      color: white;
      width: 32px;
      height: 32px;
      border-radius: 10px;
      font-size: 18px;
      cursor: pointer;
      display: grid;
      place-items: center;
      font-weight: bold;
      line-height: 1;
      transition: .15s ease;
    }

    .modal-close:hover {
      background: rgba(255,255,255,.12);
      transform: scale(1.05);
    }

    @keyframes tvOpen {
      0% { opacity: 0; transform: scaleX(.96) scaleY(.06); filter: brightness(1.25); }
      55% { opacity: 1; transform: scaleX(1.02) scaleY(.18); }
      100% { opacity: 1; transform: scaleX(1) scaleY(1); }
    }

    /* Custom edit button */
    .custom-edit-btn {
      position: relative;
      isolation: isolate;
      overflow: hidden;
      margin-top: 10px;
      width: 100%;
      height: 32px;
      justify-content: center;
      color: #fff;
      font-size: 11px;
      border-color: color-mix(in srgb, var(--cyan) 44%, transparent);
      background:
        radial-gradient(circle at 18% 50%, color-mix(in srgb, var(--cyan) 28%, transparent), transparent 34%),
        linear-gradient(90deg, var(--surface-cyan-strong), var(--surface-purple-strong));
      box-shadow:
        0 0 0 1px color-mix(in srgb, var(--cyan) 10%, transparent),
        0 0 20px var(--glow-cyan),
        0 0 15px var(--glow-purple),
        inset 0 0 0 1px rgba(255,255,255,.06);
    }

    .custom-edit-btn:hover {
      transform: translateY(-1px);
      border-color: color-mix(in srgb, var(--cyan) 64%, transparent);
      box-shadow:
        0 0 0 1px color-mix(in srgb, var(--cyan) 18%, transparent),
        0 0 28px var(--glow-cyan),
        0 0 20px var(--glow-purple),
        inset 0 0 0 1px rgba(255,255,255,.10);
    }

    /* Custom color inputs rows inside creator modal */
    .custom-theme-controls {
      display: grid;
      gap: 10px;
    }

    .custom-row {
      display: grid;
      grid-template-columns: 130px 1fr auto;
      gap: 12px;
      align-items: center;
    }

    .custom-row label {
      font-size: 12px;
      font-weight: 800;
      color: var(--muted);
    }

    .custom-row input[type="color"] {
      width: 50px;
      height: 36px;
      padding: 1px;
      border: 1px solid rgba(255,255,255,.12);
      border-radius: 8px;
      background: rgba(255,255,255,.06);
      cursor: pointer;
    }

    .hex-input {
      width: 110px;
      height: 36px;
      border: 1px solid rgba(255,255,255,.08);
      border-radius: 8px;
      background: rgba(0,0,0,.18);
      color: var(--text);
      padding: 0 10px;
      outline: none;
      font-weight: 800;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    }

    /* About details */
    .about-item {
      padding: 10px 14px;
      border-radius: 10px;
      background: rgba(255,255,255,.02);
      border: 1px solid rgba(255,255,255,.05);
      margin-bottom: 8px;
    }

    .about-label {
      font-size: 10px;
      font-weight: 800;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: .05em;
    }

    .about-value {
      font-size: 13.5px;
      font-weight: 700;
      margin-top: 3px;
    }

    /* Footer styling */
    .footer {
      padding: 10px 20px 14px;
      text-align: center;
      color: rgba(136, 149, 173, 0.4);
      font-size: 11.5px;
      font-weight: 600;
    }

    /* Toast */
    .toast {
      position: fixed;
      left: 50%;
      bottom: 24px;
      transform: translateX(-50%);
      padding: 12px 18px;
      border-radius: 10px;
      background: #12192a;
      border: 1px solid rgba(255,255,255,.08);
      color: var(--green);
      font-size: 13px;
      font-weight: bold;
      box-shadow: var(--shadow);
      z-index: 9999;
      opacity: 0;
      pointer-events: none;
      transition: opacity .2s ease;
    }

    .toast.show { opacity: 1; }
  </style>
</head>
<body data-theme="midnight">

  <div class="app">
    <!-- Topbar Header -->
    <header class="topbar">
      <div class="brand">
        <div class="brand-icon">🔒</div>
        <div>
          <div class="brand-title">HashGuard</div>
          <div class="brand-sub">v<span id="app-version-label">1.0.0</span> • <span class="desktop">Offline Cryptographic Hub</span></div>
        </div>
      </div>
      <div class="tabs">
        <button class="tab active" onclick="switchMainTab('hashing')">Hashing Tool</button>
        <button class="tab" onclick="switchMainTab('settings')">⚙ Settings</button>
      </div>
    </header>

    <!-- Content Sections -->
    <div class="view-wrap">
      
      <!-- HASHING TOOL VIEW (Re-architected Side-by-Side to fit window with zero scrolling) -->
      <section id="view-hashing" class="view active">
        <div class="hashing-dashboard">
          
          <!-- LEFT PANEL (Methods, Select, Generated) -->
          <div class="dashboard-col">
            <!-- Section 1: Hashing Methods -->
            <div class="card">
              <div class="section-title">Hash Methods</div>
              <div class="checkbox-row">
                <label class="check-container">MD5
                  <input type="checkbox" id="chk-md5" checked onchange="toggleAlgorithm('md5')" />
                  <span class="checkmark"></span>
                </label>
                <label class="check-container">SHA-1
                  <input type="checkbox" id="chk-sha1" onchange="toggleAlgorithm('sha1')" />
                  <span class="checkmark"></span>
                </label>
                <label class="check-container">SHA-256
                  <input type="checkbox" id="chk-sha256" checked onchange="toggleAlgorithm('sha256')" />
                  <span class="checkmark"></span>
                </label>
                <label class="check-container">SHA-512
                  <input type="checkbox" id="chk-sha512" onchange="toggleAlgorithm('sha512')" />
                  <span class="checkmark"></span>
                </label>
              </div>
            </div>

            <!-- Section 2: File Select -->
            <div class="card">
              <div class="section-title">Select or Drag & Drop File</div>
              <div style="display:flex; flex-direction:column; gap:10px;">
                <div style="display:flex; gap:10px;">
                  <input class="input-shell readonly" id="file-path-input" value="No file selected…" readonly />
                  <button class="btn primary" onclick="browseFile()">Browse…</button>
                </div>
                <!-- Drag and drop zone -->
                <div class="drop-box" id="file-drop-zone"
                     ondragover="onDragOver(event)" ondragleave="onDragLeave(event)" ondrop="onDropMainFile(event)">
                  ⬇   Drop target file here to hash
                </div>
              </div>
              <div class="progress-wrap" id="hash-progress-wrap">
                <div class="progress-bar" id="hash-progress-bar"></div>
              </div>
              <div id="hash-progress-lbl" style="font-size:12px; color:var(--muted); margin-top:6px; display:none;">Computing…</div>
            </div>

            <!-- Section 3: Generated Hashes -->
            <div class="card">
              <div class="section-title">Generated Hashes</div>
              <div id="hash-rows-container">
                <div class="hash-row" id="row-md5">
                  <label>MD5</label>
                  <input class="input-shell readonly" id="hash-val-md5" value="—" readonly />
                  <button class="btn" onclick="copyHash('md5')">Copy</button>
                </div>
                <div class="hash-row" id="row-sha1" style="display:none;">
                  <label>SHA-1</label>
                  <input class="input-shell readonly" id="hash-val-sha1" value="—" readonly />
                  <button class="btn" onclick="copyHash('sha1')">Copy</button>
                </div>
                <div class="hash-row" id="row-sha256">
                  <label>SHA-256</label>
                  <input class="input-shell readonly" id="hash-val-sha256" value="—" readonly />
                  <button class="btn" onclick="copyHash('sha256')">Copy</button>
                </div>
                <div class="hash-row" id="row-sha512" style="display:none;">
                  <label>SHA-512</label>
                  <input class="input-shell readonly" id="hash-val-sha512" value="—" readonly />
                  <button class="btn" onclick="copyHash('sha512')">Copy</button>
                </div>
              </div>
              <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-top:8px;">
                <button class="btn primary" onclick="recomputeHashes()">⟳  Recompute</button>
                <button class="btn" onclick="exportHashes()">Export Report</button>
              </div>
            </div>
          </div>

          <!-- RIGHT PANEL (Verify Card) -->
          <div class="dashboard-col">
            <!-- Section 4: Verify hashes -->
            <div class="card" style="height:100%; display:flex; flex-direction:column; justify-content:space-between;">
              <div>
                <div class="section-title">Verify Integrity</div>
                <div style="font-size:11.5px; color:var(--muted); margin-bottom:10px; line-height:1.4;">
                  Paste an expected checksum or load/drop a `.txt` hash report file (MD5: and SHA-256:). Multiple loaded hashes will be matched together.
                </div>
                
                <div style="display:flex; gap:10px; margin-bottom:10px;">
                  <input class="input-shell" id="verify-hash-input" placeholder="Paste single hash to verify…" oninput="onVerifyInput()" />
                  <button class="btn" onclick="pasteHash()">Paste</button>
                </div>
                <div id="pasted-detected-lbl" style="font-size:11px; color:var(--cyan); margin-bottom:10px; display:none; font-weight:bold;"></div>
                
                <div style="display:flex; gap:10px; margin-bottom:10px;">
                  <input class="input-shell readonly" id="hash-file-input" value="No hash text file loaded." readonly />
                  <button class="btn" onclick="browseHashFile()">Load .txt</button>
                </div>
                
                <div class="drop-box" id="hash-drop-zone" style="margin-bottom:10px;"
                     ondragover="onDragOver(event)" ondragleave="onDragLeave(event)" ondrop="onDropHashFile(event)">
                  ⬇   Drop hash .txt report file here
                </div>
                <div id="loaded-summary-lbl" style="font-size:11.5px; color:var(--cyan); margin-top:6px; display:none; font-weight:bold;"></div>
              </div>
              
              <!-- Matched Results Overlay -->
              <div class="result-panel" id="verification-results"></div>
              
              <button class="btn primary" style="width:100%; height:42px; font-size:14px;" onclick="verifyIntegrity()">✔ Run Match Verification</button>
            </div>
          </div>

        </div>
      </section>

      <!-- SETTINGS VIEW -->
      <section id="view-settings" class="view">
        <div class="card" style="height: calc(100% - 10px);">
          <div class="settings-grid">
            
            <!-- Left sidebar navigation -->
            <div class="settings-nav-sidebar">
              <button class="settings-nav-btn active" id="btn-pane-about" onclick="switchSettingsPane('about')">About</button>
              <button class="settings-nav-btn" id="btn-pane-appearance" onclick="switchSettingsPane('appearance')">Appearance</button>
              <button class="settings-nav-btn" id="btn-pane-updates" onclick="switchSettingsPane('updates')">Updates</button>
            </div>
            
            <!-- Right Content Panels -->
            <div class="settings-content-pane">
              
              <!-- About Panel -->
              <div class="settings-pane active" id="pane-about">
                <div class="section-title" style="margin-top:0;">About HashGuard</div>
                <div class="settings-sub" style="color:var(--muted); font-size:13px; line-height:1.5; margin-bottom:16px;">
                  HashGuard is a lightweight, high-performance cybersecurity asset designed to verify file integrity. Checking publishers' hashes ensures software downloads are authentic and untampered.
                </div>
                <div class="about-item">
                  <div class="about-label">Version</div>
                  <div class="about-value">v<span id="settings-version-lbl">1.0.0</span></div>
                </div>
                <div class="about-item">
                  <div class="about-label">Creator</div>
                  <div class="about-value">MarchTheDev</div>
                </div>
                <div class="about-item">
                  <div class="about-label">Release Source</div>
                  <div class="about-value">GitHub API Secured Connection</div>
                </div>
                <button class="btn primary" style="margin-top:14px;" onclick="openRepo()">GitHub Project Repository ↗</button>
              </div>

              <!-- Appearance Panel - GHP HIGH-FIDELITY PRESET CARD GRID -->
              <div class="settings-pane" id="pane-appearance">
                <div class="section-title" style="margin-top:0;">Select Theme Preset</div>
                <div class="theme-grid">
                  
                  <div class="theme-card active" id="theme-card-default">
                    <div class="theme-card-main" onclick="selectPresetTheme('Default (Midnight Glow)')">
                      <div class="theme-swatch-preview glow"></div>
                      <div class="theme-card-title">Midnight Glow</div>
                      <div class="theme-card-sub">The classic GHP neon cyan & midnight look.</div>
                    </div>
                  </div>
                  
                  <div class="theme-card" id="theme-card-blue">
                    <div class="theme-card-main" onclick="selectPresetTheme('Midnight Blue')">
                      <div class="theme-swatch-preview blue"></div>
                      <div class="theme-card-title">Midnight Blue</div>
                      <div class="theme-card-sub">Arctic slate background & cool blue highlights.</div>
                    </div>
                  </div>
                  
                  <div class="theme-card" id="theme-card-ruby">
                    <div class="theme-card-main" onclick="selectPresetTheme('Rubellite Crimson')">
                      <div class="theme-swatch-preview ruby"></div>
                      <div class="theme-card-title">Rubellite Crimson</div>
                      <div class="theme-card-sub">Deep dark burgundy & bright crimson accents.</div>
                    </div>
                  </div>
                  
                  <div class="theme-card" id="theme-card-ember">
                    <div class="theme-card-main" onclick="selectPresetTheme('Ember Orange')">
                      <div class="theme-swatch-preview ember"></div>
                      <div class="theme-card-title">Ember Orange</div>
                      <div class="theme-card-sub">Sunset warm gold & active orange glows.</div>
                    </div>
                  </div>
                  
                  <div class="theme-card" id="theme-card-mint">
                    <div class="theme-card-main" onclick="selectPresetTheme('Emerald Mint')">
                      <div class="theme-swatch-preview mint"></div>
                      <div class="theme-card-title">Emerald Mint</div>
                      <div class="theme-card-sub">Lush minty-green glows over dark rich emerald.</div>
                    </div>
                  </div>
                  
                  <div class="theme-card" id="theme-card-custom">
                    <div class="theme-card-main" onclick="selectPresetTheme('Custom Theme')">
                      <div class="theme-swatch-preview custom" id="custom-theme-swatch"></div>
                      <div class="theme-card-title">Custom Theme</div>
                      <div class="theme-card-sub">Create your own perfect visual workspace.</div>
                    </div>
                    <button class="settings-tab custom-edit-btn" onclick="openCustomThemeEditor()">🎨 Edit Colors</button>
                  </div>

                </div>
              </div>

              <!-- Updates Panel -->
              <div class="settings-pane" id="pane-updates">
                <div class="section-title" style="margin-top:0;">Updates Hub</div>
                <div class="settings-sub" style="color:var(--muted); font-size:13px; line-height:1.5; margin-bottom:16px;">
                  Check GitHub Releases for the latest verified installer and portable packages. Updates must be downloaded manually.
                </div>
                <div class="about-item">
                  <div class="about-label">Installed Version</div>
                  <div class="about-value">v<span id="updates-installed-lbl">1.0.0</span></div>
                </div>
                <div class="about-item">
                  <div class="about-label">Latest Online Release</div>
                  <div class="about-value" id="updates-latest-lbl">Unknown</div>
                </div>
                
                <div class="settings-note" id="update-status-msg" style="margin-top:14px; padding:12px 14px; background:rgba(255,255,255,.02); border:1px solid rgba(255,255,255,.05); border-radius:10px; font-size:13px; color:var(--muted); min-height:42px;">
                  Press 'Check for Updates' to query the server.
                </div>
                
                <div class="settings-actions" style="display:flex; gap:12px; margin-top:16px;">
                  <button class="btn primary" id="btn-check-updates" onclick="checkUpdates()">Check for Updates</button>
                  <button class="btn" id="btn-download-update" onclick="downloadUpdate()" disabled>Download & Install</button>
                </div>
              </div>

            </div>
          </div>
        </div>
      </section>

    </div>

    <!-- GHP style footer -->
    <footer class="footer">
      <span>HashGuard v<span id="footer-version-lbl">1.0.0</span></span> • Uses Python Hashlib • Fully Offline Utility<br />
      Cryptographic processes run locally in memory. No file data leaves your machine.
    </footer>
  </div>

  <!-- GHP CUSTOM THEME MODAL CARD OVERLAY (Real-time sliding custom editor!) -->
  <div id="custom-theme-overlay" class="modal-overlay">
    <div class="custom-theme-modal-card card" role="dialog" aria-modal="true">
      <div class="custom-theme-modal-head">
        <div>
          <h3 class="brand-title" style="font-size:20px; font-family:'JetBrains Mono'; margin:0 0 4px;">Custom Theme Editor</h3>
          <div class="theme-card-sub">Fine-tune your custom workspace accents, background panels, and text tints. All sliders preview instantly!</div>
        </div>
        <button class="modal-close" onclick="closeCustomThemeEditor()">×</button>
      </div>
      <div class="custom-theme-modal-body">
        <div class="custom-theme-modal-preview"></div>
        
        <div class="custom-theme-controls">
          <div class="custom-row">
            <label>Accent Color</label>
            <input type="color" id="picker-accent" oninput="onCustomColorPick('ACCENT', this.value)" />
            <input class="hex-input" id="hex-accent" maxlength="7" oninput="onCustomHexInput('ACCENT', this.value)" />
          </div>
          <div class="custom-row">
            <label>Root Background</label>
            <input type="color" id="picker-bg-root" oninput="onCustomColorPick('BG_ROOT', this.value)" />
            <input class="hex-input" id="hex-bg-root" maxlength="7" oninput="onCustomHexInput('BG_ROOT', this.value)" />
          </div>
          <div class="custom-row">
            <label>Card Background</label>
            <input type="color" id="picker-bg-card" oninput="onCustomColorPick('BG_CARD', this.value)" />
            <input class="hex-input" id="hex-bg-card" maxlength="7" oninput="onCustomHexInput('BG_CARD', this.value)" />
          </div>
          <div class="custom-row">
            <label>Main Text</label>
            <input type="color" id="picker-fg-main" oninput="onCustomColorPick('FG_MAIN', this.value)" />
            <input class="hex-input" id="hex-fg-main" maxlength="7" oninput="onCustomHexInput('FG_MAIN', this.value)" />
          </div>
          <div class="custom-row">
            <label>Dim Text</label>
            <input type="color" id="picker-fg-dim" oninput="onCustomColorPick('FG_DIM', this.value)" />
            <input class="hex-input" id="hex-fg-dim" maxlength="7" oninput="onCustomHexInput('FG_DIM', this.value)" />
          </div>
        </div>

        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px; margin-top:20px;">
          <button class="btn" onclick="magicGenerate()">⚡ Quick Magic Auto-Theme</button>
          <button class="btn primary" onclick="saveCustomTheme()">💾 Save Custom Theme</button>
        </div>
      </div>
    </div>
  </div>

  <div id="toast-notify" class="toast">✔ Copied!</div>

  <script>
    // Local Javascript State
    let appState = {
      theme: 'Default (Midnight Glow)',
      algorithms: ['md5', 'sha256'],
      filepath: '',
      hashes: {},
      loadedHashes: {},
      loadedHashFile: '',
      latestVersionInfo: null,
      customTheme: {
        ACCENT: '#1AC7FF',
        BG_ROOT: '#070B14',
        BG_CARD: '#12192A',
        FG_MAIN: '#ECF2FB',
        FG_DIM: '#8A96AD'
      }
    };

    const HASH_LENGTHS = {
      'md5': 32, 'sha1': 40, 'sha256': 64, 'sha512': 128
    };

    function showToast(msg) {
      const el = document.getElementById('toast-notify');
      el.textContent = msg;
      el.classList.add('show');
      setTimeout(() => el.classList.remove('show'), 2000);
    }

    function switchMainTab(tab) {
      document.querySelectorAll('.tab').forEach(btn => {
        btn.classList.toggle('active', btn.textContent.toLowerCase().includes(tab));
      });
      document.getElementById('view-hashing').classList.toggle('active', tab === 'hashing');
      document.getElementById('view-settings').classList.toggle('active', tab === 'settings');
    }

    function switchSettingsPane(pane) {
      document.querySelectorAll('.settings-nav-btn').forEach(btn => {
        btn.classList.toggle('active', btn.id.includes(pane));
      });
      document.querySelectorAll('.settings-pane').forEach(panel => {
        panel.classList.toggle('active', panel.id.includes(pane));
      });
    }

    // HTML5 Drag and drop helpers
    function onDragOver(e) {
      e.preventDefault();
      e.currentTarget.classList.add('dragover');
    }

    function onDragLeave(e) {
      e.currentTarget.classList.remove('dragover');
    }

    function onDropMainFile(e) {
      e.preventDefault();
      e.currentTarget.classList.remove('dragover');
      if (e.dataTransfer.files.length) {
        let file = e.dataTransfer.files[0];
        window.pywebview.api.load_dragged_file(file.name, file.size);
      }
    }

    function onDropHashFile(e) {
      e.preventDefault();
      e.currentTarget.classList.remove('dragover');
      if (e.dataTransfer.files.length) {
        let file = e.dataTransfer.files[0];
        if (file.name.toLowerCase().endsWith('.txt')) {
          window.pywebview.api.load_dragged_hash_file(file.name);
        } else {
          alert("Wrong file type! Please drop a .txt hash report.");
        }
      }
    }

    function openCustomThemeEditor() {
      // Toggle Option Menu to Custom Theme
      selectPresetTheme('Custom Theme');
      document.getElementById('custom-theme-overlay').classList.add('show');
    }

    function closeCustomThemeEditor() {
      document.getElementById('custom-theme-overlay').classList.remove('show');
    }

    // Backend listeners & evaluated js
    function setAppState(stateStr) {
      let data = JSON.parse(stateStr);
      appState = {...appState, ...data};
      
      // Update UI checkboxes
      document.getElementById('chk-md5').checked = appState.algorithms.includes('md5');
      document.getElementById('chk-sha1').checked = appState.algorithms.includes('sha1');
      document.getElementById('chk-sha256').checked = appState.algorithms.includes('sha256');
      document.getElementById('chk-sha512').checked = appState.algorithms.includes('sha512');
      
      // Show/Hide rows in Generated section
      document.getElementById('row-md5').style.display = appState.algorithms.includes('md5') ? 'grid' : 'none';
      document.getElementById('row-sha1').style.display = appState.algorithms.includes('sha1') ? 'grid' : 'none';
      document.getElementById('row-sha256').style.display = appState.algorithms.includes('sha256') ? 'grid' : 'none';
      document.getElementById('row-sha512').style.display = appState.algorithms.includes('sha512') ? 'grid' : 'none';
      
      // Update custom colors picker inputs
      if (appState.customTheme) {
        for (let role in appState.customTheme) {
          let val = appState.customTheme[role];
          let picker = document.getElementById('picker-' + role.toLowerCase().replace('_', '-'));
          let hexInput = document.getElementById('hex-' + role.toLowerCase().replace('_', '-'));
          if (picker) picker.value = val;
          if (hexInput) hexInput.value = val;
        }
      }

      applyThemeStyle(appState.theme);
    }

    function applyThemeStyle(themeName) {
      appState.theme = themeName;
      
      // Render GHP style background themes
      let themeAttr = 'midnight';
      if (themeName.includes('Blue')) themeAttr = 'midnight';
      else if (themeName.includes('Crimson')) themeAttr = 'rubellite';
      else if (themeName.includes('Orange')) themeAttr = 'ember';
      else if (themeName.includes('Mint')) themeAttr = 'emerald';
      else if (themeName.includes('Custom')) themeAttr = 'custom';
      
      document.body.dataset.theme = themeAttr;

      // Highlight active theme cards
      document.querySelectorAll('.theme-card').forEach(card => {
        card.classList.remove('active');
      });
      if (themeName.includes('Glow')) document.getElementById('theme-card-default').classList.add('active');
      else if (themeName.includes('Blue')) document.getElementById('theme-card-blue').classList.add('active');
      else if (themeName.includes('Crimson')) document.getElementById('theme-card-ruby').classList.add('active');
      else if (themeName.includes('Orange')) document.getElementById('theme-card-ember').classList.add('active');
      else if (themeName.includes('Mint')) document.getElementById('theme-card-mint').classList.add('active');
      else if (themeName.includes('Custom')) document.getElementById('theme-card-custom').classList.add('active');

      // Load CSS custom properties instantly for Custom Theme
      if (themeName === 'Custom Theme') {
        for (let k in appState.customTheme) {
          let val = appState.customTheme[k];
          document.body.style.setProperty('--custom-' + k.toLowerCase().replace('_', '-'), val);
        }
      }
    }

    // Python-JS Triggers
    function browseFile() {
      window.pywebview.api.select_file();
    }

    function onFileLoaded(filename, displaySize) {
      document.getElementById('file-path-input').value = filename + " (" + displaySize + ")";
      document.getElementById('file-drop-zone').textContent = "✔ Loaded: " + filename;
      document.getElementById('file-drop-zone').style.color = "var(--green)";
      
      // Reset hash row values
      document.getElementById('hash-val-md5').value = "—";
      document.getElementById('hash-val-sha1').value = "—";
      document.getElementById('hash-val-sha256').value = "—";
      document.getElementById('hash-val-sha512').value = "—";
      
      hideResults();
    }

    function updateProgress(pct) {
      document.getElementById('hash-progress-wrap').style.display = "block";
      document.getElementById('hash-progress-lbl').style.display = "block";
      document.getElementById('hash-progress-bar').style.width = (pct * 100) + "%";
      document.getElementById('hash-progress-lbl').textContent = "Computing Hashes: " + Math.round(pct * 100) + "%";
    }

    function onHashingDone(hashesStr) {
      document.getElementById('hash-progress-wrap').style.display = "none";
      document.getElementById('hash-progress-lbl').style.display = "none";
      let data = JSON.parse(hashesStr);
      appState.hashes = data;

      for (let algo in data) {
        let el = document.getElementById('hash-val-' + algo);
        if (el) el.value = data[algo];
      }

      // Check verification again if loaded or typed
      verifyIntegritySilent();
    }

    function recomputeHashes() {
      window.pywebview.api.recompute_hashes();
    }

    function copyHash(algo) {
      let val = document.getElementById('hash-val-' + algo).value;
      if (val && val !== '—' && val !== 'Computing…') {
        window.pywebview.api.copy_clipboard(val);
        showToast("✔ " + algo.toUpperCase() + " Copied!");
      }
    }

    function exportHashes() {
      window.pywebview.api.export_hashes_report();
    }

    // Verification elements
    function pasteHash() {
      window.pywebview.api.get_clipboard().then(val => {
        document.getElementById('verify-hash-input').value = val.trim();
        onVerifyInput();
      });
    }

    function onVerifyInput() {
      let text = document.getElementById('verify-hash-input').value.trim().toUpperCase();
      let detectedLabel = document.getElementById('pasted-detected-lbl');
      
      let detected = null;
      for (let algo in HASH_LENGTHS) {
        if (text.length === HASH_LENGTHS[algo] && /^[0-9A-F]+$/.test(text)) {
          detected = algo.toUpperCase();
          break;
        }
      }

      if (detected) {
        detectedLabel.style.display = "block";
        detectedLabel.textContent = "✔ Detected pasted hash type: " + detected;
        detectedLabel.style.color = "var(--cyan)";
      } else if (text) {
        detectedLabel.style.display = "block";
        detectedLabel.textContent = "⚠ Not a valid MD5, SHA-1, SHA-256 or SHA-512 hash.";
        detectedLabel.style.color = "var(--yellow)";
      } else {
        detectedLabel.style.display = "none";
      }
      hideResults();
    }

    function browseHashFile() {
      window.pywebview.api.select_hash_file();
    }

    function onHashFileLoaded(filename, summaryText, parsedHashesStr) {
      document.getElementById('hash-file-input').value = filename;
      document.getElementById('hash-drop-zone').textContent = "✔ Loaded Report: " + filename;
      document.getElementById('hash-drop-zone').style.color = "var(--green)";
      
      let lbl = document.getElementById('loaded-summary-lbl');
      lbl.style.display = "block";
      lbl.textContent = "Loaded hashes: " + summaryText;

      appState.loadedHashes = JSON.parse(parsedHashesStr);
      verifyIntegritySilent();
    }

    function verifyIntegrity() {
      let pasted = document.getElementById('verify-hash-input').value.trim().toUpperCase();
      let hasComputed = Object.keys(appState.hashes).length > 0;
      let hasLoaded = Object.keys(appState.loadedHashes).length > 0;

      if (!hasComputed) {
        alert("Please load and compute a target file's hashes first!");
        return;
      }

      if (!pasted && !hasLoaded) {
        alert("Please paste a hash or load a report text file to compare!");
        return;
      }

      runIntegrityMatching(pasted);
    }

    function verifyIntegritySilent() {
      let pasted = document.getElementById('verify-hash-input').value.trim().toUpperCase();
      if (Object.keys(appState.hashes).length > 0 && (pasted || Object.keys(appState.loadedHashes).length > 0)) {
        runIntegrityMatching(pasted);
      }
    }

    function runIntegrityMatching(pasted) {
      let panel = document.getElementById('verification-results');
      
      // Batch comparison if .txt loaded
      if (Object.keys(appState.loadedHashes).length > 0) {
        let lines = [];
        let matches = 0;
        let mismatches = 0;
        let missing = 0;

        for (let algo in appState.loadedHashes) {
          let expected = appState.loadedHashes[algo];
          let computed = appState.hashes[algo];

          if (!computed) {
            lines.push("⚠ " + algo.toUpperCase() + ": not computed (Enable in Hash Methods)");
            missing++;
          } else if (computed === expected) {
            lines.push("✔ " + algo.toUpperCase() + ": MATCH");
            matches++;
          } else {
            lines.push("✗ " + algo.toUpperCase() + ": MISMATCH (" + computed + " vs " + expected + ")");
            mismatches++;
          }
        }

        let cls = "success";
        let header = "All loaded report hashes matched successfully!";
        if (mismatches > 0) {
          cls = "error";
          header = "Hash report verification failed!";
        } else if (missing > 0) {
          cls = "warning";
          header = "Hash report partially matched with warnings:";
        }

        panel.className = "result-panel " + cls;
        panel.innerHTML = header + "<br/><br/>" + lines.join("<br/>");
        return;
      }

      // Single paste check
      let detectedAlgo = null;
      for (let algo in HASH_LENGTHS) {
        if (pasted.length === HASH_LENGTHS[algo]) {
          detectedAlgo = algo;
          break;
        }
      }

      if (!detectedAlgo) {
        panel.className = "result-panel error";
        panel.textContent = "✗ Verification failed: Paste was not a recognized hash length.";
        return;
      }

      let computed = appState.hashes[detectedAlgo];
      if (!computed) {
        panel.className = "result-panel warning";
        panel.textContent = "⚠ Verification warning: " + detectedAlgo.toUpperCase() + " was not computed. Enable it in methods and recompute.";
        return;
      }

      if (computed === pasted) {
        panel.className = "result-panel success";
        panel.textContent = "✔ " + detectedAlgo.toUpperCase() + " MATCH — The file is intact!";
      } else {
        panel.className = "result-panel error";
        panel.textContent = "✗ " + detectedAlgo.toUpperCase() + " MISMATCH — The file is corrupted or modified!";
      }
    }

    function hideResults() {
      document.getElementById('verification-results').style.display = "none";
    }

    // Settings actions
    function selectPresetTheme(themeName) {
      applyThemeStyle(themeName);
      window.pywebview.api.select_theme(themeName);
    }

    function onCustomColorPick(role, hex) {
      appState.customTheme[role] = hex.toUpperCase();
      document.getElementById('hex-' + role.toLowerCase().replace('_', '-')).value = hex.toUpperCase();
      document.body.style.setProperty('--custom-' + role.toLowerCase().replace('_', '-'), hex);
      
      // Auto-preview live!
      applyThemeStyle('Custom Theme');
    }

    function onCustomHexInput(role, hex) {
      if (reHexMatch(hex)) {
        appState.customTheme[role] = hex.toUpperCase();
        let picker = document.getElementById('picker-' + role.toLowerCase().replace('_', '-'));
        if (picker) picker.value = hex;
        document.body.style.setProperty('--custom-' + role.toLowerCase().replace('_', '-'), hex);
        applyThemeStyle('Custom Theme');
      }
    }

    function reHexMatch(hex) {
      return /^#[0-9A-Fa-f]{6}$/.test(hex);
    }

    function magicGenerate() {
      let currentAccent = appState.customTheme['ACCENT'];
      window.pywebview.api.generate_from_accent(currentAccent).then(resStr => {
        let generated = JSON.parse(resStr);
        appState.customTheme = generated;
        
        for (let role in generated) {
          let val = generated[role];
          let picker = document.getElementById('picker-' + role.toLowerCase().replace('_', '-'));
          let hexInput = document.getElementById('hex-' + role.toLowerCase().replace('_', '-'));
          if (picker) picker.value = val;
          if (hexInput) hexInput.value = val;
          document.body.style.setProperty('--custom-' + role.toLowerCase().replace('_', '-'), val);
        }
        
        applyThemeStyle('Custom Theme');
        showToast("⚡ Full Theme Generated!");
      });
    }

    function saveCustomTheme() {
      window.pywebview.api.save_custom_colors(JSON.stringify(appState.customTheme)).then(() => {
        showToast("💾 Custom Theme Saved!");
      });
    }

    function openRepo() {
      window.pywebview.api.open_github_link();
    }

    // Updates actions
    function checkUpdates() {
      let btn = document.getElementById('btn-check-updates');
      btn.disabled = true;
      btn.textContent = "Checking…";
      document.getElementById('update-status-msg').textContent = "Querying GitHub release repositories...";
      
      window.pywebview.api.check_updates_hub().then(resStr => {
        btn.disabled = false;
        btn.textContent = "Check for Updates";
        
        let info = JSON.parse(resStr);
        appState.latestVersionInfo = info;
        
        document.getElementById('updates-latest-lbl').textContent = "v" + info.latest_version;
        
        if (info.update_available) {
          document.getElementById('update-status-msg').style.color = "var(--green)";
          document.getElementById('update-status-msg').textContent = "Update found! Version v" + info.latest_version + " is available for download.\\n\\nRelease Notes:\\n" + info.release_notes;
          document.getElementById('btn-download-update').disabled = false;
        } else {
          document.getElementById('update-status-msg').style.color = "var(--green)";
          document.getElementById('update-status-msg').textContent = "You are currently running the latest release version of HashGuard!";
          document.getElementById('btn-download-update').disabled = true;
        }
      });
    }

    function downloadUpdate() {
      let btn = document.getElementById('btn-download-update');
      btn.disabled = true;
      btn.textContent = "Downloading…";
      document.getElementById('update-status-msg').textContent = "Downloading latest installer package from GitHub releases... Please do not close the app.";
      
      window.pywebview.api.download_and_launch_setup().then(ok => {
        btn.disabled = false;
        btn.textContent = "Download & Install";
        if (!ok) {
          document.getElementById('update-status-msg').style.color = "var(--red)";
          document.getElementById('update-status-msg').textContent = "Download failed! Please verify your internet connection and try again.";
        }
      });
    }

    // Bootstrap app
    window.addEventListener('pywebviewready', () => {
      // Expose current app details
      window.pywebview.api.get_init_details().then(initDetails => {
        let details = JSON.parse(initDetails);
        document.getElementById('app-version-label').textContent = details.version;
        document.getElementById('settings-version-lbl').textContent = details.version;
        document.getElementById('updates-installed-lbl').textContent = details.version;
        document.getElementById('footer-version-lbl').textContent = details.version;
        
        setAppState(initDetails);
      });
    });
  </script>
</body>
</html>
"""
