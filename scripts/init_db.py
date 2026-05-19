import sys
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(root_dir))

from app.database.db_manager import db

def main():
    print("Initializing SQLite Database...")
    try:
        db.init_db()
        print(f"Database successfully initialized at: {db.db_path}")
    except Exception as e:
        print(f"Database initialization failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
