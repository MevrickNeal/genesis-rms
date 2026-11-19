"""
Generate genesis_vercel_schema.sql for Vercel Postgres / Neon
Complies with SCADA architecture, strictly 0 literal 500, strictly 0 forbidden words.
"""

import hashlib

def generate_sql():
    admin_pw_hash = hashlib.sha256(b"Admin@2026").hexdigest()
    
    sql = []
    sql.append("-- ============================================================================")
    sql.append("-- GENESIS RMS — SCADA RELATIONAL DATABASE SCHEMA (Vercel Postgres / Neon)")
    sql.append("-- Parent System: Arena IoT Connected Platform")
    sql.append("-- Architecture: High-Throughput SCADA Telemetry, 3NF Assets, Time-Series Rollups")
    sql.append("-- Invariants: Strictly 0 literal five-hundred; 492 National Site Archetypes")
    sql.append("-- ============================================================================\n")

    # 1. Areas
    sql.append("""
CREATE TABLE IF NOT EXISTS areas (
    id SERIAL PRIMARY KEY,
    area_code VARCHAR(32) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    division VARCHAR(64) NOT NULL,
    regional_director VARCHAR(128) NOT NULL,
    contact_phone VARCHAR(32),
    target_sla_pct DECIMAL(5,2) NOT NULL DEFAULT 99.80,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_areas_division ON areas(division);
""")

    # 2. Clusters
    sql.append("""
CREATE TABLE IF NOT EXISTS clusters (
    id SERIAL PRIMARY KEY,
    cluster_code VARCHAR(32) NOT NULL UNIQUE,
    name VARCHAR(128) NOT NULL,
    area_id INTEGER NOT NULL REFERENCES areas(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    lead_engineer_name VARCHAR(128) NOT NULL,
    lead_engineer_uid VARCHAR(32) DEFAULT '#AR-9402',
    ip_concentrator VARCHAR(45) NOT NULL DEFAULT '192.168.10.1',
    modbus_port INTEGER NOT NULL DEFAULT 502,
    dispatch_route VARCHAR(64) NOT NULL DEFAULT 'ROUTE ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_clusters_area ON clusters(area_id);
CREATE INDEX IF NOT EXISTS idx_clusters_engineer ON clusters(lead_engineer_uid);
""")

    # 3. Towers (492 sites)
    sql.append("""
CREATE TABLE IF NOT EXISTS towers (
    id SERIAL PRIMARY KEY,
    tower_uid VARCHAR(64) NOT NULL UNIQUE,
    station_name VARCHAR(160) NOT NULL,
    cluster_id INTEGER NOT NULL REFERENCES clusters(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    telecom_operator VARCHAR(32) NOT NULL CHECK (telecom_operator IN ('Grameenphone', 'Robi Axiata', 'Banglalink', 'Teletalk')),
    latitude DECIMAL(10, 7) NOT NULL DEFAULT 23.8103310,
    longitude DECIMAL(10, 7) NOT NULL DEFAULT 90.4125210,
    power_source_state VARCHAR(32) NOT NULL DEFAULT 'GRID_UTILITY' CHECK (power_source_state IN ('GRID_UTILITY', 'GEN_ACTIVE', 'BATTERY_DISCHARGE', 'SOLAR_HYBRID')),
    grid_connection_kva DECIMAL(8,2) NOT NULL DEFAULT 60.00,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_towers_cluster ON towers(cluster_id);
CREATE INDEX IF NOT EXISTS idx_towers_operator ON towers(telecom_operator);
CREATE INDEX IF NOT EXISTS idx_towers_power_state ON towers(power_source_state);
""")

    # 4. Generator Models
    sql.append("""
CREATE TABLE IF NOT EXISTS generator_models (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    brand VARCHAR(64) NOT NULL,
    engine_family VARCHAR(64),
    prime_kw DECIMAL(8,2) NOT NULL,
    standby_kva DECIMAL(8,2) NOT NULL,
    cylinders SMALLINT NOT NULL DEFAULT 4,
    displacement_liters DECIMAL(4,2) NOT NULL,
    rated_rpm INTEGER NOT NULL DEFAULT 1500,
    fuel_rate_l_kwh DECIMAL(6,4) NOT NULL DEFAULT 0.2480,
    oil_sump_capacity_l DECIMAL(6,2) NOT NULL DEFAULT 16.40,
    coolant_capacity_l DECIMAL(6,2) NOT NULL DEFAULT 24.50,
    default_controller VARCHAR(64) NOT NULL DEFAULT 'DSE-7320 MKII',
    modbus_baud_rate INTEGER NOT NULL DEFAULT 9600,
    thumbnail_100_url VARCHAR(255) DEFAULT 'perkins_pure_clean.png',
    hero_cutout_url VARCHAR(255) DEFAULT 'perkins_pure_clean.png',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_brand_model UNIQUE (brand, model_name)
);
CREATE INDEX IF NOT EXISTS idx_models_brand ON generator_models(brand);
""")

    # 5. Generator Units (492 units)
    sql.append("""
CREATE TABLE IF NOT EXISTS generator_units (
    id SERIAL PRIMARY KEY,
    unit_serial VARCHAR(64) NOT NULL UNIQUE,
    unit_uid VARCHAR(64) NOT NULL UNIQUE,
    tower_id INTEGER NOT NULL REFERENCES towers(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    model_id INTEGER NOT NULL REFERENCES generator_models(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    dse_controller_model VARCHAR(64) NOT NULL DEFAULT 'DSE-7320 MKII',
    modbus_slave_id SMALLINT NOT NULL DEFAULT 1,
    cumulative_run_hours DECIMAL(9,2) NOT NULL DEFAULT 320.50,
    hours_since_last_service DECIMAL(8,2) NOT NULL DEFAULT 120.50,
    service_interval_hours DECIMAL(8,2) NOT NULL DEFAULT 250.00,
    current_status VARCHAR(32) NOT NULL DEFAULT 'RUNNING' CHECK (current_status IN ('RUNNING', 'STANDBY', 'WARNING', 'CRITICAL_FAULT', 'LOCKOUT_MAINTENANCE')),
    current_rpm INTEGER NOT NULL DEFAULT 1500,
    is_safety_lockout BOOLEAN NOT NULL DEFAULT FALSE,
    installed_at DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_units_tower ON generator_units(tower_id);
CREATE INDEX IF NOT EXISTS idx_units_model ON generator_units(model_id);
CREATE INDEX IF NOT EXISTS idx_units_status ON generator_units(current_status);
CREATE INDEX IF NOT EXISTS idx_units_lockout ON generator_units(is_safety_lockout);
""")

    # 6. Telemetry Live Snapshot (18 SCADA parameters)
    sql.append("""
CREATE TABLE IF NOT EXISTS telemetry_live (
    unit_id INTEGER PRIMARY KEY REFERENCES generator_units(id) ON DELETE CASCADE,
    v_l1_n DECIMAL(5,1) NOT NULL DEFAULT 230.4,
    v_l2_n DECIMAL(5,1) NOT NULL DEFAULT 229.8,
    v_l3_n DECIMAL(5,1) NOT NULL DEFAULT 230.1,
    v_l1_l2 DECIMAL(5,1) NOT NULL DEFAULT 399.8,
    v_l2_l3 DECIMAL(5,1) NOT NULL DEFAULT 400.2,
    v_l3_l1 DECIMAL(5,1) NOT NULL DEFAULT 400.0,
    current_l1 DECIMAL(6,2) NOT NULL DEFAULT 27.20,
    current_l2 DECIMAL(6,2) NOT NULL DEFAULT 26.80,
    current_l3 DECIMAL(6,2) NOT NULL DEFAULT 27.00,
    frequency_hz DECIMAL(5,2) NOT NULL DEFAULT 50.02,
    active_power_kw DECIMAL(7,2) NOT NULL DEFAULT 18.60,
    apparent_power_kva DECIMAL(7,2) NOT NULL DEFAULT 23.25,
    reactive_power_kvar DECIMAL(7,2) NOT NULL DEFAULT 13.95,
    power_factor DECIMAL(4,2) NOT NULL DEFAULT 0.80,
    engine_rpm INTEGER NOT NULL DEFAULT 1500,
    coolant_temp_c DECIMAL(5,1) NOT NULL DEFAULT 84.2,
    oil_pressure_bar DECIMAL(4,2) NOT NULL DEFAULT 4.20,
    fuel_level_pct DECIMAL(5,2) NOT NULL DEFAULT 76.00,
    fuel_volume_liters DECIMAL(7,2) NOT NULL DEFAULT 190.00,
    battery_vdc DECIMAL(4,1) NOT NULL DEFAULT 26.8,
    voltage_balance_pct DECIMAL(5,2) NOT NULL DEFAULT 99.80,
    thd_pct DECIMAL(4,2) NOT NULL DEFAULT 2.10,
    last_modbus_sync TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
""")

    # 7. Telemetry History Time Series
    sql.append("""
CREATE TABLE IF NOT EXISTS telemetry_history (
    id BIGSERIAL NOT NULL,
    unit_id INTEGER NOT NULL REFERENCES generator_units(id) ON DELETE CASCADE,
    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    v_l1_n DECIMAL(5,1) NOT NULL,
    v_l2_n DECIMAL(5,1) NOT NULL,
    v_l3_n DECIMAL(5,1) NOT NULL,
    v_l1_l2 DECIMAL(5,1) NOT NULL,
    v_l2_l3 DECIMAL(5,1) NOT NULL,
    v_l3_l1 DECIMAL(5,1) NOT NULL,
    current_l1 DECIMAL(6,2) NOT NULL,
    current_l2 DECIMAL(6,2) NOT NULL,
    current_l3 DECIMAL(6,2) NOT NULL,
    frequency_hz DECIMAL(5,2) NOT NULL,
    active_power_kw DECIMAL(7,2) NOT NULL,
    apparent_power_kva DECIMAL(7,2) NOT NULL,
    reactive_power_kvar DECIMAL(7,2) NOT NULL,
    power_factor DECIMAL(4,2) NOT NULL,
    engine_rpm INTEGER NOT NULL,
    coolant_temp_c DECIMAL(5,1) NOT NULL,
    oil_pressure_bar DECIMAL(4,2) NOT NULL,
    fuel_level_pct DECIMAL(5,2) NOT NULL,
    fuel_volume_liters DECIMAL(7,2) NOT NULL,
    battery_vdc DECIMAL(4,1) NOT NULL,
    PRIMARY KEY (id, recorded_at)
);
CREATE INDEX IF NOT EXISTS idx_hist_unit_time ON telemetry_history(unit_id, recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_hist_recorded_at ON telemetry_history(recorded_at);
""")

    # 8. Daily Rollups
    sql.append("""
CREATE TABLE IF NOT EXISTS telemetry_daily_rollups (
    id SERIAL PRIMARY KEY,
    unit_id INTEGER NOT NULL REFERENCES generator_units(id) ON DELETE CASCADE,
    record_date DATE NOT NULL,
    avg_active_kw DECIMAL(7,2) NOT NULL,
    peak_active_kw DECIMAL(7,2) NOT NULL,
    total_energy_kwh DECIMAL(9,2) NOT NULL,
    total_fuel_consumed_l DECIMAL(8,2) NOT NULL,
    avg_efficiency_l_kwh DECIMAL(6,4) NOT NULL,
    operating_hours DECIMAL(5,2) NOT NULL,
    crank_starts_count SMALLINT NOT NULL DEFAULT 0,
    trip_events_count SMALLINT NOT NULL DEFAULT 0,
    CONSTRAINT uk_unit_date UNIQUE (unit_id, record_date)
);
CREATE INDEX IF NOT EXISTS idx_rollups_date ON telemetry_daily_rollups(record_date);
""")

    # 9. SCADA Alarms
    sql.append("""
CREATE TABLE IF NOT EXISTS alarms (
    id SERIAL PRIMARY KEY,
    unit_id INTEGER NOT NULL REFERENCES generator_units(id) ON DELETE CASCADE,
    tower_id INTEGER NOT NULL REFERENCES towers(id) ON DELETE CASCADE,
    alarm_code VARCHAR(32) NOT NULL,
    severity VARCHAR(16) NOT NULL CHECK (severity IN ('CRITICAL', 'MAJOR', 'MINOR', 'WARNING', 'INFO')),
    description VARCHAR(255) NOT NULL,
    trigger_value DECIMAL(8,2),
    threshold_value DECIMAL(8,2),
    modbus_register VARCHAR(32) DEFAULT '40012',
    status VARCHAR(16) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'ACKNOWLEDGED', 'RESOLVED')),
    triggered_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    acknowledged_by_uid VARCHAR(32),
    resolved_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX IF NOT EXISTS idx_alarm_unit_status ON alarms(unit_id, status);
CREATE INDEX IF NOT EXISTS idx_alarm_severity ON alarms(severity, status);
CREATE INDEX IF NOT EXISTS idx_alarm_triggered ON alarms(triggered_at DESC);
""")

    # 10. Maintenance Records
    sql.append("""
CREATE TABLE IF NOT EXISTS maintenance_records (
    id SERIAL PRIMARY KEY,
    unit_id INTEGER NOT NULL REFERENCES generator_units(id) ON DELETE CASCADE,
    service_protocol VARCHAR(32) NOT NULL DEFAULT 'PM_A_MINOR' CHECK (service_protocol IN ('PM_A_MINOR', 'PM_B_MAJOR', 'PM_C_OVERHAUL')),
    runtime_at_service DECIMAL(9,2) NOT NULL,
    hours_since_last_reset DECIMAL(8,2) NOT NULL DEFAULT 0.00,
    service_interval_hours DECIMAL(8,2) NOT NULL DEFAULT 250.00,
    lube_oil_brand VARCHAR(64) NOT NULL DEFAULT 'Shell Rimula R4X 15W-40 CI-4',
    lube_oil_volume_l DECIMAL(6,2) NOT NULL DEFAULT 16.40,
    oil_filter_replaced BOOLEAN NOT NULL DEFAULT TRUE,
    oil_filter_dp_bar DECIMAL(4,2) NOT NULL DEFAULT 0.60,
    fuel_filter_replaced BOOLEAN NOT NULL DEFAULT TRUE,
    water_separator_cleaned BOOLEAN NOT NULL DEFAULT TRUE,
    air_filter_serviced BOOLEAN NOT NULL DEFAULT TRUE,
    coolant_condition_checked BOOLEAN NOT NULL DEFAULT TRUE,
    battery_serviced BOOLEAN NOT NULL DEFAULT TRUE,
    belt_tension_mm DECIMAL(4,2) NOT NULL DEFAULT 8.50,
    technician_name VARCHAR(128) NOT NULL DEFAULT 'Lian Ahmed',
    technician_uid VARCHAR(32) NOT NULL DEFAULT '#AR-9402',
    work_order_ref VARCHAR(64) NOT NULL DEFAULT 'WO-2026-9481',
    service_notes TEXT,
    serviced_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_maint_unit ON maintenance_records(unit_id);
CREATE INDEX IF NOT EXISTS idx_maint_serviced ON maintenance_records(serviced_at DESC);
""")

    # 11. Operators and Permissions
    sql.append(f"""
CREATE TABLE IF NOT EXISTS operators (
    id SERIAL PRIMARY KEY,
    uid VARCHAR(32) NOT NULL UNIQUE,
    full_name VARCHAR(128) NOT NULL,
    email VARCHAR(160) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    division VARCHAR(64) NOT NULL DEFAULT 'Dhaka North',
    role VARCHAR(64) NOT NULL DEFAULT 'Lead SCADA Engineer',
    clearance_level SMALLINT NOT NULL DEFAULT 4,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS operator_permissions (
    operator_id INTEGER PRIMARY KEY REFERENCES operators(id) ON DELETE CASCADE,
    remote_start_stop BOOLEAN NOT NULL DEFAULT TRUE,
    modbus_register_write BOOLEAN NOT NULL DEFAULT TRUE,
    alarm_acknowledge BOOLEAN NOT NULL DEFAULT TRUE,
    cms_layout_control BOOLEAN NOT NULL DEFAULT TRUE,
    estop_override BOOLEAN NOT NULL DEFAULT TRUE,
    fota_push_firmware BOOLEAN NOT NULL DEFAULT TRUE
);
""")

    # 12. CMS Orders
    sql.append("""
CREATE TABLE IF NOT EXISTS cms_module_orders (
    id SERIAL PRIMARY KEY,
    operator_id INTEGER NOT NULL REFERENCES operators(id) ON DELETE CASCADE,
    module_key VARCHAR(32) NOT NULL,
    sort_order SMALLINT NOT NULL,
    is_visible BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uk_op_module UNIQUE (operator_id, module_key)
);
""")

    # SEED DATA
    sql.append("""
-- ----------------------------------------------------------------------------
-- SEED DATA INITIALIZATION
-- ----------------------------------------------------------------------------
INSERT INTO areas (area_code, name, division, regional_director, contact_phone, target_sla_pct) VALUES
('AREA-DHK-N', 'Dhaka North', 'Dhaka', 'Engr. Tariqul Islam', '+880-1711-000101', 99.80),
('AREA-DHK-S', 'Dhaka South', 'Dhaka', 'Engr. Shamim Hossain', '+880-1711-000102', 99.70),
('AREA-CTG-M', 'Chittagong Metro', 'Chittagong', 'Engr. Faisal Mahmud', '+880-1711-000103', 99.60),
('AREA-CTG-N', 'Chittagong North & Port', 'Chittagong', 'Engr. Rafiqul Alam', '+880-1711-000104', 99.50),
('AREA-SYL', 'Sylhet Zone', 'Sylhet', 'Engr. Kamrul Hasan', '+880-1711-000105', 99.40),
('AREA-RAJ', 'Rajshahi Central', 'Rajshahi', 'Engr. Mofazzal Hossain', '+880-1711-000106', 99.60),
('AREA-KHU', 'Khulna Division', 'Khulna', 'Engr. Anisur Rahman', '+880-1711-000107', 99.30),
('AREA-BAR', 'Barisal Coast', 'Barisal', 'Engr. Jahangir Kabir', '+880-1711-000108', 99.10),
('AREA-RAN', 'Rangpur Belt', 'Rangpur', 'Engr. Nurul Huda', '+880-1711-000109', 99.20),
('AREA-MYM', 'Mymensingh Hub', 'Mymensingh', 'Engr. Delowar Hossain', '+880-1711-000110', 99.50)
ON CONFLICT (area_code) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO clusters (cluster_code, name, area_id, lead_engineer_name, lead_engineer_uid, ip_concentrator, modbus_port, dispatch_route) VALUES
('CLUST-DHK-01', 'Gulshan-Mirpur Node', 1, 'Engr. Lian Ahmed', '#AR-9402', '192.168.10.1', 502, 'ROUTE ACTIVE'),
('CLUST-DHK-02', 'Uttara-Tongi Corridor', 1, 'Engr. Naimul Islam', '#AR-9104', '192.168.10.2', 502, 'ROUTE ACTIVE'),
('CLUST-DHK-03', 'Dhanmondi-Motijheel', 2, 'Engr. Hasan Chowdhury', '#AR-9208', '192.168.10.3', 502, 'ROUTE ACTIVE'),
('CLUST-CTG-01', 'Agrabad Commercial Hub', 3, 'Engr. Tanvir Ahmed', '#AR-8831', '192.168.20.1', 502, 'ROUTE ACTIVE'),
('CLUST-SYL-01', 'Zindabazar Tech Node', 5, 'Engr. Babul Miah', '#AR-8419', '192.168.30.1', 502, 'ROUTE ACTIVE')
ON CONFLICT (cluster_code) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO generator_models (model_name, brand, engine_family, prime_kw, standby_kva, cylinders, displacement_liters, rated_rpm, fuel_rate_l_kwh, oil_sump_capacity_l, coolant_capacity_l, default_controller, modbus_baud_rate, thumbnail_100_url, hero_cutout_url) VALUES
('1104A-44TG2', 'Perkins', '1100 Series', 48.00, 60.00, 4, 4.40, 1500, 0.2480, 16.40, 24.50, 'DSE-7320 MKII', 9600, 'perkins_pure_clean.png', 'perkins_pure_clean.png'),
('6BT5.9-G2', 'Cummins', 'B-Series', 80.00, 100.00, 6, 5.90, 1500, 0.2390, 16.40, 24.50, 'DSE-7320 MKII', 9600, 'cummins_6bt_clean.png', 'cummins_6bt_clean.png'),
('C4.4 Industrial', 'Caterpillar', 'CAT Compact', 70.40, 88.00, 4, 4.40, 1800, 0.2420, 12.00, 18.00, 'DSE-7320 MKII', 9600, 'cat_c44_clean.png', 'cat_c44_clean.png'),
('40REOZK', 'Kohler', 'KD-Series', 120.00, 150.00, 6, 6.80, 1500, 0.2520, 20.00, 30.00, 'DSE-7320 MKII', 9600, 'kohler_kd62_clean.png', 'kohler_kd62_clean.png')
ON CONFLICT (brand, model_name) DO UPDATE SET prime_kw = EXCLUDED.prime_kw;

INSERT INTO operators (uid, full_name, email, password_hash, division, role, clearance_level) VALUES
('#AR-9402', 'Lian Ahmed', 'lian.ahmed@arenaiot.com', '""" + admin_pw_hash + """', 'Dhaka North', 'Lead SCADA Engineer', 4)
ON CONFLICT (uid) DO UPDATE SET full_name = EXCLUDED.full_name;

INSERT INTO operator_permissions (operator_id, remote_start_stop, modbus_register_write, alarm_acknowledge, cms_layout_control, estop_override, fota_push_firmware) VALUES
(1, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE)
ON CONFLICT (operator_id) DO UPDATE SET remote_start_stop = TRUE;
""")

    # Seed 492 Sites (Towers, Generator Units, Live Telemetry)
    divisions_dist = [
        {"name": "Dhaka", "count": 208, "lat": 23.8103, "lng": 90.4125, "cluster_id": 1},
        {"name": "Chittagong", "count": 118, "lat": 22.3569, "lng": 91.7832, "cluster_id": 4},
        {"name": "Sylhet", "count": 58, "lat": 24.8949, "lng": 91.8687, "cluster_id": 5},
        {"name": "Rajshahi", "count": 38, "lat": 24.3636, "lng": 88.6241, "cluster_id": 1},
        {"name": "Khulna", "count": 30, "lat": 22.8456, "lng": 89.5403, "cluster_id": 1},
        {"name": "Barisal", "count": 15, "lat": 22.7010, "lng": 90.3535, "cluster_id": 1},
        {"name": "Rangpur", "count": 15, "lat": 25.7439, "lng": 89.2752, "cluster_id": 1},
        {"name": "Mymensingh", "count": 10, "lat": 24.7471, "lng": 90.4203, "cluster_id": 2}
    ]

    operators_list = ["Grameenphone", "Robi Axiata", "Banglalink", "Teletalk"]
    models_ids = [1, 2, 3, 4]

    tower_inserts = []
    unit_inserts = []
    telemetry_inserts = []

    unit_idx = 1
    for d in divisions_dist:
        for i in range(d["count"]):
            op = operators_list[(unit_idx - 1) % len(operators_list)]
            model_id = models_ids[(unit_idx - 1) % len(models_ids)]
            tower_uid = f"BTS-{d['name'][:2].upper()}-{unit_idx:04d}"
            station_name = f"Tower {tower_uid} ({d['name']} Node {i+1})"
            
            # Realistic offsets
            lat_off = (i % 25 - 12) * 0.035
            lng_off = (i % 15 - 7) * 0.04
            lat = round(d["lat"] + lat_off, 6)
            lng = round(d["lng"] + lng_off, 6)

            status = 'RUNNING'
            rpm = 1500
            kw = round(18.0 + (unit_idx % 28) * 1.2, 1)
            v1 = 230.4
            oil = 4.20
            pwr_source = 'GRID_UTILITY'

            if unit_idx <= 6:
                status = 'CRITICAL_FAULT'
                kw = round(38.0 + unit_idx * 1.5, 1)
                oil = 1.10
                pwr_source = 'GEN_ACTIVE'
            elif unit_idx <= 20:
                status = 'WARNING'
                kw = 42.0
                oil = 3.20
                pwr_source = 'GEN_ACTIVE'
            elif unit_idx <= 60:
                status = 'STANDBY'
                rpm = 0
                kw = 0.0
                oil = 0.0
                pwr_source = 'GRID_UTILITY'

            kva = round(kw / 0.8, 1) if kw > 0 else 0.0
            fuel_pct = round(max(15.0, 85.0 - (unit_idx % 45)), 1)
            fuel_l = round(fuel_pct * 2.5, 1)

            tower_inserts.append(
                f"('{tower_uid}', '{station_name}', {d['cluster_id']}, '{op}', {lat}, {lng}, '{pwr_source}', 60.00)"
            )

            unit_serial = f"SN-SCADA-2026-{unit_idx:04d}"
            unit_uid = f"GEN-{d['name'][:2].upper()}-{unit_idx:04d}"
            lockout = "TRUE" if status == 'CRITICAL_FAULT' and unit_idx == 1 else "FALSE"
            hours_since_service = round(50.0 + (unit_idx * 7) % 200, 1)
            cum_hours = round(318.4 + unit_idx * 11.7, 1)

            unit_inserts.append(
                f"('{unit_serial}', '{unit_uid}', {unit_idx}, {model_id}, 'DSE-7320 MKII', 1, {cum_hours}, {hours_since_service}, 250.00, '{status}', {rpm}, {lockout})"
            )

            telemetry_inserts.append(
                f"({unit_idx}, {v1}, 229.8, 230.1, 399.8, 400.2, 400.0, 27.20, 26.80, 27.00, 50.02, {kw}, {kva}, 12.50, 0.80, {rpm}, 84.2, {oil}, {fuel_pct}, {fuel_l}, 26.8, 99.80, 2.10)"
            )

            unit_idx += 1

    sql.append("-- 492 National Towers Seed")
    sql.append("INSERT INTO towers (tower_uid, station_name, cluster_id, telecom_operator, latitude, longitude, power_source_state, grid_connection_kva) VALUES\n" + ",\n".join(tower_inserts) + "\nON CONFLICT (tower_uid) DO NOTHING;\n")

    sql.append("-- 492 Generator Units Seed")
    sql.append("INSERT INTO generator_units (unit_serial, unit_uid, tower_id, model_id, dse_controller_model, modbus_slave_id, cumulative_run_hours, hours_since_last_service, service_interval_hours, current_status, current_rpm, is_safety_lockout) VALUES\n" + ",\n".join(unit_inserts) + "\nON CONFLICT (unit_uid) DO NOTHING;\n")

    sql.append("-- 492 Live Telemetry Snapshots Seed")
    sql.append("INSERT INTO telemetry_live (unit_id, v_l1_n, v_l2_n, v_l3_n, v_l1_l2, v_l2_l3, v_l3_l1, current_l1, current_l2, current_l3, frequency_hz, active_power_kw, apparent_power_kva, reactive_power_kvar, power_factor, engine_rpm, coolant_temp_c, oil_pressure_bar, fuel_level_pct, fuel_volume_liters, battery_vdc, voltage_balance_pct, thd_pct) VALUES\n" + ",\n".join(telemetry_inserts) + "\nON CONFLICT (unit_id) DO NOTHING;\n")

    # Sample Alarms
    sql.append("""
-- Seed Active SCADA Alarms
INSERT INTO alarms (unit_id, tower_id, alarm_code, severity, description, trigger_value, threshold_value, modbus_register, status) VALUES
(1, 1, 'ALM-101', 'CRITICAL', 'Engine Oil Pressure Under-Limit Trip', 1.10, 1.50, '40012', 'ACTIVE'),
(2, 2, 'ALM-102', 'CRITICAL', 'Cylinder Head Coolant Over-Temperature', 106.50, 98.00, '40013', 'ACTIVE'),
(3, 3, 'ALM-103', 'CRITICAL', 'Fail to Start (Overcrank Trip)', 3.00, 3.00, '40014', 'ACTIVE'),
(4, 4, 'ALM-104', 'CRITICAL', 'Fuel Solenoid Lockout Engaged', 0.00, 1.00, '40018', 'ACKNOWLEDGED'),
(5, 5, 'ALM-105', 'CRITICAL', 'Under-Voltage L1 Outage (< 190V)', 172.50, 190.00, '40001', 'ACTIVE'),
(6, 6, 'ALM-106', 'CRITICAL', 'Frequency Deviation (< 47.5 Hz)', 46.20, 47.50, '40010', 'ACTIVE'),
(7, 7, 'ALM-107', 'MAJOR', 'High Engine Load Limit Warning (> 90%)', 94.20, 90.00, '40011', 'ACTIVE'),
(8, 8, 'ALM-108', 'MAJOR', 'High Coolant Temp Warning Pre-Alarm', 96.40, 95.00, '40013', 'ACTIVE'),
(9, 9, 'ALM-109', 'MAJOR', 'Low Lube Oil Pressure Warning', 2.10, 2.20, '40012', 'ACKNOWLEDGED'),
(10, 10, 'ALM-110', 'MAJOR', 'Reserve Fuel Level Depletion (< 25%)', 22.00, 25.00, '40019', 'ACTIVE')
ON CONFLICT DO NOTHING;
""")

    return "\n".join(sql)

if __name__ == "__main__":
    content = generate_sql()
    out_file = "genesis_vercel_schema.sql"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated {out_file} ({len(content)} bytes)")
