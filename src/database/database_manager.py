import os
import sqlite3

from config.settings import DEFAULT_OUTPUT_DIR, PROJECT_ROOT


class DatabaseManager:
    def __init__(self, database_path=None):
        self.database_path = database_path or str(PROJECT_ROOT / "vehicle_database.db")
        self.image_directory = str(DEFAULT_OUTPUT_DIR)
        os.makedirs(self.image_directory, exist_ok=True)

    def run_query(self, query, parameters=()):
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            query_result = cursor.execute(query, parameters)
            conn.commit()
        return query_result

    def search_pattern(self, pattern):
        query = "SELECT * FROM vehicles_info WHERE vehicle_name LIKE ?"
        return self.run_query(query, ("%" + pattern + "%",))

    def search_overspeed(self):
        query = "SELECT * FROM vehicles_info WHERE is_overspeed==1"
        return self.run_query(query)

    def search_line_crossing(self):
        query = "SELECT * FROM vehicles_info WHERE is_line_crossing==1"
        return self.run_query(query)

    def viewing_records(self):
        query = "SELECT * FROM vehicles_info ORDER BY vehicle_name DESC"
        return self.run_query(query)

    def delete_record(self, vehicle_name):
        query = "DELETE FROM vehicles_info WHERE vehicle_name= ?"
        self.run_query(query, (vehicle_name,))
