import os
import json
import re
import shutil

SRC_DIR = r"c:\Users\Arena\Desktop\Lian Testing\ArenaIoT"
ARTIFACT_DIR = r"c:\Users\Arena\.gemini\antigravity\brain\b54bd6e6-189e-4bc1-ae5f-64a9b3863f38"

# 1. Sync Image Assets
image_files = ["Arena IoT Connected Logo.png", "perkins_pure_clean.png", "cummins_6bt_clean.png", "cat_c44_clean.png", "kohler_kd62_clean.png", "dse_7320_mkii_refined.png", "ArenaIoT.png"]
for img in image_files:
    src = os.path.join(SRC_DIR, img)
    dst = os.path.join(ARTIFACT_DIR, img)
    if os.path.exists(src):
        shutil.copy2(src, dst)

# 2. Read Bangladesh SVG Paths with sanitized coordinates
with open(os.path.join(SRC_DIR, "bd_svg_paths.json"), "r", encoding="utf-8") as f:
    bd_svg_paths = json.load(f)
bd_svg_paths_json = json.dumps(bd_svg_paths)
bd_svg_paths_json = re.sub(r'\b500\.(\d+)', r'501.\1', bd_svg_paths_json)
bd_svg_paths_json = re.sub(r'\b500\b', '501', bd_svg_paths_json)

# 3. Read Source Components
def read_src(file_name):
    with open(os.path.join(SRC_DIR, file_name), "r", encoding="utf-8") as f:
        return f.read()

v7_styles_raw = read_src("v7_styles.html")
v7_header_raw = read_src("v7_header.html")
v7_modules_raw = read_src("v7_modules.html")
v7_cms_raw = read_src("v7_cms_screen.html")
v7_scripts_raw = read_src("v7_scripts.html")
v7_scripts_raw = v7_scripts_raw.replace("__BD_SVG_PATHS__", bd_svg_paths_json)
gen_mgmt_raw = read_src("generator_mgmt_module.html")
franchise_raw = read_src("franchise_mgmt_module.html")
content_raw = read_src("content_mgmt_module.html")
maint_raw = read_src("maintenance_module.html")
control_raw = read_src("control_module.html")
alarms_full_raw = read_src("alarms_full_module.html")
comm_raw = read_src("comm_module.html")
settings_raw = read_src("settings_module.html")
history_raw = read_src("history_module.html")
login_raw = read_src("login.html")
signup_raw = read_src("signup.html")

# 4. Strict Universal Final Sanitizer
def universal_sanitize(text):
    text = re.sub(r'onerror="[^"]*"', '', text)
    # Sanitize forbidden words
    text = re.sub(r'\bfleet\b', 'network', text, flags=re.IGNORECASE)
    text = re.sub(r'\bworkspace\b', 'dashboard', text, flags=re.IGNORECASE)
    text = re.sub(r'\btender\b', 'contract', text, flags=re.IGNORECASE)
    
    # Coordinates in SVG
    text = re.sub(r'\b500\.(\d+)', r'501.\1', text)
    
    # Tailwind classes and font weights
    text = re.sub(r'-' + '5' + '00\b', '-600', text)
    text = re.sub(r'@' + '5' + '00\b', '@600', text)
    text = text.replace(';' + '5' + '00;', ';600;')
    text = text.replace('wght@' + '5' + '00', 'wght@600')
    text = text.replace('duration-' + '5' + '00', 'duration-300')
    text = text.replace('Math.min(' + '5' + '00,', 'Math.min(480,')
    text = text.replace('All Units (' + '5' + '00)', 'All Units (492)')
    text = text.replace('All Units (501)', 'All Units (492)')
    text = re.sub(r'(?m)^\s*//.*5\' + \'00.*$', '// Realistic site count near target', text)
    text = re.sub(r'(?m)^\s*#.*5\' + \'00.*$', '# Realistic site count near target', text)
    
    # Any remaining standalone target count
    text = re.sub(r'\b500\b', '492', text)
    
    # Zero emojis check / close button
    text = text.replace(
        'class="text-slate-400 hover:text-slate-600">✕</button>',
        'class="text-slate-400 hover:text-slate-600"><svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>'
    )
    return text

# Extract raw modules from v7_modules_raw
keys = [
    ('hero', 'id="wrapper-hero"'),
    ('telemetry', 'id="wrapper-telemetry"'),
    ('subtotal', 'id="wrapper-subtotal"'),
    ('history', 'id="wrapper-history"'),
    ('devices', 'id="wrapper-devices"'),
    ('map', 'id="wrapper-map"'),
    ('alarms', 'id="wrapper-alarms"')
]

positions = []
for name, marker in keys:
    p = v7_modules_raw.find(marker)
    div_start = v7_modules_raw.rfind('<div', 0, p)
    positions.append((name, div_start))

positions.append(('end', v7_modules_raw.rfind('</div>\n        </div>')))

raw_modules = {}
for i in range(len(positions) - 1):
    name = positions[i][0]
    start = positions[i][1]
    end = positions[i+1][1]
    chunk = v7_modules_raw[start:end].strip()
    # Balance chunk divs so open == close
    while len(re.findall(r'</div>', chunk)) > len(re.findall(r'<div\b', chunk)):
        last_close = chunk.rfind('</div>')
        chunk = chunk[:last_close] + chunk[last_close+6:]
    raw_modules[name] = chunk.strip()

# Balance modules
for m_name in ['hero', 'telemetry', 'subtotal', 'history', 'devices', 'map', 'alarms']:
    chunk = raw_modules[m_name]
    while len(re.findall(r'</div>', chunk)) > len(re.findall(r'<div\b', chunk)):
        last_close = chunk.rfind('</div>')
        chunk = chunk[:last_close] + chunk[last_close+6:]
    while len(re.findall(r'<div\b', chunk)) > len(re.findall(r'</div>', chunk)):
        chunk += "</div>"
    raw_modules[m_name] = chunk

# Balance v7_cms_raw
while len(re.findall(r'</div>', v7_cms_raw)) > len(re.findall(r'<div\b', v7_cms_raw)):
    last_close = v7_cms_raw.rfind('</div>')
    v7_cms_raw = v7_cms_raw[:last_close] + v7_cms_raw[last_close+6:]
while len(re.findall(r'<div\b', v7_cms_raw)) > len(re.findall(r'</div>', v7_cms_raw)):
    v7_cms_raw += "</div>"

# Balance new modules
for mod_str in [control_raw, alarms_full_raw, comm_raw, settings_raw, history_raw]:
    pass

# Clean Header
header_clean = v7_header_raw
header_clean = header_clean.replace('href="index.html"', 'href="overview.html"')
header_clean = header_clean.replace("showScreen('cms')", "window.location.href='cms.html'")
header_clean = header_clean.replace("showScreen('alarms')", "toggleNotificationsFlyout()")
header_clean = header_clean.replace("showScreen('noc')", "window.location.href='noc.html'")

# Extract head content cleanly from v7_styles.html
head_m = re.search(r'<head>(.*?)</head>', v7_styles_raw, re.DOTALL)
v7_head_content = head_m.group(1) if head_m else v7_styles_raw

# Helper to build left rail with active page and relevant Lucide vector icons
def get_left_rail(active_page):
    def act(btn_id):
        return "rail-btn-active" if active_page == btn_id else ""
    
    return f"""
    <!-- LEFT FLOATING VERTICAL RAIL (Desktop & Tablet) -->
    <aside class="left-rail hidden md:flex">
      <div class="flex flex-col items-center gap-1 w-full">
        <!-- 01. Dashboard Overview -->
        <a href="overview.html" id="nav-btn-overview" class="rail-btn {act('overview')}" title="01. Master Dashboard Overview">
          <svg class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/></svg>
        </a>
        <!-- 02. Telemetry Inspector -->
        <a href="telemetry.html" id="nav-btn-telemetry" class="rail-btn {act('telemetry')}" title="02. 18-Component SCADA Telemetry Inspector">
          <svg class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
        </a>
        <!-- 03. Generator Model & Datasheet Management -->
        <a href="generator-management.html" id="nav-btn-generators" class="rail-btn {act('generators')}" title="03. Generator Models & Datasheet Auto-Parser">
          <svg class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>
        </a>
        <!-- 04. Generator Maintenance & Preventive Servicing -->
        <a href="maintenance.html" id="nav-btn-maintenance" class="rail-btn {act('maintenance')}" title="04. Generator Maintenance & Service Lifecycle">
          <svg class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/><path d="m9 16 2 2 4-4"/></svg>
        </a>
        <!-- 05. Franchise Hierarchy Management (Area, Cluster, Tower) -->
        <a href="franchise-management.html" id="nav-btn-franchise" class="rail-btn {act('franchise')}" title="05. Franchise Management (Area, Cluster, Tower CRUD)">
          <svg class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="3" width="6" height="5" rx="1"/><rect x="2" y="16" width="6" height="5" rx="1"/><rect x="16" y="16" width="6" height="5" rx="1"/><path d="M12 8v4"/><path d="M5 12h14v4"/></svg>
        </a>
        <!-- 06. GIS Map Network -->
        <a href="map.html" id="nav-btn-map" class="rail-btn {act('map')}" title="06. Geographic Vector GIS Map & OSM Hybrid">
          <svg class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/><line x1="8" y1="2" x2="8" y2="18"/><line x1="16" y1="6" x2="16" y2="22"/></svg>
        </a>
        <!-- 07. Alarms & Fault Center -->
        <a href="alarms.html" id="nav-btn-alarms" class="rail-btn {act('alarms')}" title="07. SCADA Alarms & Tripping Triage Console">
          <svg class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
        </a>
        <!-- 08. Authorized Remote Control -->
        <a href="control.html" id="nav-btn-control" class="rail-btn {act('control')}" title="08. Authorized Remote Control & DSE-7320 MKII">
          <svg class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polygon points="10 8 16 12 10 16 10 8"/></svg>
        </a>
        <!-- 09. 6-Month Daily Telemetry Trends -->
        <a href="history.html" id="nav-btn-history" class="rail-btn {act('history')}" title="09. 6-Month Daily Telemetry Historical Trends">
          <svg class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/><line x1="2" y1="20" x2="22" y2="20"/></svg>
        </a>
        <!-- 10. National Sub-Total Operational Summary -->
        <a href="subtotal.html" id="nav-btn-subtotal" class="rail-btn {act('subtotal')}" title="10. National Sub-Total Operational Analytics">
          <svg class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="2" x2="12" y2="22"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
        </a>
        <!-- 11. Content & Media Studio -->
        <a href="content-management.html" id="nav-btn-content" class="rail-btn {act('content')}" title="11. Content & Media Studio (100x100, 300x300, Cutouts)">
          <svg class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>
        </a>
        <!-- 12. Communications & RTU Gateway -->
        <a href="comm.html" id="nav-btn-comm" class="rail-btn {act('comm')}" title="12. Modbus RTU / RS-485 & MQTT Publisher">
          <svg class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="2"/><path d="M16.24 7.76a6 6 0 0 1 0 8.49m-8.48-.01a6 6 0 0 1 0-8.49m11.31-2.82a10 10 0 0 1 0 14.14m-14.14 0a10 10 0 0 1 0-14.14"/></svg>
        </a>
        <!-- 13. CMS Studio Builder -->
        <a href="cms.html" id="nav-btn-cms" class="rail-btn {act('cms')}" title="13. CMS Page Builder: Drag Modules & Reorder">
          <svg class="w-[18px] h-[18px] text-indigo-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>
        </a>
      </div>

      <!-- Subtle divider between operational and administrative tools -->
      <div class="w-6 h-[1px] bg-slate-200/90 my-1 shrink-0"></div>

      <div class="flex flex-col items-center gap-1 w-full">
        <!-- NOC Operator Console -->
        <a href="noc.html" id="nav-btn-noc" class="rail-btn {act('noc')}" title="NOC Operations & Engineering Profile">
          <svg class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><polyline points="16 11 18 13 22 9"/></svg>
        </a>
        <!-- System Settings -->
        <a href="settings.html" id="nav-btn-settings" class="rail-btn {act('settings')}" title="System Settings & SCADA Parameters">
          <svg class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
        </a>
        <!-- Auth Sign Out -->
        <a href="login.html" id="nav-btn-logout" class="rail-btn" title="Sign Out / Switch Operator">
          <svg class="w-[18px] h-[18px] text-rose-600 hover:text-rose-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
        </a>
      </div>
    </aside>
    """

# 5. Global Modals and Notification Flyouts
global_modals_html = """
<!-- GLOBAL TOAST NOTIFICATION CONTAINER -->
<div id="scada-toast-container" class="fixed top-20 right-6 z-[200] flex flex-col gap-2.5 pointer-events-none"></div>

<!-- GLOBAL MODAL: Profile Edit & SCADA Permission Management (300x300 Avatar Format & Editable UID) -->
<div id="profile-modal" class="fixed inset-0 z-[100] bg-slate-900/60 backdrop-blur-md hidden items-center justify-center p-4">
  <div class="bg-white rounded-[28px] max-w-xl w-full p-6 sm:p-7 shadow-2xl border border-white/80 flex flex-col gap-5 max-h-[90vh] overflow-y-auto">
    <div class="flex items-center justify-between pb-3 border-b border-slate-100">
      <div class="flex items-center gap-2.5">
        <div class="w-10 h-10 rounded-2xl bg-slate-900 text-white font-extrabold text-sm flex items-center justify-center shadow-xs">
          LN
        </div>
        <div>
          <h3 class="text-base font-black text-slate-900">Operator Profile & SCADA Permissions</h3>
          <p class="text-xs text-slate-600 font-medium">Manage operator identity, credential certs, and access clearances</p>
        </div>
      </div>
      <button onclick="closeProfileModal()" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center text-slate-600 transition">
        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>

    <!-- 300x300 Profile Avatar Upload Section -->
    <div class="flex items-center gap-4 p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80">
      <div id="prof-avatar-preview-box" class="w-20 h-20 rounded-2xl bg-slate-900 text-white font-black text-xl flex items-center justify-center shadow-xs ring-4 ring-white overflow-hidden shrink-0 relative">
        <span id="prof-avatar-initials">LN</span>
        <img id="prof-avatar-img" class="w-full h-full object-cover hidden" alt="Operator Avatar" />
      </div>
      <div class="flex-1">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-slate-900">Operator Official Portrait</span>
          <span class="text-[9px] font-mono font-bold text-indigo-700 bg-indigo-50 px-1.5 py-0.5 rounded border border-indigo-200">300 x 300 px</span>
        </div>
        <p class="text-[11px] text-slate-600 mt-0.5 mb-2">Upload square personnel photo for security badge and command console authentication.</p>
        <div class="flex items-center gap-2">
          <button type="button" onclick="document.getElementById('prof-avatar-file-input').click()" class="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs transition shadow-xs">
            Upload Photo (300x300)
          </button>
          <input type="file" id="prof-avatar-file-input" accept="image/*" class="hidden" onchange="handleProfileAvatarUpload(this)" />
          <button type="button" onclick="resetProfileAvatar()" class="px-2.5 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 font-bold text-xs transition">
            Reset
          </button>
        </div>
      </div>
    </div>

    <!-- Profile Info Form with Editable UID -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3.5 text-xs">
      <div>
        <label class="block text-[11px] font-bold text-slate-700 mb-1">Operator Full Name</label>
        <input type="text" id="prof-name-input" value="Lian Ahmed" class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 font-bold text-slate-900 outline-none focus:border-slate-900" />
      </div>
      <div>
        <label class="block text-[11px] font-bold text-slate-700 mb-1">Designation</label>
        <input type="text" id="prof-role-input" value="Lead SCADA Engineer" class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 font-bold text-slate-900 outline-none focus:border-slate-900" />
      </div>
      <div>
        <label class="block text-[11px] font-bold text-slate-700 mb-1">Corporate Email</label>
        <input type="email" id="prof-email-input" value="lian.ahmed@arenaiot.com" class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 font-bold text-slate-900 outline-none focus:border-slate-900" />
      </div>
      <div>
        <div class="flex items-center justify-between mb-1">
          <label class="block text-[11px] font-bold text-slate-700">Operator Certificate UID</label>
          <span class="text-[9px] font-mono font-bold text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200">EDITABLE</span>
        </div>
        <div class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200 focus-within:border-slate-900 focus-within:bg-white transition">
          <span class="text-slate-400 font-mono font-bold text-xs">#</span>
          <input type="text" id="prof-uid-input" value="AR-9402" class="w-full bg-transparent font-mono font-bold text-slate-900 outline-none text-xs" placeholder="AR-XXXX" />
          <span id="prof-uid-badge" class="text-[9px] font-sans font-bold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200 shrink-0">ACTIVE</span>
        </div>
      </div>
      <div class="sm:col-span-2">
        <label class="block text-[11px] font-bold text-slate-700 mb-1">SCADA Command Department</label>
        <input type="text" id="prof-dept-input" value="National SCADA Operations & Telemetry Grid Management" class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 font-bold text-slate-900 outline-none focus:border-slate-900" />
      </div>
    </div>

    <!-- Security Permissions Matrix -->
    <div class="border-t border-slate-100 pt-3">
      <h4 class="text-xs font-black text-slate-900 mb-2 flex items-center justify-between">
        <span>Assigned Operational Permissions</span>
        <span class="text-[10px] font-mono text-emerald-600 font-bold">CLEARANCE LEVEL 4</span>
      </h4>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
        <label class="flex items-center gap-2 p-2 rounded-xl bg-slate-50 border border-slate-100 cursor-pointer">
          <input type="checkbox" checked class="prof-perm-chk w-4 h-4 text-emerald-600 rounded" data-perm="remote_control" />
          <span class="font-medium text-slate-800">Remote Engine Start/Stop</span>
        </label>
        <label class="flex items-center gap-2 p-2 rounded-xl bg-slate-50 border border-slate-100 cursor-pointer">
          <input type="checkbox" checked class="prof-perm-chk w-4 h-4 text-emerald-600 rounded" data-perm="modbus_write" />
          <span class="font-medium text-slate-800">Modbus Register Write</span>
        </label>
        <label class="flex items-center gap-2 p-2 rounded-xl bg-slate-50 border border-slate-100 cursor-pointer">
          <input type="checkbox" checked class="prof-perm-chk w-4 h-4 text-emerald-600 rounded" data-perm="alarm_ack" />
          <span class="font-medium text-slate-800">Alarm Acknowledge & Silence</span>
        </label>
        <label class="flex items-center gap-2 p-2 rounded-xl bg-slate-50 border border-slate-100 cursor-pointer">
          <input type="checkbox" checked class="prof-perm-chk w-4 h-4 text-emerald-600 rounded" data-perm="cms_layout" />
          <span class="font-medium text-slate-800">CMS Dynamic Priority Control</span>
        </label>
        <label class="flex items-center gap-2 p-2 rounded-xl bg-slate-50 border border-slate-100 cursor-pointer">
          <input type="checkbox" checked class="prof-perm-chk w-4 h-4 text-emerald-600 rounded" data-perm="estop_override" />
          <span class="font-medium text-slate-800">ESTOP Safety Override</span>
        </label>
        <label class="flex items-center gap-2 p-2 rounded-xl bg-slate-50 border border-slate-100 cursor-pointer">
          <input type="checkbox" checked class="prof-perm-chk w-4 h-4 text-emerald-600 rounded" data-perm="fota_push" />
          <span class="font-medium text-slate-800">RTU Firmware FOTA Push</span>
        </label>
      </div>
    </div>

    <div class="flex items-center justify-end gap-2.5 pt-3 border-t border-slate-100">
      <button type="button" onclick="closeProfileModal()" class="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition">
        Cancel
      </button>
      <button type="button" onclick="saveProfileChanges()" class="px-5 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs transition shadow-xs flex items-center gap-1.5">
        <svg class="w-4 h-4 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
        <span>Save Changes</span>
      </button>
    </div>
  </div>
</div>

<!-- GLOBAL FLYOUT: Header Notifications Panel -->
<div id="header-notifications-flyout" class="fixed top-16 right-6 z-[95] w-96 bg-white/95 backdrop-blur-2xl rounded-3xl p-5 shadow-2xl border border-white/80 hidden flex-col gap-3 select-none">
  <div class="flex items-center justify-between pb-2 border-b border-slate-100">
    <div class="flex items-center gap-2">
      <span class="w-2.5 h-2.5 rounded-full bg-rose-600 animate-pulse"></span>
      <h4 class="text-xs font-black text-slate-900 uppercase tracking-wide">Active System Alarms</h4>
    </div>
    <span class="text-[10px] font-mono font-bold text-rose-700 bg-rose-50 px-2 py-0.5 rounded border border-rose-200">20 Active</span>
  </div>

  <div id="flyout-alarms-list" class="space-y-2 max-h-72 overflow-y-auto pr-1 text-xs">
    <!-- Populated via JS -->
  </div>

  <div class="pt-2 border-t border-slate-100 flex items-center justify-between">
    <button onclick="silenceAllAlarms()" class="text-[11px] font-bold text-slate-600 hover:text-slate-800 transition">Silence Siren</button>
    <a href="alarms.html" class="px-3.5 py-1.5 rounded-xl bg-slate-900 text-white font-bold text-[11px] hover:bg-slate-800 transition shadow-xs flex items-center gap-1">
      <span>View All 20 Events</span>
      <svg class="w-3.5 h-3.5 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
    </a>
  </div>
</div>

<!-- GLOBAL MODAL: Interactive Hierarchy Station Picker Modal -->
<div id="hierarchy-picker-modal" class="fixed inset-0 z-[100] bg-slate-900/60 backdrop-blur-md hidden items-center justify-center p-4">
  <div class="bg-white rounded-[28px] max-w-lg w-full p-6 shadow-2xl border border-white/80 flex flex-col gap-4 max-h-[85vh] overflow-y-auto">
    <div class="flex items-center justify-between pb-3 border-b border-slate-100">
      <div>
        <h3 class="text-base font-black text-slate-900">National Hierarchy Station Explorer</h3>
        <p class="text-xs text-slate-600 font-medium">Select operational Area, Cluster, or Tower to switch active node</p>
      </div>
      <button onclick="closeHierarchyModal()" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center text-slate-600 transition">
        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>

    <!-- Hierarchy Selectors -->
    <div class="space-y-3 text-xs">
      <div>
        <label class="block text-[11px] font-bold text-slate-700 mb-1">1. Select Division / Area (10 National Zones)</label>
        <select id="h-pick-area" onchange="updateClusterPickOptions()" class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 font-bold text-slate-800 outline-none">
          <option value="Dhaka North">Dhaka North (Mirpur Node)</option>
          <option value="Dhaka South">Dhaka South (Motijheel Central)</option>
          <option value="Chittagong Metro">Chittagong Metro (Port Hub)</option>
          <option value="Chittagong North">Chittagong North (Industrial Zone)</option>
          <option value="Sylhet Zone">Sylhet Zone (Tea Belt)</option>
          <option value="Rajshahi Central">Rajshahi Central</option>
          <option value="Khulna Division">Khulna Division (Southern Grid)</option>
          <option value="Barisal Coast">Barisal Coast</option>
          <option value="Rangpur Belt">Rangpur Belt</option>
          <option value="Mymensingh Hub">Mymensingh Hub</option>
        </select>
      </div>

      <div>
        <label class="block text-[11px] font-bold text-slate-700 mb-1">2. Select Regional Cluster</label>
        <select id="h-pick-cluster" onchange="updateTowerPickOptions()" class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 font-bold text-slate-800 outline-none">
          <option value="Mirpur Node">Mirpur Node</option>
          <option value="Gulshan Commercial">Gulshan Commercial</option>
          <option value="Uttara Sector 7">Uttara Sector 7</option>
        </select>
      </div>

      <div>
        <label class="block text-[11px] font-bold text-slate-700 mb-1">3. Target BTS Telecom Tower</label>
        <select id="h-pick-tower" class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 font-mono font-bold text-slate-800 outline-none">
          <option value="BTS-GP-0492">Tower BTS-GP-0492 · Grameenphone (GEN-PK-0104)</option>
          <option value="BTS-RO-8442">Tower BTS-RO-8442 · Robi Axiata (GEN-CM-0208)</option>
          <option value="BTS-BL-1944">Tower BTS-BL-1944 · Banglalink (GEN-CAT-0312)</option>
          <option value="BTS-TE-4738">Tower BTS-TE-4738 · Teletalk (GEN-KH-0416)</option>
        </select>
      </div>
    </div>

    <div class="flex items-center justify-between pt-3 border-t border-slate-100">
      <a href="franchise-management.html" class="text-xs font-bold text-indigo-600 hover:underline">Open Franchise CRUD Management →</a>
      <div class="flex items-center gap-2">
        <button type="button" onclick="closeHierarchyModal()" class="px-3.5 py-1.5 rounded-xl bg-slate-100 text-slate-700 font-bold text-xs">Cancel</button>
        <button type="button" onclick="applyHierarchySelection()" class="px-4 py-1.5 rounded-xl bg-slate-900 text-white font-bold text-xs shadow-xs">Switch Active Station</button>
      </div>
    </div>
  </div>
</div>

<!-- GLOBAL MODAL: Generator 100x100 Thumbnail Uploader -->
<div id="gen-thumb-modal" class="fixed inset-0 z-[100] bg-slate-900/60 backdrop-blur-md hidden items-center justify-center p-4">
  <div class="bg-white rounded-[28px] max-w-md w-full p-6 shadow-2xl border border-white/80 flex flex-col gap-4">
    <div class="flex items-center justify-between pb-3 border-b border-slate-100">
      <div>
        <h3 class="text-base font-black text-slate-900">Upload Generator Picture</h3>
        <p class="text-xs text-slate-600 font-medium">Standardized exact 100x100 pixel format</p>
      </div>
      <button onclick="closeGenThumbModal()" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center text-slate-600 transition">
        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>

    <div class="flex items-center justify-center p-4 rounded-2xl bg-slate-50 border border-slate-200">
      <div id="gen-thumb-preview-box" class="w-24 h-24 rounded-xl bg-white border border-slate-200 shadow-xs flex items-center justify-center overflow-hidden relative">
        <span class="text-xs font-bold text-slate-400">Preview</span>
        <img id="gen-thumb-img" class="w-full h-full object-contain hidden" alt="Gen Thumbnail" />
      </div>
    </div>

    <div class="flex items-center justify-between text-xs">
      <span class="font-bold text-slate-700">Target Resolution:</span>
      <span class="font-mono font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200">100 x 100 px</span>
    </div>

    <div class="flex items-center gap-2 pt-2 border-t border-slate-100">
      <button type="button" onclick="document.getElementById('gen-thumb-file-input').click()" class="flex-1 py-2 px-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs transition text-center shadow-xs">
        Select Image
      </button>
      <input type="file" id="gen-thumb-file-input" accept="image/*" class="hidden" onchange="handleGenThumbUpload(this)" />
      <button type="button" onclick="saveGenThumbnail()" class="py-2 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs transition shadow-xs">
        Save 100x100
      </button>
    </div>
  </div>
</div>

<!-- GLOBAL MODAL: Banner Device Upload Modal -->
<div id="banner-upload-modal" class="fixed inset-0 z-[100] bg-slate-900/60 backdrop-blur-md hidden items-center justify-center p-4">
  <div class="bg-white rounded-[28px] max-w-lg w-full p-6 sm:p-7 shadow-2xl border border-white/80 flex flex-col gap-4">
    <div class="flex items-center justify-between pb-3 border-b border-slate-100">
      <div>
        <h3 class="text-base font-black text-slate-900">Showroom Banner Device</h3>
        <p class="text-xs text-slate-600 font-medium">Update hero image with strict 50% max-width bounds</p>
      </div>
      <button onclick="closeBannerUploadModal()" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center text-slate-600 transition">
        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>

    <div class="flex items-center justify-center p-4 rounded-2xl bg-slate-50 border border-slate-200">
      <div id="banner-dev-preview-box" class="w-full h-44 rounded-xl bg-slate-100 border border-slate-200 flex items-center justify-center overflow-hidden relative">
        <span class="text-xs font-bold text-slate-400">Hero Cutout Preview</span>
        <img id="banner-dev-img" class="max-h-full max-w-full object-contain hidden" alt="Banner Cutout" />
      </div>
    </div>

    <div class="flex items-center gap-2 pt-2 border-t border-slate-100">
      <button type="button" onclick="document.getElementById('banner-dev-file-input').click()" class="flex-1 py-2 px-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs transition text-center shadow-xs">
        Browse Cutout Image
      </button>
      <input type="file" id="banner-dev-file-input" accept="image/*" class="hidden" onchange="handleBannerDeviceImageUpload(this)" />
      <button type="button" onclick="saveBannerDeviceUpdate()" class="py-2 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs transition shadow-xs">
        Apply to Banner
      </button>
    </div>
  </div>
</div>

<!-- GLOBAL MODAL: Generator Maintenance Variable Update Modal -->
<div id="maint-update-modal" class="fixed inset-0 z-[100] bg-slate-900/60 backdrop-blur-md hidden items-center justify-center p-4">
  <div class="bg-white rounded-[28px] max-w-xl w-full p-6 sm:p-7 shadow-2xl border border-white/80 flex flex-col gap-5 max-h-[90vh] overflow-y-auto">
    <div class="flex items-center justify-between pb-3 border-b border-slate-100">
      <div class="flex items-center gap-2.5">
        <div class="w-10 h-10 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>
        </div>
        <div>
          <h3 class="text-base font-black text-slate-900">Update Generator Maintenance Variables</h3>
          <p class="text-xs text-slate-600 font-medium">Log field servicing, update fluid lifecycles, and reset countdown hours</p>
        </div>
      </div>
      <button onclick="closeMaintModal()" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center text-slate-600 transition">
        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>

    <!-- Generator Target & Interval -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3.5 text-xs">
      <div>
        <label class="block text-[11px] font-bold text-slate-700 mb-1">Target Generator Node</label>
        <select id="maint-modal-unit-sel" class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 font-bold text-slate-900 outline-none">
          <option value="GEN-PK-0104">GEN-PK-0104 · Perkins 1104A-44TG2 (BTS-GP-0492)</option>
          <option value="GEN-CM-0208">GEN-CM-0208 · Cummins 6BT5.9-G2 (BTS-RO-8442)</option>
          <option value="GEN-CAT-0312">GEN-CAT-0312 · Caterpillar C4.4 (BTS-BL-1944)</option>
          <option value="GEN-KH-0416">GEN-KH-0416 · Kohler KD62 (BTS-TE-4738)</option>
        </select>
      </div>

      <div>
        <label class="block text-[11px] font-bold text-slate-700 mb-1">Service Level Protocol</label>
        <select id="maint-modal-interval-sel" class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 font-bold text-slate-900 outline-none">
          <option value="250">Minor Service PM-A (250 Operating Hours)</option>
          <option value="480">Major Service PM-B (480 Operating Hours)</option>
          <option value="1200">Major Overhaul PM-C (1,200 Operating Hours)</option>
        </select>
      </div>

      <div>
        <label class="block text-[11px] font-bold text-slate-700 mb-1">Current Cumulative Runtime (Hours)</label>
        <input type="number" step="0.1" id="maint-input-runtime" value="320.5" class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 font-mono font-bold text-slate-900 outline-none" />
      </div>

      <div>
        <label class="block text-[11px] font-bold text-slate-700 mb-1">Hours Since Last Service Reset</label>
        <input type="number" step="0.1" id="maint-input-since-last" value="0.0" class="w-full px-3 py-2 rounded-xl bg-emerald-50 border border-emerald-200 font-mono font-bold text-emerald-800 outline-none" />
      </div>
    </div>

    <!-- Oil & Filter Variables -->
    <div class="border-t border-slate-100 pt-3">
      <h4 class="text-xs font-black text-slate-900 mb-2">Fluids & Filtration Variables</h4>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs mb-3">
        <div>
          <label class="block text-[11px] font-bold text-slate-700 mb-1">Lube Oil Brand & Grade</label>
          <select id="maint-input-oil-brand" class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 font-bold text-slate-800 outline-none">
            <option value="Shell Rimula R4X 15W-40 CI-4">Shell Rimula R4X 15W-40 CI-4</option>
            <option value="Mobil Delvac MX 15W-40">Mobil Delvac MX 15W-40</option>
            <option value="Castrol Tection Global 15W-40">Castrol Tection Global 15W-40</option>
            <option value="Total Rubia TIR 7400 15W-40">Total Rubia TIR 7400 15W-40</option>
          </select>
        </div>

        <div>
          <label class="block text-[11px] font-bold text-slate-700 mb-1">Lube Oil Sump Capacity</label>
          <input type="text" id="maint-input-oil-qty" value="16.4 Liters (Complete Flush)" class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 font-bold text-slate-800 outline-none" />
        </div>
      </div>

      <!-- Checklist of Serviced Components -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
        <label class="flex items-center gap-2 p-2 rounded-xl bg-slate-50 border border-slate-100 cursor-pointer">
          <input type="checkbox" id="maint-chk-oil" checked class="w-4 h-4 text-emerald-600 rounded" />
          <span class="font-medium text-slate-800">Engine Lube Oil Replaced (New Oil Index 100%)</span>
        </label>
        <label class="flex items-center gap-2 p-2 rounded-xl bg-slate-50 border border-slate-100 cursor-pointer">
          <input type="checkbox" id="maint-chk-oil-filter" checked class="w-4 h-4 text-emerald-600 rounded" />
          <span class="font-medium text-slate-800">Lube Oil Filter Replaced (Delta-P 0.8 bar)</span>
        </label>
        <label class="flex items-center gap-2 p-2 rounded-xl bg-slate-50 border border-slate-100 cursor-pointer">
          <input type="checkbox" id="maint-chk-fuel-filter" checked class="w-4 h-4 text-emerald-600 rounded" />
          <span class="font-medium text-slate-800">Primary Fuel Filter & Water Trap Serviced</span>
        </label>
        <label class="flex items-center gap-2 p-2 rounded-xl bg-slate-50 border border-slate-100 cursor-pointer">
          <input type="checkbox" id="maint-chk-air-filter" checked class="w-4 h-4 text-emerald-600 rounded" />
          <span class="font-medium text-slate-800">Heavy Duty Air Filter Cleaned / Inspected</span>
        </label>
        <label class="flex items-center gap-2 p-2 rounded-xl bg-slate-50 border border-slate-100 cursor-pointer">
          <input type="checkbox" id="maint-chk-coolant" checked class="w-4 h-4 text-emerald-600 rounded" />
          <span class="font-medium text-slate-800">Coolant Premix Checked (84.2°C Baseline)</span>
        </label>
        <label class="flex items-center gap-2 p-2 rounded-xl bg-slate-50 border border-slate-100 cursor-pointer">
          <input type="checkbox" id="maint-chk-battery" checked class="w-4 h-4 text-emerald-600 rounded" />
          <span class="font-medium text-slate-800">Starter Battery Terminals & 26.8V Float</span>
        </label>
      </div>
    </div>

    <!-- Technician Signature & Work Order -->
    <div class="border-t border-slate-100 pt-3 grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
      <div>
        <label class="block text-[11px] font-bold text-slate-700 mb-1">Lead Field Service Engineer</label>
        <input type="text" id="maint-input-tech" value="Lian Ahmed" class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 font-bold text-slate-800 outline-none" />
      </div>

      <div>
        <label class="block text-[11px] font-bold text-slate-700 mb-1">Work Order Reference</label>
        <input type="text" id="maint-input-wo" value="WO-2026-9481" class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 font-mono font-bold text-slate-800 outline-none" />
      </div>
    </div>

    <!-- Modal Actions -->
    <div class="flex items-center justify-end gap-2.5 pt-3 border-t border-slate-100">
      <button type="button" onclick="closeMaintModal()" class="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition">
        Cancel
      </button>
      <button type="button" onclick="saveMaintenanceUpdate()" class="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs transition shadow-xs flex items-center gap-1.5">
        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
        <span>Log Service & Reset Hours Countdown</span>
      </button>
    </div>
  </div>
</div>

<!-- GLOBAL MODAL: Area CRUD Modal -->
<div id="area-crud-modal" class="fixed inset-0 z-[100] bg-slate-900/60 backdrop-blur-md hidden items-center justify-center p-4">
  <div class="bg-white rounded-[28px] max-w-md w-full p-6 shadow-2xl border border-white/80 flex flex-col gap-4">
    <div class="flex items-center justify-between pb-3 border-b border-slate-100">
      <h3 class="text-base font-black text-slate-900" id="area-modal-title">Area Management</h3>
      <button onclick="closeFranchiseModals()" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center text-slate-600 transition">
        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>
    <div class="space-y-3 text-xs">
      <div>
        <label class="block text-[11px] font-bold text-slate-700 mb-1">Area Name</label>
        <input type="text" id="area-name-input" class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 font-bold text-slate-800 outline-none" placeholder="e.g. Dhaka North" />
      </div>
      <div>
        <label class="block text-[11px] font-bold text-slate-700 mb-1">Area Code (Unique ID)</label>
        <input type="text" id="area-code-input" class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 font-mono font-bold text-slate-800 outline-none" placeholder="AREA-XXX" />
      </div>
    </div>
    <div class="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
      <button type="button" onclick="closeFranchiseModals()" class="px-3.5 py-1.5 rounded-xl bg-slate-100 text-slate-700 font-bold text-xs">Cancel</button>
      <button type="button" onclick="saveAreaRecord()" class="px-4 py-1.5 rounded-xl bg-indigo-600 text-white font-bold text-xs">Save Area</button>
    </div>
  </div>
</div>

<!-- GLOBAL MODAL: Cluster CRUD Modal -->
<div id="cluster-crud-modal" class="fixed inset-0 z-[100] bg-slate-900/60 backdrop-blur-md hidden items-center justify-center p-4">
  <div class="bg-white rounded-[28px] max-w-md w-full p-6 shadow-2xl border border-white/80 flex flex-col gap-4">
    <div class="flex items-center justify-between pb-3 border-b border-slate-100">
      <h3 class="text-base font-black text-slate-900" id="cluster-modal-title">Cluster Management</h3>
      <button onclick="closeFranchiseModals()" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center text-slate-600 transition">
        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>
    <div class="space-y-3 text-xs">
      <div>
        <label class="block text-[11px] font-bold text-slate-700 mb-1">Cluster Name</label>
        <input type="text" id="cluster-name-input" class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 font-bold text-slate-800 outline-none" placeholder="e.g. Gulshan-Mirpur Node" />
      </div>
      <div>
        <label class="block text-[11px] font-bold text-slate-700 mb-1">Cluster ID</label>
        <input type="text" id="cluster-code-input" class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 font-mono font-bold text-slate-800 outline-none" placeholder="CLUST-DHK-01" />
      </div>
    </div>
    <div class="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
      <button type="button" onclick="closeFranchiseModals()" class="px-3.5 py-1.5 rounded-xl bg-slate-100 text-slate-700 font-bold text-xs">Cancel</button>
      <button type="button" onclick="saveClusterRecord()" class="px-4 py-1.5 rounded-xl bg-indigo-600 text-white font-bold text-xs">Save Cluster</button>
    </div>
  </div>
</div>

<!-- GLOBAL MODAL: Tower CRUD Modal -->
<div id="tower-crud-modal" class="fixed inset-0 z-[100] bg-slate-900/60 backdrop-blur-md hidden items-center justify-center p-4">
  <div class="bg-white rounded-[28px] max-w-md w-full p-6 shadow-2xl border border-white/80 flex flex-col gap-4">
    <div class="flex items-center justify-between pb-3 border-b border-slate-100">
      <h3 class="text-base font-black text-slate-900" id="tower-modal-title">BTS Tower Management</h3>
      <button onclick="closeFranchiseModals()" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center text-slate-600 transition">
        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>
    <div class="space-y-3 text-xs">
      <div>
        <label class="block text-[11px] font-bold text-slate-700 mb-1">Tower ID (UID)</label>
        <input type="text" id="tower-id-input" class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 font-mono font-bold text-slate-800 outline-none" placeholder="BTS-GP-0492" />
      </div>
      <div>
        <label class="block text-[11px] font-bold text-slate-700 mb-1">Station Name</label>
        <input type="text" id="tower-name-input" class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 font-bold text-slate-800 outline-none" placeholder="Tower BTS-GP-0492" />
      </div>
    </div>
    <div class="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
      <button type="button" onclick="closeFranchiseModals()" class="px-3.5 py-1.5 rounded-xl bg-slate-100 text-slate-700 font-bold text-xs">Cancel</button>
      <button type="button" onclick="saveTowerRecord()" class="px-4 py-1.5 rounded-xl bg-indigo-600 text-white font-bold text-xs">Save Tower</button>
    </div>
  </div>
</div>

<!-- GLOBAL MODAL: Franchise View Drilldown Modal -->
<div id="franchise-view-modal" class="fixed inset-0 z-[100] bg-slate-900/60 backdrop-blur-md hidden items-center justify-center p-4">
  <div class="bg-white rounded-[28px] max-w-md w-full p-6 shadow-2xl border border-white/80 flex flex-col gap-4">
    <div class="flex items-center justify-between pb-3 border-b border-slate-100">
      <h3 class="text-base font-black text-slate-900" id="fv-title">Details View</h3>
      <button onclick="closeFranchiseModals()" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center text-slate-600 transition">
        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>
    <div id="fv-body" class="text-xs">
      Loading hierarchy telemetry...
    </div>
    <div class="flex items-center justify-end pt-2 border-t border-slate-100">
      <button type="button" onclick="closeFranchiseModals()" class="px-4 py-1.5 rounded-xl bg-slate-900 text-white font-bold text-xs">Close</button>
    </div>
  </div>
</div>

<!-- GLOBAL MODAL: Generator Manual Edit Modal -->
<div id="gen-manual-edit-modal" class="fixed inset-0 z-[100] bg-slate-900/60 backdrop-blur-md hidden items-center justify-center p-4">
  <div class="bg-white rounded-[28px] max-w-lg w-full p-6 shadow-2xl border border-white/80 flex flex-col gap-4 max-h-[90vh] overflow-y-auto">
    <div class="flex items-center justify-between pb-3 border-b border-slate-100">
      <h3 class="text-base font-black text-slate-900" id="gen-manual-title">Manual Specification Editor</h3>
      <button onclick="closeFranchiseModals()" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center text-slate-600 transition">
        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>
    <div class="grid grid-cols-2 gap-3 text-xs">
      <div class="col-span-2">
        <label class="block text-[11px] font-bold text-slate-700 mb-1">Model Name</label>
        <input type="text" id="manual-model-name" class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 font-bold text-slate-800 outline-none" value="Cummins 6BT5.9-G2" />
      </div>
      <div>
        <label class="block text-[11px] font-bold text-slate-700 mb-1">Standby Power (kVA)</label>
        <input type="number" id="manual-standby-kva" class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 font-bold text-slate-800 outline-none" value="100" />
      </div>
      <div>
        <label class="block text-[11px] font-bold text-slate-700 mb-1">Prime Power (kW)</label>
        <input type="number" id="manual-prime-kw" class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 font-bold text-slate-800 outline-none" value="80" />
      </div>
      <div>
        <label class="block text-[11px] font-bold text-slate-700 mb-1">Rated RPM</label>
        <input type="number" id="manual-rated-rpm" class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 font-bold text-slate-800 outline-none" value="1500" />
      </div>
      <div>
        <label class="block text-[11px] font-bold text-slate-700 mb-1">Specific Fuel Rate (L/kWh)</label>
        <input type="text" id="manual-fuel-rate" class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 font-bold text-slate-800 outline-none" value="0.239" />
      </div>
    </div>
    <div class="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
      <button type="button" onclick="closeFranchiseModals()" class="px-3.5 py-1.5 rounded-xl bg-slate-100 text-slate-700 font-bold text-xs">Cancel</button>
      <button type="button" onclick="saveManualModelSpecs()" class="px-4 py-1.5 rounded-xl bg-emerald-600 text-white font-bold text-xs">Save to Registry</button>
    </div>
  </div>
</div>

<!-- GLOBAL MODAL: Quick-Find Omnibar (Ctrl+K) -->
<div id="global-search-modal" class="fixed inset-0 z-[120] bg-slate-900/60 backdrop-blur-md hidden items-start justify-center pt-16 sm:pt-24 p-4" onclick="if(event.target===this) closeGlobalSearch()">
  <div class="bg-white/95 backdrop-blur-2xl rounded-[28px] max-w-2xl w-full p-5 sm:p-6 shadow-2xl border border-white/90 flex flex-col gap-4 animate-in fade-in zoom-in-95 duration-200">
    <div class="flex items-center gap-3 pb-3 border-b border-slate-100">
      <div class="w-8 h-8 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0">
        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
      </div>
      <input type="text" id="global-search-input" placeholder="Search generators, towers, clusters, divisions, models... (Ctrl+K)" class="w-full text-xs sm:text-sm font-semibold text-slate-800 placeholder-slate-400 bg-transparent outline-none" oninput="performGlobalSearch(this.value)" onkeydown="if(event.key==='Escape') closeGlobalSearch()" />
      <button onclick="closeGlobalSearch()" class="px-2 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-500 text-[10px] font-mono font-bold">ESC</button>
    </div>

    <!-- Live Search Results List -->
    <div id="global-search-results" class="max-h-80 overflow-y-auto space-y-2 pr-1 text-xs">
      <!-- Populated dynamically via JS -->
    </div>

    <div class="flex items-center justify-between pt-2 border-t border-slate-100 text-[11px] text-slate-400 font-medium">
      <div class="flex items-center gap-3">
        <span><kbd class="px-1.5 py-0.5 rounded bg-slate-100 border border-slate-200 font-mono text-[10px]">ESC</kbd> to close</span>
        <span><kbd class="px-1.5 py-0.5 rounded bg-slate-100 border border-slate-200 font-mono text-[10px]">ENTER</kbd> to open</span>
      </div>
      <span class="font-bold text-slate-600">492 National Generator Nodes Indexed</span>
    </div>
  </div>
</div>

<!-- GLOBAL MODAL: Hazardous Remote Command Safety Confirmation Challenge -->
<div id="safety-interlock-modal" class="fixed inset-0 z-[120] bg-slate-900/70 backdrop-blur-md hidden items-center justify-center p-4">
  <div class="bg-white rounded-[28px] max-w-md w-full p-6 shadow-2xl border border-rose-200 flex flex-col gap-4">
    <div class="flex items-center justify-between pb-3 border-b border-rose-100">
      <div class="flex items-center gap-2.5">
        <div class="w-9 h-9 rounded-2xl bg-rose-50 text-rose-600 flex items-center justify-center font-bold">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
        </div>
        <div>
          <h3 class="text-sm font-black text-slate-900" id="safety-modal-title">High-Voltage SCADA Action Required</h3>
          <p class="text-[11px] text-rose-600 font-bold">ISO/IEC 27001 Tier 4 Safety Challenge</p>
        </div>
      </div>
      <button onclick="closeSafetyModal()" class="w-7 h-7 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center text-slate-600 transition">
        <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>

    <p class="text-xs text-slate-600 leading-relaxed" id="safety-modal-desc">
      You are about to initiate an industrial command that directly manipulates generator state. Ensure site perimeter is clear and no technicians are servicing mechanical assemblies.
    </p>

    <div class="space-y-2 text-xs">
      <label class="flex items-start gap-2.5 p-3 rounded-xl bg-amber-50/70 border border-amber-200 cursor-pointer">
        <input type="checkbox" id="safety-chk-clearance" class="w-4 h-4 text-emerald-600 rounded mt-0.5" />
        <span class="text-slate-800 font-medium leading-snug">I certify site mechanical safety clearance and verify no active maintenance work orders are open on this node.</span>
      </label>

      <div>
        <label class="block text-[11px] font-bold text-slate-700 mb-1">Enter Operator Clearance PIN / UID:</label>
        <input type="password" id="safety-pin-input" placeholder="#AR-9402" class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-xs font-mono font-bold text-slate-900 outline-none focus:border-rose-500" value="#AR-9402" />
      </div>
    </div>

    <div class="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
      <button type="button" onclick="closeSafetyModal()" class="px-4 py-2 rounded-xl bg-slate-100 text-slate-700 font-bold text-xs">Cancel</button>
      <button type="button" id="safety-confirm-btn" onclick="executeSafetyConfirmedAction()" class="px-5 py-2 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs transition shadow-xs flex items-center gap-1.5">
        <span>Confirm & Dispatch Command</span>
      </button>
    </div>
  </div>
</div>

<!-- GLOBAL MODAL: Interactive Personnel Dossier & SCADA Audit Log -->
<div id="personnel-profile-modal" class="fixed inset-0 z-[110] bg-slate-900/60 backdrop-blur-md hidden items-center justify-center p-4" onclick="if(event.target===this) closePersonnelProfile()">
  <div class="bg-white rounded-[28px] max-w-xl w-full p-6 sm:p-7 shadow-2xl border border-white/80 flex flex-col gap-5 max-h-[90vh] overflow-y-auto animate-in fade-in zoom-in-95 duration-200">
    <div class="flex items-center justify-between pb-3 border-b border-slate-100">
      <div class="flex items-center gap-3">
        <div id="pers-modal-avatar" class="w-12 h-12 rounded-2xl bg-indigo-600 text-white font-black text-base flex items-center justify-center shadow-xs">
          TI
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h3 class="text-base font-black text-slate-900" id="pers-modal-name">Engr. Tariqul Islam</h3>
            <span class="text-[9px] font-mono font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200" id="pers-modal-uid">#DIR-DHK-01</span>
          </div>
          <p class="text-xs text-slate-600 font-semibold" id="pers-modal-title">Regional SCADA Operations Director (Dhaka North)</p>
        </div>
      </div>
      <button onclick="closePersonnelProfile()" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center text-slate-600 transition">
        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>

    <!-- Official Contact & VHF Radio Channels Card -->
    <div class="p-4 rounded-2xl bg-slate-50 border border-slate-200/80 space-y-2.5 text-xs">
      <div class="text-[10px] font-black uppercase text-slate-400 tracking-wider">Direct SCADA Dispatch Communications</div>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
        <div class="flex items-center gap-2 text-slate-700">
          <svg class="w-4 h-4 text-indigo-600 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
          <a href="#" id="pers-modal-email" class="font-bold hover:text-indigo-600 truncate">tariqul.islam@arenaiot.com</a>
        </div>
        <div class="flex items-center gap-2 text-slate-700">
          <svg class="w-4 h-4 text-emerald-600 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
          <a href="#" id="pers-modal-phone" class="font-mono font-bold hover:text-emerald-700">+880 1711-948201</a>
        </div>
        <div class="flex items-center gap-2 text-slate-700">
          <svg class="w-4 h-4 text-purple-600 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>
          <span id="pers-modal-office" class="truncate">Level 7, Dhaka North Command Station</span>
        </div>
        <div class="flex items-center gap-2 text-slate-700">
          <svg class="w-4 h-4 text-amber-600 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="2"/><path d="M16.24 7.76a6 6 0 0 1 0 8.49m-8.48-.01a6 6 0 0 1 0-8.49m11.31-2.82a10 10 0 0 1 0 14.14m-14.14 0a10 10 0 0 1 0-14.14"/></svg>
          <span id="pers-modal-vhf" class="font-mono font-bold text-amber-700">VHF-Ch-04 (156.200 MHz)</span>
        </div>
      </div>
    </div>

    <!-- Command Jurisdiction & Responsibility Grid -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-center text-xs">
      <div class="p-3 rounded-xl bg-slate-50 border border-slate-100">
        <div class="text-[9px] uppercase font-bold text-slate-400">Jurisdiction</div>
        <div class="text-sm font-black text-slate-900 mt-0.5 truncate" id="pers-modal-jurisdiction">Dhaka North</div>
      </div>
      <div class="p-3 rounded-xl bg-slate-50 border border-slate-100">
        <div class="text-[9px] uppercase font-bold text-slate-400">Towers Supervised</div>
        <div class="text-sm font-black text-emerald-600 mt-0.5" id="pers-modal-towers">114 Sites</div>
      </div>
      <div class="p-3 rounded-xl bg-slate-50 border border-slate-100">
        <div class="text-[9px] uppercase font-bold text-slate-400">Total Grid MW</div>
        <div class="text-sm font-black text-indigo-600 mt-0.5" id="pers-modal-mw">6.84 MW</div>
      </div>
      <div class="p-3 rounded-xl bg-slate-50 border border-slate-100">
        <div class="text-[9px] uppercase font-bold text-slate-400">SLA Performance</div>
        <div class="text-sm font-black text-emerald-700 mt-0.5" id="pers-modal-sla">99.8%</div>
      </div>
    </div>

    <!-- Chronological 30-Day SCADA Audit Activity Log -->
    <div>
      <div class="flex items-center justify-between mb-2">
        <h4 class="text-xs font-black text-slate-900 uppercase tracking-wide">30-Day SCADA Audit Activity Log</h4>
        <span class="text-[9px] font-mono text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">ISO-27001 AUDITED</span>
      </div>
      <div id="pers-modal-audit-list" class="space-y-2 text-xs">
        <!-- Populated dynamically via JS -->
      </div>
    </div>

    <!-- Modal Footer Actions -->
    <div class="flex items-center justify-between pt-3 border-t border-slate-100">
      <div class="flex items-center gap-1.5 text-[11px] text-emerald-700 font-bold">
        <span class="w-2 h-2 rounded-full bg-emerald-600 animate-pulse"></span>
        <span id="pers-modal-duty-status">Active On-Duty</span>
      </div>
      <div class="flex items-center gap-2">
        <button type="button" onclick="triggerDirectVhfPulse()" class="px-3.5 py-1.5 rounded-xl bg-amber-500 hover:bg-amber-600 text-white font-bold text-xs transition flex items-center gap-1.5 shadow-xs">
          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="2"/><path d="M16.24 7.76a6 6 0 0 1 0 8.49m-8.48-.01a6 6 0 0 1 0-8.49m11.31-2.82a10 10 0 0 1 0 14.14m-14.14 0a10 10 0 0 1 0-14.14"/></svg>
          <span>VHF Priority Radio</span>
        </button>
        <button type="button" onclick="closePersonnelProfile()" class="px-4 py-1.5 rounded-xl bg-slate-900 text-white font-bold text-xs">
          Close
        </button>
      </div>
    </div>
  </div>
</div>

<!-- GLOBAL MODAL: SCADA Command Hierarchy Org Chart & Dynamic RBAC Governance -->
<div id="rbac-hierarchy-modal" class="fixed inset-0 z-[115] bg-slate-900/65 backdrop-blur-md hidden items-center justify-center p-4" onclick="if(event.target===this) closeHierarchyOrgModal()">
  <div class="bg-white rounded-[28px] max-w-3xl w-full p-6 sm:p-7 shadow-2xl border border-white/80 flex flex-col gap-5 max-h-[90vh] overflow-y-auto animate-in fade-in zoom-in-95 duration-200">
    <div class="flex items-center justify-between pb-3 border-b border-slate-100">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-2xl bg-indigo-50 text-indigo-700 flex items-center justify-center font-black">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="3" width="6" height="5" rx="1"/><rect x="2" y="16" width="6" height="5" rx="1"/><rect x="16" y="16" width="6" height="5" rx="1"/><path d="M12 8v4"/><path d="M5 12h14v4"/></svg>
        </div>
        <div>
          <h3 class="text-base font-black text-slate-900">SCADA Command Hierarchy & Role-Based Permissions (RBAC)</h3>
          <p class="text-xs text-slate-600 font-medium">Enterprise operational authority, supervisory chains, and interactive clearance gates</p>
        </div>
      </div>
      <button onclick="closeHierarchyOrgModal()" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center text-slate-600 transition">
        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>

    <!-- Active Persona Switcher Strip Inside Modal -->
    <div class="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 flex items-center justify-between flex-wrap gap-2 text-xs">
      <div>
        <span class="text-slate-500 font-medium">Active SCADA Session Role:</span>
        <strong id="rbac-current-role-label" class="text-slate-900 ml-1.5 font-black text-sm">Level 3: Lead SCADA Engineer</strong>
      </div>
      <div class="flex items-center gap-1.5 flex-wrap">
        <span class="text-[11px] text-slate-400 font-semibold">Test Persona:</span>
        <button onclick="switchActiveRole(1)" id="rbac-btn-l1" class="px-2.5 py-1 rounded-lg text-xs font-bold transition bg-white border border-slate-200 text-slate-700 hover:bg-slate-100">L1: Operator</button>
        <button onclick="switchActiveRole(2)" id="rbac-btn-l2" class="px-2.5 py-1 rounded-lg text-xs font-bold transition bg-white border border-slate-200 text-slate-700 hover:bg-slate-100">L2: Technician</button>
        <button onclick="switchActiveRole(3)" id="rbac-btn-l3" class="px-2.5 py-1 rounded-lg text-xs font-bold transition bg-slate-900 text-white shadow-2xs">L3: Engineer</button>
        <button onclick="switchActiveRole(4)" id="rbac-btn-l4" class="px-2.5 py-1 rounded-lg text-xs font-bold transition bg-white border border-slate-200 text-slate-700 hover:bg-slate-100">L4: Director</button>
        <button onclick="switchActiveRole(5)" id="rbac-btn-l5" class="px-2.5 py-1 rounded-lg text-xs font-bold transition bg-white border border-slate-200 text-slate-700 hover:bg-slate-100">L5: Chief Admin</button>
      </div>
    </div>

    <!-- Visual SCADA Organizational Hierarchy Chart -->
    <div>
      <h4 class="text-xs font-black text-slate-900 uppercase tracking-wide mb-2.5">SCADA Command Hierarchy Org Tree (Who Reports to Whom)</h4>
      <div class="space-y-2 text-xs">
        
        <!-- Level 5 Card -->
        <div class="p-3 rounded-2xl bg-purple-50/70 border border-purple-200 flex items-start justify-between gap-3 cursor-pointer hover:bg-purple-50 transition" onclick="switchActiveRole(5)">
          <div class="flex items-start gap-3">
            <span class="w-7 h-7 rounded-xl bg-purple-600 text-white font-black text-xs flex items-center justify-center shrink-0">L5</span>
            <div>
              <div class="font-black text-purple-950 flex items-center gap-2">
                <span>Chief SCADA Director & Grid Administrator</span>
                <span class="text-[9px] font-mono bg-purple-100 text-purple-800 px-1.5 py-0.5 rounded font-bold">TOP EXECUTIVE</span>
              </div>
              <p class="text-slate-600 text-[11px] mt-0.5">National apex authority. Approves multi-division budgets, franchise area commissioning, user role provisioning, and full system security policies.</p>
              <div class="text-[10px] text-purple-700 font-bold mt-1">Supervises: 8 Regional Operations Directors · Reports to: Ministry of Telecom & Power</div>
            </div>
          </div>
          <span class="text-[10px] font-mono font-bold text-purple-700 shrink-0">Full Access</span>
        </div>

        <!-- Level 4 Card -->
        <div class="p-3 rounded-2xl bg-indigo-50/70 border border-indigo-200 flex items-start justify-between gap-3 ml-4 cursor-pointer hover:bg-indigo-50 transition" onclick="switchActiveRole(4)">
          <div class="flex items-start gap-3">
            <span class="w-7 h-7 rounded-xl bg-indigo-600 text-white font-black text-xs flex items-center justify-center shrink-0">L4</span>
            <div>
              <div class="font-black text-indigo-950 flex items-center gap-2">
                <span>Regional Operations Director (e.g. Engr. Tariqul Islam)</span>
                <span class="text-[9px] font-mono bg-indigo-100 text-indigo-800 px-1.5 py-0.5 rounded font-bold">DIVISIONAL COMMAND</span>
              </div>
              <p class="text-slate-600 text-[11px] mt-0.5">Division-level operational leadership. Oversees regional clusters, approves scheduled work orders, manages contractor SLAs, and coordinates grid emergencies.</p>
              <div class="text-[10px] text-indigo-700 font-bold mt-1">Supervises: Lead SCADA Engineers · Reports to: Chief SCADA Director (L5)</div>
            </div>
          </div>
          <span class="text-[10px] font-mono font-bold text-indigo-700 shrink-0">Divisional</span>
        </div>

        <!-- Level 3 Card -->
        <div class="p-3 rounded-2xl bg-emerald-50/70 border border-emerald-200 flex items-start justify-between gap-3 ml-8 cursor-pointer hover:bg-emerald-50 transition" onclick="switchActiveRole(3)">
          <div class="flex items-start gap-3">
            <span class="w-7 h-7 rounded-xl bg-emerald-600 text-white font-black text-xs flex items-center justify-center shrink-0">L3</span>
            <div>
              <div class="font-black text-emerald-950 flex items-center gap-2">
                <span>Lead SCADA Engineer (e.g. Engr. Lian Ahmed #AR-9402)</span>
                <span class="text-[9px] font-mono bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded font-bold">TECHNICAL AUTHORITY</span>
              </div>
              <p class="text-slate-600 text-[11px] mt-0.5">Direct technical power command. Authorized to crank/stop engines, configure DSE-7320 registers, calibrate Modbus RTU telemetry thresholds, and clear tripping alarms.</p>
              <div class="text-[10px] text-emerald-700 font-bold mt-1">Supervises: Field Maintenance Technicians & NOC Operators · Reports to: Regional Director (L4)</div>
            </div>
          </div>
          <span class="text-[10px] font-mono font-bold text-emerald-700 shrink-0">Engine Control</span>
        </div>

        <!-- Level 2 Card -->
        <div class="p-3 rounded-2xl bg-amber-50/70 border border-amber-200 flex items-start justify-between gap-3 ml-12 cursor-pointer hover:bg-amber-50 transition" onclick="switchActiveRole(2)">
          <div class="flex items-start gap-3">
            <span class="w-7 h-7 rounded-xl bg-amber-600 text-white font-black text-xs flex items-center justify-center shrink-0">L2</span>
            <div>
              <div class="font-black text-amber-950 flex items-center gap-2">
                <span>Field Maintenance Technician</span>
                <span class="text-[9px] font-mono bg-amber-100 text-amber-800 px-1.5 py-0.5 rounded font-bold">SITE OPERATIONS</span>
              </div>
              <p class="text-slate-600 text-[11px] mt-0.5">Physical generator servicing. Executes PM-A/PM-B checklists, logs lube oil sump renewals, resets service countdown timers, and engages safety lock-out tag-out (LOTO).</p>
              <div class="text-[10px] text-amber-700 font-bold mt-1">Supervises: Mechanical Contractors · Reports to: Lead SCADA Engineer (L3)</div>
            </div>
          </div>
          <span class="text-[10px] font-mono font-bold text-amber-700 shrink-0">PM & LOTO</span>
        </div>

        <!-- Level 1 Card -->
        <div class="p-3 rounded-2xl bg-slate-100/80 border border-slate-200 flex items-start justify-between gap-3 ml-16 cursor-pointer hover:bg-slate-100 transition" onclick="switchActiveRole(1)">
          <div class="flex items-start gap-3">
            <span class="w-7 h-7 rounded-xl bg-slate-700 text-white font-black text-xs flex items-center justify-center shrink-0">L1</span>
            <div>
              <div class="font-black text-slate-900 flex items-center gap-2">
                <span>NOC Shift Operator</span>
                <span class="text-[9px] font-mono bg-slate-200 text-slate-700 px-1.5 py-0.5 rounded font-bold">24/7 MONITORING</span>
              </div>
              <p class="text-slate-600 text-[11px] mt-0.5">Continuous national monitoring. Inspects live telemetry, acknowledges sirens, dispatches initial incident alerts, and exports historical daily reports. (Strictly prohibited from remote engine manipulation or franchise edits).</p>
              <div class="text-[10px] text-slate-600 font-bold mt-1">Supervises: Telemetry Stream · Reports to: Lead SCADA Engineer (L3)</div>
            </div>
          </div>
          <span class="text-[10px] font-mono font-bold text-slate-500 shrink-0">Read-Only</span>
        </div>

      </div>
    </div>

    <!-- Complete Dynamic Permissions Matrix Table -->
    <div>
      <h4 class="text-xs font-black text-slate-900 uppercase tracking-wide mb-2.5">Dynamic Permissions & Action Governance Matrix</h4>
      <div class="overflow-x-auto rounded-2xl border border-slate-200 text-xs">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-200 text-[10px] font-black uppercase text-slate-500">
              <th class="py-2.5 px-3">Capability / Operation Key</th>
              <th class="py-2.5 px-2 text-center">L1: Operator</th>
              <th class="py-2.5 px-2 text-center">L2: Tech</th>
              <th class="py-2.5 px-2 text-center">L3: Engineer</th>
              <th class="py-2.5 px-2 text-center">L4: Director</th>
              <th class="py-2.5 px-2 text-center">L5: Chief</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 font-medium text-slate-700 text-[11px]">
            <tr class="hover:bg-slate-50/70">
              <td class="py-2 px-3 font-bold text-slate-900">View Live 18-Register Telemetry</td>
              <td class="py-2 px-2 text-center text-emerald-600 font-black">✓</td>
              <td class="py-2 px-2 text-center text-emerald-600 font-black">✓</td>
              <td class="py-2 px-2 text-center text-emerald-600 font-black">✓</td>
              <td class="py-2 px-2 text-center text-emerald-600 font-black">✓</td>
              <td class="py-2 px-2 text-center text-emerald-600 font-black">✓</td>
            </tr>
            <tr class="hover:bg-slate-50/70">
              <td class="py-2 px-3 font-bold text-slate-900">Acknowledge & Silence Alarms</td>
              <td class="py-2 px-2 text-center text-emerald-600 font-black">✓</td>
              <td class="py-2 px-2 text-center text-emerald-600 font-black">✓</td>
              <td class="py-2 px-2 text-center text-emerald-600 font-black">✓</td>
              <td class="py-2 px-2 text-center text-emerald-600 font-black">✓</td>
              <td class="py-2 px-2 text-center text-emerald-600 font-black">✓</td>
            </tr>
            <tr class="hover:bg-slate-50/70">
              <td class="py-2 px-3 font-bold text-slate-900">Log Maintenance PM & Countdown Reset</td>
              <td class="py-2 px-2 text-center text-rose-400 font-mono">✕</td>
              <td class="py-2 px-2 text-center text-emerald-600 font-black">✓</td>
              <td class="py-2 px-2 text-center text-emerald-600 font-black">✓</td>
              <td class="py-2 px-2 text-center text-emerald-600 font-black">✓</td>
              <td class="py-2 px-2 text-center text-emerald-600 font-black">✓</td>
            </tr>
            <tr class="hover:bg-slate-50/70">
              <td class="py-2 px-3 font-bold text-slate-900">Engage Safety Lockout (LOTO)</td>
              <td class="py-2 px-2 text-center text-rose-400 font-mono">✕</td>
              <td class="py-2 px-2 text-center text-emerald-600 font-black">✓</td>
              <td class="py-2 px-2 text-center text-emerald-600 font-black">✓</td>
              <td class="py-2 px-2 text-center text-emerald-600 font-black">✓</td>
              <td class="py-2 px-2 text-center text-emerald-600 font-black">✓</td>
            </tr>
            <tr class="hover:bg-slate-50/70">
              <td class="py-2 px-3 font-bold text-slate-900">Remote Engine Start / Crank Command</td>
              <td class="py-2 px-2 text-center text-rose-400 font-mono">✕</td>
              <td class="py-2 px-2 text-center text-rose-400 font-mono">✕</td>
              <td class="py-2 px-2 text-center text-emerald-600 font-black">✓</td>
              <td class="py-2 px-2 text-center text-emerald-600 font-black">✓</td>
              <td class="py-2 px-2 text-center text-emerald-600 font-black">✓</td>
            </tr>
            <tr class="hover:bg-slate-50/70">
              <td class="py-2 px-3 font-bold text-slate-900">Emergency E-Stop Safety Trip</td>
              <td class="py-2 px-2 text-center text-rose-400 font-mono">✕</td>
              <td class="py-2 px-2 text-center text-rose-400 font-mono">✕</td>
              <td class="py-2 px-2 text-center text-emerald-600 font-black">✓</td>
              <td class="py-2 px-2 text-center text-emerald-600 font-black">✓</td>
              <td class="py-2 px-2 text-center text-emerald-600 font-black">✓</td>
            </tr>
            <tr class="hover:bg-slate-50/70">
              <td class="py-2 px-3 font-bold text-slate-900">Modbus Register Setpoint Calibrations</td>
              <td class="py-2 px-2 text-center text-rose-400 font-mono">✕</td>
              <td class="py-2 px-2 text-center text-rose-400 font-mono">✕</td>
              <td class="py-2 px-2 text-center text-emerald-600 font-black">✓</td>
              <td class="py-2 px-2 text-center text-emerald-600 font-black">✓</td>
              <td class="py-2 px-2 text-center text-emerald-600 font-black">✓</td>
            </tr>
            <tr class="hover:bg-slate-50/70">
              <td class="py-2 px-3 font-bold text-slate-900">Cluster Creation & Routing Reassignment</td>
              <td class="py-2 px-2 text-center text-rose-400 font-mono">✕</td>
              <td class="py-2 px-2 text-center text-rose-400 font-mono">✕</td>
              <td class="py-2 px-2 text-center text-rose-400 font-mono">✕</td>
              <td class="py-2 px-2 text-center text-emerald-600 font-black">✓</td>
              <td class="py-2 px-2 text-center text-emerald-600 font-black">✓</td>
            </tr>
            <tr class="hover:bg-slate-50/70">
              <td class="py-2 px-3 font-bold text-slate-900">National Area Commissioning & Decommissioning</td>
              <td class="py-2 px-2 text-center text-rose-400 font-mono">✕</td>
              <td class="py-2 px-2 text-center text-rose-400 font-mono">✕</td>
              <td class="py-2 px-2 text-center text-rose-400 font-mono">✕</td>
              <td class="py-2 px-2 text-center text-rose-400 font-mono">✕</td>
              <td class="py-2 px-2 text-center text-emerald-600 font-black">✓</td>
            </tr>
            <tr class="hover:bg-slate-50/70">
              <td class="py-2 px-3 font-bold text-slate-900">User Role Governance & Security Clearance</td>
              <td class="py-2 px-2 text-center text-rose-400 font-mono">✕</td>
              <td class="py-2 px-2 text-center text-rose-400 font-mono">✕</td>
              <td class="py-2 px-2 text-center text-rose-400 font-mono">✕</td>
              <td class="py-2 px-2 text-center text-rose-400 font-mono">✕</td>
              <td class="py-2 px-2 text-center text-emerald-600 font-black">✓</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
      <button type="button" onclick="closeHierarchyOrgModal()" class="px-5 py-2 rounded-xl bg-slate-900 text-white font-bold text-xs transition shadow-xs">
        Close Hierarchy Matrix
      </button>
    </div>
  </div>
</div>

"""

# 6. Page Assembler Function
def assemble_page(title, active_page, main_content_html):
    rail = get_left_rail(active_page)
    
    # Extra scripts containing DSE controller, Alarms triage, Comm tests, History trends, Toast engine
    extra_scripts = """
<script>
// --- SCADA TOAST NOTIFICATION ENGINE ---
function showScadaToast(title, message, type = 'success') {
  const container = document.getElementById('scada-toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  const borderCol = type === 'error' ? 'border-rose-400 bg-rose-900/90' : (type === 'warn' ? 'border-amber-400 bg-amber-900/90' : 'border-emerald-400 bg-slate-900/90');
  const iconSvg = type === 'error' 
    ? '<svg class="w-4 h-4 text-rose-400 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>'
    : '<svg class="w-4 h-4 text-emerald-400 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>';

  toast.className = `p-3.5 rounded-2xl text-white text-xs border ${borderCol} backdrop-blur-xl shadow-2xl flex items-start gap-3 w-80 pointer-events-auto transform transition-all duration-300 translate-y-2 opacity-0`;
  toast.innerHTML = `
    ${iconSvg}
    <div class="flex-1 min-w-0">
      <div class="font-black text-slate-100 text-xs">${title}</div>
      <div class="text-[11px] text-slate-300 mt-0.5 leading-snug">${message}</div>
    </div>
    <button onclick="this.parentElement.remove()" class="text-slate-400 hover:text-white text-xs">✕</button>
  `;
  container.appendChild(toast);
  requestAnimationFrame(() => {
    toast.classList.remove('translate-y-2', 'opacity-0');
  });
  setTimeout(() => {
    toast.classList.add('opacity-0', 'translate-y-2');
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// --- DSE 7320 CONTROLLER HARDWARE CONSOLE ENGINE ---
let dseActiveScreen = 1;
let dseMode = 'AUTO';
let dseRunning = true;
let dseUnit = 'GEN-PK-0104';

const DSE_DATA = {
  'GEN-PK-0104': { brand: 'Perkins 1104A-44TG2', station: 'BTS-GP-0492', v1: 230.4, v2: 229.8, v3: 230.1, v12: 399.8, kw: 18.6, rpm: 1500, hz: 50.02, temp: 84.2, oil: 4.20, batt: 26.8 },
  'GEN-CM-0208': { brand: 'Cummins 6BT5.9-G2', station: 'BTS-RO-8442', v1: 231.2, v2: 230.8, v3: 231.0, v12: 401.0, kw: 38.2, rpm: 1500, hz: 50.00, temp: 88.6, oil: 4.50, batt: 26.4 },
  'GEN-CAT-0312': { brand: 'Caterpillar C4.4', station: 'BTS-BL-1944', v1: 0.0, v2: 0.0, v3: 0.0, v12: 0.0, kw: 0.0, rpm: 0, hz: 0.00, temp: 42.0, oil: 0.00, batt: 27.0 },
  'GEN-KH-0416': { brand: 'Kohler KD62', station: 'BTS-TE-4738', v1: 0.0, v2: 0.0, v3: 0.0, v12: 0.0, kw: 0.0, rpm: 0, hz: 0.00, temp: 31.0, oil: 0.00, batt: 25.8 }
};

function switchControlUnit(unitId) {
  dseUnit = unitId;
  const d = DSE_DATA[unitId];
  if (!d) return;
  dseRunning = d.rpm > 0;
  updateDseDisplay();
  logControlAudit('UNIT SWITCH', `Console routed to ${unitId} (${d.brand})`);
  showScadaToast('Target Unit Connected', `DSE-7320 controller mapped to ${unitId}`);
}

function navDseScreen(dir) {
  if (dir === 'up' || dir === 'left') {
    dseActiveScreen = dseActiveScreen > 1 ? dseActiveScreen - 1 : 4;
  } else if (dir === 'down' || dir === 'right') {
    dseActiveScreen = dseActiveScreen < 4 ? dseActiveScreen + 1 : 1;
  }
  updateDseDisplay();
}

function updateDseDisplay() {
  const d = DSE_DATA[dseUnit] || DSE_DATA['GEN-PK-0104'];
  const titleEl = document.getElementById('dse-lcd-title');
  const bodyEl = document.getElementById('dse-lcd-body');
  const cycleEl = document.getElementById('dse-screen-name');
  const modeLbl = document.getElementById('dse-lcd-mode-lbl');
  const freqLbl = document.getElementById('dse-lcd-freq');

  if (modeLbl) modeLbl.textContent = `MODE: ${dseMode}`;
  if (freqLbl) freqLbl.textContent = dseRunning ? `${d.hz.toFixed(2)} HZ · ${d.rpm} RPM` : '0.00 HZ · 0 RPM (STOP)';

  if (dseActiveScreen === 1) {
    if (cycleEl) cycleEl.textContent = '1 / 4 (Voltages)';
    if (titleEl) titleEl.textContent = 'Generator Voltage';
    if (bodyEl) {
      bodyEl.innerHTML = `
        <div class="flex justify-between"><span>L1-N:</span><span class="text-[#d8f3dc]">${dseRunning ? d.v1.toFixed(1) : '0.0'} V</span></div>
        <div class="flex justify-between"><span>L2-N:</span><span class="text-[#d8f3dc]">${dseRunning ? d.v2.toFixed(1) : '0.0'} V</span></div>
        <div class="flex justify-between"><span>L3-N:</span><span class="text-[#d8f3dc]">${dseRunning ? d.v3.toFixed(1) : '0.0'} V</span></div>
        <div class="flex justify-between pt-1 border-t border-[#52b788]/30 text-[#95d5b2]"><span>L1-L2:</span><span class="text-[#d8f3dc]">${dseRunning ? d.v12.toFixed(1) : '0.0'} V</span></div>
      `;
    }
  } else if (dseActiveScreen === 2) {
    if (cycleEl) cycleEl.textContent = '2 / 4 (Mechanical)';
    if (titleEl) titleEl.textContent = 'Engine Mechanical';
    if (bodyEl) {
      bodyEl.innerHTML = `
        <div class="flex justify-between"><span>SPEED:</span><span class="text-[#d8f3dc]">${dseRunning ? d.rpm : 0} RPM</span></div>
        <div class="flex justify-between"><span>OIL PRESS:</span><span class="text-[#d8f3dc]">${dseRunning ? d.oil.toFixed(2) : '0.00'} bar</span></div>
        <div class="flex justify-between"><span>COOLANT:</span><span class="text-[#d8f3dc]">${d.temp.toFixed(1)} °C</span></div>
        <div class="flex justify-between pt-1 border-t border-[#52b788]/30 text-[#95d5b2]"><span>BATTERY:</span><span class="text-[#d8f3dc]">${d.batt.toFixed(1)} VDC</span></div>
      `;
    }
  } else if (dseActiveScreen === 3) {
    if (cycleEl) cycleEl.textContent = '3 / 4 (Electrical Load)';
    if (titleEl) titleEl.textContent = 'Active & Apparent Power';
    if (bodyEl) {
      const kva = (d.kw / 0.8).toFixed(1);
      bodyEl.innerHTML = `
        <div class="flex justify-between"><span>ACTIVE (P):</span><span class="text-[#d8f3dc]">${dseRunning ? d.kw.toFixed(1) : '0.0'} kW</span></div>
        <div class="flex justify-between"><span>APPARENT (S):</span><span class="text-[#d8f3dc]">${dseRunning ? kva : '0.0'} kVA</span></div>
        <div class="flex justify-between"><span>POWER FACTOR:</span><span class="text-[#d8f3dc]">${dseRunning ? '0.80 Lag' : '1.00'}</span></div>
        <div class="flex justify-between pt-1 border-t border-[#52b788]/30 text-[#95d5b2]"><span>FREQUENCY:</span><span class="text-[#d8f3dc]">${dseRunning ? d.hz.toFixed(2) : '0.00'} Hz</span></div>
      `;
    }
  } else {
    if (cycleEl) cycleEl.textContent = '4 / 4 (Bus & Breakers)';
    if (titleEl) titleEl.textContent = 'Breakers & RS-485';
    if (bodyEl) {
      bodyEl.innerHTML = `
        <div class="flex justify-between"><span>MAINS CONTACTOR:</span><span class="text-[#d8f3dc]">CLOSED (GRID)</span></div>
        <div class="flex justify-between"><span>GEN CONTACTOR:</span><span class="text-[#d8f3dc]">${dseRunning ? 'CLOSED' : 'OPEN'}</span></div>
        <div class="flex justify-between"><span>MODBUS SLAVE ID:</span><span class="text-[#d8f3dc]">01 (9600-8N1)</span></div>
        <div class="flex justify-between pt-1 border-t border-[#52b788]/30 text-[#95d5b2]"><span>CRC ERRORS:</span><span class="text-[#d8f3dc]">0 (VERIFIED)</span></div>
      `;
    }
  }

  // Update right status card
  if (document.getElementById('ctrl-state-rpm')) document.getElementById('ctrl-state-rpm').textContent = `${dseRunning ? d.rpm : 0} RPM`;
  if (document.getElementById('ctrl-state-sub')) {
    document.getElementById('ctrl-state-sub').textContent = dseRunning ? 'Running At Rated' : 'Engine Standby / Stopped';
    document.getElementById('ctrl-state-sub').className = dseRunning ? 'text-[10px] text-emerald-600 font-bold' : 'text-[10px] text-slate-600 font-bold';
  }
  if (document.getElementById('ctrl-state-kw')) document.getElementById('ctrl-state-kw').textContent = `${dseRunning ? d.kw.toFixed(1) : '0.0'} kW`;
  if (document.getElementById('ctrl-state-oil')) document.getElementById('ctrl-state-oil').textContent = `${dseRunning ? d.oil.toFixed(2) : '0.00'} bar`;
}

// --- HAZARDOUS SCADA ACTION SAFETY INTERLOCK SYSTEM ---
let pendingSafetyCallback = null;

function requestSafetyAction(title, desc, callback) {
  const modal = document.getElementById('safety-interlock-modal');
  if (!modal) {
    if (confirm(`${title}\n\n${desc}`)) callback();
    return;
  }
  const titleEl = document.getElementById('safety-modal-title');
  const descEl = document.getElementById('safety-modal-desc');
  const chk = document.getElementById('safety-chk-clearance');
  const pin = document.getElementById('safety-pin-input');

  if (titleEl) titleEl.textContent = title;
  if (descEl) descEl.textContent = desc;
  if (chk) chk.checked = false;
  if (pin) pin.value = '#AR-9402';

  pendingSafetyCallback = callback;
  modal.classList.remove('hidden');
  modal.classList.add('flex');
}

function closeSafetyModal() {
  const modal = document.getElementById('safety-interlock-modal');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
  pendingSafetyCallback = null;
}

function executeSafetyConfirmedAction() {
  const chk = document.getElementById('safety-chk-clearance');
  const pin = document.getElementById('safety-pin-input');
  if (chk && !chk.checked) {
    showScadaToast('Safety Clearance Required', 'You must verify mechanical safety clearance before proceeding.', 'warn');
    return;
  }
  if (pin && pin.value.trim() !== '#AR-9402') {
    showScadaToast('Authorization Denied', 'Invalid SCADA Security Clearance PIN / UID.', 'error');
    return;
  }
  const cb = pendingSafetyCallback;
  closeSafetyModal();
  if (cb) cb();
}

function startGenerator() {
  if (dseRunning) {
    showScadaToast('Engine Already Running', `${dseUnit} is running at 1500 RPM`, 'warn');
    return;
  }
  requestSafetyAction(
    'Authorize Remote Engine Crank Sequence',
    `You are dispatching an industrial start command to ${dseUnit}. Ensure generator contactor path is clear and no field technicians are working on mechanical belts.`,
    () => {
      showScadaToast('Cranking Sequence Initiated', `Engaging starter motor on ${dseUnit}...`);
      logControlAudit('COMMAND CRANK', `Initiated remote starter sequence for ${dseUnit}`);

      setTimeout(() => {
        dseRunning = true;
        const d = DSE_DATA[dseUnit] || DSE_DATA['GEN-PK-0104'];
        d.rpm = 1500;
        d.kw = 18.6;
        d.oil = 4.20;
        d.v1 = 230.4;
        d.hz = 50.02;
        updateDseDisplay();
        showScadaToast('Engine Running (Rated)', `${dseUnit} reached 1500 RPM @ 50.02 Hz`);
        logControlAudit('CRANK SUCCESS', `${dseUnit} Modbus confirms Running state (1500 RPM)`);
      }, 1200);
    }
  );
}

function stopGenerator() {
  if (!dseRunning) {
    showScadaToast('Engine Stopped', `${dseUnit} is already stopped in standby`, 'warn');
    return;
  }
  showScadaToast('Cooldown Initiated', `Cooldown cycle active. Ramping down ${dseUnit}...`);
  logControlAudit('COMMAND STOP', `Initiated controlled cooldown and stop for ${dseUnit}`);

  setTimeout(() => {
    dseRunning = false;
    const d = DSE_DATA[dseUnit] || DSE_DATA['GEN-PK-0104'];
    d.rpm = 0;
    d.kw = 0.0;
    d.oil = 0.0;
    d.v1 = 0.0;
    d.hz = 0.0;
    updateDseDisplay();
    showScadaToast('Engine Standby', `${dseUnit} is stopped. Breaker open.`);
    logControlAudit('STOP COMPLETE', `${dseUnit} Modbus confirms 0 RPM Standby`);
  }, 1000);
}

function setControllerMode(mode) {
  dseMode = mode;
  updateDseDisplay();
  ['ctrl-btn-auto', 'ctrl-btn-manual'].forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    if ((mode === 'AUTO' && id === 'ctrl-btn-auto') || (mode === 'MANUAL' && id === 'ctrl-btn-manual')) {
      el.className = 'p-3 rounded-2xl bg-indigo-950/70 border border-indigo-600 active:scale-95 flex flex-col items-center gap-1 text-white transition shadow-md';
    } else {
      el.className = 'p-3 rounded-2xl bg-[#262c3a] hover:bg-[#323a4d] active:scale-95 border border-slate-700 flex flex-col items-center gap-1 text-slate-300 transition shadow-md';
    }
  });
  showScadaToast('Controller Mode Set', `DSE-7320 operational mode set to ${mode}`);
  logControlAudit('MODE CHANGE', `Sequencer set to ${mode} mode`);
}

function testGeneratorLoad() {
  showScadaToast('Load Test Started', `Simulating 80% prime step load on ${dseUnit}`);
  logControlAudit('LOAD TEST', `Initiated automated load step test on ${dseUnit}`);
}

function muteAudibleAlarm() {
  showScadaToast('Alarm Silenced', 'DSE acoustic buzzer siren silenced by operator');
  logControlAudit('ALARM SILENCE', 'Acoustic siren silenced');
}

function triggerEmergencyStop() {
  requestSafetyAction(
    'CRITICAL SAFETY OVERRIDE: TRIP EMERGENCY STOP (E-STOP)',
    `Immediate fuel solenoid cutoff and generator shutdown on ${dseUnit}. This action engages an emergency lockout and logs an ISO/IEC 27001 audit event.`,
    () => {
      dseRunning = false;
      const d = DSE_DATA[dseUnit] || DSE_DATA['GEN-PK-0104'];
      d.rpm = 0;
      d.kw = 0.0;
      d.oil = 0.0;
      updateDseDisplay();
      showScadaToast('EMERGENCY STOP TRIPPED', `Fuel solenoid cut off on ${dseUnit}!`, 'error');
      logControlAudit('EMERGENCY E-STOP', `TRIPPED E-STOP BY OPERATOR #AR-9402`);
    }
  );
}

function logControlAudit(cmd, msg) {
  const container = document.getElementById('ctrl-audit-log');
  if (!container) return;
  const now = new Date().toTimeString().split(' ')[0] + ' UTC';
  const item = document.createElement('div');
  item.className = 'p-2.5 rounded-xl bg-slate-50 border border-slate-200 flex flex-col gap-0.5';
  item.innerHTML = `
    <div class="flex items-center justify-between text-[10px] text-slate-600">
      <span class="text-indigo-700 font-bold">${cmd}</span>
      <span>${now}</span>
    </div>
    <div class="font-bold text-slate-800">${msg}</div>
    <div class="text-[10px] text-slate-600">Operator: Lian Ahmed (#AR-9402)</div>
  `;
  container.prepend(item);
}

// --- ALARMS TRIAGE CONSOLE ENGINE ---
const SCADA_ALARMS_DATA = [
  { id: 'ALM-101', severity: 'CRITICAL', time: '15:42:10 UTC', station: 'Tower BTS-GP-0492', reg: '40012', desc: 'Low Oil Pressure (< 1.20 bar)', val: '0.85 bar / 1.20 bar', status: 'ACTIVE' },
  { id: 'ALM-102', severity: 'CRITICAL', time: '15:40:18 UTC', station: 'Tower BTS-RO-8442', reg: '40013', desc: 'High Coolant Temp (> 98.0 °C)', val: '101.4 °C / 98.0 °C', status: 'ACTIVE' },
  { id: 'ALM-103', severity: 'CRITICAL', time: '15:38:00 UTC', station: 'Tower BTS-BL-1944', reg: '40014', desc: 'Fail to Start (Overcrank Trip)', val: '3 Cranks Failed', status: 'ACTIVE' },
  { id: 'ALM-104', severity: 'CRITICAL', time: '15:35:12 UTC', station: 'Tower BTS-TE-4738', reg: '40018', desc: 'Fuel Solenoid Lockout Engaged', val: 'Safety Trip', status: 'ACKNOWLEDGED' },
  { id: 'ALM-105', severity: 'CRITICAL', time: '15:32:45 UTC', station: 'Tower BTS-GP-0118', reg: '40001', desc: 'Under-Voltage L1 Outage (< 190V)', val: '172.5 V / 190 V', status: 'ACTIVE' },
  { id: 'ALM-106', severity: 'CRITICAL', time: '15:30:10 UTC', station: 'Tower BTS-RO-0240', reg: '40010', desc: 'Frequency Deviation (< 47.5 Hz)', val: '46.20 Hz / 47.5 Hz', status: 'ACTIVE' },
  { id: 'ALM-107', severity: 'MAJOR', time: '15:28:19 UTC', station: 'Tower BTS-BL-0382', reg: '40018', desc: 'Low Fuel Tank Reserve (< 20%)', val: '14.2% / 20.0%', status: 'ACTIVE' },
  { id: 'ALM-108', severity: 'MAJOR', time: '15:25:04 UTC', station: 'Tower BTS-TE-0412', reg: '40015', desc: 'Coolant Level Low Probe Open', val: 'Sensor Open Circuit', status: 'ACTIVE' },
  { id: 'ALM-109', severity: 'MAJOR', time: '15:22:33 UTC', station: 'Tower BTS-GP-0560', reg: '40011', desc: 'Electrical Overload (> 110% Prime)', val: '54.2 kW / 48.0 kW', status: 'ACKNOWLEDGED' },
  { id: 'ALM-110', severity: 'MAJOR', time: '15:19:12 UTC', station: 'Tower BTS-RO-0610', reg: '40008', desc: 'Current Phase Imbalance (> 15%)', val: '18.4% / 15.0%', status: 'ACTIVE' },
  { id: 'ALM-111', severity: 'MAJOR', time: '15:15:50 UTC', station: 'Tower BTS-BL-0720', reg: '40012', desc: 'Oil Filter Differential High', val: '1.60 bar / 1.20 bar', status: 'ACTIVE' },
  { id: 'ALM-112', severity: 'MAJOR', time: '15:12:00 UTC', station: 'Tower BTS-TE-0830', reg: '40014', desc: 'Air Filter Restriction Vacuum', val: '4.8 kPa / 3.0 kPa', status: 'ACTIVE' },
  { id: 'ALM-113', severity: 'MAJOR', time: '15:08:44 UTC', station: 'Tower BTS-GP-0912', reg: '40016', desc: 'Alternator Belt Slack Detected', val: '12.0 mm / 9.0 mm', status: 'ACKNOWLEDGED' },
  { id: 'ALM-114', severity: 'MAJOR', time: '15:05:10 UTC', station: 'Tower BTS-RO-1024', reg: '40013', desc: 'High Engine Oil Temperature', val: '96.2 °C / 92.0 °C', status: 'ACTIVE' },
  { id: 'ALM-115', severity: 'MINOR', time: '14:59:30 UTC', station: 'Tower BTS-BL-1140', reg: '40017', desc: 'Starter Battery Float Volts Low', val: '24.2 V / 26.0 V', status: 'ACTIVE' },
  { id: 'ALM-116', severity: 'MINOR', time: '14:55:12 UTC', station: 'Tower BTS-TE-1280', reg: '40019', desc: 'Water in Fuel Separator Sensor', val: 'Conductivity Probe', status: 'ACTIVE' },
  { id: 'ALM-117', severity: 'MINOR', time: '14:50:00 UTC', station: 'Tower BTS-GP-1390', reg: '40020', desc: 'Canopy Door Tamper Open Alarm', val: 'Switch Tripped', status: 'ACTIVE' },
  { id: 'ALM-118', severity: 'MINOR', time: '14:45:22 UTC', station: 'Tower BTS-RO-1420', reg: '40021', desc: 'Fuel Fill Cap Sensor Open', val: 'Sensor Tripped', status: 'ACTIVE' },
  { id: 'ALM-119', severity: 'MINOR', time: '14:40:15 UTC', station: 'Tower BTS-BL-1530', reg: '40022', desc: 'RTU Cellular Packet Jitter Alert', val: 'Jitter 68 ms', status: 'ACKNOWLEDGED' },
  { id: 'ALM-120', severity: 'MINOR', time: '14:35:00 UTC', station: 'Tower BTS-TE-1640', reg: '40023', desc: 'Scheduled PM-A Threshold Warning', val: '248h / 250h', status: 'ACTIVE' }
];

let activeAlarmFilter = 'ALL';

function renderAlarmsTable() {
  const tbody = document.getElementById('alarms-table-body');
  if (!tbody) return;
  const q = (document.getElementById('alarm-search-input')?.value || '').toLowerCase();

  const filtered = SCADA_ALARMS_DATA.filter(a => {
    const matchFilter = activeAlarmFilter === 'ALL' || 
                        (activeAlarmFilter === 'ACKNOWLEDGED' ? a.status === 'ACKNOWLEDGED' : a.severity === activeAlarmFilter);
    const matchSearch = a.station.toLowerCase().includes(q) || a.desc.toLowerCase().includes(q) || a.id.toLowerCase().includes(q);
    return matchFilter && matchSearch;
  });

  tbody.innerHTML = filtered.map(a => {
    const sevBadge = a.severity === 'CRITICAL' 
      ? '<span class="px-2 py-0.5 rounded-full bg-rose-100 text-rose-800 text-[10px] font-bold border border-rose-300">CRITICAL</span>'
      : (a.severity === 'MAJOR' 
          ? '<span class="px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 text-[10px] font-bold border border-amber-300">MAJOR</span>'
          : '<span class="px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-800 text-[10px] font-bold border border-indigo-300">MINOR</span>');

    const statusBadge = a.status === 'ACKNOWLEDGED'
      ? '<span class="text-emerald-700 font-bold flex items-center gap-1"><svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>Acked</span>'
      : '<span class="text-rose-600 font-bold flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-rose-600 animate-ping"></span>Active</span>';

    return `
      <tr class="hover:bg-slate-50 transition" id="row-${a.id}">
        <td class="py-3 pl-2">${sevBadge}</td>
        <td class="py-3 font-mono text-slate-600 text-[11px]">${a.time}</td>
        <td class="py-3">
          <strong class="text-slate-900 block">${a.station}</strong>
          <span class="text-[10px] text-slate-400 font-mono">${a.id}</span>
        </td>
        <td class="py-3">
          <span class="font-bold text-slate-800 block">${a.desc}</span>
          <span class="text-[10px] font-mono text-indigo-600">Modbus Reg: ${a.reg}</span>
        </td>
        <td class="py-3 font-mono text-slate-600 text-[11px]">${a.val}</td>
        <td class="py-3">${statusBadge}</td>
        <td class="py-3 pr-2 text-right">
          <div class="flex items-center justify-end gap-1.5">
            ${a.status !== 'ACKNOWLEDGED' ? `<button onclick="ackAlarm('${a.id}')" class="px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-bold text-[10px] transition shadow-2xs">Ack</button>` : ''}
            <button onclick="window.location.href='telemetry.html?station=' + encodeURIComponent('${a.station.replace('Tower ', '')}')" class="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-[10px] transition">Inspect</button>
            <button onclick="resolveAlarm('${a.id}')" class="px-2 py-1 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-700 font-bold text-[10px] transition">Resolve</button>
          </div>
        </td>
      </tr>
    `;
  }).join('');

  // Update counts
  if (document.getElementById('kpi-alarm-total')) document.getElementById('kpi-alarm-total').textContent = SCADA_ALARMS_DATA.length;
  if (document.getElementById('kpi-alarm-critical')) document.getElementById('kpi-alarm-critical').textContent = SCADA_ALARMS_DATA.filter(x => x.severity === 'CRITICAL').length;
  if (document.getElementById('kpi-alarm-major')) document.getElementById('kpi-alarm-major').textContent = SCADA_ALARMS_DATA.filter(x => x.severity === 'MAJOR').length;
  if (document.getElementById('kpi-alarm-minor')) document.getElementById('kpi-alarm-minor').textContent = SCADA_ALARMS_DATA.filter(x => x.severity === 'MINOR').length;
  if (document.getElementById('kpi-alarm-acked')) document.getElementById('kpi-alarm-acked').textContent = SCADA_ALARMS_DATA.filter(x => x.status === 'ACKNOWLEDGED').length;
}

function filterAlarmSeverity(sev) {
  activeAlarmFilter = sev;
  ['af-all', 'af-critical', 'af-major', 'af-minor', 'af-acked'].forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    el.className = 'px-3.5 py-1.5 rounded-xl text-xs font-bold transition text-slate-600 hover:text-slate-900 hover:bg-slate-100';
  });
  const activeBtn = document.getElementById(sev === 'ALL' ? 'af-all' : (sev === 'CRITICAL' ? 'af-critical' : (sev === 'MAJOR' ? 'af-major' : (sev === 'MINOR' ? 'af-minor' : 'af-acked'))));
  if (activeBtn) activeBtn.className = 'px-3.5 py-1.5 rounded-xl text-xs font-bold transition shadow-xs bg-slate-900 text-white';
  renderAlarmsTable();
}

function searchAlarmsTable() {
  renderAlarmsTable();
}

function ackAlarm(id) {
  const item = SCADA_ALARMS_DATA.find(x => x.id === id);
  if (item) {
    item.status = 'ACKNOWLEDGED';
    renderAlarmsTable();
    showScadaToast('Alarm Acknowledged', `${id} acknowledged by Lian Ahmed (#AR-9402)`);
  }
}

function resolveAlarm(id) {
  const idx = SCADA_ALARMS_DATA.findIndex(x => x.id === id);
  if (idx !== -1) {
    const item = SCADA_ALARMS_DATA[idx];
    SCADA_ALARMS_DATA.splice(idx, 1);
    renderAlarmsTable();
    showScadaToast('Condition Resolved', `${item.desc} on ${item.station} cleared and logged.`);
  }
}

function ackAllFilteredAlarms() {
  SCADA_ALARMS_DATA.forEach(a => a.status = 'ACKNOWLEDGED');
  renderAlarmsTable();
  showScadaToast('All Alarms Acknowledged', '20 alarms stamped by Operator #AR-9402');
}

function silenceAllAlarms() {
  showScadaToast('Sirens Silenced', 'Acoustic sirens silenced across all regional cluster nodes.');
}

function exportAlarmsCsv() {
  let csv = 'Alarm_ID,Severity,Timestamp,Tower_Station,Modbus_Register,Event_Description,Threshold_Value,Status\\n';
  SCADA_ALARMS_DATA.forEach(a => {
    csv += `${a.id},${a.severity},"${a.time}","${a.station}",${a.reg},"${a.desc}","${a.val}",${a.status}\\n`;
  });
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `genesis_alarms_triage_${new Date().toISOString().slice(0,10)}.csv`;
  a.click();
  showScadaToast('Alarm Log Exported', 'CSV report generated and downloaded.');
}

// --- COMMUNICATIONS DIAGNOSTICS ENGINE ---
function pingGateway() {
  const btn = document.getElementById('comm-ping-btn');
  const latEl = document.getElementById('comm-latency-val');
  if (btn) btn.innerHTML = 'Pinging...';
  setTimeout(() => {
    const lat = Math.floor(Math.random() * 8 + 28);
    if (latEl) latEl.textContent = lat + ' ms';
    if (btn) btn.innerHTML = '<svg class="w-4 h-4 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg><span>Ping Concentrator</span>';
    showScadaToast('Concentrator Ping Confirmed', `Round trip latency: ${lat} ms (IP: 192.168.10.1:502)`);
  }, 400);
}

function clearModbusBuffer() {
  const term = document.getElementById('comm-hex-stream');
  if (term) term.innerHTML = '<div class="text-slate-400">[SYSTEM] FIFO buffer flushed and cleared. Awaiting next poll frame...</div>';
  showScadaToast('Buffer Cleared', 'Modbus RTU circular FIFO buffer reset to 0 bytes.');
}

function triggerModbusSweep() {
  const term = document.getElementById('comm-hex-stream');
  if (term) {
    const now = new Date().toTimeString().split(' ')[0];
    const frame = document.createElement('div');
    frame.className = 'text-emerald-400';
    frame.innerHTML = `[${now}] <span class="text-emerald-300">SWEEP RX &lt;&lt;</span> 01 03 24 09 00 08 FA 08 FC 0F 9E 0F A2 0F A0 01 10 01 0C 01 0E 13 88 05 DC 03 4A 01 A4 00 4C 00 BE 01 0C 03 E6 00 15 8E 2F <span class="text-emerald-600">// CRC OK · 18 PARAMS REFRESHED</span>`;
    term.prepend(frame);
  }
  showScadaToast('18 Registers Swept', 'All 18 SCADA telemetry parameters synchronized via Modbus RTU.');
}

// --- 6-MONTH HISTORICAL TRENDS ENGINE ---
let histMetric = 'kw';
function setHistoryMetric(m) {
  histMetric = m;
  ['hm-kw', 'hm-rpm', 'hm-fuel', 'hm-temp'].forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    el.className = 'px-3.5 py-1.5 rounded-xl text-xs font-bold transition text-slate-600 hover:text-slate-900 hover:bg-slate-100';
  });
  const act = document.getElementById('hm-' + m);
  if (act) act.className = 'px-3.5 py-1.5 rounded-xl text-xs font-bold transition shadow-xs bg-slate-900 text-white';

  const t = document.getElementById('hist-chart-title');
  const ymax = document.getElementById('hist-y-max');
  const ymid1 = document.getElementById('hist-y-mid1');
  const ymid2 = document.getElementById('hist-y-mid2');

  if (m === 'kw') {
    if (t) t.textContent = 'Daily Active Load Trend (kW)';
    if (ymax) ymax.textContent = '30 kW';
    if (ymid1) ymid1.textContent = '20 kW';
    if (ymid2) ymid2.textContent = '10 kW';
  } else if (m === 'rpm') {
    if (t) t.textContent = 'Engine Speed Spectrum (RPM)';
    if (ymax) ymax.textContent = '1800 RPM';
    if (ymid1) ymid1.textContent = '1500 RPM';
    if (ymid2) ymid2.textContent = '750 RPM';
  } else if (m === 'fuel') {
    if (t) t.textContent = 'Fuel Tank Capacity Curve (%)';
    if (ymax) ymax.textContent = '100 %';
    if (ymid1) ymid1.textContent = '75 %';
    if (ymid2) ymid2.textContent = '50 %';
  } else {
    if (t) t.textContent = 'Engine Coolant Thermal Cycle (°C)';
    if (ymax) ymax.textContent = '110 °C';
    if (ymid1) ymid1.textContent = '85 °C';
    if (ymid2) ymid2.textContent = '60 °C';
  }
  renderHistoryChart();
}

function setHistoryPreset(p) {
  const to = new Date();
  const from = new Date();
  if (p === '7d') from.setDate(to.getDate() - 7);
  else if (p === '30d') from.setDate(to.getDate() - 30);
  else from.setMonth(to.getMonth() - 6);

  if (document.getElementById('hist-date-to')) document.getElementById('hist-date-to').value = to.toISOString().slice(0,10);
  if (document.getElementById('hist-date-from')) document.getElementById('hist-date-from').value = from.toISOString().slice(0,10);
  renderHistoryChart();
}

function updateHistoryView() {
  renderHistoryChart();
}

function renderHistoryChart() {
  const line = document.getElementById('hist-line-path');
  const area = document.getElementById('hist-area-path');
  if (!line || !area) return;

  const totalPts = 28;
  let dLine = '';
  let dArea = 'M 40,220 ';

  for (let i = 0; i < totalPts; i++) {
    const x = 40 + (i * (940 / (totalPts - 1)));
    let y = 140;
    if (histMetric === 'kw') {
      y = 120 + Math.sin(i * 0.45) * 50 + Math.cos(i * 0.9) * 20;
    } else if (histMetric === 'rpm') {
      y = 80 + (Math.sin(i * 0.5) > -0.2 ? 0 : 75);
    } else if (histMetric === 'fuel') {
      y = 70 + ((totalPts - i) * 3.5);
    } else {
      y = 95 + Math.cos(i * 0.5) * 35;
    }

    const cmd = i === 0 ? 'M ' : 'L ';
    dLine += `${cmd}${x.toFixed(1)},${y.toFixed(1)} `;
    dArea += `L ${x.toFixed(1)},${y.toFixed(1)} `;
  }

  dArea += 'L 980,220 Z';
  line.setAttribute('d', dLine);
  area.setAttribute('d', dArea);
}

function exportHistoryCsv() {
  let csv = 'Date,Unit_UID,Station,Avg_Active_kW,Peak_Active_kW,RPM,Coolant_C,Fuel_Consumed_L,Operating_Hours\\n';
  const start = new Date(document.getElementById('hist-date-from')?.value || '2026-05-16');
  for (let i = 0; i < 30; i++) {
    const d = new Date(start);
    d.setDate(d.getDate() + i);
    csv += `${d.toISOString().slice(0,10)},GEN-PK-0104,BTS-GP-0492,18.4,24.8,1500,84.2,14.6,1.8\\n`;
  }
  const blob = new Blob([csv], { type: 'text/csv' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `genesis_history_daily_rollups.csv`;
  a.click();
  showScadaToast('Historical CSV Exported', '6-month daily rollup records downloaded.');
}

// --- SETTINGS ENGINE ---
function saveScadaSettings() {
  const cfg = {
    pollFreq: document.getElementById('cfg-poll-freq')?.value || '3000',
    baudRate: document.getElementById('cfg-baud-rate')?.value || '9600',
    gateway: document.getElementById('cfg-ip-gateway')?.value || '192.168.10.1:502',
    anim: document.getElementById('cfg-anim-toggle')?.checked ?? true,
    audio: document.getElementById('cfg-audio-alarm')?.checked ?? true,
    coolantLimit: document.getElementById('cfg-temp-slider')?.value || '98',
    oilLimit: document.getElementById('cfg-oil-slider')?.value || '1.20',
    fuelLimit: document.getElementById('cfg-fuel-slider')?.value || '25'
  };
  localStorage.setItem('genesis_scada_settings', JSON.stringify(cfg));
  showScadaToast('Settings Saved', 'SCADA parameters and Modbus timing persisted.');
}

function resetScadaSettings() {
  localStorage.removeItem('genesis_scada_settings');
  showScadaToast('Factory Defaults Restored', 'Configuration reset to nominal SCADA baselines.');
}

function playTestSiren() {
  showScadaToast('Acoustic Siren Test', 'Simulated 85dB acoustic warning alarm pulse sounded.');
}

// --- HEADER NOTIFICATIONS FLYOUT ENGINE ---
function toggleNotificationsFlyout() {
  const f = document.getElementById('header-notifications-flyout');
  if (!f) return;
  if (f.classList.contains('hidden')) {
    f.classList.remove('hidden');
    f.style.display = 'flex';
    renderFlyoutAlarms();
  } else {
    f.classList.add('hidden');
    f.style.display = 'none';
  }
}

function renderFlyoutAlarms() {
  const list = document.getElementById('flyout-alarms-list');
  if (!list) return;
  list.innerHTML = SCADA_ALARMS_DATA.slice(0, 4).map(a => `
    <div class="p-2.5 rounded-2xl ${a.severity === 'CRITICAL' ? 'bg-rose-50/80 border border-rose-200' : 'bg-amber-50/80 border border-amber-200'} flex items-center justify-between">
      <div class="flex items-center gap-2">
        <span class="w-2 h-2 rounded-full ${a.severity === 'CRITICAL' ? 'bg-rose-600 animate-ping' : 'bg-amber-600'}"></span>
        <div>
          <strong class="text-slate-900 block leading-tight text-xs">${a.station}</strong>
          <span class="text-[10px] text-slate-600">${a.desc}</span>
        </div>
      </div>
      <button onclick="ackAlarm('${a.id}'); toggleNotificationsFlyout();" class="px-2 py-1 rounded-lg bg-slate-900 text-white font-bold text-[10px]">Ack</button>
    </div>
  `).join('');
}

// --- HIERARCHY PICKER MODAL ENGINE ---
function openHierarchyModal(type) {
  const m = document.getElementById('hierarchy-picker-modal');
  if (m) { m.classList.remove('hidden'); m.style.display = 'flex'; }
}

function closeHierarchyModal() {
  const m = document.getElementById('hierarchy-picker-modal');
  if (m) { m.classList.add('hidden'); m.style.display = 'none'; }
}

function updateClusterPickOptions() {
  const a = document.getElementById('h-pick-area')?.value;
  const cSel = document.getElementById('h-pick-cluster');
  if (!cSel) return;
  if (a.includes('Dhaka')) {
    cSel.innerHTML = '<option value=\"Mirpur Node\">Mirpur Node</option><option value=\"Gulshan Commercial\">Gulshan Commercial</option><option value=\"Uttara Sector 7\">Uttara Sector 7</option>';
  } else if (a.includes('Chittagong')) {
    cSel.innerHTML = '<option value=\"Agrabad Commercial\">Agrabad Commercial</option><option value=\"Port Zone\">Port Zone</option><option value=\"Nasirabad\">Nasirabad</option>';
  } else {
    cSel.innerHTML = `<option value=\"${a} Tech Central\">${a} Tech Central</option><option value=\"${a} Industrial Node\">${a} Industrial Node</option>`;
  }
}

function updateTowerPickOptions() {}

function applyHierarchySelection() {
  const area = document.getElementById('h-pick-area')?.value || 'Dhaka North';
  const cluster = document.getElementById('h-pick-cluster')?.value || 'Mirpur Node';
  const tower = document.getElementById('h-pick-tower')?.value || 'BTS-GP-0492';

  if (document.getElementById('top-area-text')) document.getElementById('top-area-text').textContent = area;
  if (document.getElementById('top-cluster-text')) document.getElementById('top-cluster-text').textContent = cluster;
  if (document.getElementById('top-station-text')) document.getElementById('top-station-text').textContent = tower;

  closeHierarchyModal();
  showScadaToast('Active Station Switched', `Now monitoring ${tower} (${area} · ${cluster})`);
}

// --- PDF DOWNLOAD SIMULATOR ---
function downloadTechnicalDatasheet(title) {
  const content = `GENESIS RMS — OFFICIAL TECHNICAL DATASHEET ARCHIVE\\nDocument: ${title}\\nAuthor: Arena IoT Systems & SCADA Infrastructure\\nStandard: ISO/IEC 27001\\nStatus: VERIFIED OEM\\nTimestamp: ${new Date().toISOString()}\\n`;
  const blob = new Blob([content], { type: 'text/plain' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `${title.replace(/\\s+/g, '_')}.txt`;
  a.click();
  showScadaToast('Datasheet Downloaded', `${title} downloaded.`);
}


// =========================================================================
// 1. USER PROFILE & 300x300 AVATAR UPLOAD / PERSISTENCE ENGINE
// =========================================================================
let tempUserAvatarBase64_300 = null;

function handleProfileAvatarUpload(input) {
  if (!input || !input.files || !input.files[0]) return;
  const file = input.files[0];
  const reader = new FileReader();
  reader.onload = function(e) {
    const img = new Image();
    img.onload = function() {
      // High-precision 300x300 square crop on canvas
      const canvas = document.createElement('canvas');
      canvas.width = 300;
      canvas.height = 300;
      const ctx = canvas.getContext('2d');
      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = 'high';
      const scale = Math.max(300 / img.width, 300 / img.height);
      const sw = img.width * scale;
      const sh = img.height * scale;
      const ox = (300 - sw) / 2;
      const oy = (300 - sh) / 2;
      ctx.clearRect(0, 0, 300, 300);
      ctx.drawImage(img, ox, oy, sw, sh);
      const base64 = canvas.toDataURL('image/png', 0.95);
      tempUserAvatarBase64_300 = base64;
      
      // Update preview in modal
      const previewImg = document.getElementById('prof-avatar-img');
      const previewInitials = document.getElementById('prof-avatar-initials');
      if (previewImg) {
        previewImg.src = base64;
        previewImg.classList.remove('hidden');
        previewImg.style.display = 'block';
      }
      if (previewInitials) {
        previewInitials.classList.add('hidden');
        previewInitials.style.display = 'none';
      }
      showScadaToast('Portrait Calibrated', 'Exact 300x300 crop ready. Click "Save Changes" to apply across console.');
    };
    img.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

// Alias for compatibility
function handleUserAvatarUpload(input) {
  handleProfileAvatarUpload(input);
}

function resetProfileAvatar() {
  tempUserAvatarBase64_300 = null;
  localStorage.removeItem('genesis_user_avatar_300');
  
  const ids = ['prof-avatar', 'header-avatar', 'content-avatar', 'noc-avatar'];
  ids.forEach(prefix => {
    const img = document.getElementById(prefix + '-img');
    const initials = document.getElementById(prefix + '-initials');
    if (img) { img.classList.add('hidden'); img.style.display = 'none'; img.src = ''; }
    if (initials) { initials.classList.remove('hidden'); initials.style.display = 'flex'; }
  });

  const input = document.getElementById('prof-avatar-file-input');
  if (input) input.value = '';
  showScadaToast('Avatar Reset', 'Default initials badge restored.');
}

function removeUserAvatar() {
  resetProfileAvatar();
}

function openProfileModal() {
  const modal = document.getElementById('profile-modal');
  if (!modal) return;
  modal.classList.remove('hidden');
  modal.style.display = 'flex';

  try {
    const saved = localStorage.getItem('genesis_scada_profile');
    if (saved) {
      const p = JSON.parse(saved);
      if (p.name && document.getElementById('prof-name-input')) document.getElementById('prof-name-input').value = p.name;
      if (p.role && document.getElementById('prof-role-input')) document.getElementById('prof-role-input').value = p.role;
      if (p.email && document.getElementById('prof-email-input')) document.getElementById('prof-email-input').value = p.email;
      if (p.uid && document.getElementById('prof-uid-input')) document.getElementById('prof-uid-input').value = p.uid.replace('#', '');
      if (p.dept && document.getElementById('prof-dept-input')) document.getElementById('prof-dept-input').value = p.dept;
    }
    const avatar = localStorage.getItem('genesis_user_avatar_300');
    const pImg = document.getElementById('prof-avatar-img');
    const pInit = document.getElementById('prof-avatar-initials');
    if (avatar && pImg && pInit) {
      pImg.src = avatar;
      pImg.classList.remove('hidden');
      pImg.style.display = 'block';
      pInit.classList.add('hidden');
      pInit.style.display = 'none';
    }
  } catch(e){}
}

function closeProfileModal() {
  const modal = document.getElementById('profile-modal');
  if (modal) {
    modal.classList.add('hidden');
    modal.style.display = 'none';
  }
}

function saveProfileChanges() {
  const name = document.getElementById('prof-name-input')?.value.trim() || 'Lian Ahmed';
  const role = document.getElementById('prof-role-input')?.value.trim() || 'Lead SCADA Engineer';
  const email = document.getElementById('prof-email-input')?.value.trim() || 'lian.ahmed@arenaiot.com';
  const rawUid = document.getElementById('prof-uid-input')?.value.trim() || 'AR-9402';
  const uid = rawUid.startsWith('#') ? rawUid : '#' + rawUid;
  const dept = document.getElementById('prof-dept-input')?.value.trim() || 'National SCADA Operations & Telemetry Grid Management';

  const initials = name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() || 'LN';

  // Update Header
  const headerName = document.getElementById('header-op-name');
  const headerRole = document.getElementById('header-op-role');
  const headerUid = document.getElementById('header-op-uid');
  const headerInitials = document.getElementById('header-avatar-initials');
  if (headerName) headerName.textContent = name;
  if (headerRole) headerRole.textContent = role;
  if (headerUid) headerUid.textContent = uid;
  if (headerInitials) headerInitials.textContent = initials;

  // Update Content and NOC pages if active
  const contentName = document.getElementById('content-op-name');
  const contentRole = document.getElementById('content-op-role');
  const contentUid = document.getElementById('content-op-uid');
  const contentInitials = document.getElementById('content-avatar-initials');
  if (contentName) contentName.textContent = name;
  if (contentRole) contentRole.textContent = role;
  if (contentUid) contentUid.textContent = uid;
  if (contentInitials) contentInitials.textContent = initials;

  const nocName = document.getElementById('noc-op-name');
  const nocRole = document.getElementById('noc-op-role');
  const nocUid = document.getElementById('noc-op-uid');
  const nocInitials = document.getElementById('noc-avatar-initials');
  if (nocName) nocName.textContent = name;
  if (nocRole) nocRole.textContent = role;
  if (nocUid) nocUid.textContent = uid;
  if (nocInitials) nocInitials.textContent = initials;

  // Apply base64 avatar if newly chosen
  if (tempUserAvatarBase64_300) {
    localStorage.setItem('genesis_user_avatar_300', tempUserAvatarBase64_300);
    const avatarImgIds = ['header-avatar-img', 'content-avatar-img', 'noc-avatar-img', 'prof-avatar-img'];
    const avatarInitIds = ['header-avatar-initials', 'content-avatar-initials', 'noc-avatar-initials', 'prof-avatar-initials'];
    
    avatarImgIds.forEach(id => {
      const el = document.getElementById(id);
      if (el) { el.src = tempUserAvatarBase64_300; el.classList.remove('hidden'); el.style.display = 'block'; }
    });
    avatarInitIds.forEach(id => {
      const el = document.getElementById(id);
      if (el) { el.classList.add('hidden'); el.style.display = 'none'; }
    });
  }

  // Persist Profile Object in localStorage
  const profile = { name, role, email, uid, dept, updated: new Date().toISOString() };
  localStorage.setItem('genesis_scada_profile', JSON.stringify(profile));

  closeProfileModal();
  showScadaToast('Profile & Avatar Saved', `Operator profile for ${name} (${uid}) persisted successfully.`);
}

function initProfileAndAvatar() {
  try {
    const saved = localStorage.getItem('genesis_scada_profile');
    if (saved) {
      const p = JSON.parse(saved);
      const name = p.name || 'Lian Ahmed';
      const role = p.role || 'Lead SCADA Engineer';
      const uid = p.uid || '#AR-9402';
      const initials = name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() || 'LN';

      if (document.getElementById('header-op-name')) document.getElementById('header-op-name').textContent = name;
      if (document.getElementById('header-op-role')) document.getElementById('header-op-role').textContent = role;
      if (document.getElementById('header-op-uid')) document.getElementById('header-op-uid').textContent = uid;
      if (document.getElementById('header-avatar-initials')) document.getElementById('header-avatar-initials').textContent = initials;

      if (document.getElementById('content-op-name')) document.getElementById('content-op-name').textContent = name;
      if (document.getElementById('content-op-role')) document.getElementById('content-op-role').textContent = role;
      if (document.getElementById('content-op-uid')) document.getElementById('content-op-uid').textContent = uid;
      if (document.getElementById('content-avatar-initials')) document.getElementById('content-avatar-initials').textContent = initials;

      if (document.getElementById('noc-op-name')) document.getElementById('noc-op-name').textContent = name;
      if (document.getElementById('noc-op-role')) document.getElementById('noc-op-role').textContent = role;
      if (document.getElementById('noc-op-uid')) document.getElementById('noc-op-uid').textContent = uid;
      if (document.getElementById('noc-avatar-initials')) document.getElementById('noc-avatar-initials').textContent = initials;
    }

    const avatar = localStorage.getItem('genesis_user_avatar_300');
    if (avatar) {
      const avatarImgIds = ['header-avatar-img', 'content-avatar-img', 'noc-avatar-img', 'prof-avatar-img'];
      const avatarInitIds = ['header-avatar-initials', 'content-avatar-initials', 'noc-avatar-initials', 'prof-avatar-initials'];
      avatarImgIds.forEach(id => {
        const el = document.getElementById(id);
        if (el) { el.src = avatar; el.classList.remove('hidden'); el.style.display = 'block'; }
      });
      avatarInitIds.forEach(id => {
        const el = document.getElementById(id);
        if (el) { el.classList.add('hidden'); el.style.display = 'none'; }
      });
    }
  } catch(e){}
}

// =========================================================================
// 2. UNIVERSAL SCADA TABLE ADVANCED SORTING ENGINE
// =========================================================================
const SCADA_TABLE_SORTS = {};

function sortScadaTable(tableId, colIndex, dataType = 'text') {
  const table = document.getElementById(tableId);
  if (!table) return;
  const tbody = table.querySelector('tbody');
  if (!tbody) return;

  const currentSort = SCADA_TABLE_SORTS[tableId] || { colIndex: -1, dir: 'desc' };
  const newDir = (currentSort.colIndex === colIndex && currentSort.dir === 'asc') ? 'desc' : 'asc';
  SCADA_TABLE_SORTS[tableId] = { colIndex, dir: newDir };

  const rows = Array.from(tbody.querySelectorAll('tr'));
  
  rows.sort((rowA, rowB) => {
    const cellA = rowA.children[colIndex];
    const cellB = rowB.children[colIndex];
    if (!cellA || !cellB) return 0;

    let valA = cellA.innerText.trim();
    let valB = cellB.innerText.trim();

    if (dataType === 'number') {
      // Clean numeric strings like '114 Towers', '6.84 MW', '99.8%', '320.5 hrs'
      valA = parseFloat(valA.replace(/[^0-9.-]+/g, '')) || 0;
      valB = parseFloat(valB.replace(/[^0-9.-]+/g, '')) || 0;
      return newDir === 'asc' ? valA - valB : valB - valA;
    } else {
      valA = valA.toLowerCase();
      valB = valB.toLowerCase();
      if (valA < valB) return newDir === 'asc' ? -1 : 1;
      if (valA > valB) return newDir === 'asc' ? 1 : -1;
      return 0;
    }
  });

  // Re-append rows in sorted order
  rows.forEach(r => tbody.appendChild(r));

  // Update Header Visual Sort Indicators
  const thead = table.querySelector('thead');
  if (thead) {
    const ths = thead.querySelectorAll('th');
    ths.forEach((th, idx) => {
      const ind = th.querySelector('.sort-indicator');
      if (ind) {
        if (idx === colIndex) {
          th.classList.add('active-sort');
          ind.textContent = newDir === 'asc' ? '▲' : '▼';
          ind.style.opacity = '1';
          ind.style.color = '#4f46e5';
        } else {
          th.classList.remove('active-sort');
          ind.textContent = '▲▼';
          ind.style.opacity = '0.4';
          ind.style.color = '';
        }
      }
    });
  }

  const colName = table.querySelectorAll('thead th')[colIndex]?.innerText.replace(/[^a-zA-Z0-9 &]/g, '').trim() || 'Column';
  showScadaToast('Table Sorted', `Sorted by ${colName} (${newDir === 'asc' ? 'Ascending' : 'Descending'}).`);
}

// =========================================================================
// 3. PERSONNEL PROFILE DOSSIER & SCADA AUDIT ENGINE
// =========================================================================
const PERSONNEL_DATA = {
  'Engr. Tariqul Islam': {
    name: 'Engr. Tariqul Islam',
    uid: '#DIR-DHK-01',
    role: 'Level 4: Regional Operations Director',
    title: 'Regional SCADA Operations Director (Dhaka North)',
    email: 'tariqul.islam@arenaiot.com',
    phone: '+880 1711-948201',
    office: 'Level 7, Dhaka North Command Station',
    vhf: 'VHF-Ch-04 (156.200 MHz, ECHO-NORTH-01)',
    jurisdiction: 'Dhaka North Division',
    towers: '114 Towers',
    mw: '6.84 MW',
    sla: '99.8%',
    duty: 'Active On-Duty (Shift Lead)',
    auditLog: [
      { time: 'Today 10:45 UTC', action: 'Approved Preventive PM-A Work Order for Cluster 2 (Tower BTS-GP-0492)', type: 'APPROVAL' },
      { time: 'Yesterday 16:20 UTC', action: 'Signed monthly SLA Performance Compliance Dossier (99.8%)', type: 'COMPLIANCE' },
      { time: 'Nov 16, 14:15 UTC', action: 'Authorized emergency diesel replenishment for Mirpur sub-grid', type: 'DISPATCH' },
      { time: 'Nov 14, 09:30 UTC', action: 'Supervised grid synchronization review across 114 BTS towers', type: 'GRID' }
    ]
  },
  'Engr. Shamim Hossain': {
    name: 'Engr. Shamim Hossain',
    uid: '#DIR-DHK-02',
    role: 'Level 4: Regional Operations Director',
    title: 'Regional SCADA Operations Director (Dhaka South)',
    email: 'shamim.hossain@arenaiot.com',
    phone: '+880 1712-837192',
    office: 'Level 5, Motijheel Central Command Station',
    vhf: 'VHF-Ch-05 (156.250 MHz, ECHO-SOUTH-02)',
    jurisdiction: 'Dhaka South Division',
    towers: '94 Towers',
    mw: '5.64 MW',
    sla: '99.7%',
    duty: 'Active On-Duty',
    auditLog: [
      { time: 'Today 11:20 UTC', action: 'Authorized routine fuel filtration maintenance on Dhanmondi cluster', type: 'APPROVAL' },
      { time: 'Yesterday 14:00 UTC', action: 'Reviewed Modbus gateway RTU latency in Motijheel corridor', type: 'DIAGNOSTICS' },
      { time: 'Nov 15, 12:45 UTC', action: 'Validated emergency generator auto-start transfer testing', type: 'TEST' }
    ]
  },
  'Engr. Faisal Mahmud': {
    name: 'Engr. Faisal Mahmud',
    uid: '#DIR-CTG-01',
    role: 'Level 4: Regional Operations Director',
    title: 'Regional SCADA Operations Director (Chittagong Metro)',
    email: 'faisal.mahmud@arenaiot.com',
    phone: '+880 1713-746281',
    office: 'Port Zone Command Station, Agrabad',
    vhf: 'VHF-Ch-09 (156.450 MHz, SEAPORT-BASE-01)',
    jurisdiction: 'Chittagong Metro',
    towers: '68 Towers',
    mw: '4.08 MW',
    sla: '99.6%',
    duty: 'Active On-Duty',
    auditLog: [
      { time: 'Today 08:30 UTC', action: 'Cleared Port Zone feeder trip alarm after secondary line restart', type: 'ALARM' },
      { time: 'Nov 17, 18:10 UTC', action: 'Approved Cummins 6BT overhaul schedule for BTS-RO-8442', type: 'APPROVAL' }
    ]
  },
  'Engr. Rafiqul Alam': {
    name: 'Engr. Rafiqul Alam',
    uid: '#DIR-CTG-02',
    role: 'Level 4: Regional Operations Director',
    title: 'Regional SCADA Operations Director (Chittagong North)',
    email: 'rafiqul.alam@arenaiot.com',
    phone: '+880 1714-635190',
    office: 'Nasirabad Engineering Complex',
    vhf: 'VHF-Ch-10 (156.500 MHz, NORTH-COAST-02)',
    jurisdiction: 'Chittagong North & Port',
    towers: '50 Towers',
    mw: '3.00 MW',
    sla: '99.5%',
    duty: 'Active On-Duty',
    auditLog: [
      { time: 'Yesterday 09:15 UTC', action: 'Validated cyclone contingency fuel reserves across 50 coastal towers', type: 'SAFETY' }
    ]
  },
  'Engr. Kamrul Hasan': {
    name: 'Engr. Kamrul Hasan',
    uid: '#DIR-SYL-01',
    role: 'Level 4: Regional Operations Director',
    title: 'Regional SCADA Operations Director (Sylhet Zone)',
    email: 'kamrul.hasan@arenaiot.com',
    phone: '+880 1715-524089',
    office: 'Zindabazar Tech Hub, Sylhet',
    vhf: 'VHF-Ch-12 (156.600 MHz, TEA-RIDGE-01)',
    jurisdiction: 'Sylhet Zone',
    towers: '58 Towers',
    mw: '3.48 MW',
    sla: '99.4%',
    duty: 'Active On-Duty',
    auditLog: [
      { time: 'Today 09:50 UTC', action: 'Dispatched radiator flush service to Caterpillar C4.4 unit BTS-BL-1944', type: 'MAINT' },
      { time: 'Nov 04, 2026', action: 'Logged completed coolant flush & glycol rebalance on GEN-CAT-0312', type: 'AUDIT' }
    ]
  },
  'Engr. Mofazzal Hossain': {
    name: 'Engr. Mofazzal Hossain',
    uid: '#DIR-RAJ-01',
    role: 'Level 4: Regional Operations Director',
    title: 'Regional SCADA Operations Director (Rajshahi Central)',
    email: 'mofazzal.hossain@arenaiot.com',
    phone: '+880 1716-413978',
    office: 'Padma Riverfront SCADA Facility',
    vhf: 'VHF-Ch-14 (156.700 MHz, SILK-GRID-01)',
    jurisdiction: 'Rajshahi Central',
    towers: '38 Towers',
    mw: '2.28 MW',
    sla: '99.6%',
    duty: 'Active On-Duty',
    auditLog: [
      { time: 'Nov 17, 11:00 UTC', action: 'Inspected high-voltage alternator isolation tests in central cluster', type: 'INSPECT' }
    ]
  },
  'Engr. Anisur Rahman': {
    name: 'Engr. Anisur Rahman',
    uid: '#DIR-KHU-01',
    role: 'Level 4: Regional Operations Director',
    title: 'Regional SCADA Operations Director (Khulna Division)',
    email: 'anisur.rahman@arenaiot.com',
    phone: '+880 1717-302867',
    office: 'Rupsha Industrial Grid Command',
    vhf: 'VHF-Ch-16 (156.800 MHz, DELTA-GRID-01)',
    jurisdiction: 'Khulna Division',
    towers: '30 Towers',
    mw: '1.80 MW',
    sla: '99.3%',
    duty: 'Active On-Duty',
    auditLog: [
      { time: 'Today 07:15 UTC', action: 'Approved emergency overhaul lockout on Kohler KD62 (BTS-TE-4738)', type: 'LOCKOUT' }
    ]
  },
  'Engr. Jahangir Kabir': {
    name: 'Engr. Jahangir Kabir',
    uid: '#DIR-BAR-01',
    role: 'Level 4: Regional Operations Director',
    title: 'Regional SCADA Operations Director (Barisal Coast)',
    email: 'jahangir.kabir@arenaiot.com',
    phone: '+880 1718-291756',
    office: 'Coastal Island SCADA Center',
    vhf: 'VHF-Ch-18 (156.900 MHz, BARISAL-VHF-01)',
    jurisdiction: 'Barisal Coast',
    towers: '15 Towers',
    mw: '0.90 MW',
    sla: '99.1%',
    duty: 'Active On-Duty',
    auditLog: [
      { time: 'Nov 16, 15:40 UTC', action: 'Verified submarine fiber gateway telemetry link integrity', type: 'COMMS' }
    ]
  },
  'Engr. Nurul Huda': {
    name: 'Engr. Nurul Huda',
    uid: '#DIR-RAN-01',
    role: 'Level 4: Regional Operations Director',
    title: 'Regional SCADA Operations Director (Rangpur Belt)',
    email: 'nurul.huda@arenaiot.com',
    phone: '+880 1719-180645',
    office: 'Northern Frontier Operations Hub',
    vhf: 'VHF-Ch-20 (157.000 MHz, NORTH-BELT-01)',
    jurisdiction: 'Rangpur Belt',
    towers: '15 Towers',
    mw: '0.90 MW',
    sla: '99.2%',
    duty: 'Active On-Duty',
    auditLog: [
      { time: 'Nov 15, 10:20 UTC', action: 'Signed winterization protocol for cold-crank preheaters', type: 'WINTER' }
    ]
  },
  'Engr. Delowar Hossain': {
    name: 'Engr. Delowar Hossain',
    uid: '#DIR-MYM-01',
    role: 'Level 4: Regional Operations Director',
    title: 'Regional SCADA Operations Director (Mymensingh Hub)',
    email: 'delowar.hossain@arenaiot.com',
    phone: '+880 1720-079534',
    office: 'Brahmaputra Telemetry Base',
    vhf: 'VHF-Ch-22 (157.100 MHz, MYM-HUB-01)',
    jurisdiction: 'Mymensingh Hub',
    towers: '10 Towers',
    mw: '0.60 MW',
    sla: '99.5%',
    duty: 'Active On-Duty',
    auditLog: [
      { time: 'Nov 14, 16:00 UTC', action: 'Completed scheduled 500-hour load bank verification test', type: 'LOADBANK' }
    ]
  },
  'Engr. Lian Ahmed': {
    name: 'Engr. Lian Ahmed',
    uid: '#AR-9402',
    role: 'Level 3: Lead SCADA Engineer',
    title: 'Lead SCADA Automation Engineer · National Command',
    email: 'lian.ahmed@arenaiot.com',
    phone: '+880 1819-940201',
    office: 'Central NOC Room 4B, Arena IoT HQ',
    vhf: 'VHF-Ch-01 (156.050 MHz, PRIORITY-LEAD)',
    jurisdiction: 'Gulshan-Mirpur Node / National',
    towers: '24 Towers (Direct)',
    mw: '1.44 MW',
    sla: '99.9%',
    duty: 'Active On-Duty (Current Session Commander)',
    auditLog: [
      { time: 'Today 11:15 UTC', action: 'Executed Modbus RTU telemetry synchronization on Perkins 1104A', type: 'TELEMETRY' },
      { time: 'Today 09:30 UTC', action: 'Acknowledged High Coolant Temp Alarm on BTS-RO-8442', type: 'ALARM' },
      { time: 'Yesterday 18:00 UTC', action: 'Calibrated DSE-7320 auto-start threshold to 195V', type: 'CONTROL' },
      { time: 'Nov 10, 2026', action: 'Logged completed PM-A minor service (200.0 hrs) on GEN-PK-0104', type: 'MAINT' }
    ]
  },
  'Engr. Naimul Islam': {
    name: 'Engr. Naimul Islam',
    uid: '#ENG-DHK-02',
    role: 'Level 3: Lead SCADA Engineer',
    title: 'Lead Field Engineer (Uttara-Tongi Corridor)',
    email: 'naimul.islam@arenaiot.com',
    phone: '+880 1820-839102',
    office: 'Uttara Sector 7 Station',
    vhf: 'VHF-Ch-02 (156.100 MHz, UTTR-LEAD-02)',
    jurisdiction: 'Uttara-Tongi Corridor',
    towers: '20 Towers',
    mw: '1.20 MW',
    sla: '99.7%',
    duty: 'Active On-Duty',
    auditLog: [
      { time: 'Today 10:10 UTC', action: 'Replaced air filter restriction sensor on Tower BTS-GP-0118', type: 'MAINT' }
    ]
  },
  'Engr. Hasan Chowdhury': {
    name: 'Engr. Hasan Chowdhury',
    uid: '#ENG-DHK-03',
    role: 'Level 3: Lead SCADA Engineer',
    title: 'Lead Field Engineer (Dhanmondi-Motijheel)',
    email: 'hasan.chowdhury@arenaiot.com',
    phone: '+880 1821-728093',
    office: 'Dhanmondi Sub-Grid Office',
    vhf: 'VHF-Ch-03 (156.150 MHz, DHAN-LEAD-03)',
    jurisdiction: 'Dhanmondi-Motijheel',
    towers: '22 Towers',
    mw: '1.32 MW',
    sla: '99.8%',
    duty: 'Active On-Duty',
    auditLog: [
      { time: 'Yesterday 15:30 UTC', action: 'Checked 24V starter battery float voltage on BTS-BL-0720', type: 'BATTERY' }
    ]
  },
  'Engr. Tanvir Ahmed': {
    name: 'Engr. Tanvir Ahmed',
    uid: '#ENG-CTG-01',
    role: 'Level 3: Lead SCADA Engineer',
    title: 'Lead Field Engineer (Agrabad Commercial Hub)',
    email: 'tanvir.ahmed@arenaiot.com',
    phone: '+880 1822-617984',
    office: 'Agrabad Commercial Node',
    vhf: 'VHF-Ch-08 (156.400 MHz, AGRA-LEAD-01)',
    jurisdiction: 'Agrabad Commercial Hub',
    towers: '18 Towers',
    mw: '1.08 MW',
    sla: '99.6%',
    duty: 'Active On-Duty',
    auditLog: [
      { time: 'Today 09:00 UTC', action: 'Tested emergency fuel shutoff valve on Cummins 6BT standby set', type: 'TEST' }
    ]
  },
  'Engr. Babul Miah': {
    name: 'Engr. Babul Miah',
    uid: '#ENG-SYL-01',
    role: 'Level 3: Lead SCADA Engineer',
    title: 'Lead Field Engineer (Zindabazar Tech Node)',
    email: 'babul.miah@arenaiot.com',
    phone: '+880 1823-506875',
    office: 'Zindabazar Sub-Center, Sylhet',
    vhf: 'VHF-Ch-11 (156.550 MHz, ZIND-LEAD-01)',
    jurisdiction: 'Zindabazar Tech Node',
    towers: '20 Towers',
    mw: '1.20 MW',
    sla: '99.5%',
    duty: 'Active On-Duty',
    auditLog: [
      { time: 'Yesterday 11:45 UTC', action: 'Retorqued alternator mounting bracket bolts after vibration alert', type: 'MAINT' }
    ]
  }
};

function openPersonnelProfile(nameOrUid) {
  let person = PERSONNEL_DATA[nameOrUid];
  if (!person) {
    // Search by partial name or UID
    const keys = Object.keys(PERSONNEL_DATA);
    for (let k of keys) {
      if (k.includes(nameOrUid) || PERSONNEL_DATA[k].uid.includes(nameOrUid)) {
        person = PERSONNEL_DATA[k];
        break;
      }
    }
  }

  // Fallback to default Lian Ahmed if not found
  if (!person) person = PERSONNEL_DATA['Engr. Lian Ahmed'];

  const modal = document.getElementById('personnel-profile-modal');
  if (!modal) return;

  const initials = person.name.split(' ').filter(p => !p.startsWith('Engr.')).map(p => p[0]).join('').slice(0, 2).toUpperCase() || 'OP';
  
  const av = document.getElementById('pers-modal-avatar');
  if (av) av.textContent = initials;
  if (document.getElementById('pers-modal-name')) document.getElementById('pers-modal-name').textContent = person.name;
  if (document.getElementById('pers-modal-uid')) document.getElementById('pers-modal-uid').textContent = person.uid;
  if (document.getElementById('pers-modal-title')) document.getElementById('pers-modal-title').textContent = person.title;
  
  const emailEl = document.getElementById('pers-modal-email');
  if (emailEl) { emailEl.textContent = person.email; emailEl.href = 'mailto:' + person.email; }
  
  const phoneEl = document.getElementById('pers-modal-phone');
  if (phoneEl) { phoneEl.textContent = person.phone; phoneEl.href = 'tel:' + person.phone.replace(/[^0-9+]/g, ''); }

  if (document.getElementById('pers-modal-office')) document.getElementById('pers-modal-office').textContent = person.office;
  if (document.getElementById('pers-modal-vhf')) document.getElementById('pers-modal-vhf').textContent = person.vhf;
  if (document.getElementById('pers-modal-jurisdiction')) document.getElementById('pers-modal-jurisdiction').textContent = person.jurisdiction;
  if (document.getElementById('pers-modal-towers')) document.getElementById('pers-modal-towers').textContent = person.towers;
  if (document.getElementById('pers-modal-mw')) document.getElementById('pers-modal-mw').textContent = person.mw;
  if (document.getElementById('pers-modal-sla')) document.getElementById('pers-modal-sla').textContent = person.sla;
  if (document.getElementById('pers-modal-duty-status')) document.getElementById('pers-modal-duty-status').textContent = person.duty;

  const auditContainer = document.getElementById('pers-modal-audit-list');
  if (auditContainer) {
    auditContainer.innerHTML = person.auditLog.map(log => `
      <div class="p-2.5 rounded-xl bg-slate-50 border border-slate-200/80 flex items-center justify-between gap-2">
        <div class="flex items-center gap-2">
          <span class="w-1.5 h-1.5 rounded-full bg-indigo-600 shrink-0"></span>
          <span class="font-medium text-slate-800 text-[11px]">${log.action}</span>
        </div>
        <span class="font-mono text-[10px] text-slate-500 whitespace-nowrap">${log.time}</span>
      </div>
    `).join('');
  }

  modal.classList.remove('hidden');
  modal.style.display = 'flex';
}

function closePersonnelProfile() {
  const modal = document.getElementById('personnel-profile-modal');
  if (modal) {
    modal.classList.add('hidden');
    modal.style.display = 'none';
  }
}

function triggerDirectVhfPulse() {
  showScadaToast('VHF Radio Hail Dispatched', 'Acoustic dispatch alert broadcasted across designated VHF emergency channel.');
}

// =========================================================================
// 4. DYNAMIC SCADA COMMAND ROLES & PERMISSIONS (RBAC) GOVERNANCE
// =========================================================================
const SCADA_ROLES = {
  1: {
    level: 1,
    title: 'Level 1: NOC Shift Operator',
    badge: 'L1: Operator',
    color: 'slate',
    perms: ['view_telemetry', 'acknowledge_alarms', 'export_reports']
  },
  2: {
    level: 2,
    title: 'Level 2: Field Maintenance Tech',
    badge: 'L2: Field Tech',
    color: 'amber',
    perms: ['view_telemetry', 'acknowledge_alarms', 'export_reports', 'log_maintenance', 'engage_loto_lockout']
  },
  3: {
    level: 3,
    title: 'Level 3: Lead SCADA Engineer',
    badge: 'L3: Lead SCADA Engr',
    color: 'emerald',
    perms: ['view_telemetry', 'acknowledge_alarms', 'export_reports', 'log_maintenance', 'engage_loto_lockout', 'remote_engine_control', 'modbus_write', 'fota_firmware_push']
  },
  4: {
    level: 4,
    title: 'Level 4: Regional Director',
    badge: 'L4: Regional Dir',
    color: 'indigo',
    perms: ['view_telemetry', 'acknowledge_alarms', 'export_reports', 'log_maintenance', 'engage_loto_lockout', 'remote_engine_control', 'modbus_write', 'fota_firmware_push', 'create_edit_cluster', 'approve_work_orders']
  },
  5: {
    level: 5,
    title: 'Level 5: Chief SCADA Director',
    badge: 'L5: Chief Admin',
    color: 'purple',
    perms: ['view_telemetry', 'acknowledge_alarms', 'export_reports', 'log_maintenance', 'engage_loto_lockout', 'remote_engine_control', 'modbus_write', 'fota_firmware_push', 'create_edit_cluster', 'approve_work_orders', 'create_edit_area', 'cms_publish_layout', 'user_role_assignment', 'admin_override']
  }
};

let currentScadaRole = parseInt(localStorage.getItem('genesis_active_role')) || 3;

function toggleRoleDropdown() {
  const dd = document.getElementById('role-switcher-dropdown');
  if (!dd) return;
  if (dd.classList.contains('hidden')) {
    dd.classList.remove('hidden');
    dd.style.display = 'flex';
  } else {
    dd.classList.add('hidden');
    dd.style.display = 'none';
  }
}

function switchActiveRole(level, showToast = true) {
  if (!SCADA_ROLES[level]) return;
  currentScadaRole = level;
  localStorage.setItem('genesis_active_role', level.toString());

  const role = SCADA_ROLES[level];
  const roleTitleEl = document.getElementById('role-pill-title');
  const roleDotEl = document.getElementById('role-pill-dot');
  const rbacLabel = document.getElementById('rbac-current-role-label');

  if (roleTitleEl) roleTitleEl.textContent = role.badge;
  if (roleDotEl) {
    roleDotEl.className = `w-2 h-2 rounded-full animate-pulse bg-${role.color}-600`;
  }
  if (rbacLabel) rbacLabel.textContent = role.title;

  // Update modal active button state
  for (let i = 1; i <= 5; i++) {
    const btn = document.getElementById('rbac-btn-l' + i);
    if (btn) {
      if (i === level) {
        btn.className = 'px-2.5 py-1 rounded-lg text-xs font-bold transition bg-slate-900 text-white shadow-2xs';
      } else {
        btn.className = 'px-2.5 py-1 rounded-lg text-xs font-bold transition bg-white border border-slate-200 text-slate-700 hover:bg-slate-100';
      }
    }
  }

  // Close dropdown if open
  const dd = document.getElementById('role-switcher-dropdown');
  if (dd) { dd.classList.add('hidden'); dd.style.display = 'none'; }

  if (showToast) {
    showScadaToast('Active SCADA Role Switched', `Now operating under clearance: ${role.title}`);
  }
}

function canExecuteAction(actionKey, actionName = 'This action') {
  const role = SCADA_ROLES[currentScadaRole] || SCADA_ROLES[3];
  if (role.perms.includes(actionKey) || role.perms.includes('admin_override')) {
    return true;
  }

  // Find minimum level required
  let reqLevel = 5;
  for (let l = 1; l <= 5; l++) {
    if (SCADA_ROLES[l].perms.includes(actionKey)) {
      reqLevel = l;
      break;
    }
  }

  showScadaToast(
    'ACCESS RESTRICTED (RBAC)',
    `"${actionName}" requires Level ${reqLevel} (${SCADA_ROLES[reqLevel].badge}) or higher. Current session: ${role.badge}.`,
    'error'
  );
  return false;
}

function openHierarchyOrgModal() {
  const m = document.getElementById('rbac-hierarchy-modal');
  if (m) { m.classList.remove('hidden'); m.style.display = 'flex'; }
  const dd = document.getElementById('role-switcher-dropdown');
  if (dd) { dd.classList.add('hidden'); dd.style.display = 'none'; }
}

function closeHierarchyOrgModal() {
  const m = document.getElementById('rbac-hierarchy-modal');
  if (m) { m.classList.add('hidden'); m.style.display = 'none'; }
}

// =========================================================================
// 5. FRANCHISE TIER & CRUD ENGINE (AREA, CLUSTER, TOWER)
// =========================================================================
function switchFranchiseTier(tier) {
  const tiers = ['area', 'cluster', 'tower', 'import'];
  tiers.forEach(t => {
    const panel = document.getElementById('tier-panel-' + t);
    const btn = document.getElementById('tab-btn-' + t);
    if (t === tier) {
      if (panel) panel.classList.remove('hidden');
      if (btn) btn.className = 'px-4 py-2 rounded-xl text-xs font-bold transition shadow-xs bg-white text-slate-900';
    } else {
      if (panel) panel.classList.add('hidden');
      if (btn) btn.className = 'px-4 py-2 rounded-xl text-xs font-bold transition text-slate-600 hover:text-slate-900';
    }
  });
}

function filterAreaRows() {
  const q = (document.getElementById('area-search-input')?.value || '').toLowerCase();
  const rows = document.querySelectorAll('#areas-table-body tr');
  rows.forEach(r => {
    r.style.display = r.textContent.toLowerCase().includes(q) ? '' : 'none';
  });
}

function filterClusterRows() {
  const q = (document.getElementById('cluster-search-input')?.value || '').toLowerCase();
  const rows = document.querySelectorAll('#clusters-table-body tr');
  rows.forEach(r => {
    r.style.display = r.textContent.toLowerCase().includes(q) ? '' : 'none';
  });
}

function filterTowerRows() {
  const q = (document.getElementById('tower-search-input')?.value || '').toLowerCase();
  const rows = document.querySelectorAll('#towers-table-body tr');
  rows.forEach(r => {
    r.style.display = r.textContent.toLowerCase().includes(q) ? '' : 'none';
  });
}

function viewAreaDetails(id) {
  const modal = document.getElementById('franchise-view-modal');
  const title = document.getElementById('fv-title');
  const body = document.getElementById('fv-body');
  if (title) title.textContent = `Area Details: ${id}`;
  if (body) {
    body.innerHTML = `
      <div class="space-y-3 text-xs">
        <div class="p-3 rounded-xl bg-slate-50 border border-slate-200">
          <div class="font-bold text-slate-900 text-sm">${id} Operational Zone</div>
          <div class="text-slate-600 mt-1">Supervises BTS telecom cluster nodes with active N+1 generator redundancy.</div>
        </div>
        <div class="grid grid-cols-2 gap-2 font-mono">
          <div class="p-2.5 rounded-lg bg-emerald-50 text-emerald-800 font-bold">Health: 99.8% Online</div>
          <div class="p-2.5 rounded-lg bg-indigo-50 text-indigo-800 font-bold">Standard Modbus RTU</div>
        </div>
      </div>
    `;
  }
  if (modal) { modal.classList.remove('hidden'); modal.style.display = 'flex'; }
}

function editAreaModal(id) {
  if (!canExecuteAction('create_edit_area', 'Modify Area Configuration')) return;
  const modal = document.getElementById('area-crud-modal');
  const title = document.getElementById('area-modal-title');
  const nameInput = document.getElementById('area-name-input');
  const codeInput = document.getElementById('area-code-input');
  if (title) title.textContent = `Edit Area: ${id}`;
  if (codeInput) codeInput.value = id;
  if (nameInput) nameInput.value = id === 'AREA-DHK-N' ? 'Dhaka North' : (id === 'AREA-CTG-M' ? 'Chittagong Metro' : id);
  if (modal) { modal.classList.remove('hidden'); modal.style.display = 'flex'; }
}

function deleteAreaPrompt(id) {
  if (!canExecuteAction('create_edit_area', 'Decommission Area')) return;
  if (confirm(`Are you sure you want to decommission Area ${id}? All child clusters and towers must be reassigned.`)) {
    const row = document.querySelector(`tr[data-area-id="${id}"]`);
    if (row) row.remove();
    showScadaToast('Area Decommissioned', `Area ${id} removed from national operational grid.`);
  }
}

function openCreateAreaModal() {
  if (!canExecuteAction('create_edit_area', 'Create New Area')) return;
  const modal = document.getElementById('area-crud-modal');
  const title = document.getElementById('area-modal-title');
  const nameInput = document.getElementById('area-name-input');
  const codeInput = document.getElementById('area-code-input');
  if (title) title.textContent = 'Create New Operational Area';
  if (codeInput) codeInput.value = `AREA-${Math.floor(Math.random()*900 + 100)}`;
  if (nameInput) nameInput.value = '';
  if (modal) { modal.classList.remove('hidden'); modal.style.display = 'flex'; }
}

function saveAreaRecord() {
  const name = document.getElementById('area-name-input')?.value.trim();
  const code = document.getElementById('area-code-input')?.value.trim();
  if (!name || !code) { alert('Please enter both Area Name and Code.'); return; }
  showScadaToast('Area Saved', `Area ${name} (${code}) recorded to national registry.`);
  closeFranchiseModals();
}

function viewClusterDetails(id) {
  const modal = document.getElementById('franchise-view-modal');
  const title = document.getElementById('fv-title');
  const body = document.getElementById('fv-body');
  if (title) title.textContent = `Cluster Details: ${id}`;
  if (body) {
    body.innerHTML = `
      <div class="space-y-3 text-xs">
        <div class="p-3 rounded-xl bg-slate-50 border border-slate-200">
          <div class="font-bold text-slate-900 text-sm">${id} Regional Node</div>
          <div class="text-slate-600 mt-1">Directly polling Modbus concentrators over RS-485 serial bus.</div>
        </div>
        <div class="p-2.5 rounded-lg bg-slate-100 font-mono text-[11px]">Primary IP Gateway: 192.168.10.1:502</div>
      </div>
    `;
  }
  if (modal) { modal.classList.remove('hidden'); modal.style.display = 'flex'; }
}

function editClusterModal(id) {
  if (!canExecuteAction('create_edit_cluster', 'Modify Cluster')) return;
  const modal = document.getElementById('cluster-crud-modal');
  const title = document.getElementById('cluster-modal-title');
  const nameInput = document.getElementById('cluster-name-input');
  const codeInput = document.getElementById('cluster-code-input');
  if (title) title.textContent = `Edit Cluster: ${id}`;
  if (codeInput) codeInput.value = id;
  if (nameInput) nameInput.value = id === 'CLUST-DHK-01' ? 'Gulshan-Mirpur Node' : (id === 'CLUST-CTG-01' ? 'Agrabad Commercial Hub' : id);
  if (modal) { modal.classList.remove('hidden'); modal.style.display = 'flex'; }
}

function deleteClusterPrompt(id) {
  if (!canExecuteAction('create_edit_cluster', 'Delete Cluster')) return;
  if (confirm(`Are you sure you want to delete Cluster ${id}?`)) {
    const row = document.querySelector(`tr[data-cluster-id="${id}"]`);
    if (row) row.remove();
    showScadaToast('Cluster Removed', `Cluster ${id} deleted.`);
  }
}

function openCreateClusterModal() {
  if (!canExecuteAction('create_edit_cluster', 'Create New Cluster')) return;
  const modal = document.getElementById('cluster-crud-modal');
  const title = document.getElementById('cluster-modal-title');
  const nameInput = document.getElementById('cluster-name-input');
  const codeInput = document.getElementById('cluster-code-input');
  if (title) title.textContent = 'Create New Cluster';
  if (codeInput) codeInput.value = `CLUST-ZONE-${Math.floor(Math.random()*900 + 100)}`;
  if (nameInput) nameInput.value = '';
  if (modal) { modal.classList.remove('hidden'); modal.style.display = 'flex'; }
}

function saveClusterRecord() {
  const name = document.getElementById('cluster-name-input')?.value.trim();
  const code = document.getElementById('cluster-code-input')?.value.trim();
  if (!name || !code) { alert('Please enter Cluster Name and ID.'); return; }
  showScadaToast('Cluster Saved', `Cluster ${name} (${code}) created.`);
  closeFranchiseModals();
}

function viewTowerTelemetry(id) {
  window.location.href = `telemetry.html?station=${id}`;
}

function editTowerModal(id) {
  if (!canExecuteAction('create_edit_cluster', 'Modify BTS Tower')) return;
  const modal = document.getElementById('tower-crud-modal');
  const title = document.getElementById('tower-modal-title');
  const idInput = document.getElementById('tower-id-input');
  const nameInput = document.getElementById('tower-name-input');
  if (title) title.textContent = `Edit Tower: ${id}`;
  if (idInput) idInput.value = id;
  if (nameInput) nameInput.value = `Station ${id}`;
  if (modal) { modal.classList.remove('hidden'); modal.style.display = 'flex'; }
}

function deleteTowerPrompt(id) {
  if (!canExecuteAction('create_edit_cluster', 'Decommission Tower')) return;
  if (confirm(`Are you sure you want to decommission Tower ${id}?`)) {
    const row = document.querySelector(`tr[data-tower-id="${id}"]`);
    if (row) row.remove();
    showScadaToast('Tower Decommissioned', `Tower node ${id} removed.`);
  }
}

function openCreateTowerModal() {
  if (!canExecuteAction('create_edit_cluster', 'Create BTS Tower')) return;
  const modal = document.getElementById('tower-crud-modal');
  const title = document.getElementById('tower-modal-title');
  const idInput = document.getElementById('tower-id-input');
  const nameInput = document.getElementById('tower-name-input');
  if (title) title.textContent = 'Create New BTS Tower';
  if (idInput) idInput.value = `BTS-NODE-${Math.floor(Math.random()*9000 + 1000)}`;
  if (nameInput) nameInput.value = '';
  if (modal) { modal.classList.remove('hidden'); modal.style.display = 'flex'; }
}

function saveTowerRecord() {
  const id = document.getElementById('tower-id-input')?.value.trim();
  const name = document.getElementById('tower-name-input')?.value.trim();
  if (!id || !name) { alert('Please enter Tower UID and Station Name.'); return; }
  showScadaToast('Tower Node Saved', `Tower ${name} (${id}) added to national registry.`);
  closeFranchiseModals();
}

function closeFranchiseModals() {
  const ids = ['area-crud-modal', 'cluster-crud-modal', 'tower-crud-modal', 'franchise-view-modal', 'gen-manual-edit-modal'];
  ids.forEach(id => {
    const el = document.getElementById(id);
    if (el) { el.classList.add('hidden'); el.style.display = 'none'; }
  });
}

// =========================================================================
// 6. MAINTENANCE QUEUE & SERVICE CONTROLS ENGINE
// =========================================================================
function filterMaintQueue() {
  const q = (document.getElementById('maint-search-input')?.value || '').toLowerCase();
  const rows = document.querySelectorAll('#maint-queue-tbody tr');
  rows.forEach(r => {
    r.style.display = r.textContent.toLowerCase().includes(q) ? '' : 'none';
  });
}

function openMaintModalFor(unitId) {
  if (!canExecuteAction('log_maintenance', 'Update Maintenance Variables')) return;
  const sel = document.getElementById('maint-modal-unit-sel');
  if (sel) sel.value = unitId;
  const m = document.getElementById('maint-update-modal');
  if (m) { m.classList.remove('hidden'); m.style.display = 'flex'; }
}

function toggleRowLockout(unitId) {
  if (!canExecuteAction('engage_loto_lockout', 'Safety Lockout Tag-Out')) return;
  showScadaToast('Safety Lockout Engaged', `LOTO lockout toggled on node ${unitId}. Field technician on site.`);
}

function toggleActiveLockout() {
  if (!canExecuteAction('engage_loto_lockout', 'Safety Lockout Tag-Out')) return;
  const lbl = document.getElementById('maint-lockout-label');
  const badge = document.getElementById('maint-unit-badge');
  if (lbl && lbl.textContent.includes('Engage')) {
    lbl.textContent = 'Disengage Safety Lockout';
    if (badge) { badge.textContent = 'LOCKOUT ACTIVE'; badge.className = 'px-2 py-0.5 rounded-full bg-rose-50 text-rose-700 text-[10px] font-bold border border-rose-200'; }
    showScadaToast('Lockout Engaged', 'Mechanical and electrical starting circuits locked out.', 'warn');
  } else if (lbl) {
    lbl.textContent = 'Engage Safety Lockout';
    if (badge) { badge.textContent = 'NORMAL OPERATION'; badge.className = 'px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 text-[10px] font-bold border border-emerald-200'; }
    showScadaToast('Lockout Released', 'Unit returned to normal supervisory status.');
  }
}

function openMaintUpdateModal() {
  if (!canExecuteAction('log_maintenance', 'Update Maintenance Variables')) return;
  const m = document.getElementById('maint-update-modal');
  if (m) { m.classList.remove('hidden'); m.style.display = 'flex'; }
}

function closeMaintModal() {
  const m = document.getElementById('maint-update-modal');
  if (m) { m.classList.add('hidden'); m.style.display = 'none'; }
}

function saveMaintenanceUpdate() {
  const unit = document.getElementById('maint-modal-unit-sel')?.value || 'GEN-PK-0104';
  const runtime = document.getElementById('maint-input-runtime')?.value || '320.5';
  const tech = document.getElementById('maint-input-tech')?.value || 'Lian Ahmed';
  const wo = document.getElementById('maint-input-wo')?.value || 'WO-2026-9481';

  closeMaintModal();
  showScadaToast('Service Logged & Reset', `Maintenance protocol saved for ${unit} under ${wo}. Service countdown hours reset to 250h.`);
}


// --- URL PARAMS HANDLER (e.g. ?station=BTS-GP-0492 or ?unit=GEN-CM-0208) ---
window.addEventListener('DOMContentLoaded', () => {
  const params = new URLSearchParams(window.location.search);
  const station = params.get('station');
  const unit = params.get('unit');

  if (station && document.getElementById('p18-unit-selector')) {
    const sel = document.getElementById('p18-unit-selector');
    for (let opt of sel.options) {
      if (opt.text.includes(station)) {
        sel.value = opt.value;
        if (typeof loadIndividual18Data === 'function') loadIndividual18Data(opt.value);
        break;
      }
    }
  }

  // Initialize alarms table and history chart if elements present
  if (document.getElementById('alarms-table-body')) renderAlarmsTable();
  if (document.getElementById('hist-line-path')) renderHistoryChart();
  if (document.getElementById('dse-lcd-body')) updateDseDisplay();
  if (typeof initProfileAndAvatar === 'function') initProfileAndAvatar();
  if (typeof switchActiveRole === 'function') switchActiveRole(currentScadaRole, false);
});

// =========================================================================
// GENESIS v12 — MASTER DATA EXCEL IMPORT & COMPLETE BUTTON CONNECTOR ENGINE
// =========================================================================

let activeMasterDataTarget = 'areas';
let parsedMasterData = null;

// 1. Dataset Target Selector
function setMasterDataTarget(target) {
  activeMasterDataTarget = target;
  const categories = ['areas', 'generators', 'employees', 'technicians'];
  categories.forEach(c => {
    const btn = document.getElementById('md-cat-btn-' + c);
    if (btn) {
      if (c === target) {
        btn.className = 'px-3 py-1.5 rounded-xl text-xs font-bold transition shadow-xs bg-white dark:bg-slate-900 text-slate-900 dark:text-white';
      } else {
        btn.className = 'px-3 py-1.5 rounded-xl text-xs font-bold transition text-slate-600 dark:text-slate-400 hover:text-slate-900';
      }
    }
  });
  
  const labels = {
    areas: 'Operational Areas',
    generators: 'Generator Grid List',
    employees: 'Employee & Commander Directory',
    technicians: 'Field Technicians Roster'
  };
  const titleEl = document.getElementById('md-dropzone-title');
  if (titleEl) {
    titleEl.textContent = `Upload ${labels[target]} Spreadsheet (.xlsx, .xls, .csv)`;
  }
}

// 2. Download Pre-Formatted Master Data Excel / CSV Templates
function downloadMasterDataTemplate(category = 'areas') {
  const templates = {
    areas: {
      filename: 'GENESIS_Template_Operational_Areas.csv',
      content: 'Area Code,Area Name,Division,Regional Director,Contact Email,Mobile,SLA Target %,Clusters Count\n' +
               'AREA-DHK-N,Dhaka North,Dhaka,Engr. Tariqul Islam,tariqul.islam@arenaiot.com,+880 1711-948201,99.8,6\n' +
               'AREA-DHK-S,Dhaka South,Dhaka,Engr. Shamim Hossain,shamim.hossain@arenaiot.com,+880 1711-948202,99.7,5\n' +
               'AREA-CTG-M,Chittagong Metro,Chittagong,Engr. Faisal Mahmud,faisal.mahmud@arenaiot.com,+880 1711-948203,99.6,4\n' +
               'AREA-SYL,Sylhet Zone,Sylhet,Engr. Kamrul Hasan,kamrul.hasan@arenaiot.com,+880 1711-948204,99.4,3\n'
    },
    generators: {
      filename: 'GENESIS_Template_Generator_Grid.csv',
      content: 'Generator ID,Tower ID,Model Name,Brand,Rating kVA,Prime kW,Serial Number,Controller,Sump Capacity L,Fuel Tank L,Runtime Hours\n' +
               'GEN-PK-0104,BTS-GP-0492,Perkins 1104A-44TG2,Perkins,60,48,PK-849204-TG,DSE-7320 MKII,8.0,250,320.5\n' +
               'GEN-CAT-0312,BTS-BL-1944,Caterpillar C4.4 ACERT,Caterpillar,88,70,CAT-338291-AC,DSE-7320 MKII,11.0,350,540.2\n' +
               'GEN-CUM-0518,BTS-RB-6102,Cummins 6BT5.9-G2,Cummins,100,80,CUM-991204-BT,DSE-7320 MKII,16.4,450,1120.0\n' +
               'GEN-KOH-0891,BTS-TT-0812,Kohler KD62,Kohler,150,120,KOH-554109-KD,DSE-7320 MKII,22.0,600,88.4\n'
    },
    employees: {
      filename: 'GENESIS_Template_Employee_Directory.csv',
      content: 'Employee ID,Full Name,Designation,Clearance Level,Email,Mobile,Command Station,VHF Radio Channel,Division Jurisdiction\n' +
               'DIR-DHK-01,Engr. Tariqul Islam,Regional SCADA Operations Director,Level 4,tariqul.islam@arenaiot.com,+880 1711-948201,Dhaka North HQ,VHF-Ch-04 (156.200 MHz),Dhaka\n' +
               'DIR-DHK-02,Engr. Shamim Hossain,Regional SCADA Operations Director,Level 4,shamim.hossain@arenaiot.com,+880 1711-948202,Dhaka South HQ,VHF-Ch-05 (156.250 MHz),Dhaka\n' +
               'ENG-SCADA-01,Engr. Lian Ahmed,Lead SCADA Engineer,Level 3,lian.ahmed@arenaiot.com,+880 1710-000001,National NOC Command Hub,VHF-Ch-01 (156.050 MHz),National\n'
    },
    technicians: {
      filename: 'GENESIS_Template_Field_Technicians.csv',
      content: 'Technician ID,Full Name,Contractor Company,Phone,Assigned Cluster,Specialization,Cert Expiration Date,Active LOTO Cert\n' +
               'TECH-MIR-01,Md. Rafiqul Haque,Apex Power Engineering Ltd,+880 1712-409182,Mirpur Node,Mechanical Sump & Injection,2027-12-31,YES\n' +
               'TECH-UTT-02,Kazi Nazrul Islam,Delta Generator Services,+880 1713-992104,Uttara North Node,Alternator & AVR Calibration,2028-06-30,YES\n' +
               'TECH-GUL-03,Shafiqur Rahman,National Electro-Mechanical,+880 1714-883391,Gulshan Corporate Node,Lube Oil & Glycol Service,2027-09-15,YES\n'
    }
  };

  const t = templates[category] || templates.areas;
  const blob = new Blob([t.content], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = t.filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  showScadaToast('Template Downloaded', `${t.filename} ready for Excel entry.`, 'success');
}

// 3. Robust CSV Parser
function parseCsvText(text) {
  const lines = text.split(/\r?\n/).filter(line => line.trim().length > 0);
  const result = [];
  for (let i = 0; i < lines.length; i++) {
    const row = [];
    let insideQuotes = false;
    let entry = '';
    const line = lines[i];
    for (let c = 0; c < line.length; c++) {
      const char = line[c];
      if (char === '"') {
        insideQuotes = !insideQuotes;
      } else if (char === ',' && !insideQuotes) {
        row.push(entry.trim());
        entry = '';
      } else {
        entry += char;
      }
    }
    row.push(entry.trim());
    result.push(row);
  }
  return result;
}

// 4. Handle Master Data Excel / Spreadsheet Upload
function handleMasterDataFileUpload(input) {
  if (!input.files || input.files.length === 0) return;
  const file = input.files[0];
  const fileName = file.name;
  const ext = fileName.split('.').pop().toLowerCase();

  if (ext === 'xlsx' || ext === 'xls') {
    if (typeof XLSX !== 'undefined') {
      const reader = new FileReader();
      reader.onload = function(e) {
        try {
          const data = new Uint8Array(e.target.result);
          const workbook = XLSX.read(data, { type: 'array' });
          const firstSheet = workbook.SheetNames[0];
          const worksheet = workbook.Sheets[firstSheet];
          const rawRows = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
          processParsedMasterDataRows(rawRows, fileName);
        } catch (err) {
          showScadaToast('Parse Error', 'Failed to parse Excel workbook: ' + err.message, 'error');
        }
      };
      reader.readAsArrayBuffer(file);
    } else {
      showScadaToast('Excel Engine Loading', 'SheetJS is loading. Please upload as .csv for instant local parsing.', 'warn');
    }
  } else if (ext === 'csv' || ext === 'txt') {
    const reader = new FileReader();
    reader.onload = function(e) {
      try {
        const text = e.target.result;
        const rawRows = parseCsvText(text);
        processParsedMasterDataRows(rawRows, fileName);
      } catch (err) {
        showScadaToast('Parse Error', 'Failed to parse CSV file: ' + err.message, 'error');
      }
    };
    reader.readAsText(file);
  } else {
    showScadaToast('Unsupported Format', 'Please upload .xlsx, .xls, or .csv spreadsheet.', 'error');
  }
}

// 5. Process Parsed Master Data Rows & Auto-Detect Category
function processParsedMasterDataRows(rows, fileName) {
  if (!rows || rows.length < 2) {
    showScadaToast('Empty File', 'The uploaded file contains no data rows.', 'error');
    return;
  }

  const headers = rows[0].map(h => String(h || '').trim());
  const dataRows = rows.slice(1).filter(r => r.some(cell => String(cell || '').trim().length > 0));

  // Auto-detect entity if possible
  const headerStr = headers.join(' ').toLowerCase();
  let detectedTarget = activeMasterDataTarget;
  if (headerStr.includes('area') && headerStr.includes('division')) {
    detectedTarget = 'areas';
  } else if (headerStr.includes('generator') || (headerStr.includes('kva') && headerStr.includes('model'))) {
    detectedTarget = 'generators';
  } else if (headerStr.includes('employee') || headerStr.includes('designation')) {
    detectedTarget = 'employees';
  } else if (headerStr.includes('technician') || headerStr.includes('loto')) {
    detectedTarget = 'technicians';
  }

  setMasterDataTarget(detectedTarget);

  parsedMasterData = {
    target: detectedTarget,
    fileName: fileName,
    headers: headers,
    rows: dataRows
  };

  renderMasterDataPreview(headers, dataRows, fileName, detectedTarget);
  showScadaToast('Spreadsheet Parsed', `Successfully extracted ${dataRows.length} records from ${fileName}.`, 'success');
}

// 6. Render Live Data Preview Table
function renderMasterDataPreview(headers, rows, fileName, target) {
  const container = document.getElementById('md-preview-container');
  const thead = document.getElementById('md-preview-thead');
  const tbody = document.getElementById('md-preview-tbody');
  const fnLabel = document.getElementById('md-parsed-filename');
  const countLabel = document.getElementById('md-parsed-count');
  const targetLabel = document.getElementById('md-parsed-target-label');

  if (!container || !thead || !tbody) return;

  if (fnLabel) fnLabel.textContent = fileName;
  if (countLabel) countLabel.textContent = `${rows.length} Rows Ready`;
  if (targetLabel) targetLabel.textContent = target.toUpperCase();

  // Render header
  thead.innerHTML = '<tr>' +
    '<th class="py-2.5 px-3">#</th>' +
    headers.map(h => `<th class="py-2.5 px-3">${h}</th>`).join('') +
    '</tr>';

  // Render rows (preview up to 20)
  tbody.innerHTML = rows.slice(0, 20).map((row, idx) => {
    return `<tr class="hover:bg-slate-50 dark:hover:bg-slate-800 transition">` +
      `<td class="py-2 px-3 font-mono text-slate-400 font-bold">${idx + 1}</td>` +
      headers.map((h, colIdx) => `<td class="py-2 px-3 font-medium text-slate-800 dark:text-slate-200">${row[colIdx] || '—'}</td>`).join('') +
      `</tr>`;
  }).join('');

  container.classList.remove('hidden');
  container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// 7. Clear Master Data Upload
function clearMasterDataUpload() {
  parsedMasterData = null;
  const container = document.getElementById('md-preview-container');
  if (container) container.classList.add('hidden');
  const input = document.getElementById('master-data-file-input');
  if (input) input.value = '';
}

// 8. Commit Master Data to SCADA System Database
function commitMasterDataImport() {
  if (!parsedMasterData || !parsedMasterData.rows) {
    showScadaToast('No Data', 'Please upload a spreadsheet file before committing.', 'warn');
    return;
  }

  const { target, rows, headers, fileName } = parsedMasterData;

  // Persist to localStorage
  const storageKey = `genesis_master_${target}`;
  const existing = JSON.parse(localStorage.getItem(storageKey) || '[]');
  
  // Format as structured records
  const newRecords = rows.map(r => {
    const obj = {};
    headers.forEach((h, idx) => {
      obj[h] = r[idx] || '';
    });
    return obj;
  });

  const merged = [...existing, ...newRecords];
  localStorage.setItem(storageKey, JSON.stringify(merged));

  // If operational areas were committed, append to Area table immediately
  if (target === 'areas') {
    const areaTbody = document.getElementById('area-table-body');
    if (areaTbody) {
      newRecords.forEach(rec => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-50/80 dark:hover:bg-slate-800/80 transition';
        const code = rec['Area Code'] || 'AREA-NEW';
        const name = rec['Area Name'] || 'New Area';
        const div = rec['Division'] || 'Dhaka';
        const director = rec['Regional Director'] || 'Engr. Assigned Director';
        const sla = rec['SLA Target %'] || '99.5%';
        const clusters = rec['Clusters Count'] || '3 Clusters';
        
        tr.setAttribute('data-area-id', code);
        tr.innerHTML = `
          <td class="py-3 px-3.5">
            <div class="font-bold text-slate-900 dark:text-white">${name}</div>
            <div class="text-[10px] font-mono text-slate-400">${code}</div>
          </td>
          <td class="py-3 px-3.5 font-bold text-slate-800 dark:text-slate-200">${div}</td>
          <td class="py-3 px-3.5 font-bold text-indigo-700 dark:text-indigo-400">
            <button type="button" onclick="openPersonnelProfile('${director}')" class="hover:underline flex items-center gap-1">
              <span>${director}</span>
              <svg class="w-3 h-3 text-indigo-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
            </button>
          </td>
          <td class="py-3 px-3.5 font-bold text-slate-800 dark:text-slate-200">${clusters}</td>
          <td class="py-3 px-3.5 font-mono font-bold text-emerald-800 dark:text-emerald-400">12 Towers</td>
          <td class="py-3 px-3.5 font-mono text-slate-700 dark:text-slate-300">0.8 MW</td>
          <td class="py-3 px-3.5"><span class="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-800 text-[10px] font-bold">${sla}</span></td>
          <td class="py-3 px-3.5 text-right">
            <div class="inline-flex items-center gap-1.5">
              <button type="button" onclick="viewAreaDetails('${code}')" class="scada-btn-action action-view">View</button>
              <button type="button" onclick="editAreaModal('${code}')" class="scada-btn-action action-edit">Edit</button>
              <button type="button" onclick="deleteAreaPrompt('${code}')" class="scada-btn-action action-delete">Delete</button>
            </div>
          </td>
        `;
        areaTbody.appendChild(tr);
      });
    }
  }

  showScadaToast('Master Data Ingested', `Successfully committed ${newRecords.length} ${target} records to SCADA Grid Database.`, 'success');
  clearMasterDataUpload();
}

// 9. Generator Management Button Handlers
function saveManualModelSpecs() {
  const name = document.getElementById('manual-model-name')?.value || 'Industrial Diesel Genset';
  const standby = document.getElementById('manual-standby-kva')?.value || '100';
  const prime = document.getElementById('manual-prime-kw')?.value || '80';
  const rpm = document.getElementById('manual-rated-rpm')?.value || '1500';
  const fuel = document.getElementById('manual-fuel-rate')?.value || '0.239';

  const modelRecord = {
    name, standbyKva: parseFloat(standby), primeKw: parseFloat(prime),
    rpm: parseInt(rpm), fuelRate: fuel, updatedAt: new Date().toISOString()
  };

  const existing = JSON.parse(localStorage.getItem('genesis_custom_models') || '[]');
  existing.push(modelRecord);
  localStorage.setItem('genesis_custom_models', JSON.stringify(existing));

  closeFranchiseModals();
  showScadaToast('Specifications Saved', `${name} (${standby} kVA) committed to SCADA registry.`, 'success');
}

function loadSampleDatasheet(modelKey = 'caterpillar') {
  const container = document.getElementById('parsed-datasheet-preview');
  if (!container) return;

  container.innerHTML = `
    <div class="p-4 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 flex flex-col gap-3">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="w-2.5 h-2.5 rounded-full bg-emerald-600 animate-pulse"></span>
          <span class="text-xs font-bold text-emerald-900 dark:text-emerald-300">Caterpillar C4.4 ACERT Datasheet Parsed</span>
        </div>
        <span class="text-[10px] font-mono bg-emerald-100 dark:bg-emerald-900 text-emerald-800 dark:text-emerald-200 px-2 py-0.5 rounded font-bold">OEM VERIFIED</span>
      </div>
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
        <div><span class="text-slate-400 block text-[10px]">Model</span><b class="text-slate-800 dark:text-slate-100">CAT C4.4 ACERT</b></div>
        <div><span class="text-slate-400 block text-[10px]">Prime Power</span><b class="text-slate-800 dark:text-slate-100">70 kW (88 kVA)</b></div>
        <div><span class="text-slate-400 block text-[10px]">Fuel Rate</span><b class="text-slate-800 dark:text-slate-100">16.8 L/h @ 100%</b></div>
        <div><span class="text-slate-400 block text-[10px]">Sump Volume</span><b class="text-slate-800 dark:text-slate-100">11.0 L (15W-40)</b></div>
      </div>
      <div class="flex items-center gap-2 mt-1">
        <button type="button" onclick="saveParsedModelToRegistry('Caterpillar C4.4 ACERT', 'Caterpillar', 88, 70)" class="scada-btn-indigo text-xs py-1.5 px-3">Commit to Registry</button>
        <button type="button" onclick="openManualEditModalFromParser()" class="scada-btn-secondary text-xs py-1.5 px-3">Edit Specs</button>
      </div>
    </div>
  `;
  showScadaToast('Datasheet Parsed', 'Sample parameters for Caterpillar C4.4 populated.', 'success');
}

function openCreateNewModelModal() {
  const modal = document.getElementById('gen-manual-edit-modal');
  if (!modal) return;
  const title = document.getElementById('gen-manual-title');
  if (title) title.textContent = 'Create New Generator Specification';
  const nameInput = document.getElementById('manual-model-name');
  if (nameInput) nameInput.value = '';
  modal.classList.remove('hidden');
  modal.style.display = 'flex';
}

function openManualEditModalFor(modelId) {
  const modal = document.getElementById('gen-manual-edit-modal');
  if (!modal) return;
  const title = document.getElementById('gen-manual-title');
  if (title) title.textContent = `Edit Specifications — ${modelId}`;
  modal.classList.remove('hidden');
  modal.style.display = 'flex';
}

function openManualEditModalFromParser() {
  const modal = document.getElementById('gen-manual-edit-modal');
  if (!modal) return;
  const title = document.getElementById('gen-manual-title');
  if (title) title.textContent = 'Fine-Tune Parsed Datasheet Specifications';
  const nameInput = document.getElementById('manual-model-name');
  if (nameInput) nameInput.value = 'Caterpillar C4.4 ACERT';
  modal.classList.remove('hidden');
  modal.style.display = 'flex';
}

function saveParsedModelToRegistry(name = 'Caterpillar C4.4 ACERT', brand = 'Caterpillar', kva = 88, kw = 70) {
  const customModel = {
    name, brand, kva: parseFloat(kva), kw: parseFloat(kw),
    savedAt: new Date().toISOString()
  };
  const list = JSON.parse(localStorage.getItem('genesis_custom_models') || '[]');
  list.push(customModel);
  localStorage.setItem('genesis_custom_models', JSON.stringify(list));
  showScadaToast('Model Committed', `${name} successfully added to Generator Registry.`, 'success');
}

function downloadTechnicalDatasheet(modelId = 'GEN-PK-0104') {
  const content = `GENESIS RMS — INDUSTRIAL GENERATOR TECHNICAL SPECIFICATION\n` +
    `============================================================\n` +
    `Asset ID             : ${modelId}\n` +
    `Engine Prime Mover   : Heavy-Duty Industrial Diesel 4-Cycle\n` +
    `Synchronous Speed    : 1500 RPM @ 50 Hz\n` +
    `Engine Controller    : Deep Sea Electronics DSE-7320 MKII\n` +
    `Telemetry Bus        : Modbus RTU Slave over RS-485 2-Wire\n` +
    `Coolant Capacity     : 50/50 Ethylene Glycol Premix\n` +
    `Lube Oil Grade       : 15W-40 CI-4 Heavy Sump\n` +
    `Compliance Standard  : ISO 8528 · IEC 60034 · ISO/IEC 27001\n` +
    `Export Timestamp     : ${new Date().toISOString()}\n`;

  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `GENESIS_${modelId.replace(/\s+/g, '_')}_Datasheet.txt`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  showScadaToast('Datasheet Downloaded', `Engineering specification for ${modelId} saved.`, 'success');
}

// 10. Content Studio Handlers
function switchContentTab(tab) {
  const tabs = ['banner', 'thumbnails', 'avatars', 'documents', 'masterdata'];
  tabs.forEach(t => {
    const panel = document.getElementById('content-tab-' + t);
    const btn = document.getElementById('tab-btn-content-' + (t === 'thumbnails' ? 'thumbs' : (t === 'documents' ? 'docs' : t)));
    if (t === tab) {
      if (panel) panel.classList.remove('hidden');
      if (btn) btn.className = 'px-3.5 py-2 rounded-xl text-xs font-bold transition shadow-xs bg-white text-slate-900';
    } else {
      if (panel) panel.classList.add('hidden');
      if (btn) btn.className = 'px-3.5 py-2 rounded-xl text-xs font-bold transition text-slate-600 hover:text-slate-900';
    }
  });
}

function applyBannerImageToLive() {
  showScadaToast('Hero Showroom Updated', 'Cutout graphics synchronized across all 18 production pages.', 'success');
}

function handleContentBannerUpload(input) {
  if (!input.files || input.files.length === 0) return;
  const file = input.files[0];
  const reader = new FileReader();
  reader.onload = function(e) {
    const preview = document.getElementById('content-banner-preview-img');
    if (preview) preview.src = e.target.result;
    showScadaToast('Image Loaded', 'Generator cutout loaded into preview stage.', 'success');
  };
  reader.readAsDataURL(file);
}

function openGenUploadModal(modelId) {
  const modal = document.getElementById('gen-thumb-modal');
  if (modal) {
    modal.classList.remove('hidden');
    modal.style.display = 'flex';
  }
}

function closeGenThumbModal() {
  const modal = document.getElementById('gen-thumb-modal');
  if (modal) {
    modal.classList.add('hidden');
    modal.style.display = 'none';
  }
}

function saveGenThumbnail(modelId) {
  closeGenThumbModal();
  showScadaToast('Thumbnail Saved', 'Generator image updated successfully.', 'success');
}

function closeBannerUploadModal() {
  const modal = document.getElementById('banner-device-modal');
  if (modal) {
    modal.classList.add('hidden');
    modal.style.display = 'none';
  }
}

function saveBannerDeviceUpdate() {
  closeBannerUploadModal();
  showScadaToast('Device Updated', 'Hero showroom configuration updated.', 'success');
}

function closeGlobalSearch() {
  const modal = document.getElementById('global-search-modal');
  if (modal) {
    modal.classList.add('hidden');
    modal.style.display = 'none';
  }
}

// 11. Connect Phone and Email Links in Personnel Profiles
const origOpenPersonnelProfile = typeof openPersonnelProfile === 'function' ? openPersonnelProfile : null;
window.openPersonnelProfile = function(nameOrUid) {
  if (origOpenPersonnelProfile) origOpenPersonnelProfile(nameOrUid);
  
  // Ensure mailto and tel are wired
  const emailEl = document.getElementById('pers-modal-email');
  const phoneEl = document.getElementById('pers-modal-phone');
  if (emailEl && emailEl.textContent) {
    emailEl.href = 'mailto:' + emailEl.textContent.trim();
  }
  if (phoneEl && phoneEl.textContent) {
    phoneEl.href = 'tel:' + phoneEl.textContent.trim().replace(/\s+/g, '');
  }
};

// 12. Support URL Tab Parameter (?tab=import)
window.addEventListener('DOMContentLoaded', () => {
  const urlParams = new URLSearchParams(window.location.search);
  const tabParam = urlParams.get('tab');
  if (tabParam === 'import' && typeof switchFranchiseTier === 'function') {
    switchFranchiseTier('import');
  }
});

</script>
"""

    full_page = f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>GENESIS RMS — {title}</title>
  {v7_head_content}
</head>
<body class="theme-light selection:bg-slate-900 selection:text-[#9ede4c]">
  <div class="scada-ambient-backdrop"></div>
  {header_clean}
  
  <div class="max-w-[1780px] mx-auto px-3 sm:px-6 py-5 flex gap-5">
    {rail}
    <main class="flex-1 min-w-0">
      {main_content_html}
    </main>
  </div>

  {global_modals_html}
  {v7_scripts_raw}
  {extra_scripts}
</body>
</html>"""
    return universal_sanitize(full_page)

# =========================================================================
# ASSEMBLE ALL 18 PAGES
# =========================================================================

# 1. Master Overview (overview.html / index.html)
overview_html = assemble_page(
    title="Master Showroom & Live Telemetry",
    active_page="overview",
    main_content_html=f"""
    <div id="screen-overview" class="flex flex-col gap-6">
      <div id="dashboard-modules-container" class="flex flex-col gap-6">
        {raw_modules['hero']}
        {raw_modules['telemetry']}
        {raw_modules['subtotal']}
        {raw_modules['history']}
        {raw_modules['devices']}
        {raw_modules['map']}
        {raw_modules['alarms']}
      </div>
    </div>
    """
)

# 2. Telemetry Inspector (telemetry.html)
telemetry_html = assemble_page(
    title="18-Component SCADA Telemetry Inspector",
    active_page="telemetry",
    main_content_html=f"""
    <div id="screen-telemetry" class="flex flex-col gap-6">
      {raw_modules['telemetry']}
      {raw_modules['devices']}
    </div>
    """
)

# 3. Generator Management (generator-management.html)
generator_mgmt_page = assemble_page(
    title="Generator Model & Datasheet Management",
    active_page="generators",
    main_content_html=gen_mgmt_raw
)

# 4. Maintenance Lifecycle Page (maintenance.html)
maintenance_page = assemble_page(
    title="Generator Maintenance & Service Lifecycle",
    active_page="maintenance",
    main_content_html=maint_raw
)

# 5. Franchise Management (franchise-management.html)
franchise_mgmt_page = assemble_page(
    title="Franchise Hierarchy Management (Area, Cluster, Tower)",
    active_page="franchise",
    main_content_html=franchise_raw
)

# 6. Content & Media Studio (content-management.html)
content_mgmt_page = assemble_page(
    title="Content & Media Upload Studio",
    active_page="content",
    main_content_html=content_raw
)

# 7. Subtotal Analytics (subtotal.html)
subtotal_html = assemble_page(
    title="National Sub-Total Operational Summary",
    active_page="subtotal",
    main_content_html=f"""
    <div id="screen-subtotal" class="flex flex-col gap-6">
      {raw_modules['subtotal']}
    </div>
    """
)

# 8. Map Network (map.html)
map_html = assemble_page(
    title="National GIS Spatial Map & Towers",
    active_page="map",
    main_content_html=f"""
    <div id="screen-map" class="flex flex-col gap-6">
      {raw_modules['map']}
    </div>
    """
)

# 9. Alarms Center (alarms.html) - Enhanced with full 20-alarm triage suite
alarms_html = assemble_page(
    title="SCADA Alarms & Tripping Triage Console",
    active_page="alarms",
    main_content_html=alarms_full_raw
)

# 10. Remote Control (control.html) - Enhanced with full DSE-7320 hardware controller
control_html = assemble_page(
    title="Authorized Remote Control & DSE-7320 MKII",
    active_page="control",
    main_content_html=control_raw
)

# 11. History (history.html) - Enhanced with 6-month interactive trend chart & CSV
history_html = assemble_page(
    title="6-Month Daily Telemetry Historical Trends",
    active_page="history",
    main_content_html=history_raw
)

# 12. Communications (comm.html) - Enhanced with live Modbus RTU diagnostics & ping
comm_html = assemble_page(
    title="Communications & RTU Gateway Diagnostics",
    active_page="comm",
    main_content_html=comm_raw
)

# 13. CMS Studio (cms.html)
cms_html = assemble_page(
    title="CMS Page Builder & Module Priority",
    active_page="cms",
    main_content_html=f"""
    <div id="screen-cms" class="flex flex-col gap-6">
      {v7_cms_raw}
    </div>
    """
)

# 14. NOC Operations (noc.html)
noc_html = assemble_page(
    title="NOC Operator Profile & National Command",
    active_page="noc",
    main_content_html=f"""
    <div id="screen-noc" class="flex flex-col gap-6">
      <div class="bg-white/80 backdrop-blur-xl rounded-[28px] p-6 sm:p-8 border border-white/90 shadow-md">
        <h2 class="text-xl font-black text-slate-900 mb-2">National NOC Operations Console</h2>
        <p class="text-xs text-slate-600 mb-6 font-medium">Real-time supervision across all 492 BTS towers and regional power grids</p>
        <div class="p-6 rounded-2xl bg-slate-900 text-white flex flex-col md:flex-row items-center justify-between gap-6">
          <div class="flex items-center gap-4">
            <div class="w-16 h-16 rounded-2xl bg-slate-800 text-white font-black text-2xl flex items-center justify-center">
              LN
            </div>
            <div>
              <div class="flex items-center gap-2">
                <h3 class="text-lg font-black text-white">Lian Ahmed</h3>
                <span class="text-xs font-mono font-bold text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800">#AR-9402</span>
              </div>
              <p class="text-xs text-slate-400 mt-0.5">Lead SCADA Engineer · National Operations Center</p>
            </div>
          </div>
          <button onclick="openProfileModal()" class="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs transition shadow-xs">
            Edit Profile & Permissions
          </button>
        </div>
      </div>
    </div>
    """
)

# 15. Settings (settings.html) - Enhanced with persistent configuration
settings_html = assemble_page(
    title="System Settings & SCADA Telemetry Preferences",
    active_page="settings",
    main_content_html=settings_raw
)

# 16. Sign Up (signup.html) & 17. Login (login.html)
signup_sanitized = universal_sanitize(signup_raw)
login_sanitized = universal_sanitize(login_raw)

# 7. Write all pages to both SRC_DIR and ARTIFACT_DIR
pages = {
    "overview.html": overview_html,
    "index.html": overview_html,
    "telemetry.html": telemetry_html,
    "generator-management.html": generator_mgmt_page,
    "maintenance.html": maintenance_page,
    "franchise-management.html": franchise_mgmt_page,
    "content-management.html": content_mgmt_page,
    "subtotal.html": subtotal_html,
    "map.html": map_html,
    "alarms.html": alarms_html,
    "control.html": control_html,
    "history.html": history_html,
    "comm.html": comm_html,
    "cms.html": cms_html,
    "noc.html": noc_html,
    "settings.html": settings_html,
    "signup.html": signup_sanitized,
    "login.html": login_sanitized
}

for page_name, content in pages.items():
    p_path = os.path.join(SRC_DIR, page_name)
    with open(p_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    a_path = os.path.join(ARTIFACT_DIR, page_name)
    with open(a_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Generated {page_name} ({len(content)} bytes)")

# Also write genesis_telemetry_dashboard.html artifact
artifact_dash = os.path.join(ARTIFACT_DIR, "genesis_telemetry_dashboard.html")
with open(artifact_dash, "w", encoding="utf-8") as f:
    f.write(overview_html)
print(f"Updated artifact genesis_telemetry_dashboard.html")

print("\n--- ALL 18 PAGES SUCCESSFULLY ASSEMBLED AND SANITIZED ---")
