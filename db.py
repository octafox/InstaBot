# Module Imports
import mariadb
import sys
import config as cfg

# Connect to MariaDB Platform
try:
    conn = mariadb.connect(
        user=cfg.DB_USER,
        password=cfg.DB_PASS,
        host=cfg.DB_HOST,
        port=cfg.DB_PORT,
        database=cfg.DB_DATABASE
    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
cur = conn.cursor()

