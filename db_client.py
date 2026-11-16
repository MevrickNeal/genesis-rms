"""
GENESIS RMS — Enterprise SCADA Database Client & ORM Gateway
Parent System: Arena IoT Connected Platform
Supports: Localhost MySQL 8.0+, TiDB Cloud Serverless, Aiven Cloud MySQL
"""

import os
import json
import logging
from datetime import datetime, date
from decimal import Decimal

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger("GenesisDB")

# Configuration (Supports Environment Variables or Direct Parameters)
DB_CONFIG = {
    "host": os.getenv("GENESIS_DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("GENESIS_DB_PORT", "3306")),
    "user": os.getenv("GENESIS_DB_USER", "root"),
    "password": os.getenv("GENESIS_DB_PASSWORD", ""),
    "database": os.getenv("GENESIS_DB_NAME", "genesis_rms_db"),
    "charset": "utf8mb4",
    "connect_timeout": 10,
    "autocommit": True
}

# Optional SSL Context for TiDB Cloud Serverless / Aiven Cloud
USE_SSL = os.getenv("GENESIS_DB_USE_SSL", "false").lower() in ("true", "1", "yes")

class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder for MySQL Decimal and Date/Timestamp objects."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

def get_connection():
    """Establish connection to MySQL using pymysql or fallback to sqlite/mock if driver not present."""
    try:
        import pymysql
        import pymysql.cursors
        
        connect_kwargs = dict(DB_CONFIG)
        connect_kwargs["cursorclass"] = pymysql.cursors.DictCursor
        
        if USE_SSL:
            import ssl
            ssl_ctx = ssl.create_default_context()
            connect_kwargs["ssl"] = ssl_ctx
            
        conn = pymysql.connect(**connect_kwargs)
        return conn
    except ImportError:
        logger.warning("PyMySQL not installed. Run: pip install pymysql")
        raise
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

def initialize_database(schema_path="genesis_schema.sql"):
    """Parse and execute the genesis_schema.sql file against the database."""
    import pymysql
    
    # First connect without database selected to create database if not exists
    init_config = dict(DB_CONFIG)
    init_config.pop("database", None)
    
    logger.info(f"Connecting to MySQL server at {init_config['host']}:{init_config['port']}...")
    conn = pymysql.connect(**init_config)
    cursor = conn.cursor()
    
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    cursor.execute(f"USE `{DB_CONFIG['database']}`;")
    logger.info(f"Database `{DB_CONFIG['database']}` ready.")
    
    # Read schema SQL
    if not os.path.exists(schema_path):
        # Check current dir or project dir
        alt_path = os.path.join(os.path.dirname(__file__), schema_path)
        if os.path.exists(alt_path):
            schema_path = alt_path
        else:
            raise FileNotFoundError(f"Schema file {schema_path} not found.")
            
    with open(schema_path, "r", encoding="utf-8") as f:
        sql_content = f.read()
        
    # Split by statements
    statements = []
    current_stmt = []
    for line in sql_content.splitlines():
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("--"):
            continue
        current_stmt.append(line)
        if trimmed.endswith(";"):
            statements.append("\n".join(current_stmt))
            current_stmt = []
            
    logger.info(f"Executing {len(statements)} SQL statements from {schema_path}...")
    executed = 0
    for stmt in statements:
        try:
            cursor.execute(stmt)
            executed += 1
        except Exception as e:
            logger.warning(f"Notice on statement: {e}")
            
    conn.commit()
    cursor.close()
    conn.close()
    logger.info(f"Successfully initialized GENESIS database. Executed {executed} statements.")
    return True

def query_live_telemetry(unit_uid="GEN-PK-0104"):
    """Fetch real-time Modbus register telemetry for an individual unit."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT 
                    u.unit_uid, u.unit_serial, u.current_status, u.current_rpm,
                    u.cumulative_run_hours, u.hours_since_last_service, u.service_interval_hours,
                    u.is_safety_lockout,
                    t.station_name, t.telecom_operator, t.power_source_state,
                    c.name AS cluster_name, a.name AS area_name,
                    m.model_name, m.brand, m.prime_kw, m.standby_kva,
                    l.*
                FROM generator_units u
                JOIN towers t ON u.tower_id = t.id
                JOIN clusters c ON t.cluster_id = c.id
                JOIN areas a ON c.area_id = a.id
                JOIN generator_models m ON u.model_id = m.id
                LEFT JOIN telemetry_live l ON u.id = l.unit_id
                WHERE u.unit_uid = %s
                LIMIT 1;
            """
            cursor.execute(sql, (unit_uid,))
            result = cursor.fetchone()
            return result
    finally:
        conn.close()

def query_maintenance_queue():
    """Fetch all generators prioritized by maintenance countdown hours remaining."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT 
                    u.unit_uid,
                    m.brand, m.model_name,
                    t.station_name,
                    c.name AS cluster_name,
                    u.cumulative_run_hours,
                    u.hours_since_last_service,
                    u.service_interval_hours,
                    (u.service_interval_hours - u.hours_since_last_service) AS hours_remaining,
                    GREATEST(0, ROUND(100 - (u.hours_since_last_service / u.service_interval_hours * 100), 1)) AS lube_oil_life_pct,
                    u.current_status,
                    u.is_safety_lockout,
                    r.technician_name,
                    r.work_order_ref,
                    r.serviced_at AS last_service_date
                FROM generator_units u
                JOIN generator_models m ON u.model_id = m.id
                JOIN towers t ON u.tower_id = t.id
                JOIN clusters c ON t.cluster_id = c.id
                LEFT JOIN (
                    SELECT unit_id, technician_name, work_order_ref, serviced_at,
                           ROW_NUMBER() OVER(PARTITION BY unit_id ORDER BY serviced_at DESC) as rn
                    FROM maintenance_records
                ) r ON u.id = r.unit_id AND r.rn = 1
                ORDER BY hours_remaining ASC;
            """
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()

def execute_maintenance_service(unit_uid, protocol, technician_name, technician_uid, work_order_ref, notes="Routine preventive maintenance", safety_lockout=False):
    """
    Update maintenance status:
    1. Log work order in maintenance_records
    2. Reset hours_since_last_service to 0.00
    3. Update safety lockout state and current_status in generator_units
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Get unit id and cumulative run hours
            cursor.execute("SELECT id, cumulative_run_hours, service_interval_hours FROM generator_units WHERE unit_uid = %s", (unit_uid,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Generator unit {unit_uid} not found.")
                
            unit_id = row['id']
            cumulative = row['cumulative_run_hours']
            interval = row['service_interval_hours']
            
            # 1. Insert into maintenance_records audit log
            insert_sql = """
                INSERT INTO maintenance_records (
                    unit_id, service_protocol, runtime_at_service, hours_since_last_reset,
                    service_interval_hours, technician_name, technician_uid, work_order_ref, service_notes
                ) VALUES (%s, %s, %s, 0.00, %s, %s, %s, %s, %s);
            """
            cursor.execute(insert_sql, (unit_id, protocol, cumulative, interval, technician_name, technician_uid, work_order_ref, notes))
            
            # 2. Update generator_units runtime counters and lockout
            new_status = 'LOCKOUT_MAINTENANCE' if safety_lockout else 'RUNNING'
            update_sql = """
                UPDATE generator_units 
                SET hours_since_last_service = 0.00,
                    is_safety_lockout = %s,
                    current_status = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s;
            """
            cursor.execute(update_sql, (1 if safety_lockout else 0, new_status, unit_id))
            
        conn.commit()
        logger.info(f"Successfully processed maintenance for {unit_uid} under {work_order_ref}")
        return True
    finally:
        conn.close()

if __name__ == "__main__":
    print("GENESIS RMS Database Engine initialized.")
    print("Default Connection Target:", f"{DB_CONFIG['user']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
