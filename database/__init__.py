import sqlite3
from pathlib import Path
from utils import logger

DB_PATH = Path(__file__).parent / "agronet.db"
_db_initialized = False

def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    global _db_initialized
    if _db_initialized:
        return
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS farmer_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT DEFAULT 'My Farm',
                state TEXT,
                district TEXT,
                crop TEXT,
                soil_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                farmer_profile_id INTEGER,
                query_text TEXT,
                response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (farmer_profile_id) REFERENCES farmer_profiles (id)
            )
        """)
        cursor.execute("PRAGMA table_info(farmer_profiles)")
        cols = {row[1] for row in cursor.fetchall()}
        if "name" not in cols:
            cursor.execute("ALTER TABLE farmer_profiles ADD COLUMN name TEXT DEFAULT 'My Farm'")
        conn.commit()
        conn.close()
        _db_initialized = True
        logger.info("Database initialized successfully")
    except sqlite3.Error as e:
        logger.error(f"Database initialization failed: {e}")
        raise

def save_farmer_profile(state: str, district: str, crop: str, soil_type: str, name: str = "My Farm") -> int:
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO farmer_profiles (name, state, district, crop, soil_type) VALUES (?, ?, ?, ?, ?)",
            (name, state, district, crop, soil_type)
        )
        conn.commit()
        profile_id = cursor.lastrowid
        conn.close()
        logger.info(f"Farmer profile saved: {profile_id} - {name} ({state}, {district}, {crop})")
        return profile_id
    except sqlite3.Error as e:
        logger.error(f"Failed to save farmer profile: {e}")
        raise

def get_profiles() -> list:
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM farmer_profiles ORDER BY created_at DESC")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows
    except sqlite3.Error as e:
        logger.error(f"Failed to get profiles: {e}")
        return []

def delete_profile(profile_id: int) -> bool:
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM queries WHERE farmer_profile_id = ?", (profile_id,))
        cursor.execute("DELETE FROM farmer_profiles WHERE id = ?", (profile_id,))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        logger.error(f"Failed to delete profile: {e}")
        return False

def save_query(profile_id: int, query_text: str, response: str) -> bool:
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO queries (farmer_profile_id, query_text, response) VALUES (?, ?, ?)",
            (profile_id, query_text, response)
        )
        conn.commit()
        conn.close()
        logger.debug(f"Query saved for profile {profile_id}")
        return True
    except sqlite3.Error as e:
        logger.error(f"Failed to save query: {e}")
        raise

def update_profile(profile_id: int, name: str = None, state: str = None, district: str = None, crop: str = None, soil_type: str = None) -> bool:
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        fields = []
        vals = []
        if name is not None:
            fields.append("name = ?"); vals.append(name)
        if state is not None:
            fields.append("state = ?"); vals.append(state)
        if district is not None:
            fields.append("district = ?"); vals.append(district)
        if crop is not None:
            fields.append("crop = ?"); vals.append(crop)
        if soil_type is not None:
            fields.append("soil_type = ?"); vals.append(soil_type)
        if not fields:
            return False
        vals.append(profile_id)
        cursor.execute(f"UPDATE farmer_profiles SET {', '.join(fields)} WHERE id = ?", vals)
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        logger.error(f"Failed to update profile {profile_id}: {e}")
        return False

def get_query_history(profile_id: int, limit: int = 50, offset: int = 0, search: str = "") -> list:
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        if search:
            cursor.execute(
                """SELECT id, query_text, response, created_at FROM queries
                   WHERE farmer_profile_id = ? AND (query_text LIKE ? OR response LIKE ?)
                   ORDER BY created_at DESC LIMIT ? OFFSET ?""",
                (profile_id, f"%{search}%", f"%{search}%", limit, offset)
            )
        else:
            cursor.execute(
                "SELECT id, query_text, response, created_at FROM queries WHERE farmer_profile_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (profile_id, limit, offset)
            )
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows
    except sqlite3.Error as e:
        logger.error(f"Failed to get query history: {e}")
        return []

def count_queries(profile_id: int, search: str = "") -> int:
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        if search:
            cursor.execute(
                "SELECT COUNT(*) FROM queries WHERE farmer_profile_id = ? AND (query_text LIKE ? OR response LIKE ?)",
                (profile_id, f"%{search}%", f"%{search}%")
            )
        else:
            cursor.execute("SELECT COUNT(*) FROM queries WHERE farmer_profile_id = ?", (profile_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except sqlite3.Error as e:
        logger.error(f"Failed to count queries: {e}")
        return 0

def get_states() -> list:
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM states ORDER BY name")
        rows = [r["name"] for r in cursor.fetchall()]
        conn.close()
        return rows
    except sqlite3.Error:
        return []

def get_districts(state: str) -> list:
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT d.name FROM districts d JOIN states s ON d.state_id = s.id WHERE s.name = ? ORDER BY d.name",
            (state,),
        )
        rows = [r["name"] for r in cursor.fetchall()]
        conn.close()
        return rows
    except sqlite3.Error:
        return []

def get_crop_types() -> list:
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT type FROM commodities ORDER BY type")
        rows = [r["type"] for r in cursor.fetchall()]
        conn.close()
        return rows
    except sqlite3.Error:
        return []

def get_crops_by_type(crop_type: str) -> list:
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM commodities WHERE type = ? ORDER BY name", (crop_type,))
        rows = [r["name"] for r in cursor.fetchall()]
        conn.close()
        return rows
    except sqlite3.Error:
        return []

def get_crop_type_for_name(name: str) -> str:
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT type FROM commodities WHERE name = ?", (name,))
        row = cursor.fetchone()
        conn.close()
        return row["type"] if row else ""
    except sqlite3.Error:
        return ""

def get_soil_types() -> list:
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM soils ORDER BY name")
        rows = [r["name"] for r in cursor.fetchall()]
        conn.close()
        return rows
    except sqlite3.Error:
        return []

def delete_query(query_id: int) -> bool:
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM queries WHERE id = ?", (query_id,))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        logger.error(f"Failed to delete query {query_id}: {e}")
        return False
