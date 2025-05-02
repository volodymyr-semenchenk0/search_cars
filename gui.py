import tkinter as tk
from tkinter import ttk, messagebox
from database.db_manager import get_all_cars, get_filtered_cars
from parsers.autoscout24_parser import parse_autoscout24
from parsers.mobile_de_parser import parse_mobile_de
from common import ENGINE_TYPES, BODY_TYPES, TRANSMISSIONS, DRIVE_TYPES, COUNTRY_NAMES

class CarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система пошуку авто")
        self.root.geometry("1440x800")
        self.sort_column = None
        self.sort_reverse = False
        self.setup_ui()

    def setup_ui(self):
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        btn_exit = tk.Button(button_frame, text="Вийти", command=self.root.quit)
        btn_exit.pack(side=tk.RIGHT, padx=5)

        link_frame = tk.LabelFrame(self.root, text="Пошук на AutoScout24 за параметрами")
        link_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(link_frame, text="Марка:").grid(row=0, column=0, padx=5, sticky="e")
        self.search_brand = tk.Entry(link_frame)
        self.search_brand.grid(row=0, column=1, padx=5)

        tk.Label(link_frame, text="Модель:").grid(row=0, column=2, padx=5, sticky="e")
        self.search_model = tk.Entry(link_frame)
        self.search_model.grid(row=0, column=3, padx=5)

        tk.Label(link_frame, text="Рік випуска:").grid(row=0, column=4, padx=15, pady=2, sticky="e")
        self.search_year = tk.Entry(link_frame)
        self.search_year.grid(row=0, column=5, padx=5)

        tk.Label(link_frame, text="Макс. пробіг:").grid(row=0, column=6, padx=5, sticky="e")
        self.search_mileage = tk.Entry(link_frame)
        self.search_mileage.grid(row=0, column=7, padx=5)

        # Ряд 1 — додаткові параметри
        tk.Label(link_frame, text="Тип пального:").grid(row=1, column=0, padx=5, pady=4, sticky="e")
        self.search_fuel = ttk.Combobox(link_frame, values=["", "Бензин", "Дизель", "Електро", "Гібрид", "Газ"], state="readonly")
        self.search_fuel.grid(row=1, column=1, padx=5)

        tk.Label(link_frame, text="Тип кузова:").grid(row=1, column=2, padx=15, pady=4, sticky="e")
        self.search_body = ttk.Combobox(link_frame, values=["", "Седан", "Хетчбек", "Купе", "Позашляховик", "Кабріолет", "Універсал", "Мінівен", "Пікап"], state="readonly")
        self.search_body.grid(row=1, column=3, padx=5)

        tk.Label(link_frame, text="Коробка передач:").grid(row=1, column=4, padx=15, pady=4, sticky="e")
        self.search_trans = ttk.Combobox(link_frame, values=["", "Автоматична", "Механічна", "Напівавтоматична"], state="readonly")
        self.search_trans.grid(row=1, column=5, padx=5)

        tk.Label(link_frame, text="Країна:").grid(row=2, column=4, padx=15, pady=4, sticky="e")
        self.search_country = ttk.Combobox(link_frame, values=[""] + ['Німеччина', 'Австрія', 'Бельгія', 'Іспанія', 'Франція', 'Італія', 'Люксембург', 'Нідерланди'], state="readonly")
        self.search_country.grid(row=2, column=5, padx=5)


        tk.Label(link_frame, text="Ціна до (€):").grid(row=2, column=0, padx=5, pady=4, sticky="e")
        self.search_price = tk.Entry(link_frame)
        self.search_price.grid(row=2, column=1, padx=5)

        btn_parse_params = tk.Button(link_frame, text="Знайти і спарсити", command=self.search_and_parse_autoscout)
        self.btn_parse_params = btn_parse_params
        btn_parse_params.grid(row=3, column=0, columnspan=8, pady=8)

        # Підключення перевірки для ввімкнення кнопки
        for widget in [
            self.search_brand, self.search_model, self.search_year, self.search_mileage,
            self.search_fuel, self.search_body, self.search_trans,
            self.search_price, self.search_country
        ]:
            widget.bind("<KeyRelease>", lambda e: self.check_parse_button_state())
            widget.bind("<<ComboboxSelected>>", lambda e: self.check_parse_button_state())
        self.check_parse_button_state()


        # ===== FILTER TABLE =====
        filter_frame = tk.Frame(self.root)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(filter_frame, text="Марка:").pack(side=tk.LEFT, padx=5)
        self.brand_entry = ttk.Entry(filter_frame, width=15)
        self.brand_entry.pack(side=tk.LEFT)

        tk.Label(filter_frame, text="Макс. ціна:").pack(side=tk.LEFT, padx=5)
        self.max_price_entry = ttk.Entry(filter_frame, width=10)
        self.max_price_entry.pack(side=tk.LEFT)

        tk.Label(filter_frame, text="Рік від:").pack(side=tk.LEFT, padx=5)
        self.year_from_entry = ttk.Entry(filter_frame, width=5)
        self.year_from_entry.pack(side=tk.LEFT)

        tk.Label(filter_frame, text="Рік до:").pack(side=tk.LEFT, padx=5)
        self.year_to_entry = ttk.Entry(filter_frame, width=5)
        self.year_to_entry.pack(side=tk.LEFT)

        btn_apply_filter = tk.Button(filter_frame, text="Застосувати фільтри", command=self.apply_filters)
        btn_apply_filter.pack(side=tk.LEFT, padx=10)

        self.sort_newest_first = tk.BooleanVar(value=True)
        self.sort_checkbox = tk.Checkbutton(filter_frame, text="Останні вгорі", variable=self.sort_newest_first, command=self.refresh_data)
        self.sort_checkbox.pack(side=tk.LEFT, padx=10)

        columns = ("Марка", "Модель",  "Рік", "Тип двигуна", "Обʼєм (л)", "Країна", "Ціна (€)", "Мито (грн)", "Фінальна ціна (грн)", "Посилання")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=20)
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=120)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.tree.bind("<Double-1>", self.open_link_on_click)
        self.refresh_data()

    def refresh_data(self):
        cars = get_all_cars()
        if self.sort_newest_first.get():
            cars = list(reversed(cars))
        self.update_table(cars)

    def apply_filters(self):
        brand = self.brand_entry.get().strip()
        max_price = self.max_price_entry.get().strip()
        year_from = self.year_from_entry.get().strip()
        year_to = self.year_to_entry.get().strip()
        cars = get_filtered_cars(brand, max_price, year_from, year_to)
        self.update_table(cars)

    def update_table(self, cars):
        self.tree.delete(*self.tree.get_children())
        for car in cars:
            values = []
            for i in range(len(self.tree["columns"])):
                if i < len(car):
                    col_name = self.tree["columns"][i]
                    val = car[i]

                    if col_name == "Тип двигуна":
                        val = ENGINE_TYPES.get(val, val)
                    elif col_name == "Тип кузова":
                        val = BODY_TYPES.get(val, val)
                    elif col_name == "Коробка передач":
                        val = TRANSMISSIONS.get(val, val)
                    elif col_name == "Привід":
                        val = DRIVE_TYPES.get(val, val)
                    elif col_name == "Країна":
                        val = COUNTRY_NAMES.get(val, val)

                    values.append(val)
                else:
                    values.append("—")
            self.tree.insert("", tk.END, values=values)

    def sort_by_column(self, column, refresh=True):
        index = self.tree["columns"].index(column)
        data = [(self.tree.item(item, "values"), item) for item in self.tree.get_children()]
        data.sort(key=lambda x: self.cast_value(x[0][index]), reverse=self.sort_reverse)
        for index, (values, item) in enumerate(data):
            self.tree.move(item, '', index)
        if refresh:
            self.sort_reverse = not self.sort_reverse
            self.sort_column = column

    def cast_value(self, value):
        try:
            return float(value.replace("€", "").replace(",", "").strip())
        except:
            try:
                return int(value)
            except:
                return value.lower()

    def run_parsers(self):
        parse_autoscout24()
        parse_mobile_de()
        self.refresh_data()
        messagebox.showinfo("Успішно", "Парсинг завершено та дані оновлено!")

    def search_and_parse_autoscout(self):
        brand = self.search_brand.get().strip()
        model = self.search_model.get().strip()
        year = self.search_year.get().strip()
        mileage = self.search_mileage.get().strip()
        priceto = self.search_price.get().strip()
        country_name = self.search_country.get().strip()
        country_code = None
        for k, v in COUNTRY_NAMES.items():
            if v == country_name:
                country_code = k
                break

        fuel_map = {
            "Бензин": "ft_gasoline", "Дизель": "D", "Електро": "E",
            "Гібрид": "H", "Газ": "L"
        }
        body_map = {
            "Седан": "1", "Хетчбек": "2", "Купе": "3", "Позашляховик": "6",
            "Кабріолет": "5", "Універсал": "7", "Мінівен": "8", "Пікап": "10"
        }
        trans_map = {
            "Автоматична": "automatic", "Механічна": "manual", "Напівавтоматична": "semiautomatic"
        }
        drive_map = {
            "Передній": "fwd", "Задній": "rwd", "Повний": "awd"
        }

        fuel = fuel_map.get(self.search_fuel.get().strip(), None)
        body = body_map.get(self.search_body.get().strip(), None)
        transmission = trans_map.get(self.search_trans.get().strip(), None)

        country_name = self.search_country.get().strip()
        country_code = {'Німеччина': 'D', 'Австрія': 'A', 'Бельгія': 'B', 'Іспанія': 'E', 'Франція': 'F', 'Італія': 'I', 'Люксембург': 'L', 'Нідерланди': 'NL'}.get(country_name, None)


        parse_autoscout24(
            brand=brand, model=model,
            year_from=year, year_to=year,
            mileage=mileage,
            fuel=fuel or None,
            body=body or None,
            priceto=priceto or None,
            transmission=transmission,
            country_code=country_code
        )
        messagebox.showinfo("Парсинг завершено", "Автомобілі за параметрами збережено.")
        self.refresh_data()
        self.root.update_idletasks()

    def open_link_on_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id:
            values = self.tree.item(item_id, "values")
            if len(values) >= 10:
                link = values[9]
                if isinstance(link, str) and link.startswith("http"):
                    import webbrowser
                    webbrowser.open(link)



    def check_parse_button_state(self):
        fields = [
            self.search_brand.get().strip(),
            self.search_model.get().strip(),
            self.search_year.get().strip(),
            self.search_mileage.get().strip(),
            self.search_fuel.get().strip(),
            self.search_body.get().strip(),
            self.search_trans.get().strip(),
            self.search_price.get().strip(),
            self.search_country.get().strip(),
        ]
        if any(fields):
            self.btn_parse_params.config(state="normal")
        else:
            self.btn_parse_params.config(state="disabled")
