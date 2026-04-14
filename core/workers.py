import time
import os
from PyQt5.QtCore import QObject, pyqtSignal
from core.report_generator import generate_report_pdf
from ml.model_handler import train_model 

class ModelTrainingWorker(QObject):
    """
    Модель сургахад ашиглагддаг Worker. 
    Prediction Tab-д шаардлагатай.
    """
    finished = pyqtSignal(dict)      
    progress = pyqtSignal(int)       
    
    def __init__(self, selected_features_list, algorithm_choice, hyperparameters):
        super().__init__()
        self.selected_features_list = selected_features_list
        self.algorithm_choice = algorithm_choice
        self.hyperparameters = hyperparameters
        self.is_running = True

    def run(self):
        for i in range(1, 6):
            if not self.is_running:
                break 
            time.sleep(1) 
            self.progress.emit(i * 15) 

        if self.is_running:
            results = train_model(
                self.selected_features_list, self.algorithm_choice, self.hyperparameters
            )
            self.progress.emit(100)
            self.finished.emit(results)

    def stop(self):
        self.is_running = False

class ReportGenerationWorker(QObject):
    """
    PDF тайлан гаргахад ашиглагддаг Worker.
    Reports Tab-д шаардлагатай.
    """
    # Сигнал: (Тайлангийн нэр, Файлын зам эсвэл алдаа, Амжилттай эсэх)
    finished = pyqtSignal(str, str, bool) 

    def __init__(self, output_path, report_name, num_months):
        super().__init__()
        self.output_path = output_path
        self.report_name = report_name
        self.num_months = num_months

    def run(self):
        try:
            # Тайлан үүсгэх процесс (1 секунд хүлээх)
            time.sleep(1)
            
            # PDF генераторыг дуудах
            generate_report_pdf(self.output_path, self.report_name, self.num_months)
            
            # Амжилттай бол сигнал илгээх
            self.finished.emit(self.report_name, self.output_path, True)
        except Exception as e:
            print(f"Report generation error: {e}")
            # Алдаа гарвал сигнал илгээх
            self.finished.emit(self.report_name, str(e), False)