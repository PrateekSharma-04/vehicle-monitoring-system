import os
import sqlite3

import PIL.Image
import tkinter as tk
from PIL import ImageTk
from tkinter import Entry, Label, W, ttk

from config.settings import DEFAULT_OUTPUT_DIR


class DatabaseUI(tk.Toplevel):
    db_vehicle_name = "vehicle_database.db"
    path = os.getcwd() + "/database_detected_vehicles_images"

    def __init__(self):
        super().__init__()
        self.title("Database UI")
        self.setup_UI()

    def run_query(self, query, parameters=()):
        with sqlite3.connect(self.db_vehicle_name) as conn:
            cursor = conn.cursor()
            query_result = cursor.execute(query, parameters)
            conn.commit()
        return query_result

    def search_pattern(self, input_pattern):
        pattern = input_pattern
        records = self.tree.get_children()
        for element in records:
            self.tree.delete(element)
        query = "SELECT * FROM vehicles_info WHERE vehicle_name LIKE ?"
        parmeters = ("%" + pattern + "%",)
        db_rows = self.run_query(query, parmeters)
        for row in db_rows:
            self.tree.insert("", 0, text=row[0], values=[row[1], row[2], row[3]])
        records = self.tree.get_children()
        for element in records:
            self.tree.bind("<Double-Button-1>", self.on_record_clicked)

    def serach_overspeed_record(self):
        records = self.tree.get_children()
        for element in records:
            self.tree.delete(element)
        query = "SELECT * FROM vehicles_info WHERE is_overspeed==1"
        db_rows = self.run_query(query)
        for row in db_rows:
            self.tree.insert("", 0, text=row[0], values=[row[1], row[2], row[3]])
        records = self.tree.get_children()
        for element in records:
            self.tree.bind("<Double-Button-1>", self.on_record_clicked)

    def serach_line_crossing_record(self):
        records = self.tree.get_children()
        for element in records:
            self.tree.delete(element)
        query = "SELECT * FROM vehicles_info WHERE is_line_crossing==1"
        db_rows = self.run_query(query)
        for row in db_rows:
            self.tree.insert("", 0, text=row[0], values=[row[1], row[2], row[3]])
        records = self.tree.get_children()
        for element in records:
            self.tree.bind("<Double-Button-1>", self.on_record_clicked)

    def viewing_records(self):
        records = self.tree.get_children()
        for element in records:
            self.tree.delete(element)
        query = "SELECT * FROM vehicles_info ORDER BY vehicle_name DESC"
        db_rows = self.run_query(query)
        for row in db_rows:
            self.tree.insert("", 0, text=row[0], values=[row[1], row[2], row[3]])
        records = self.tree.get_children()
        for element in records:
            self.tree.bind("<Double-Button-1>", self.on_record_clicked)

    def on_record_clicked(self, event):
        current_values = self.tree.item(self.tree.selection())["values"][0]
        file_info = current_values.split("_")
        vehicle_name = file_info[1]
        image_path = self.path + "/" + current_values + ".png"
        image = PIL.Image.open(image_path)
        try:
            resample_filter = PIL.Image.Resampling.LANCZOS
        except AttributeError:
            resample_filter = PIL.Image.LANCZOS
        image = image.resize((700, 500), resample_filter)
        photo = ImageTk.PhotoImage(image)
        label = Label(self, image=photo)
        label.image = photo  # keep a reference!
        label.grid(row=6, column=0, rowspan=5)

    def deleting(self):
        vehicle_name = self.tree.item(self.tree.selection())["values"][0]
        query = "DELETE FROM vehicles_info WHERE vehicle_name= ?"
        self.run_query(query, (vehicle_name,))
        image_path = self.path + "/" + vehicle_name + ".png"
        os.remove(image_path)
        print(image_path, " has been deleted")
        self.viewing_records()

    def setup_UI(self):
        tree_frame = tk.Frame(self)
        tree_frame.grid(row=0, column=0)
        self.tree = ttk.Treeview(tree_frame, height=7, columns=("col1", "col2", "col3"))
        self.tree.grid(row=2, column=0, columnspan=3)
        self.tree.heading("#0", text="id", anchor=W)
        self.tree.heading("col1", text="name", anchor=W)
        self.tree.heading("col2", text="line_crossing", anchor=W)
        self.tree.heading("col3", text="overspeed", anchor=W)

        bottom_frame = tk.Frame(self)
        bottom_frame.grid(row=3, column=0)

        ttk.Button(bottom_frame, text="Delete record", command=self.deleting).grid(
            row=0, column=0
        )
        ttk.Button(bottom_frame, text="Refresh", command=self.viewing_records).grid(
            row=0, column=1
        )
        ttk.Button(
            bottom_frame,
            text="Search by pattern",
            command=lambda: self.search_pattern(pattern_name.get()),
        ).grid(row=0, column=2)
        pattern_name = Entry(bottom_frame)
        pattern_name.grid(row=0, column=3)
        ttk.Button(
            bottom_frame,
            text="Search overspeed record",
            command=self.serach_overspeed_record,
        ).grid(row=1, column=0)
        ttk.Button(
            bottom_frame,
            text="Search line crossing record",
            command=self.serach_line_crossing_record,
        ).grid(row=1, column=2)

        self.viewing_records()
