import os
import sys
import datetime
import subprocess
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QLabel, QPushButton, QListWidget, QListWidgetItem, QComboBox)
from PyQt5.QtCore import QThread
from core.workers import ReportGenerationWorker

class ReportsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.thread = None
        self.worker = None
        self.init_ui()
        self.populate_reports_list()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        generator_group = QGroupBox("Historical Performance Reports")
        generator_layout = QHBoxLayout()
        
        generator_layout.addWidget(QLabel("Forecast Period:"))
        self.period_combo = QComboBox()
        self.period_combo.addItems(["1 Quarter (3 Months)", "2 Quarters (6 Months)", 
                                    "3 Quarters (9 Months)", "4 Quarters (12 Months)"])
        self.period_combo.setCurrentIndex(3)
        generator_layout.addWidget(self.period_combo)

        generator_layout.addWidget(QLabel("Region:"))
        generator_layout.addWidget(QPushButton("Global"))
        generator_layout.addStretch()
        
        self.generate_button = QPushButton("Generate New Report")
        self.generate_button.clicked.connect(self.start_report_generation)
        generator_layout.addWidget(self.generate_button)
        generator_group.setLayout(generator_layout)

        list_group = QGroupBox("Generated Reports")
        list_layout = QVBoxLayout()
        self.report_list = QListWidget()
        list_layout.addWidget(self.report_list)
        list_group.setLayout(list_layout)

        main_layout.addWidget(generator_group)
        main_layout.addWidget(list_group)
        self.setLayout(main_layout)
        
    def populate_reports_list(self):
        self.report_list.clear()
        report_dir = "reports"
        if not os.path.exists(report_dir): os.makedirs(report_dir); return
        files = [f for f in os.listdir(report_dir) if f.endswith('.pdf')]
        files.sort(key=lambda x: os.path.getmtime(os.path.join(report_dir, x)), reverse=True)
        for filename in files:
            self.add_report_item(os.path.splitext(filename)[0], "Completed", os.path.join(report_dir, filename))

    def start_report_generation(self):
        num_months = (self.period_combo.currentIndex() + 1) * 3
        self.generate_button.setEnabled(False)
        self.generate_button.setText("Generating...")

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = f"Sales_Forecast_{num_months}m_{timestamp}"
        output_path = os.path.join("reports", f"{report_name}.pdf")

        self.add_report_item(report_name, "In Progress")

        self.thread = QThread()
        self.worker = ReportGenerationWorker(output_path, report_name, num_months)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_report_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_report_finished(self, report_name, result, success):
        for i in range(self.report_list.count()):
            item = self.report_list.item(i)
            widget = self.report_list.itemWidget(item)
            if widget.property("report_name") == report_name:
                status_label = widget.findChild(QLabel, "status_label")
                if success:
                    status_label.setText("Completed")
                    status_label.setStyleSheet("color: #03dac6;")
                else:
                    status_label.setText("Failed")
                    status_label.setStyleSheet("color: #ff4444;")
                break
        self.generate_button.setEnabled(True)
        self.generate_button.setText("Generate New Report")

    def add_report_item(self, name, status, file_path=None):
        item = QListWidgetItem(self.report_list)
        item_widget = QWidget()
        item_layout = QHBoxLayout()
        date_str = datetime.date.today().strftime('%Y-%m-%d')
        item_layout.addWidget(QLabel(f"{name}\nDate: {date_str}"))
        item_layout.addStretch()
        status_label = QLabel(status)
        status_label.setObjectName("status_label")
        status_label.setStyleSheet("color: #03dac6;" if status == "Completed" else "color: orange;")
        item_layout.addWidget(status_label)
        view_button = QPushButton("View")
        view_button.clicked.connect(lambda: self.view_report(name))
        item_layout.addWidget(view_button)
        item_widget.setLayout(item_layout)
        item_widget.setProperty("report_name", name)
        item.setSizeHint(item_widget.sizeHint())
        self.report_list.addItem(item)
        self.report_list.setItemWidget(item, item_widget)
        
    def view_report(self, report_name):
        path = os.path.abspath(os.path.join("reports", f"{report_name}.pdf"))
        if os.path.exists(path):
            if sys.platform == "win32": os.startfile(path)
            elif sys.platform == "darwin": subprocess.call(["open", path])
            else: subprocess.call(["xdg-open", path])