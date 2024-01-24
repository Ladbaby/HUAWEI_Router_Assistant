import os
import time
import sqlite3
from typing import Dict

from .global_logger import logger

class Cache:
    def __init__(self) -> None:
        data_path = os.getcwd()
        db_cache_path = os.path.join(data_path, "sqlite.db")
        logger.debug(db_cache_path)

        # os.makedirs(data_path, exist_ok=True)
        try:
            self.db_cache_conn = sqlite3.connect(db_cache_path,  check_same_thread=False)
            self.db_cache_cursor = self.db_cache_conn.cursor()
            self.db_cache_cursor.execute('''
                CREATE TABLE IF NOT EXISTS battery (
                    timestamp INTEGER PRIMARY KEY,
                    percentage INTEGER,
                    charging INTEGER
                )
            ''')
            self.db_cache_conn.commit()
        except Exception as e:
            logger.error(e)
            exit(1)

    def read_battery_history(self):
        try:
            self.db_cache_cursor.execute('''
                SELECT * FROM battery ORDER BY timestamp DESC LIMIT 1440
            ''')
            # return a list of tuple, each representing a record
            return self.db_cache_cursor.fetchall()
        except Exception as e:
            logger.error(e)
            return None

    def write_battery_history(self, battery_history_record: Dict[int, int]):
        try:
            self.db_cache_cursor.execute('''
                INSERT INTO battery (timestamp, percentage, charging)
                VALUES (?, ?, ?)
            ''', (battery_history_record["timestamp"], battery_history_record["percentage"], battery_history_record["charging"]))
            self.db_cache_conn.commit()
        except Exception as e:
            logger.error(e)
        
    def remove_battery_history(self):
        try:
            # Calculate the timestamp 12 hours ago
            twelve_hours_ago = int(time.time()) - (12 * 60 * 60)

            # Delete records with timestamps older than twelve_hours_ago
            self.db_cache_cursor.execute('''
                DELETE FROM battery WHERE timestamp < ?
            ''', (twelve_hours_ago,))
            self.db_cache_conn.commit()

            return True
        except Exception as e:
            logger.error(e)
            return False
