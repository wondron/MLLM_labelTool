import paramiko, os, sys, json
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap
import configparser


class SSHClient:
    def __init__(self, config_path):

        config = configparser.ConfigParser()
        config.read(config_path)
        self.ipNum = config['Credentials']['ip_num']
        self.userName = config['Credentials']['username']
        self.password = config['Credentials']['password']
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        self.ssh_client_dtct = paramiko.SSHClient()
        self.ssh_client_dtct.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.is_connected = False

    def get_image_names(self, folderPath):
        if not self.is_connected:
            raise ConnectionError("未连接远程服务器，返回NG")
        if folderPath[-1] != '/':
            folderPath = folderPath + '/'
        try:
            nameList = self.sftp.listdir(folderPath)
        except Exception as e:
            raise ConnectionError(f"sftp获取信息失败，{e}")
        
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
        
        image_dict = {}
        for path in nameList:
            if not any(path.lower().endswith(ext) for ext in image_extensions):
                continue
            image_dict[path.split('.')[0]] = os.path.join(folderPath, path)

        return image_dict
        
    def connect_linux(self):
        self.ssh_client.close()
        self.is_connected = False
        try:
            self.ssh_client.connect(self.ipNum, username=self.userName, password=self.password)
            self.ssh_client_dtct.connect(self.ipNum, username=self.userName, password=self.password)
            self.sftp = self.ssh_client.open_sftp()
            self.sftp_total_dtct = self.ssh_client.open_sftp()
            self.is_connected = True
            print("ssh远程链接成功！")
        except Exception as e:
            raise ConnectionError(f"远程连接失败，{e}")
    
    def get_image(self, image_path, temp_name = "temp_name"):
        if not self.is_connected:
            raise ConnectionError("未连接远程服务器，无法获取图像信息！")
        try:
            self.sftp.get(image_path, temp_name)
            pixmap = QPixmap(temp_name)
            return pixmap
        except Exception as e:
            raise ConnectionError(f"图像获取失败，{os.path.basename(image_path)}:{e}")
    
    def writeJson(self, file_path, data):
        if data is None:
            return
        
        if not self.is_connected:
            raise ConnectionError("未连接远程服务器，无法写入JSON文件！")
        try:
            json_str = json.dumps(data, ensure_ascii=False, indent=4)
            with self.sftp.open(file_path, 'w') as f:
                f.write(json_str)
        except Exception as e:
            raise ConnectionError(f"写入JSON文件失败，{e}")
        
        
    def get_delete(self, json_path):
        """
        删除远程文件，如果jsonpath不存在则返回。
        :param json_path: 要删除的远程文件路径。
        """
       
        if not self.is_connected:
            raise ConnectionError("未连接远程服务器，无法删除文件！")
        try:
            if not self.check_file_exists(json_path):
                print(f"文件 {json_path} 不存在，无需删除。")
                return
            self.sftp.remove(json_path)
            print(f"文件 {json_path} 已成功删除。")
        except Exception as e:
            raise ConnectionError(f"删除文件失败，{e}")
        
        
    def copyfile_to_remote(self, local_file_path, 
                           remote_file_path = '/data/wangzhuo/01-code/99-qita/01-QWen/z_dataprocess.py'):
        """
        将本地文件复制到远程服务器中。
        :param local_file_path: 本地文件路径。
        :param remote_file_path: 远程服务器上的目标路径。
        """
        if not self.is_connected:
            raise ConnectionError("未连接远程服务器，无法复制文件！")
        try:
            with open(local_file_path, 'rb') as local_file:
                self.sftp.putfo(local_file, remote_file_path)
            print(f"文件 {local_file_path} 已成功复制到 {remote_file_path}")
        except Exception as e:
            raise ConnectionError(f"复制文件失败，{e}")
        
    def check_file_exists(self, file_path):
        """
        检测远程服务器上是否存在指定文件。
        :param file_path: 要检测的文件路径。
        :return: 如果文件存在返回True，否则返回False。
        """
        if not self.is_connected:
            raise ConnectionError("未连接远程服务器，无法检测文件是否存在！")
        try:
            self.sftp.stat(file_path)
            # print(f"文件 {file_path} 存在")
            return True
        except FileNotFoundError:
            # print(f"文件 {file_path} 不存在")
            return False
        except Exception as e:
            raise ConnectionError(f"检测文件是否存在失败，{e}")

    def read_json(self, file_path):
        """
        远程读取保存的json文件。
        :param file_path: 要读取的json文件路径。
        :return: 读取的json数据。
        """
        if not self.is_connected:
            print("未连接远程服务器，无法读取JSON文件！")
            return None
            
        if not self.check_file_exists(file_path):
            return None
        
        json_data = None
        with self.sftp.open(file_path, 'r') as f:
            json_data = json.load(f)
        return json_data
        
        
    def create_remote_folder(self, folder_path):
        """
        远程创建服务器的文件夹。
        :param folder_path: 要创建的文件夹路径。
        """
        if not self.is_connected:
            raise ConnectionError("未连接远程服务器，无法创建文件夹！")
        try:
            try:
                self.sftp.stat(folder_path)
                print(f"文件夹 {folder_path} 已存在，无需创建")
            except FileNotFoundError:
                self.sftp.mkdir(folder_path)
                print(f"文件夹 {folder_path} 已成功创建")
        except Exception as e:
            raise ConnectionError(f"创建文件夹失败，{e}")
 
    def start_python_file(self, image_path, quote, save_path, methodNum):
        """
        远程启动服务器的python文件。
        :param image_path: 要处理的图像路径。
        :param quote: 检测时的提示信息。
        :param save_path: 保存结果的路径。
        """
        if not self.is_connected:
            raise ConnectionError("未连接远程服务器，无法启动Python文件！")
        try:
            print("-------start python file------")
            command = (
                f"source /root/miniconda3/etc/profile.d/conda.sh && "
                f"conda activate foodCog && "
                f"python /data/wangzhuo/01-code/99-qita/01-QWen/z_detect.py "
                f"--image_path {image_path} --quote '{quote}' --save_path {save_path} --process_index {methodNum}"
            )
            stdin, stdout, stderr = self.ssh_client_dtct.exec_command(command)
            print("-------Done eeeeeeeeeeee------")
            print(stdin)
            print(stdout)
            print(stderr)
        except Exception as e:
            raise ConnectionError(f"启动Python文件失败，{e}")

    def close(self):
        # 关闭连接
        if self.is_connected:
            self.ssh_client.close()
            self.sftp.close()
            self.is_connected = False

    def read_progress_index(self, progress_file_path):
        """
        远程读取服务器上的progress.ini中的current_index值。
        :param progress_file_path: progress.ini文件的路径。
        :return: current_index值。
        """
        try:
            self.sftp_total_dtct.stat(progress_file_path)
        except FileNotFoundError:
            # print(f"文件 {progress_file_path} 不存在")
            return None
        
        if not self.is_connected:
            raise ConnectionError("未连接远程服务器，无法读取progress.ini文件！")
        try:
            with self.sftp_total_dtct.open(progress_file_path, 'r') as f:
                content = f.read().decode()
                current_index = int(content.split("=")[1])
                return current_index
        except Exception as e:
            print(f"读取progress.ini文件失败，{progress_file_path}{e}")
            return None
            # raise ConnectionError(f"读取progress.ini文件失败，{progress_file_path}{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = SSHClient('config/ssh_config.ini')
    try:
        client.connect_linux()
        image_dict = client.get_image_names("/data/wangzhuo/00-dataset/55-test/菠萝/")
        client.get_image(image_dict[list(image_dict.keys())[0]], "temp_image")
        json_data = client.read_json('/data/wangzhuo/00-dataset/55-test/菠萝lbld/boluo_0910_0002.json')
        
        dd = json_data[0]['消息'][1]['content']
        print(json_data)
        
        client.copyfile_to_remote(r"D:\01-code\00-python\03-showfile\z_dataprocess.py")
        
        image_path = '/data/wangzhuo/01-code/99-qita/01-QWen/image'
        save_path = '/data/wangzhuo/01-code/99-qita/01-QWen/imagelbld'
        quote = '图中存在哪些食材？没有食材就返回“无”，请简短回答无需输出无关字符。'
        # client.start_python_file(image_path, quote, save_path)
        
        client.read_progress_index('/data/wangzhuo/01-code/99-qita/01-QWen/imagelbld/progress.ini')
        
    except Exception as e:
        print(e)