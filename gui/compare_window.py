from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidgetItem,
    QTableWidget, QPushButton, QVBoxLayout, QWidget
)
from car_table_model import CarTableModel
import sys

class CompareWindow(QMainWindow):
    def __init__(self, parent=None):
        super(CompareWindow, self).__init__(parent)
        self.setWindowTitle("Порівняння автомобілів")
        self.setGeometry(100, 100, 1000, 600)

        self.model = CarTableModel()  # Підключення до моделі даних
        self.selected_cars = []       # Для майбутнього порівняння

        self.init_ui()

    def init_ui(self):
        # 10 колонок під ваш набір полів
        self.table = QTableWidget(self)
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "Марка", "Модель", "Тип двигуна", "Об'єм двигуна",
            "Рік випуску", "Країна", "Вартість (€)",
            "Сума розмитнення (₴)", "Фінальна вартість (₴)",
            "Посилання"
        ])
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        self.load_data()

        self.compare_button = QPushButton("Порівняти", self)
        self.compare_button.clicked.connect(self.compare_selected_cars)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(self.compare_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_data(self):
        """Завантажує дані автомобілів в таблицю"""
        cars = self.model.get_all_cars()  # Очікуємо список dict-ів
        self.table.setRowCount(len(cars))

        for row, car in enumerate(cars):
            row_values = [
                car.get("brand", ""),
                car.get("model", ""),
                car.get("engine_type", ""),
                car.get("engine_volume", ""),
                car.get("year", ""),
                car.get("country", ""),
                car.get("price_eur", ""),
                car.get("customs_uah", ""),
                car.get("final_price_uah", ""),
                car.get("link", "")
            ]
            for col, val in enumerate(row_values):
                item = QTableWidgetItem(str(val))
                # якщо це посилання, можна додати можливість копіювання
                if col == 9:
                    item.setToolTip(str(val))
                self.table.setItem(row, col, item)

    def compare_selected_cars(self):
        """Порівнює вибрані автомобілі."""
        selected = self.table.selectionModel().selectedRows()
        if len(selected) != 2:
            print("Будь ласка, виберіть рівно два автомобілі для порівняння.")
            return

        cars = self.model.get_all_cars()
        self.selected_cars = []
        for sel in selected:
            idx = sel.row()
            # беремо весь dict-рядок
            self.selected_cars.append(cars[idx])
        self.show_comparison()

    def show_comparison(self):
        """Вивід у консоль деталей двох авто для простоти"""
        c1, c2 = self.selected_cars
        txt = (
            f"=== Порівняння ===\n\n"
            f"Авто 1: {c1['brand']} {c1['model']} | "
            f"{c1['engine_type']}, {c1['engine_volume']} л | "
            f"{c1['year']} | {c1['country']} | "
            f"Цена: €{c1['price_eur']} | Розмитнення: ₴{c1['customs_uah']} | "
            f"Фінальна: ₴{c1['final_price_uah']}\n\n"
            f"Авто 2: {c2['brand']} {c2['model']} | "
            f"{c2['engine_type']}, {c2['engine_volume']} л | "
            f"{c2['year']} | {c2['country']} | "
            f"Ціна: €{c2['price_eur']} | Розмитнення: ₴{c2['customs_uah']} | "
            f"Фінальна: ₴{c2['final_price_uah']}\n"
        )
        print(txt)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = CompareWindow()
    win.show()
    sys.exit(app.exec_())