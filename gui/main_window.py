import tkinter as tk
from tkinter import ttk, messagebox
from database.db_manager import get_all_cars
from parsers.autoscout24_parser import parse_autoscout24

class CarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Car Search System")
        self.root.geometry("1200x700")

        # Форма параметрів
        form_frame = tk.Frame(self.root)
        form_frame.pack(padx=10, pady=10, fill="x")

        self.entries = {}
        fields = [
            ("Brand", "brand"), ("Model", "model"), ("Body Type", "body_type"),
            ("Year From", "year_from"), ("Year To", "year_to"),
            ("Engine Type", "engine_type"), ("Volume From", "vol_from"), ("Volume To", "vol_to"),
            ("Transmission", "transmission"), ("Drive", "drive"),
            ("Max Mileage", "mileage"), ("Price From", "price_from"), ("Price To", "price_to")
        ]

        for idx, (label, key) in enumerate(fields):
            tk.Label(form_frame, text=label).grid(row=idx//4, column=(idx%4)*2, sticky="e")
            entry = tk.Entry(form_frame)
            entry.grid(row=idx//4, column=(idx%4)*2+1, padx=5, pady=3)
            self.entries[key] = entry

        tk.Button(form_frame, text="Search AutoScout24", command=self.search_autoscout).pack(pady=10, anchor="w")
        tk.Button(form_frame, text="Refresh Table", command=self.load_data).pack(pady=5, anchor="w")

        # Таблиця
        columns = ("brand", "model", "engine_type", "engine_volume", "year", "country", "price_eur", "customs_uah", "final_price_uah", "link")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=120)

        self.tree.pack(fill="both", expand=True)
        self.load_data()

    def search_autoscout(self):
        params = {key: entry.get().strip() for key, entry in self.entries.items() if entry.get().strip()}
        parse_autoscout24(**params)
        messagebox.showinfo("Парсинг завершено", "Дані отримано і збережено")
        self.load_data()

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for car in get_all_cars():
            self.tree.insert("", "end", values=(
                car["brand"], car["model"], car["engine_type"], car["engine_volume"],
                car["year"], car["country"], car["price_eur"],
                car["customs_uah"], car["final_price_uah"], car["link"]
            ))

if __name__ == "__main__":
    root = tk.Tk()
    app = CarApp(root)
    root.mainloop()
