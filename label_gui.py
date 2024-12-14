import sys, os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QTextEdit,QLineEdit, QComboBox, QSpinBox
from PyQt5.QtWidgets import QHBoxLayout, QFileDialog, QSizePolicy, QSplitter, QTableWidget, QTableWidgetItem, QSpacerItem
from PyQt5.QtGui import QPixmap, QImage, QTextCursor
from PyQt5.QtCore import pyqtSignal, QThread, QUrl, QByteArray, Qt
from z_sshTool import SSHClient
from z_lightTool import CircleLabel
from z_showfileTol import FileReview
from z_imageViewer import ImageViewer
from z_openai_test import MLLMClient
import z_dataprocess
import image_detect_thread

qLineEditStyle = """
            QLineEdit {
                border: 2px solid #8F8F91;
                border-radius: 5px;
                padding: 2px;
                background: white;
                selection-background-color: darkgray;
            }
        """

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.iniThread()        
        self.isLinux = False
        
    def iniThread(self):
        self.thread_dtct = image_detect_thread.WorkThread()
        self.thread_count = image_detect_thread.CountThread()
        self.thread_count.complete_index_signal.connect(self.handle_thread)
        
    def handle_thread(self, index):
        self.complete_index = index
        print(f"完成第{index}张图像检测！")

    def initUI(self):
        self.setWindowTitle('食材标注软件')
        self.api_client = None

        # 创建两个窗口
        self.l_widget = QWidget()
        self.m_widet = QWidget()
        self.r_widget = QWidget()

        # 设置窗口背景颜色以便于区分
        self.l_widget.setStyleSheet("background-color: #E6F7FF; border: 2px solid #87CEFA; border-radius: 5px; padding: 5px;")
        self.m_widet.setStyleSheet("background-color: #E6F7FF; border: 2px solid #87CEFA; border-radius: 5px; padding: 5px;")
        self.r_widget.setStyleSheet("background-color: #F0F0F0; border: 2px solid #C0C0C0; border-radius: 5px; padding: 5px;")

        # 在每个窗口中添加布局
        left_layout = QVBoxLayout()
        mid_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # 在布局中添加控件
        self.l_widget.setLayout(left_layout)
        self.m_widet.setLayout(mid_layout)
        self.r_widget.setLayout(right_layout)

        # 创建一个水平分割器
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.l_widget)
        splitter.addWidget(self.m_widet)
        splitter.addWidget(self.r_widget)

        # 设置分割器比例
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 4)
        splitter.setStretchFactor(2, 3)

        # 创建一个垂直布局并添加分割器
        vbox = QVBoxLayout(self)
        vbox.addWidget(splitter)
        self.setLayout(vbox)

        # 设置窗口初始大小
        self.resize(1000, 700)
        
        #右侧文件名显示
        file_layout = QVBoxLayout()
        self.fileReview = FileReview('文件列表')
        self.fileReview.itemClicked.connect(self.on_image_clicked)
        file_layout.addWidget(self.fileReview)
        file_layout.setStretch(0, 2)
        
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        file_layout.addWidget(self.log_edit)
        file_layout.setStretch(1, 1)
        
        left_layout.addLayout(file_layout)
        
        # 服务器配置
        server_layout = QHBoxLayout()
        self.label = QLabel("配置文件路径")
        server_layout.addWidget(self.label)
        self.config_edit = QLineEdit ("./config")
        self.config_edit.setStyleSheet(qLineEditStyle)
        self.config_edit.setMaximumHeight(25)
        server_layout.addWidget(self.config_edit)
        self.select_config = QPushButton("...")
        self.select_config.setMaximumWidth(50)
        self.select_config.clicked.connect(self.on_broswer_clicked)
        server_layout.addWidget(self.select_config)
        self.connect_state = CircleLabel(25)
        self.connect_state.stateChanged.connect(self.on_ssh_state_changed)
        server_layout.addWidget(self.connect_state)
        self.btn_connect_ssh = QPushButton("SSH连接")
        self.btn_connect_ssh.clicked.connect(self.get_client)
        server_layout.addWidget(self.btn_connect_ssh)
        mid_layout.addLayout(server_layout)
        
        # 食材名称选择
        label_layout = QHBoxLayout()
        self.remote_path_label = QLabel("远程路径")
        label_layout.addWidget(self.remote_path_label)
        self.remote_path_edit = QLineEdit("/data/wangzhuo/00-dataset/01-MLLM/00_image/多宝鱼")
        label_layout.addWidget(self.remote_path_edit)
        self.btn_get_imagefiles = QPushButton("文件列表获取")
        self.btn_get_imagefiles.clicked.connect(self.on_getfiles_clicked)
        label_layout.addWidget(self.btn_get_imagefiles)
        mid_layout.addLayout(label_layout)

        # 图像显示
        self.image_display = ImageViewer()
        self.image_display.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        mid_layout.addWidget(self.image_display)

        #操作按钮
        operator_layout = QHBoxLayout()
        self.up = QPushButton("上一张(1)")
        self.up.clicked.connect(self.on_btn_up)
        self.up.setEnabled(False)
        self.up.setShortcut("1")
        operator_layout.addWidget(self.up)
        
        self.down = QPushButton("下一张(2)")
        self.down.clicked.connect(self.on_btn_down)
        self.down.setEnabled(False)
        self.down.setShortcut("2")
        operator_layout.addWidget(self.down)
        
        self.save = QPushButton("保存(c)")
        self.save.clicked.connect(self.on_btn_save)
        self.save.setEnabled(False)
        self.save.setShortcut("c")
        operator_layout.addWidget(self.save)
        
        self.delete = QPushButton("删除(v)")
        self.delete.clicked.connect(self.on_btn_delete)
        self.delete.setEnabled(False)
        self.delete.setShortcut("v")
        operator_layout.addWidget(self.delete)
        
        mid_layout.addLayout(operator_layout)

        # 右边布局
        API_operator_layout = QHBoxLayout()
        
        self.api_onnect_state = CircleLabel(25)
        self.api_onnect_state.stateChanged.connect(self.on_api_state_changed)
        API_operator_layout.addWidget(self.api_onnect_state)
        
        self.btn_connect_api = QPushButton("api连接")
        self.btn_connect_api.setMinimumHeight(40)
        self.btn_connect_api.clicked.connect(self.on_mllm_connect)
        API_operator_layout.addWidget(self.btn_connect_api)
        
        self.btn_detect_api = QPushButton("检测(3)")
        self.btn_detect_api.setShortcut("3")
        self.btn_detect_api.setMinimumHeight(40)
        self.btn_detect_api.clicked.connect(self.on_mllm_detect)
        API_operator_layout.addWidget(self.btn_detect_api)
        
        self.btn_detect_total_api = QPushButton("全部检测")
        self.btn_detect_total_api.setMinimumHeight(40)
        self.btn_detect_total_api.clicked.connect(self.on_mllm_total_detect)
        API_operator_layout.addWidget(self.btn_detect_total_api)
        right_layout.addLayout(API_operator_layout)
        
        quote_layout = QHBoxLayout()
        quote_label = QLabel("quote输入")
        quote_label.setStyleSheet("border: none;")
        quote_layout.addWidget(quote_label)
        
        # qspace = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        # quote_layout.addWidget(qspace)
        
        self.qSpin = QSpinBox()
        self.qSpin.setRange(0, 9999)
        self.qSpin.setValue(980)
        quote_layout.addWidget(self.qSpin)
        
        right_layout.addLayout(quote_layout)
        self.quote_edit = QTextEdit("图中存在哪些食材？没有食材就返回“无”，请简短回答无需输出无关字符。")
        self.quote_edit.setMaximumHeight(150)
        right_layout.addWidget(self.quote_edit)
        
        answer_label = QLabel("大模型输出")
        right_layout.addWidget(answer_label)
        answer_label.setStyleSheet("border: none;")
        self.api_result_edit = QTextEdit()
        self.api_result_edit.setMinimumHeight(150)
        self.api_result_edit.setReadOnly(True)
        right_layout.addWidget(self.api_result_edit)
        
        #表格修改
        json_operator_layout = QHBoxLayout()
        json_label = QLabel("图像描述")
        json_label.setStyleSheet("border: none;")
        json_operator_layout.addWidget(json_label)
        right_layout.addLayout(json_operator_layout)
        
        self.label_text_edit = QTextEdit()        
        right_layout.addWidget(self.label_text_edit)
        right_layout.setContentsMargins(5, 5, 5, 5)
        self.label_text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.label_text_edit.setSizeAdjustPolicy(QTableWidget.AdjustToContents)
        
        #标签列表
        food_label = QLabel("食材列表")
        food_label.setStyleSheet("border: none;")
        self.label_food_list_edit = QTextEdit()
        right_layout.addWidget(food_label)
        right_layout.addWidget(self.label_food_list_edit)
        
             
    def get_client(self):
        try:
            client_config = os.path.join(self.config_edit.text(), "ssh_config.ini")
            client_config = client_config.replace('\\', '/')
            self.client = SSHClient(client_config)
            self.client.connect_linux()
            self.connect_state.setState(1)
        except Exception as e:
            raise ConnectionError(f"SSH连接失败->{e}")
        
    def on_ssh_state_changed(self):
        self.btn_connect_ssh.setEnabled(not self.connect_state.getState())
        
    def on_api_state_changed(self):
        self.btn_connect_api.setEnabled(not self.api_onnect_state.getState())
        
    def on_broswer_clicked(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹", options=options)
        self.config_edit.setText(folder_path)
                
    def on_confirm_savedir(self):
        current_dir = self.remote_path_edit.text()
        current_dir = current_dir.replace('\\', '/')
        current_dir = current_dir.replace('//', '/')
        self.remote_path_edit.setText(current_dir)
        if not (current_dir.endswith('/')):
            current_dir = current_dir + '/'
            self.remote_path_edit.setText(current_dir)
        
        #获取标注文件夹
        if '00_image' not in current_dir:
            print("---标注文件夹命名错误，直接返回！--- ")
            return False
        
        # 获取 current_dir 含有 00_image 字符串的数量
        count_00_image = current_dir.count('00_image')
        if count_00_image > 1:
            print(f"当前路径中包含 '00_image' 的数量: {count_00_image} > 1，命名错误返回NG！")
            return False

        self.mllm_descri = current_dir.replace('00_image', '01_descri')
        self.mllm_foodList = current_dir.replace('00_image', '02_foodList')
        return True
        
    def on_getfiles_clicked(self):
        if not self.on_confirm_savedir():
            return 
        #当前文件夹
        current_dir = self.remote_path_edit.text()
        
        if z_dataprocess.is_linux_folder_path(current_dir):
            self.isLinux = True
            #图像更新
            self.name_dict = self.client.get_image_names(self.remote_path_edit.text())
        else:
            self.isLinux = False
            self.name_dict = z_dataprocess.get_image_dict(self.remote_path_edit.text())
            
        self.fileReview.update_list(self.name_dict)
        
        if len(self.name_dict):
            self.up.setEnabled(True)
            self.down.setEnabled(True)
            self.save.setEnabled(True)
            self.delete.setEnabled(True)
           
    def on_image_clicked(self, item_name, item_index):
        if self.isLinux:
            pixmap = self.client.get_image(item_name, "temp_name")
            self.image_display.display_image(pixmap)
        else:
            pixmap = QPixmap(item_name)
            self.image_display.display_image(pixmap)
            
        self.item_index = item_index
        self.cur_image_path = item_name
        self.label_text_edit.clear()
        self.api_result_edit.clear()

        #保存文件名
        self.on_confirm_savedir()
        json_name = list(self.name_dict.keys())[self.item_index] + '.json'
        label_json_file = os.path.join(self.mllm_descri, json_name)
        list_json_file = os.path.join(self.mllm_foodList, json_name)
        
        if self.isLinux:
            json_descri = self.client.read_json(label_json_file)
            json_list = self.client.read_json(list_json_file)
        else:
            json_descri = z_dataprocess.read_json(label_json_file)
            json_list = z_dataprocess.read_json(list_json_file)
        
        descri_str = z_dataprocess.parse_json_data(json_descri, 1)
        list_str = z_dataprocess.parse_json_data(json_list, 1)
        self.label_text_edit.setText(descri_str)
        self.label_food_list_edit.setText(list_str)

    def write(self, text):
        cursor = self.log_edit.textCursor()
        cursor.insertText(text)
        self.log_edit.moveCursor(QTextCursor.End)
        
    def close(self):
        sys.stdout = self.original_stdout
        
    def on_mllm_connect(self):
        ssh_config = os.path.join(self.config_edit.text(), "mllm_config.ini")
        ssh_config = ssh_config.replace('\\', '/')
        self.api_client = MLLMClient(ssh_config)
        self.api_onnect_state.setState(1)
    
    def on_mllm_detect(self):
        if self.isLinux:
            self.client.get_image(self.cur_image_path)
            result = self.api_client.detect('temp_name', self.quote_edit.toPlainText(), self.qSpin.value())
        else:
            result = self.api_client.detect(self.cur_image_path, self.quote_edit.toPlainText(), self.qSpin.value())    
            
        self.api_result_edit.setText(result)
        show_res = z_dataprocess.parse_mllm_result(result, 1)
        
        # self.label_text_edit.clear()
        # self.label_text_edit.setText(show_res)
 
    def on_mllm_total_detect(self):
        quote = self.quote_edit.toPlainText()
        image_folder = self.remote_path_edit.text()
        self.on_confirm_savedir()
        save_dir = self.save_dir
        # self.thread_dtct.set_save_path(image_folder, save_dir)
        # self.thread_dtct.set_parameter(self.client, quote, self.comb_func.currentIndex())
        # self.thread_dtct.start()
        self.client.start_python_file(image_folder, quote, save_dir, self.comb_func.currentIndex())
        
        self.thread_count.set_save_path(len(self.name_dict.keys()), save_dir)
        self.thread_count.set_client(self.client)
        self.thread_count.start()

    def on_btn_up(self):
        if self.item_index == 0:
            print("已是第一张图像")
            return
        self.item_index = self.item_index - 1
        self.fileReview.setCurrentIndex(self.item_index)
    
    def on_btn_down(self):
        if self.item_index + 1 == len(list(self.name_dict.keys())):
            print("已是最后一张图像")
            return
        self.item_index = self.item_index + 1
        self.fileReview.setCurrentIndex(self.item_index)
    
    def on_btn_save(self):
        self.on_confirm_savedir()

        json_name = list(self.name_dict.keys())[self.item_index] + '.json'
        label_json_file = os.path.join(self.mllm_descri, json_name)
        list_json_file = os.path.join(self.mllm_foodList, json_name)

        descri_text = self.label_text_edit.toPlainText()
        foodList_text = self.label_food_list_edit.toPlainText()
        
        descri_data = z_dataprocess.generate_sharegpt_data(descri_text, self.cur_image_path, 1)
        foodList_data = z_dataprocess.generate_sharegpt_data(foodList_text, self.cur_image_path, 2)

        if self.isLinux:
            self.client.create_remote_folder(os.path.dirname(label_json_file))
            self.client.create_remote_folder(os.path.dirname(list_json_file))        
            self.client.writeJson(label_json_file, descri_data)
            self.client.writeJson(list_json_file, foodList_data)
        else:
            os.makedirs(os.path.pardir(label_json_file), exist_ok=True)
            os.makedirs(os.path.pardir(list_json_file), exist_ok=True)
            z_dataprocess.writeJson(label_json_file, descri_data)
            z_dataprocess.writeJson(list_json_file, foodList_data)
        self.on_btn_down()
                   
    def on_btn_delete(self):
        json_name = list(self.name_dict.keys())[self.item_index] + '.json'
        label_json_file = os.path.join(self.mllm_descri, json_name)
        list_json_file = os.path.join(self.mllm_foodList, json_name)

        print(f"删除文件：{json_name}")
        if self.isLinux:
            self.client.get_delete(label_json_file)
            self.client.get_delete(list_json_file)
        else:
            os.remove(label_json_file)
            os.remove(list_json_file)
        self.on_btn_down()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = Window()
    main_window.show()
    main_window.original_stdout = sys.stdout
    sys.stdout = main_window
    sys.exit(app.exec_())