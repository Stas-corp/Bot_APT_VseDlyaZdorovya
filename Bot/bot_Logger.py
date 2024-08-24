import logging
from logging.handlers import TimedRotatingFileHandler
from logging import StreamHandler
import os
import glob
import time

class Logger:
    def __init__(self, log_directory='logs', log_filename="app_log", retention_days=30):
        self.log_directory = log_directory
        self.log_filename = log_filename
        self.retention_days = retention_days
        self.logger = logging.getLogger()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        log_file_path = os.path.join(log_directory, log_filename)
        self.handler = TimedRotatingFileHandler(log_file_path, 
                                                when='midnight',
                                                interval=1, 
                                                backupCount=retention_days, 
                                                encoding='utf-8')
        self.handler.setFormatter(formatter)

        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setFormatter(formatter)
        
        self.logger.setLevel(logging.WARN)
        self.logger.addHandler(self.handler)
        self.logger.addHandler(self.stream_handler)

    def delete_old_logs(self):
        """Dell log file olded retention_days"""
        now = time.time()
        cutoff_time = now - (self.retention_days * 86400)  # 86400 секунд в одном дне

        for log_file in glob.glob(os.path.join(self.log_directory, f"{self.log_filename}*")):
            if os.path.isfile(log_file):
                file_creation_time = os.path.getctime(log_file)
                if file_creation_time < cutoff_time:
                    os.remove(log_file)
                    self.logger.info(f"Удален старый лог файл: {log_file}")

    def info(self, message):
        self.logger.info(message)

    def warn(self, message):
        self.logger.warn(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)
