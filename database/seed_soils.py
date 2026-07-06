from . import _get_conn

SOILS = [
    "Alluvial Soil", "Black Soil (Regur)", "Red and Yellow Soil",
    "Laterite Soil", "Arid and Desert Soil", "Saline and Alkaline Soil",
    "Peaty and Marshy Soil", "Forest and Mountain Soil",
]

def seed():
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS soils")
    cursor.execute("""
        CREATE TABLE soils (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)
    for s in SOILS:
        cursor.execute("INSERT OR IGNORE INTO soils (name) VALUES (?)", (s,))
    conn.commit()
    conn.close()
    print(f"Seeded {len(SOILS)} soil types.")

if __name__ == "__main__":
    seed()
