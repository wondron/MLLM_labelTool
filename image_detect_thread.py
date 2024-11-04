from PyQt5.QtCore import pyqtSignal, QThread
import os, time

class WorkThread(QThread):
    def __init__(self):
        super().__init__()
        self.detect_name = ""
        
    def set_save_path(self, image_folder, save_path):
        self.save_path = save_path
        self.image_folder = image_folder
    
    def set_parameter(self, ssh_client, quote, method):
        self.ssh_client = ssh_client
        self.quote = quote
        self.method = method

    def run(self):
        # while True:
        print("thread_work start")
            # time.sleep(1)
        self.ssh_client.start_python_file(self.image_folder, self.quote, self.save_path, self.method)
        
        
class CountThread(QThread):
    complete_index_signal = pyqtSignal(int)
    def __init__(self):
        super().__init__()
        self.detect_name = ""
    
    def set_save_path(self, image_lens, save_path):
        self.save_path = os.path.join(save_path, "progress.ini")
        self.image_lens = image_lens
        print(self.save_path)
        
    def set_client(self, ssh_client):
        self.client = ssh_client
        
    def run(self):
        print("thread_count start")
        while True:
            index = self.client.read_progress_index(self.save_path)
            time.sleep(1)
            if index == None:
                continue
            
            # print(f'thread_count clicked，path={self.save_path}, val={index}, len={self.image_lens}')
            self.complete_index_signal.emit(index)
            if index >= self.image_lens - 1:
                print(f"index = {index}, 退出循环检测！")
                break