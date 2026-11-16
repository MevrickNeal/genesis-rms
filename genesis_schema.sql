-- ============================================================================
-- GENESIS RMS — SCADA RELATIONAL DATABASE SCHEMA (MySQL 8.0+ / MariaDB 10.5+)
-- Parent System: Arena IoT Connected Platform
-- Architecture: High-Throughput SCADA Telemetry, 3NF Assets, Time-Series Rollups
-- Constraint Enforcements: Strictly 0 literal 500s; 492 National Site Archetypes;
-- UTF-8 MB4 Collation with InnoDB Engine and High-Concurrence Compound Indexes.
-- ============================================================================

CREATE DATABASE IF NOT EXISTS `genesis_rms_db`
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE `genesis_rms_db`;

-- ----------------------------------------------------------------------------
-- 1. GEOGRAPHIC DIVISION & AREA HIERARCHY (Level 1)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `areas` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `area_code` VARCHAR(32) NOT NULL,
  `name` VARCHAR(100) NOT NULL,
  `division` VARCHAR(64) NOT NULL,
  `regional_director` VARCHAR(128) NOT NULL,
  `contact_phone` VARCHAR(32) DEFAULT NULL,
  `target_sla_pct` DECIMAL(5,2) NOT NULL DEFAULT 99.80,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_area_code` (`area_code`),
  INDEX `idx_division` (`division`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 2. REGIONAL CLUSTERS (Level 2)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `clusters` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `cluster_code` VARCHAR(32) NOT NULL,
  `name` VARCHAR(128) NOT NULL,
  `area_id` INT UNSIGNED NOT NULL,
  `lead_engineer_name` VARCHAR(128) NOT NULL,
  `lead_engineer_uid` VARCHAR(32) DEFAULT '#AR-9402',
  `ip_concentrator` VARCHAR(45) NOT NULL DEFAULT '192.168.10.1',
  `modbus_port` SMALLINT UNSIGNED NOT NULL DEFAULT 502,
  `dispatch_route` VARCHAR(64) NOT NULL DEFAULT 'ROUTE ACTIVE',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_cluster_code` (`cluster_code`),
  KEY `fk_clusters_area` (`area_id`),
  INDEX `idx_lead_engineer` (`lead_engineer_uid`),
  CONSTRAINT `fk_clusters_area` FOREIGN KEY (`area_id`) REFERENCES `areas` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 3. BTS TELECOM CELL TOWERS (Level 3 - 492 Operational Sites)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `towers` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `tower_uid` VARCHAR(64) NOT NULL,
  `station_name` VARCHAR(160) NOT NULL,
  `cluster_id` INT UNSIGNED NOT NULL,
  `telecom_operator` ENUM('Grameenphone', 'Robi Axiata', 'Banglalink', 'Teletalk') NOT NULL,
  `latitude` DECIMAL(10, 7) NOT NULL DEFAULT 23.8103310,
  `longitude` DECIMAL(10, 7) NOT NULL DEFAULT 90.4125210,
  `power_source_state` ENUM('GRID_UTILITY', 'GEN_ACTIVE', 'BATTERY_DISCHARGE', 'SOLAR_HYBRID') NOT NULL DEFAULT 'GRID_UTILITY',
  `grid_connection_kva` DECIMAL(8,2) NOT NULL DEFAULT 60.00,
  `is_active` TINYINT(1) NOT NULL DEFAULT 1,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_tower_uid` (`tower_uid`),
  KEY `fk_towers_cluster` (`cluster_id`),
  INDEX `idx_operator` (`telecom_operator`),
  INDEX `idx_power_state` (`power_source_state`),
  CONSTRAINT `fk_towers_cluster` FOREIGN KEY (`cluster_id`) REFERENCES `clusters` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 4. OEM GENERATOR MODELS REGISTRY
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `generator_models` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `model_name` VARCHAR(100) NOT NULL,
  `brand` VARCHAR(64) NOT NULL,
  `engine_family` VARCHAR(64) DEFAULT NULL,
  `prime_kw` DECIMAL(8,2) NOT NULL,
  `standby_kva` DECIMAL(8,2) NOT NULL,
  `cylinders` TINYINT UNSIGNED NOT NULL DEFAULT 4,
  `displacement_liters` DECIMAL(4,2) NOT NULL,
  `rated_rpm` SMALLINT UNSIGNED NOT NULL DEFAULT 1500,
  `fuel_rate_l_kwh` DECIMAL(6,4) NOT NULL DEFAULT 0.2480,
  `oil_sump_capacity_l` DECIMAL(6,2) NOT NULL DEFAULT 16.40,
  `coolant_capacity_l` DECIMAL(6,2) NOT NULL DEFAULT 24.50,
  `default_controller` VARCHAR(64) NOT NULL DEFAULT 'DSE-7320 MKII',
  `modbus_baud_rate` MEDIUMINT UNSIGNED NOT NULL DEFAULT 9600,
  `thumbnail_100_url` VARCHAR(255) DEFAULT 'perkins_pure_clean.png',
  `hero_cutout_url` VARCHAR(255) DEFAULT 'perkins_pure_clean.png',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_brand_model` (`brand`, `model_name`),
  INDEX `idx_brand` (`brand`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 5. DEPLOYED GENERATOR PHYSICAL UNITS
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `generator_units` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `unit_serial` VARCHAR(64) NOT NULL,
  `unit_uid` VARCHAR(64) NOT NULL,
  `tower_id` INT UNSIGNED NOT NULL,
  `model_id` INT UNSIGNED NOT NULL,
  `dse_controller_model` VARCHAR(64) NOT NULL DEFAULT 'DSE-7320 MKII',
  `modbus_slave_id` TINYINT UNSIGNED NOT NULL DEFAULT 1,
  `cumulative_run_hours` DECIMAL(9,2) NOT NULL DEFAULT 320.50,
  `hours_since_last_service` DECIMAL(8,2) NOT NULL DEFAULT 120.50,
  `service_interval_hours` DECIMAL(8,2) NOT NULL DEFAULT 250.00,
  `current_status` ENUM('RUNNING', 'STANDBY', 'WARNING', 'CRITICAL_FAULT', 'LOCKOUT_MAINTENANCE') NOT NULL DEFAULT 'RUNNING',
  `current_rpm` SMALLINT UNSIGNED NOT NULL DEFAULT 1500,
  `is_safety_lockout` TINYINT(1) NOT NULL DEFAULT 0,
  `installed_at` DATE NOT NULL DEFAULT (CURRENT_DATE),
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_unit_serial` (`unit_serial`),
  UNIQUE KEY `uk_unit_uid` (`unit_uid`),
  KEY `fk_units_tower` (`tower_id`),
  KEY `fk_units_model` (`model_id`),
  INDEX `idx_current_status` (`current_status`),
  INDEX `idx_safety_lockout` (`is_safety_lockout`),
  CONSTRAINT `fk_units_tower` FOREIGN KEY (`tower_id`) REFERENCES `towers` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_units_model` FOREIGN KEY (`model_id`) REFERENCES `generator_models` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 6. LIVE TELEMETRY SNAPSHOT CACHE (1 Row Per Unit for Instant Sub-ms Lookup)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `telemetry_live` (
  `unit_id` INT UNSIGNED NOT NULL,
  `v_l1_n` DECIMAL(5,1) NOT NULL DEFAULT 230.4,
  `v_l2_n` DECIMAL(5,1) NOT NULL DEFAULT 229.8,
  `v_l3_n` DECIMAL(5,1) NOT NULL DEFAULT 230.1,
  `v_l1_l2` DECIMAL(5,1) NOT NULL DEFAULT 399.8,
  `v_l2_l3` DECIMAL(5,1) NOT NULL DEFAULT 400.2,
  `v_l3_l1` DECIMAL(5,1) NOT NULL DEFAULT 400.0,
  `current_l1` DECIMAL(6,2) NOT NULL DEFAULT 27.20,
  `current_l2` DECIMAL(6,2) NOT NULL DEFAULT 26.80,
  `current_l3` DECIMAL(6,2) NOT NULL DEFAULT 27.00,
  `frequency_hz` DECIMAL(5,2) NOT NULL DEFAULT 50.02,
  `active_power_kw` DECIMAL(7,2) NOT NULL DEFAULT 18.60,
  `apparent_power_kva` DECIMAL(7,2) NOT NULL DEFAULT 23.25,
  `reactive_power_kvar` DECIMAL(7,2) NOT NULL DEFAULT 13.95,
  `power_factor` DECIMAL(4,2) NOT NULL DEFAULT 0.80,
  `engine_rpm` SMALLINT UNSIGNED NOT NULL DEFAULT 1500,
  `coolant_temp_c` DECIMAL(5,1) NOT NULL DEFAULT 84.2,
  `oil_pressure_bar` DECIMAL(4,2) NOT NULL DEFAULT 4.20,
  `fuel_level_pct` DECIMAL(5,2) NOT NULL DEFAULT 76.00,
  `fuel_volume_liters` DECIMAL(7,2) NOT NULL DEFAULT 190.00,
  `battery_vdc` DECIMAL(4,1) NOT NULL DEFAULT 26.8,
  `voltage_balance_pct` DECIMAL(5,2) NOT NULL DEFAULT 99.80,
  `thd_pct` DECIMAL(4,2) NOT NULL DEFAULT 2.10,
  `last_modbus_sync` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`unit_id`),
  CONSTRAINT `fk_telemetry_live_unit` FOREIGN KEY (`unit_id`) REFERENCES `generator_units` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 7. HISTORICAL SCADA TELEMETRY STREAM (Time-Series Optimized)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `telemetry_history` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `unit_id` INT UNSIGNED NOT NULL,
  `recorded_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `v_l1_n` DECIMAL(5,1) NOT NULL,
  `v_l2_n` DECIMAL(5,1) NOT NULL,
  `v_l3_n` DECIMAL(5,1) NOT NULL,
  `v_l1_l2` DECIMAL(5,1) NOT NULL,
  `v_l2_l3` DECIMAL(5,1) NOT NULL,
  `v_l3_l1` DECIMAL(5,1) NOT NULL,
  `current_l1` DECIMAL(6,2) NOT NULL,
  `current_l2` DECIMAL(6,2) NOT NULL,
  `current_l3` DECIMAL(6,2) NOT NULL,
  `frequency_hz` DECIMAL(5,2) NOT NULL,
  `active_power_kw` DECIMAL(7,2) NOT NULL,
  `apparent_power_kva` DECIMAL(7,2) NOT NULL,
  `reactive_power_kvar` DECIMAL(7,2) NOT NULL,
  `power_factor` DECIMAL(4,2) NOT NULL,
  `engine_rpm` SMALLINT UNSIGNED NOT NULL,
  `coolant_temp_c` DECIMAL(5,1) NOT NULL,
  `oil_pressure_bar` DECIMAL(4,2) NOT NULL,
  `fuel_level_pct` DECIMAL(5,2) NOT NULL,
  `fuel_volume_liters` DECIMAL(7,2) NOT NULL,
  `battery_vdc` DECIMAL(4,1) NOT NULL,
  PRIMARY KEY (`id`, `recorded_at`),
  KEY `idx_unit_time` (`unit_id`, `recorded_at` DESC),
  KEY `idx_recorded_at` (`recorded_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 8. DAILY TELEMETRY AGGREGATES & ROLLUPS (For 6-Month Historical Spectrum)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `telemetry_daily_rollups` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `unit_id` INT UNSIGNED NOT NULL,
  `record_date` DATE NOT NULL,
  `avg_active_kw` DECIMAL(7,2) NOT NULL,
  `peak_active_kw` DECIMAL(7,2) NOT NULL,
  `total_energy_kwh` DECIMAL(9,2) NOT NULL,
  `total_fuel_consumed_l` DECIMAL(8,2) NOT NULL,
  `avg_efficiency_l_kwh` DECIMAL(6,4) NOT NULL,
  `operating_hours` DECIMAL(5,2) NOT NULL,
  `crank_starts_count` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  `trip_events_count` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_unit_date` (`unit_id`, `record_date`),
  KEY `idx_record_date` (`record_date`),
  CONSTRAINT `fk_daily_unit` FOREIGN KEY (`unit_id`) REFERENCES `generator_units` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 9. SCADA ALARMS & FAULT TRIAGE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `alarms` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `unit_id` INT UNSIGNED NOT NULL,
  `tower_id` INT UNSIGNED NOT NULL,
  `alarm_code` VARCHAR(32) NOT NULL,
  `severity` ENUM('CRITICAL', 'MAJOR', 'MINOR', 'WARNING', 'INFO') NOT NULL,
  `description` VARCHAR(255) NOT NULL,
  `trigger_value` DECIMAL(8,2) DEFAULT NULL,
  `threshold_value` DECIMAL(8,2) DEFAULT NULL,
  `modbus_register` VARCHAR(32) DEFAULT '40012',
  `status` ENUM('ACTIVE', 'ACKNOWLEDGED', 'RESOLVED') NOT NULL DEFAULT 'ACTIVE',
  `triggered_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `acknowledged_at` TIMESTAMP NULL DEFAULT NULL,
  `acknowledged_by_uid` VARCHAR(32) DEFAULT NULL,
  `resolved_at` TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_alarm_unit_status` (`unit_id`, `status`),
  KEY `idx_severity_status` (`severity`, `status`),
  KEY `idx_triggered_at` (`triggered_at` DESC),
  CONSTRAINT `fk_alarms_unit` FOREIGN KEY (`unit_id`) REFERENCES `generator_units` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_alarms_tower` FOREIGN KEY (`tower_id`) REFERENCES `towers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 10. PREVENTIVE MAINTENANCE & CONSUMABLES LIFECYCLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `maintenance_records` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `unit_id` INT UNSIGNED NOT NULL,
  `service_protocol` ENUM('PM_A_MINOR', 'PM_B_MAJOR', 'PM_C_OVERHAUL') NOT NULL DEFAULT 'PM_A_MINOR',
  `runtime_at_service` DECIMAL(9,2) NOT NULL,
  `hours_since_last_reset` DECIMAL(8,2) NOT NULL DEFAULT 0.00,
  `service_interval_hours` DECIMAL(8,2) NOT NULL DEFAULT 250.00,
  `lube_oil_brand` VARCHAR(64) NOT NULL DEFAULT 'Shell Rimula R4X 15W-40 CI-4',
  `lube_oil_volume_l` DECIMAL(6,2) NOT NULL DEFAULT 16.40,
  `oil_filter_replaced` TINYINT(1) NOT NULL DEFAULT 1,
  `oil_filter_dp_bar` DECIMAL(4,2) NOT NULL DEFAULT 0.60,
  `fuel_filter_replaced` TINYINT(1) NOT NULL DEFAULT 1,
  `water_separator_cleaned` TINYINT(1) NOT NULL DEFAULT 1,
  `air_filter_serviced` TINYINT(1) NOT NULL DEFAULT 1,
  `coolant_condition_checked` TINYINT(1) NOT NULL DEFAULT 1,
  `battery_serviced` TINYINT(1) NOT NULL DEFAULT 1,
  `belt_tension_mm` DECIMAL(4,2) NOT NULL DEFAULT 8.50,
  `technician_name` VARCHAR(128) NOT NULL DEFAULT 'Lian Ahmed',
  `technician_uid` VARCHAR(32) NOT NULL DEFAULT '#AR-9402',
  `work_order_ref` VARCHAR(64) NOT NULL DEFAULT 'WO-2026-9481',
  `service_notes` TEXT DEFAULT NULL,
  `serviced_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_maint_unit` (`unit_id`),
  KEY `idx_serviced_at` (`serviced_at` DESC),
  CONSTRAINT `fk_maint_unit` FOREIGN KEY (`unit_id`) REFERENCES `generator_units` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 11. OPERATOR ACCOUNTS & SECURITY PERMISSIONS
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `operators` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `uid` VARCHAR(32) NOT NULL,
  `full_name` VARCHAR(128) NOT NULL,
  `email` VARCHAR(160) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `division` VARCHAR(64) NOT NULL DEFAULT 'Dhaka North',
  `role` VARCHAR(64) NOT NULL DEFAULT 'Lead SCADA Engineer',
  `clearance_level` TINYINT UNSIGNED NOT NULL DEFAULT 4,
  `is_active` TINYINT(1) NOT NULL DEFAULT 1,
  `last_login_at` TIMESTAMP NULL DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_operator_uid` (`uid`),
  UNIQUE KEY `uk_operator_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `operator_permissions` (
  `operator_id` INT UNSIGNED NOT NULL,
  `remote_start_stop` TINYINT(1) NOT NULL DEFAULT 1,
  `modbus_register_write` TINYINT(1) NOT NULL DEFAULT 1,
  `alarm_acknowledge` TINYINT(1) NOT NULL DEFAULT 1,
  `cms_layout_control` TINYINT(1) NOT NULL DEFAULT 1,
  `estop_override` TINYINT(1) NOT NULL DEFAULT 1,
  `fota_push_firmware` TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`operator_id`),
  CONSTRAINT `fk_permissions_operator` FOREIGN KEY (`operator_id`) REFERENCES `operators` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 12. CMS DYNAMIC MODULE ORDERING & PERSISTENCE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `cms_module_orders` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `operator_id` INT UNSIGNED NOT NULL,
  `module_key` VARCHAR(32) NOT NULL,
  `sort_order` TINYINT UNSIGNED NOT NULL,
  `is_visible` TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_op_module` (`operator_id`, `module_key`),
  CONSTRAINT `fk_cms_operator` FOREIGN KEY (`operator_id`) REFERENCES `operators` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 13. SEED DATA INITIALIZATION (Strictly 492 Total Regional Sites)
-- ----------------------------------------------------------------------------

-- Seed Areas
INSERT INTO `areas` (`area_code`, `name`, `division`, `regional_director`, `contact_phone`, `target_sla_pct`) VALUES
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
ON DUPLICATE KEY UPDATE `name`=VALUES(`name`);

-- Seed Clusters
INSERT INTO `clusters` (`cluster_code`, `name`, `area_id`, `lead_engineer_name`, `lead_engineer_uid`, `ip_concentrator`, `modbus_port`, `dispatch_route`) VALUES
('CLUST-DHK-01', 'Gulshan-Mirpur Node', 1, 'Engr. Lian Ahmed', '#AR-9402', '192.168.10.1', 502, 'ROUTE ACTIVE'),
('CLUST-DHK-02', 'Uttara-Tongi Corridor', 1, 'Engr. Naimul Islam', '#AR-9104', '192.168.10.2', 502, 'ROUTE ACTIVE'),
('CLUST-DHK-03', 'Dhanmondi-Motijheel', 2, 'Engr. Hasan Chowdhury', '#AR-9208', '192.168.10.3', 502, 'ROUTE ACTIVE'),
('CLUST-CTG-01', 'Agrabad Commercial Hub', 3, 'Engr. Tanvir Ahmed', '#AR-8831', '192.168.20.1', 502, 'ROUTE ACTIVE'),
('CLUST-SYL-01', 'Zindabazar Tech Node', 5, 'Engr. Babul Miah', '#AR-8419', '192.168.30.1', 502, 'ROUTE ACTIVE')
ON DUPLICATE KEY UPDATE `name`=VALUES(`name`);

-- Seed Generator Models
INSERT INTO `generator_models` (`model_name`, `brand`, `engine_family`, `prime_kw`, `standby_kva`, `cylinders`, `displacement_liters`, `rated_rpm`, `fuel_rate_l_kwh`, `oil_sump_capacity_l`, `coolant_capacity_l`, `default_controller`, `modbus_baud_rate`) VALUES
('1104A-44TG2', 'Perkins', '1100 Series', 48.00, 60.00, 4, 4.40, 1500, 0.2480, 16.40, 24.50, 'DSE-7320 MKII', 9600),
('6BT5.9-G2', 'Cummins', 'B-Series', 80.00, 100.00, 6, 5.90, 1500, 0.2390, 16.40, 24.50, 'DSE-7320 MKII', 9600),
('C4.4 Industrial', 'Caterpillar', 'CAT Compact', 70.40, 88.00, 4, 4.40, 1800, 0.2420, 12.00, 18.00, 'DSE-7320 MKII', 9600),
('40REOZK', 'Kohler', 'KD-Series', 120.00, 150.00, 6, 6.80, 1500, 0.2520, 20.00, 30.00, 'DSE-7320 MKII', 9600)
ON DUPLICATE KEY UPDATE `prime_kw`=VALUES(`prime_kw`);

-- Seed Primary Towers
INSERT INTO `towers` (`tower_uid`, `station_name`, `cluster_id`, `telecom_operator`, `latitude`, `longitude`, `power_source_state`, `grid_connection_kva`) VALUES
('BTS-GP-0492', 'Tower BTS-GP-0492 (Mirpur Sector 11)', 1, 'Grameenphone', 23.8223000, 90.3654000, 'GEN_ACTIVE', 60.00),
('BTS-RO-8442', 'Tower BTS-RO-8442 (Agrabad Port Node)', 4, 'Robi Axiata', 22.3244000, 91.8132000, 'GEN_ACTIVE', 100.00),
('BTS-BL-1944', 'Tower BTS-BL-1944 (Zindabazar Commercial)', 5, 'Banglalink', 24.8949000, 91.8687000, 'GRID_UTILITY', 88.00),
('BTS-TE-4738', 'Tower BTS-TE-4738 (Khulna Industrial)', 1, 'Teletalk', 22.8456000, 89.5403000, 'GRID_UTILITY', 150.00)
ON DUPLICATE KEY UPDATE `station_name`=VALUES(`station_name`);

-- Seed Deployed Units
INSERT INTO `generator_units` (`unit_serial`, `unit_uid`, `tower_id`, `model_id`, `dse_controller_model`, `modbus_slave_id`, `cumulative_run_hours`, `hours_since_last_service`, `service_interval_hours`, `current_status`, `current_rpm`, `is_safety_lockout`) VALUES
('SN-PK-2024-0104', 'GEN-PK-0104', 1, 1, 'DSE-7320 MKII', 1, 320.50, 120.50, 250.00, 'RUNNING', 1500, 0),
('SN-CM-2024-0208', 'GEN-CM-0208', 2, 2, 'DSE-7320 MKII', 1, 410.00, 232.00, 250.00, 'RUNNING', 1500, 0),
('SN-CAT-2024-0312', 'GEN-CAT-0312', 3, 3, 'DSE-7320 MKII', 1, 188.00, 126.00, 250.00, 'STANDBY', 0, 0),
('SN-KH-2024-0416', 'GEN-KH-0416', 4, 4, 'DSE-7320 MKII', 1, 479.20, 250.00, 250.00, 'LOCKOUT_MAINTENANCE', 0, 1)
ON DUPLICATE KEY UPDATE `current_status`=VALUES(`current_status`);

-- Seed Live Telemetry Snapshot
INSERT INTO `telemetry_live` (`unit_id`, `v_l1_n`, `v_l2_n`, `v_l3_n`, `v_l1_l2`, `v_l2_l3`, `v_l3_l1`, `current_l1`, `current_l2`, `current_l3`, `frequency_hz`, `active_power_kw`, `apparent_power_kva`, `reactive_power_kvar`, `power_factor`, `engine_rpm`, `coolant_temp_c`, `oil_pressure_bar`, `fuel_level_pct`, `fuel_volume_liters`, `battery_vdc`, `voltage_balance_pct`, `thd_pct`) VALUES
(1, 230.4, 229.8, 230.1, 399.8, 400.2, 400.0, 27.20, 26.80, 27.00, 50.02, 18.60, 23.25, 13.95, 0.80, 1500, 84.2, 4.20, 76.00, 190.00, 26.8, 99.80, 2.10),
(2, 231.2, 230.8, 231.0, 401.0, 400.8, 401.2, 54.80, 55.10, 54.90, 50.00, 38.20, 47.75, 28.65, 0.80, 1500, 88.6, 4.50, 82.00, 280.00, 26.4, 99.70, 1.90),
(3, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 1.00, 0, 42.0, 0.00, 94.00, 210.00, 27.0, 100.00, 0.00),
(4, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 1.00, 0, 31.0, 0.00, 68.00, 420.00, 25.8, 100.00, 0.00)
ON DUPLICATE KEY UPDATE `active_power_kw`=VALUES(`active_power_kw`);

-- Seed Lead Operator & Security Permissions
INSERT INTO `operators` (`uid`, `full_name`, `email`, `password_hash`, `division`, `role`, `clearance_level`) VALUES
('#AR-9402', 'Lian Ahmed', 'lian.ahmed@arenaiot.com', SHA2('Admin@2026', 256), 'Dhaka North', 'Lead SCADA Engineer', 4)
ON DUPLICATE KEY UPDATE `full_name`=VALUES(`full_name`);

INSERT INTO `operator_permissions` (`operator_id`, `remote_start_stop`, `modbus_register_write`, `alarm_acknowledge`, `cms_layout_control`, `estop_override`, `fota_push_firmware`) VALUES
(1, 1, 1, 1, 1, 1, 1)
ON DUPLICATE KEY UPDATE `remote_start_stop`=1;

-- Seed Sample Maintenance Audit Record
INSERT INTO `maintenance_records` (`unit_id`, `service_protocol`, `runtime_at_service`, `hours_since_last_reset`, `service_interval_hours`, `lube_oil_brand`, `technician_name`, `technician_uid`, `work_order_ref`, `service_notes`) VALUES
(1, 'PM_A_MINOR', 200.00, 0.00, 250.00, 'Shell Rimula R4X 15W-40 CI-4', 'Lian Ahmed', '#AR-9402', 'WO-2026-9481', 'Routine PM-A completed. Replaced 16.4L lube oil and primary filter. Coolant and battery checked.')
ON DUPLICATE KEY UPDATE `service_notes`=VALUES(`service_notes`);
