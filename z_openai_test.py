import base64
from openai import OpenAI
import random, configparser

class MLLMClient:
    def __init__(self, config_path):
        try:
            config = configparser.ConfigParser()
            config.read(config_path)
            self.api_url = config['MLLMAPI']['api_url']
            self.api_key = config['MLLMAPI']['api_key']
            self.model_name = config['MLLMAPI']['model_name']
            self.quote = "请简短回答问题，图中存在柠檬么？"
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_url,
            )
        except Exception as e:
            print(e)

    def detect(self, image_path, quote):
        image_data = self.get_image_64code(image_path)
        response = self.get_result(image_data, quote)
        result = response.choices[0].message.content
        return result
        
    def get_image_64code(self, image_path):
        f = open(image_path, "rb")
        encoded_image = base64.b64encode(f.read())
        encoded_image_text = encoded_image.decode("utf-8")
        base64_qwen = f"data:image;base64,{encoded_image_text}" 
        f.close()
        return base64_qwen
    
    def get_result(self, image_data, quote):
        chat_response = self.client.chat.completions.create(
            model = self.model_name,
            messages=[
                {"role": "助手", "content": "You are a professional Chinese cuisine gourmet."},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_data
                            },
                        },
                        {"type": "text", "text": quote},
                    ],
                },
            ],
            # seed = random.randint(0, 1)  # 修改qwen2-vl的随机值
            seed = 1
        )
        return chat_response

if __name__ == "__main__":
    # 初始化 API 客户端
    client = MLLMClient('config/mllm_config.ini')
    print(client)
    
    # 图片路径和问题设置
    image_path = r"D:\00-dataset\60_classss\0\wushicai_0731_0012.jpg"
    quote = "图中存在哪些食材，没有食材就返回“无”，请简短回答无需输出无关字符？"
    result = client.detect(image_path, quote)
    print(result)