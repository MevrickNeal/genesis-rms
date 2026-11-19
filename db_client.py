"""
GENESIS RMS — Enterprise SCADA Database Client & ORM Gateway
Parent System: Arena IoT Connected Platform
Supports:
  1. Vercel Postgres (Neon) via pg8000 with TLS/SSL encryption
  2. Cloud / Local MySQL 8.0+ via PyMySQL (TiDB Cloud Serverless, Aiven)
  3. Local SQLite3 fallback for offline sandboxed development

Invariants: Strictly 0 literal five-hundred; 492 National Site Archetypes.
"""

import os
import sys
import json
import ssl
import logging
from datetime import datetime, date
from decimal import Decimal
import urllib.parse

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger("GenesisDB")

# Auto-load .env file if present without external dependencies
def load_dotenv():
    env_paths = [
        os.path.join(os.path.dirname(__file__), ".env"),
        os.path.join(os.getcwd(), ".env")
    ]
    for p in env_paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip("'\"")
                            if k not in os.environ:
                                os.environ[k] = v
                logger.info(f"Loaded environment variables from {p}")
                break
            except Exception as e:
                logger.warning(f"Could not load .env file {p}: {e}")

load_dotenv()

# Determine Primary Database Engine
POSTGRES_URL = (
    os.getenv("POSTGRES_URL") or
    os.getenv("DATABASE_URL") or
    os.getenv("VERCEL_DATABASE_URL") or
    os.getenv("POSTGRES_PRISMA_URL") or
    os.getenv("POSTGRES_URL_NON_POOLING")
)

MYSQL_HOST = os.getenv("GENESIS_DB_HOST")

class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder for Decimal and Date/Timestamp SCADA telemetry objects."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

class DictCursorWrapper:
    """Wrapper around DB-API cursor to return dictionary rows uniformly."""
    def __init__(self, cursor):
        self.cursor = cursor

    def __iter__(self):
        return self

    def __next__(self):
        row = self.cursor.fetchone()
        if row is None:
            raise StopIteration
        return self._to_dict(row)

    def _to_dict(self, row):
        if row is None:
            return None
        if isinstance(row, dict):
            return row
        cols = [d[0] for d in self.cursor.description]
        return dict(zip(cols, row))

    def fetchone(self):
        row = self.cursor.fetchone()
        return self._to_dict(row)

    def fetchall(self):
        rows = self.cursor.fetchall()
        if not rows:
            return []
        if isinstance(rows[0], dict):
            return rows
        cols = [d[0] for d in self.cursor.description]
        return [dict(zip(cols, r)) for r in rows]

    def execute(self, query, params=None):
        if params is not None:
            return self.cursor.execute(query, params)
        return self.cursor.execute(query)

    def close(self):
        self.cursor.close()

class DatabaseConnection:
    """Universal connection wrapper supporting Postgres, MySQL, and SQLite."""
    def __init__(self, raw_conn, engine_name):
        self.raw_conn = raw_conn
        self.engine_name = engine_name

    def cursor(self):
        if self.engine_name == "mysql":
            return self.raw_conn.cursor()
        elif self.engine_name == "postgres":
            return DictCursorWrapper(self.raw_conn.cursor())
        elif self.engine_name == "sqlite":
            return DictCursorWrapper(self.raw_conn.cursor())
        return self.raw_conn.cursor()

    def commit(self):
        self.raw_conn.commit()

    def rollback(self):
        self.raw_conn.rollback()

    def close(self):
        self.raw_conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.close()

def get_connection():
    """
    Establish active database connection:
    Priority 1: Vercel Postgres (Neon) if POSTGRES_URL is configured
    Priority 2: Cloud / Local MySQL if GENESIS_DB_HOST is configured
    Priority 3: SQLite fallback (genesis_local.db) for instant offline sandbox testing
    """
    # 1. Vercel Postgres (Neon) Connection
    if POSTGRES_URL and (POSTGRES_URL.startswith("postgres://") or POSTGRES_URL.startswith("postgresql://")):
        try:
            import pg8000
            
            # Parse connection URI
            parsed = urllib.parse.urlparse(POSTGRES_URL)
            user = parsed.username or "default"
            password = parsed.password or ""
            host = parsed.hostname or "localhost"
            port = parsed.port or 5432
            database = parsed.path.lstrip("/") or "verceldb"
            
            # Enforce TLS context for Vercel / Neon
            ssl_ctx = ssl.create_default_context()
            
            logger.info(f"Connecting to Vercel Postgres at {host}:{port}/{database}...")
            raw_conn = pg8000.connect(
                user=user,
                password=password,
                host=host,
                port=port,
                database=database,
                ssl_context=ssl_ctx,
                timeout=15
            )
            return DatabaseConnection(raw_conn, "postgres")
        except Exception as e:
            logger.error(f"Vercel Postgres connection failed: {e}")
            raise

    # 2. Cloud / Local MySQL Connection
    elif MYSQL_HOST:
        try:
            import pymysql
            import pymysql.cursors

            connect_kwargs = {
                "host": MYSQL_HOST,
                "port": int(os.getenv("GENESIS_DB_PORT", "3306")),
                "user": os.getenv("GENESIS_DB_USER", "root"),
                "password": os.getenv("GENESIS_DB_PASSWORD", ""),
                "database": os.getenv("GENESIS_DB_NAME", "genesis_rms_db"),
                "charset": "utf8mb4",
                "connect_timeout": 10,
                "autocommit": True,
                "cursorclass": pymysql.cursors.DictCursor
            }

            if os.getenv("GENESIS_DB_USE_SSL", "false").lower() in ("true", "1", "yes"):
                connect_kwargs["ssl"] = ssl.create_default_context()

            logger.info(f"Connecting to MySQL at {connect_kwargs['host']}:{connect_kwargs['port']}...")
            raw_conn = pymysql.connect(**connect_kwargs)
            return DatabaseConnection(raw_conn, "mysql")
        except Exception as e:
            logger.error(f"MySQL connection failed: {e}")
            raise

    # 3. SQLite Local Fallback
    else:
        import sqlite3
        db_path = os.path.join(os.path.dirname(__file__), "genesis_local.db")
        logger.info(f"Using local SQLite SCADA cache at {db_path}...")
        raw_conn = sqlite3.connect(db_path)
        raw_conn.row_factory = sqlite3.Row
        return DatabaseConnection(raw_conn, "sqlite")

def get_engine_status():
    """Return summary dictionary of database engine configuration."""
    if POSTGRES_URL and (POSTGRES_URL.startswith("postgres://") or POSTGRES_URL.startswith("postgresql://")):
        parsed = urllib.parse.urlparse(POSTGRES_URL)
        return {
            "engine": "Vercel Postgres (Neon)",
            "host": parsed.hostname,
            "port": parsed.port or 5432,
            "database": parsed.path.lstrip("/"),
            "ssl": True,
            "driver": "pg8000"
        }
    elif MYSQL_HOST:
        return {
            "engine": "MySQL / TiDB Cloud",
            "host": MYSQL_HOST,
            "port": int(os.getenv("GENESIS_DB_PORT", "3306")),
            "database": os.getenv("GENESIS_DB_NAME", "genesis_rms_db"),
            "ssl": os.getenv("GENESIS_DB_USE_SSL", "false"),
            "driver": "PyMySQL"
        }
    else:
        return {
            "engine": "Local SQLite SCADA Sandbox",
            "database": "genesis_local.db",
            "driver": "sqlite3"
        }

def initialize_vercel_database(schema_path="genesis_vercel_schema.sql"):
    """Parse and execute the genesis_vercel_schema.sql file against Vercel Postgres."""
    if not os.path.isabs(schema_path):
        schema_path = os.path.join(os.path.dirname(__file__), schema_path)

    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Vercel schema file {schema_path} not found.")

    with open(schema_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Split into clean statements by semicolons, preserving multi-line blocks
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

    conn = get_connection()
    logger.info(f"Target Database Engine: {conn.engine_name}")
    logger.info(f"Executing {len(statements)} DDL/DML statements from {schema_path}...")
    
    executed = 0
    cur = conn.cursor()
    for stmt in statements:
        try:
            cur.execute(stmt)
            executed += 1
        except Exception as e:
            logger.warning(f"Notice on statement: {e}")

    conn.commit()
    conn.close()
    logger.info(f"Successfully applied GENESIS SCADA schema to {conn.engine_name}. Executed: {executed} statements.")
    return executed

def query_live_telemetry(unit_uid="GEN-DH-0001"):
    """Fetch real-time Modbus register telemetry for an individual unit."""
    conn = get_connection()
    try:
        cur = conn.cursor()
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
        # SQLite uses ? placeholder, Postgres/MySQL use %s
        if conn.engine_name == "sqlite":
            sql = sql.replace("%s", "?")
            
        cur.execute(sql, (unit_uid,))
        result = cur.fetchone()
        return result
    finally:
        conn.close()

def query_maintenance_queue():
    """Fetch all generators prioritized by maintenance countdown hours remaining."""
    conn = get_connection()
    try:
        cur = conn.cursor()
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
            ORDER BY hours_remaining ASC
            LIMIT 50;
        """
        cur.execute(sql)
        return cur.fetchall()
    finally:
        conn.close()

def execute_maintenance_service(unit_uid, protocol, technician_name, technician_uid, work_order_ref, notes="Preventive maintenance reset", safety_lockout=False):
    """
    Log work order in maintenance_records, reset service timer, and update lockout.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        placeholder = "?" if conn.engine_name == "sqlite" else "%s"

        # 1. Fetch unit id and runtime
        select_sql = f"SELECT id, cumulative_run_hours, service_interval_hours FROM generator_units WHERE unit_uid = {placeholder}"
        cur.execute(select_sql, (unit_uid,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Generator unit {unit_uid} not found.")

        unit_id = row['id']
        cum_hours = row['cumulative_run_hours']
        interval = row['service_interval_hours']

        # 2. Insert maintenance record
        insert_sql = f"""
            INSERT INTO maintenance_records (
                unit_id, service_protocol, runtime_at_service, hours_since_last_reset,
                service_interval_hours, technician_name, technician_uid, work_order_ref, service_notes
            ) VALUES ({placeholder}, {placeholder}, {placeholder}, 0.00, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder});
        """
        cur.execute(insert_sql, (unit_id, protocol, cum_hours, interval, technician_name, technician_uid, work_order_ref, notes))

        # 3. Update unit counters
        new_status = 'LOCKOUT_MAINTENANCE' if safety_lockout else 'RUNNING'
        update_sql = f"""
            UPDATE generator_units 
            SET hours_since_last_service = 0.00,
                is_safety_lockout = {placeholder},
                current_status = {placeholder},
                updated_at = CURRENT_TIMESTAMP
            WHERE id = {placeholder};
        """
        cur.execute(update_sql, (1 if safety_lockout else 0, new_status, unit_id))

        conn.commit()
        logger.info(f"Successfully processed maintenance for {unit_uid} ({work_order_ref})")
        return True
    finally:
        conn.close()

if __name__ == "__main__":
    status = get_engine_status()
    print("\n=======================================================")
    print("GENESIS RMS — SCADA DATABASE GATEWAY")
    print("=======================================================")
    print(f"Active Engine: {status['engine']}")
    for k, v in status.items():
        if k != "engine":
            print(f"  {k}: {v}")
    print("=======================================================\n")

    if "--init-vercel" in sys.argv:
        print("Applying Vercel Postgres schema (genesis_vercel_schema.sql)...")
        initialize_vercel_database("genesis_vercel_schema.sql")
    elif "--test-connection" in sys.argv or "--status" in sys.argv:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT 1 AS test_val;")
            res = cur.fetchone()
            print(f"Connection test SUCCESSFUL on {conn.engine_name}! Test result:", res)
            conn.close()
        except Exception as err:
            print(f"Connection test FAILED: {err}")
    else:
        print("Usage:")
        print("  python db_client.py --status           # Check configured database engine")
        print("  python db_client.py --test-connection  # Test live connectivity")
        print("  python db_client.py --init-vercel      # Apply genesis_vercel_schema.sql")
