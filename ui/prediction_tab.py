from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QLabel, QCheckBox, QLineEdit, QSlider, QPushButton,
                             QProgressBar, QSpacerItem, QSizePolicy, QButtonGroup)
from PyQt5.QtCore import Qt, QThread
from core.workers import ModelTrainingWorker
from ui.widgets.circular_progress import CircularProgressBar
from ui.widgets.toggle_switch import ToggleSwitch

class PredictionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.thread = None
        self.worker = None
        self.init_ui()
        
        # Connect signals to slots
        self.retrain_button.clicked.connect(self.start_training)
        self.cancel_button.clicked.connect(self.cancel_training)

    def init_ui(self):
        # 1. Create the main vertical layout for the entire tab
        final_layout = QVBoxLayout(self)
        # 2. Create a horizontal layout for the three content columns
        content_layout = QHBoxLayout()
        left_vbox = QVBoxLayout()
        feature_group = QGroupBox("Feature Selection")
        feature_layout = QVBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search")
        feature_layout.addWidget(self.search_bar)
        self.feature_checkboxes = {
            "Historical Sales Data": QCheckBox("Historical Sales Data"),
            "Economic Indicators": QCheckBox("Economic Indicators"),
            "Competitor Activity": QCheckBox("Competitor Activity"),
            "Website Traffic": QCheckBox("Website Traffic"),
        }
        self.feature_checkboxes["Historical Sales Data"].setChecked(True)
        self.feature_checkboxes["Economic Indicators"].setChecked(True)
        for name, checkbox in self.feature_checkboxes.items():
            feature_layout.addWidget(checkbox)
        feature_layout.addStretch(1)
        feature_group.setLayout(feature_layout)
        left_vbox.addWidget(feature_group)
        content_layout.addLayout(left_vbox, 1)
        center_vbox = QVBoxLayout()
        algo_group = QGroupBox("Algorithm Choice")
        algo_layout = QVBoxLayout()
        # UI
        self.algo_gradient_boosting = ToggleSwitch()
        self.algo_random_forest = ToggleSwitch()
        self.algo_neural_network = ToggleSwitch()
        self.algo_gradient_boosting.setChecked(True)
        
        self.algo_button_group = QButtonGroup(self)
        self.algo_button_group.setExclusive(True)
        
        self.algo_button_group.addButton(self.algo_gradient_boosting)
        self.algo_button_group.addButton(self.algo_random_forest)
        self.algo_button_group.addButton(self.algo_neural_network)
        
        gb_layout = QHBoxLayout()
        gb_layout.addWidget(QLabel("Gradient Boosting"))
        gb_layout.addStretch()
        gb_layout.addWidget(self.algo_gradient_boosting)
        
        rf_layout = QHBoxLayout()
        rf_layout.addWidget(QLabel("Random Forest"))
        rf_layout.addStretch()
        rf_layout.addWidget(self.algo_random_forest)
        
        nn_layout = QHBoxLayout()
        nn_layout.addWidget(QLabel("Neural Network"))
        nn_layout.addStretch()
        nn_layout.addWidget(self.algo_neural_network)

        algo_layout.addLayout(gb_layout)
        algo_layout.addLayout(rf_layout)
        algo_layout.addLayout(nn_layout)
        #UI
        algo_group.setLayout(algo_layout)
        center_vbox.addWidget(algo_group)
        hyper_group = QGroupBox("Hyperparameters")
        hyper_layout = QVBoxLayout()
        hyper_layout.addWidget(QLabel("N_Estimators"))
        self.n_estimators_slider = QSlider(Qt.Horizontal)
        self.n_estimators_slider.setRange(100, 1000)
        self.n_estimators_slider.setValue(100)
        hyper_layout.addWidget(self.n_estimators_slider)
        hyper_layout.addWidget(QLabel("Max Training:"))
        self.max_training_slider = QSlider(Qt.Horizontal)
        self.max_training_slider.setValue(100)
        hyper_layout.addWidget(self.max_training_slider)
        hyper_group.setLayout(hyper_layout)
        center_vbox.addWidget(hyper_group)
        content_layout.addLayout(center_vbox, 1)
        right_vbox = QVBoxLayout()
        #UI
        self.training_progress = CircularProgressBar()
        self.training_progress.setFixedSize(200, 200)
        self.training_progress.setValue(0)
        self.training_status_label = QLabel("Ready to train")
        self.training_status_label.setAlignment(Qt.AlignCenter)
        self.training_status_label.setStyleSheet("color: #d0d0d0; font-size: 16px; font-weight: bold;")
        right_vbox.addWidget(self.training_progress, alignment=Qt.AlignCenter)
        right_vbox.addWidget(self.training_status_label)
        #UI
        summary_group = QGroupBox("Last Training Summary")
        summary_layout = QVBoxLayout()
        
        subtle_style = "color: #888888; font-size: 12px;"
        
        # These labels show the actual results, so they can keep the default style
        self.summary_label_progress = QLabel("-") 
        self.summary_label_accuracy = QLabel("-")
        self.summary_label_model_id = QLabel("-")

        # Create new labels for the static text and style them
        progress_title_label = QLabel("Training Progress:")
        progress_title_label.setStyleSheet(subtle_style)
        
        accuracy_title_label = QLabel("Model Metric (RMSE):")
        accuracy_title_label.setStyleSheet(subtle_style)
        
        model_id_title_label = QLabel("Model ID:")
        model_id_title_label.setStyleSheet(subtle_style)

        # Add widgets to layout
        summary_layout.addWidget(progress_title_label)
        summary_layout.addWidget(self.summary_label_progress)
        summary_layout.addSpacing(10) # Add a little space between sections
        summary_layout.addWidget(accuracy_title_label)
        summary_layout.addWidget(self.summary_label_accuracy)
        summary_layout.addSpacing(10)
        summary_layout.addWidget(model_id_title_label)
        summary_layout.addWidget(self.summary_label_model_id)
        
        summary_group.setLayout(summary_layout)
        right_vbox.addWidget(summary_group)
        content_layout.addLayout(right_vbox, 1)
        # --- End of columns setup ---
        final_layout.addLayout(content_layout)
        bottom_hbox = QHBoxLayout()
        self.retrain_button = QPushButton("RETRAIN MODEL")
        self.cancel_button = QPushButton("CANCEL TRAINING")
        self.cancel_button.setEnabled(False)
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        bottom_hbox.addSpacerItem(spacer)
        bottom_hbox.addWidget(self.cancel_button)
        bottom_hbox.addWidget(self.retrain_button)
        final_layout.addLayout(bottom_hbox)


    def start_training(self):
        """Gathers UI settings and starts the worker thread."""
        print("UI: Starting training process...")
        # Prevent starting a new training run while one is active
        if self.thread and self.thread.isRunning():
            print("UI: A training process is already running.")
            return

        # 1. Update UI to reflect training state
        self.retrain_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.training_progress.setValue(0)
        self.training_status_label.setText("Training in progress...") 

        # 2. Gather data from UI
        selected_features_list = [name for name, cb in self.feature_checkboxes.items() if cb.isChecked()]
        
        algorithm_choice = "Gradient Boosting" # Default
        if self.algo_random_forest.isChecked():
            algorithm_choice = "Random Forest"
        elif self.algo_neural_network.isChecked():
            algorithm_choice = "Neural Network"
            
        hyperparameters = {
            "n_estimators": self.n_estimators_slider.value()
            # You can add more here as you add more sliders
        }
        
        # 3. Create a QThread and a worker object
        self.thread = QThread()
        self.worker = ModelTrainingWorker(
            selected_features_list=selected_features_list,
            algorithm_choice=algorithm_choice,
            hyperparameters=hyperparameters
        )
        
        # 4. Move worker to the thread
        self.worker.moveToThread(self.thread)
        
        # 5. Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_training_finished)
        self.worker.progress.connect(self.set_progress)
        
        # Cleanup connections
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.thread.finished.connect(self.on_thread_finished)
        
        # 6. Start the thread
        self.thread.start()

    def cancel_training(self):
        """Stops the training thread."""
        print("UI: Attempting to cancel training...")
        if self.thread and self.thread.isRunning():
            self.worker.stop()
            self.thread.quit()
            self.thread.wait() # Wait for the thread to finish
            print("UI: Training canceled.")
            self.retrain_button.setEnabled(True)
            self.cancel_button.setEnabled(False)
            self.training_progress.setValue(0)
            self.training_status_label.setText("Cancelled")

    def set_progress(self, value):#UI
        """Updates the progress bar."""
        self.training_progress.setValue(value)

    def on_training_finished(self, results):
        """Handles the results from the worker thread."""
        print("UI: Worker finished, received results.")
        
        # Check if an error occurred during training
        if "error" in results:
            self.summary_label_progress.setText("Error")
            self.summary_label_accuracy.setText("-")
            self.summary_label_model_id.setText(f"{results['error']}")
            self.training_status_label.setText("Error")
            self.training_status_label.setStyleSheet("color: red; font-size: 16px; font-weight: bold;")
        else:
            self.summary_label_progress.setText("Completed")
            self.summary_label_accuracy.setText(str(results['rmse']))
            self.summary_label_model_id.setText(results['model_id'])
            self.training_status_label.setText("Completed")
            self.training_status_label.setStyleSheet("color: #03dac6; font-size: 16px; font-weight: bold;")

        # Re-enable the UI
        self.retrain_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        
    def on_thread_finished(self):
        """Cleans up thread and worker references after the thread has finished."""
        print("UI: Thread has finished. Cleaning up references.")
        self.thread = None
        self.worker = None