from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QGroupBox, QLabel)
from PyQt5.QtGui import QFont, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from ui.widgets.circular_progress import CircularProgressBar

from ml.predictor import generate_prediction_data

class OverviewTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.update_dashboard()

    def init_ui(self):
        # --- Main Layout ---
        main_layout = QVBoxLayout(self)
        top_layout = QHBoxLayout()
        bottom_layout = QHBoxLayout()

        # --- Top Section: Chart and KPIs ---
        # Chart
        chart_group = QGroupBox("Quarterly Sales Projections")
        self.chart_layout = QVBoxLayout()
        self.canvas = MplCanvas(self, width=8, height=4, dpi=100)
        self.chart_layout.addWidget(self.canvas)
        chart_group.setLayout(self.chart_layout)
        top_layout.addWidget(chart_group, 3) # Give chart more space (ratio 3:1)

        # KPIs
        kpi_group = QGroupBox("Prediction Summary")
        kpi_layout = QVBoxLayout()
        self.kpi_prediction_label = QLabel("N/A")
        #UI
        self.kpi_prediction_label.setStyleSheet("""
            color: #ffffff;
            font-size: 60px;
            font-weight: bold;
        """)
        self.kpi_prediction_label.setAlignment(Qt.AlignCenter)

        self.kpi_title_label = QLabel("NEXT QUARTER PREDICTION")
        self.kpi_title_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.kpi_title_label.setAlignment(Qt.AlignCenter)
        # Use a stylesheet for the muted grey color and letter spacing for effect
        self.kpi_title_label.setStyleSheet("color: #888888; letter-spacing: 1px;")

        self.kpi_details_label = QLabel("+X.X% vs. Previous Quarter\nTOP PERFORMING SEGMENT: Enterprise")
        self.kpi_details_label.setAlignment(Qt.AlignCenter)
        self.kpi_details_label.setStyleSheet("color: #d0d0d0;")
        
        kpi_layout.addStretch(1)
        kpi_layout.addWidget(self.kpi_prediction_label)
        kpi_layout.addWidget(self.kpi_title_label)
        kpi_layout.addWidget(self.kpi_details_label)
        kpi_layout.addStretch(1)
        kpi_group.setLayout(kpi_layout)
        top_layout.addWidget(kpi_group, 1)
        #UI

        # --- Bottom Section: Performance Metrics ---
        # Model Performance
        model_perf_group = QGroupBox("Model Performance")
        self.model_perf_layout = QGridLayout()
        # We will populate this grid layout in update_dashboard
        model_perf_group.setLayout(self.model_perf_layout)
        bottom_layout.addWidget(model_perf_group)

        # Feature Weights
        feature_group = QGroupBox("Feature Weights")
        self.feature_layout = QGridLayout()
        # We will populate this grid layout in update_dashboard
        feature_group.setLayout(self.feature_layout)
        bottom_layout.addWidget(feature_group)
        
        # Data Quality
        quality_group = QGroupBox("Data Quality Score")
        quality_layout = QVBoxLayout()
        #UI
        self.quality_score_progress = CircularProgressBar()
        self.quality_score_progress.setFixedSize(150, 150)
        self.quality_score_progress.font_size = 28
        self.quality_score_progress.progress_width = 10
        self.quality_score_progress.progress_color = QColor("#4CAF50")
        quality_layout.addWidget(self.quality_score_progress, alignment=Qt.AlignCenter)
        #UI
        quality_group.setLayout(quality_layout)
        bottom_layout.addWidget(quality_group)

        # --- Assemble Layouts ---
        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_layout)

    def update_dashboard(self):
        """Fetches new data and updates all UI elements."""
        data = generate_prediction_data()
        
        if data.get("error"):
            # Clear the plot and display the error message
            self.canvas.axes.clear()
            self.canvas.axes.text(0.5, 0.5, data["error"], 
                                  ha='center', va='center', fontsize=12, wrap=True)
            self.canvas.draw()
            # Clear other UI elements
            self.kpi_prediction_label.setText("N/A")
            self.quality_score_label.setText("0%")
            self.clear_layout(self.model_perf_layout)
            self.clear_layout(self.feature_layout)
            return

        # Update Chart -UI
        self.canvas.axes.clear()
        self.canvas.axes.grid(True, color='#4a4a6a', linestyle='--', linewidth=0.5)
        self.canvas.axes.plot(data['historical_x'], data['historical_y'], marker='o', color='#03dac6', label='Actual Sales History')
        self.canvas.axes.plot(data['predicted_x'], data['predicted_y'], marker='o', linestyle='--', color='#bb86fc', label='Predicted')
        self.canvas.axes.set_title("Revenue Forecast")
        self.canvas.axes.set_xlabel("Time Period Index")
        self.canvas.axes.set_ylabel("Sales")
        legend = self.canvas.axes.legend()
        plt.setp(legend.get_texts(), color='#d0d0d0')
        self.canvas.draw()

        # Update KPI
        self.kpi_prediction_label.setText(data['next_quarter_prediction'])

        # Update Model Performance Table
        self.clear_layout(self.model_perf_layout)
        self.model_perf_layout.addWidget(QLabel("<b>Metric</b>"), 0, 0)
        self.model_perf_layout.addWidget(QLabel("<b>Value</b>"), 0, 1)
        row = 1
        for key, value in data['model_performance'].items():
            self.model_perf_layout.addWidget(QLabel(key), row, 0)
            self.model_perf_layout.addWidget(QLabel(str(value)), row, 1)
            row += 1


        # Update Feature Weights Table
        self.clear_layout(self.feature_layout)
        self.feature_layout.addWidget(QLabel("<b>Feature</b>"), 0, 0)
        self.feature_layout.addWidget(QLabel("<b>Weight</b>"), 0, 1)
        row = 1
        for key, value in data['feature_weights'].items():
            self.feature_layout.addWidget(QLabel(key), row, 0)
            self.feature_layout.addWidget(QLabel(f"{value:.2%}"), row, 1)
            row += 1

        # Update Data Quality Score -UI
        self.quality_score_progress.setValue(data['data_quality_score'])

    def clear_layout(self, layout):
        """Helper function to clear all widgets from a layout."""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()


class MplCanvas(FigureCanvas): # UI
    """A custom Matplotlib canvas widget to embed in PyQt."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        # Use a dark theme for the plot
        plt.style.use('dark_background')
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.patch.set_facecolor('#2a2a45') # Match groupbox background
        self.axes = fig.add_subplot(111)
        self.axes.set_facecolor('#2a2a45') # Match groupbox background
        
        # Style the axes
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.spines['bottom'].set_color('#888888')
        self.axes.spines['left'].set_color('#888888')
        self.axes.tick_params(axis='x', colors='#d0d0d0')
        self.axes.tick_params(axis='y', colors='#d0d0d0')
        self.axes.yaxis.label.set_color('#d0d0d0')
        self.axes.xaxis.label.set_color('#d0d0d0')
        self.axes.title.set_color('#ffffff')
        
        super(MplCanvas, self).__init__(fig)