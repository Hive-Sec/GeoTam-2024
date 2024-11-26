from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, QTimer
import sys
import io
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QFileDialog, QMessageBox, QComboBox)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QFont
import folium
import duckdb
import pandas as pd

COMPANY_CATEGORIES = [
    "Private Limited Company",
    "Charitable Incorporated Organisation",
    "PRI/LBG/NSC (Private, Limited by guarantee, no share capital, use of 'Limited' exemption)",
    "Limited Partnership",
    "Royal Charter Company"
]

def estimate_store_turnover(average_category_turnover, spatial_multiplier=1.2):
    estimated_turnover = average_category_turnover * spatial_multiplier
    return estimated_turnover

class CustomMessageBox(QMessageBox):
    def __init__(self, parent=None, title="", message=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setText(message)
        self.setStyleSheet("QMessageBox { background-color: black; color: #39FF14; }")
        self.addButton(QMessageBox.Ok)

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manchester Store Analysis")
        self.setGeometry(100, 100, 800, 700)
        self.setStyleSheet("background-color: black; color: #39FF14;")

        self.db_conn = None
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        title_label = QLabel("Manchester Store Analysis")
        title_label.setFont(QFont("Arial", 16))
        layout.addWidget(title_label, alignment=Qt.AlignCenter)

        input_layout = QHBoxLayout()
        self.file_entry = QLineEdit()
        self.file_entry.setStyleSheet("background-color: black; color: #39FF14; border: 1px solid #39FF14;")
        input_layout.addWidget(self.file_entry)

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_file)
        browse_button.setStyleSheet("background-color: black; color: #39FF14; border: 1px solid #39FF14;")
        input_layout.addWidget(browse_button)

        layout.addLayout(input_layout)

        upload_button = QPushButton("Upload")
        upload_button.clicked.connect(self.upload_file)
        upload_button.setStyleSheet("background-color: black; color: #39FF14; border: 1px solid #39FF14;")
        layout.addWidget(upload_button, alignment=Qt.AlignCenter)

        store_layout = QHBoxLayout()
        self.store_combo = QComboBox()
        self.store_combo.setStyleSheet("background-color: black; color: #39FF14; border: 1px solid #39FF14;")
        store_layout.addWidget(self.store_combo)

        estimate_button = QPushButton("Estimate Turnover")
        estimate_button.clicked.connect(self.estimate_turnover)
        estimate_button.setStyleSheet("background-color: black; color: #39FF14; border: 1px solid #39FF14;")
        store_layout.addWidget(estimate_button)

        layout.addLayout(store_layout)

        self.map_view = QWebEngineView()
        self.create_map()
        layout.addWidget(self.map_view)

        quit_button = QPushButton("Quit")
        quit_button.clicked.connect(self.close)
        quit_button.setStyleSheet("background-color: #00FF00; color: black;")
        quit_button.setFixedSize(50, 30)
        layout.addWidget(quit_button, alignment=Qt.AlignRight | Qt.AlignBottom)

    def create_map(self):
        manchester_coords = (53.4808, -2.2426)
        m = folium.Map(location=manchester_coords, zoom_start=12)

        stores = [
            {"name": "Store 1", "location": (53.4751, -2.2332), "category": "Retail"},
            {"name": "Store 2", "location": (53.4831, -2.2504), "category": "Restaurant"},
            {"name": "Store 3", "location": (53.4875, -2.2901), "category": "Service"}
        ]

        for store in stores:
            folium.Marker(
                store["location"],
                popup=f"{store['name']} - {store['category']}",
                icon=folium.Icon(color="green", icon="info-sign")
            ).add_to(m)

        data = io.BytesIO()
        m.save(data, close_file=False)
        self.map_view.setHtml(data.getvalue().decode())

    def browse_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select File", "", "CSV Files (*.csv)")
        if filename:
            self.file_entry.setText(filename)

    def upload_file(self):
        file_path = self.file_entry.text()
        if file_path:
            try:
                self.db_conn = self.create_duckdb_from_csv(file_path)
                self.update_store_combo()
                CustomMessageBox(self, "File Uploaded", f"File uploaded and database created: {file_path}").exec_()
            except Exception as e:
                CustomMessageBox(self, "Error", f"Failed to create database: {str(e)}").exec_()
        else:
            CustomMessageBox(self, "Error", "No file selected").exec_()

    def create_duckdb_from_csv(self, csv_path):
        conn = duckdb.connect('company_database.db')
        df = pd.read_csv(csv_path)
        filtered_df = df[df['CompanyCategory'].isin(COMPANY_CATEGORIES)]
        conn.register('companies_temp', filtered_df)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS companies AS 
            SELECT * FROM companies_temp
        ''')
        return conn

    def update_store_combo(self):
        if self.db_conn:
            companies = self.db_conn.execute('SELECT CompanyName FROM companies LIMIT 100').fetchdf()
            self.store_combo.clear()
            self.store_combo.addItems(companies['CompanyName'].tolist())

    def estimate_turnover(self):
        if not self.db_conn:
            CustomMessageBox(self, "Error", "No database loaded. Please upload a file first.").exec_()
            return

        selected_company = self.store_combo.currentText()
        company_info = self.db_conn.execute(f'''
            SELECT CompanyCategory, CompanyStatus
            FROM companies
            WHERE CompanyName = '{selected_company}'
        ''').fetchone()

        if company_info:
            category, status = company_info
            avg_turnover = 500000  # Placeholder value, replace with actual data if available
            estimated_turnover = estimate_store_turnover(avg_turnover)
            message = f"Estimated turnover for {selected_company}:\nCategory: {category}\nStatus: {status}\nEstimated Turnover: £{estimated_turnover:,.2f}"
            CustomMessageBox(self, "Turnover Estimate", message).exec_()
        else:
            CustomMessageBox(self, "Error", "Company information not found").exec_()

class WelcomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Welcome")
        self.setGeometry(100, 100, 400, 200)
        self.setStyleSheet("background-color: black; color: #39FF14;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.welcome_label = QLabel("Welcome to Manchester Store Analysis")
        self.welcome_label.setFont(QFont("Arial", 16))
        self.welcome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.welcome_label)

        self.animated_label = QLabel("")
        self.animated_label.setFont(QFont("Arial", 12))
        self.animated_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.animated_label)

        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.on_ok)
        ok_button.setStyleSheet("background-color: black; color: #39FF14; border: 1px solid #39FF14;")
        button_layout.addWidget(ok_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close)
        cancel_button.setStyleSheet("background-color: black; color: #39FF14; border: 1px solid #39FF14;")
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.animation_text = """Welcome 2 GEOTAM 
        Loading spatial analysis data..."""
        self.animation_index = 0
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.animate_text)
        self.animation_timer.start(100)

    def animate_text(self):
        self.animation_index += 1
        if self.animation_index > len(self.animation_text):
            self.animation_index = 0
        self.animated_label.setText(self.animation_text[:self.animation_index])

    def on_ok(self):
        self.animation_timer.stop()
        self.close()
        self.main_app = MainApp()
        self.main_app.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    welcome_window = WelcomeWindow()
    welcome_window.show()
    sys.exit(app.exec_())
