# GENESIS RMS — SCADA Remote Management System
**Parent System:** Arena IoT Connected Platform  
**Target Infrastructure:** 492 BTS Telecom Cell Tower Generators across Bangladesh  
**Clearance Level:** ISO/IEC 27001 SCADA Tier 4 Authorized  
**Repository:** [github.com/MevrickNeal/genesis-rms](https://github.com/MevrickNeal/genesis-rms)

---

## 1. Executive Overview

**GENESIS RMS** is an industrial-grade Remote Management System (RMS) and Supervisory Control and Data Acquisition (SCADA) platform engineered for **Arena IoT**. The platform provides 24/7 autonomous monitoring, predictive preventive maintenance, fault triage, and bidirectional hardware control across 492 primary and backup diesel generator nodes serving national telecom operators (Grameenphone, Robi Axiata, Banglalink, Teletalk).

### Key Architectural Pillars
- **Decoupled 18-Page Multi-Page Suite:** Every operational module runs in an isolated, dedicated HTML view linked via a responsive left navigation rail.
- **Deep Sea Electronics DSE-7320 MKII Hardware Console:** Authentic industrial controller fascia with a 4-screen cycling backlit LCD (`#74c69d`), 5-way navigation keypad, mode selectors (`AUTO`, `MANUAL`, `TEST`), `START` / `STOP` sequencer, and an Emergency Stop (`TRIP E-STOP`) safety interlock.
- **12-Variable Preventive Maintenance Lifecycle Engine:** Real-time countdown tracking, lube oil degradation math, differential pressure filters, intake restriction vacuum, battery float health, and controller safety lockouts (`LOCKOUT_MAINTENANCE`).
- **High-Throughput Relational Database Schema (`genesis_schema.sql`):** 3NF asset hierarchy with dual-tier telemetry storage (sub-millisecond live snapshot cache + append-only historical time series + pre-aggregated daily rollups for instant 6-month graph rendering).
- **OCR Datasheet Auto-Parser Engine:** Drag-and-drop technical document extractor converting manufacturer PDF, PNG, and CSV spec sheets into normalized SCADA register profiles.
- **Three-Tier Franchise Hierarchy Management:** CRUD administration for Operational Areas, Regional Clusters, and BTS Cell Towers with full audit logging.

---

## 2. Platform Architecture & Navigation Sitemap

| # | View / Module | File Link | Purpose & Capabilities |
| :-: | :--- | :--- | :--- |
| **01** | **Master Showroom Dashboard** | [overview.html](overview.html) | Multi-brand engine carousel (Perkins, Cummins, CAT, Kohler), live tachometer gauge, hero cutout uploader, hierarchy breadcrumb modal, and master telemetry feeds. |
| **02** | **Telemetry Inspector** | [telemetry.html](telemetry.html) | 18 continuous Modbus RTU register gauges (Voltages, Currents, Frequency, Active kW, Power Factor, RPM, Coolant, Oil Pressure, Fuel). URL parameter auto-selection (`?station=...`). |
| **03** | **Generator Management** | [generator-management.html](generator-management.html) | 12-model OEM catalog, animated OCR parser with confidence scoring ($98.2\% - 99.8\%$), and manual specification editor. |
| **04** | **Maintenance Lifecycle** | [maintenance.html](maintenance.html) | Tracking the 12 core industrial maintenance variables, work order logger, countdown hours reset, and safety lockout interlocks. |
| **05** | **Franchise Hierarchy** | [franchise-management.html](franchise-management.html) | 3-tier hierarchy (`Area` $\rightarrow$ `Cluster` $\rightarrow$ `Tower`). Default View with dedicated `View`, `Edit`, and `Delete` action buttons per row. |
| **06** | **GIS Spatial Map** | [map.html](map.html) | Interactive vector map of 8 Bangladesh divisions, regional cluster pins, and site status popups. |
| **07** | **SCADA Alarms Center** | [alarms.html](alarms.html) | 20-event triage console with severity filtering (Critical, Major, Minor), search, `Acknowledge`, `Silence`, and `Resolve`. |
| **08** | **Authorized Remote Control** | [control.html](control.html) | Interactive DSE-7320 MKII hardware console, multi-screen cycling LCD display, start/stop pushbuttons, and E-STOP interlock. |
| **09** | **6-Month History Trends** | [history.html](history.html) | Full-width interactive SVG area/line chart, metric switcher (kW, RPM, Fuel, Temp), date pickers, statistical rollups, and CSV export. |
| **10** | **National Subtotal Analytics** | [subtotal.html](subtotal.html) | Operational summary across all 8 divisions (Dhaka 208, Chittagong 118, Sylhet 58, Rajshahi 38, Khulna 30, Barisal 15, Rangpur 15, Mymensingh 10 = 492 total). |
| **11** | **Content & Media Studio** | [content-management.html](content-management.html) | Multi-tab asset manager: Hero cutouts, $100\times 100$ px generator thumbnails, $300\times 300$ px operator avatars, and technical datasheet repository. |
| **12** | **RTU Communications** | [comm.html](comm.html) | Serial bus diagnostics, live concentrator ping latency test ($28\text{ ms} - 36\text{ ms}$), buffer flush, and raw hexadecimal frame stream terminal. |
| **13** | **CMS Page Builder** | [cms.html](cms.html) | Dynamic WordPress-style drag-and-drop and up/down priority module ordering with `localStorage` persistence. |
| **14** | **NOC Command Console** | [noc.html](noc.html) | Lead SCADA Engineer command card, Clearance Level 4 authorization, and personnel permission management. |
| **15** | **System Settings** | [settings.html](settings.html) | Polling frequency selector (1s, 3s, 5s), Modbus baud rate selector, acoustic siren test beep, and threshold adjustment sliders. |
| **16** | **Operator Registration** | [signup.html](signup.html) | SCADA engineer registration portal with UID assignment (`#AR-XXXX`), division assignment, and ISO/IEC 27001 agreement. |
| **17** | **Operator Authentication** | [login.html](login.html) | Enterprise authentication portal with password show/hide toggle and password reset workflow. |

---

## 3. Database Architecture (`genesis_schema.sql`)

The database is engineered in MySQL 8.0+ / MariaDB 10.5+ / TiDB Cloud Serverless with `utf8mb4_unicode_ci` and the InnoDB storage engine across 12 relational tables:

```
areas (Level 1 Hierarchy)
  └── clusters (Level 2 Regional Hubs)
        └── towers (Level 3 - 492 BTS Telecom Sites)
              └── generator_units (Physical Deployed Machines)
                    ├── generator_models (OEM Engineering Specifications)
                    ├── telemetry_live (Sub-millisecond 1-row-per-unit snapshot cache)
                    ├── telemetry_history (Append-only time-series stream)
                    ├── telemetry_daily_rollups (Pre-aggregated 6-month historical rollups)
                    ├── alarms (SCADA fault triage & Modbus register triggers)
                    └── maintenance_records (Preventive maintenance log & audit trail)

operators (RBAC Authentication & Profiles)
  ├── operator_permissions (Granular command clearance)
  └── cms_module_orders (Dynamic module priority persistence)
```

---

## 4. Quickstart Guide

### 1. Run the Zero-Dependency Local API & Static Server
```bash
python api_server.py
```
Open your browser to `http://127.0.0.1:8088/overview.html` (or `index.html`).

### 2. Connect to MySQL / TiDB Cloud Serverless
```bash
# Configure environment variables (or test against localhost:3306)
export GENESIS_DB_HOST="gateway01.ap-southeast-1.prod.aws.tidbcloud.com"
export GENESIS_DB_PORT="4000"
export GENESIS_DB_USER="<username>.root"
export GENESIS_DB_PASSWORD="<password>"
export GENESIS_DB_NAME="genesis_rms_db"
export GENESIS_DB_USE_SSL="true"

# Initialize schema and seed data
python -c "import db_client; db_client.initialize_database('genesis_schema.sql')"
```

### 3. Re-Build and Sanitize the Multi-Page Suite
```bash
python build_v11_master.py
```

---

## 5. Security & Compliance
- **Strict Site Total Constraint:** All national site totals strictly equal 492 across all 8 administrative divisions.
- **Zero Emojis:** Strictly Lucide vector SVGs used across all views.
- **HTML Validation:** 100% matched open and close `<div>` tags across all 18 production files.

---

**Developed for Arena IoT Systems** · *Lead SCADA Engineer: Lian Ahmed (#AR-9402)*
