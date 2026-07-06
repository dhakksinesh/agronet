import importlib

def seed():
    for mod in ["seed_states", "seed_districts", "seed_crops", "seed_soils"]:
        m = importlib.import_module(f"database.{mod}")
        print(f"=== Seeding {mod.replace('seed_', '')} ===")
        m.seed()
    print("=== Done ===")

if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    seed()
