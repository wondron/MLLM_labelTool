import base64
from openai import OpenAI
import random, configparser

class OpenAITest:
    def __init__(self, config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        self.api_url = config['MLLMAPI']['api_url']
        self.api_key = config['MLLMAPI']['api_key']
        self.model_name = config['MLLMAPI']['model_name']
        self.quote = "请简短回答问题，图中存在柠檬么？"
        self.client = OpenAI(
            api_key = self.api_key,
            base_url = self.api_url,
        )
        
    def detect(self, image_path):
        image_data = self.get_image_64code(image_path)
        response = self.get_result(image_data)
        result = response.choices[0].message.content
        return result

    def get_image_64code(self, image_path):
        f = open(image_path, "rb")
        encoded_image = base64.b64encode(f.read())
        encoded_image_text = encoded_image.decode("utf-8")
        base64_qwen = f"data:image;base64,{encoded_image_text}" 
        f.close()
        return base64_qwen

    def get_result(self, image_data):
        chat_response = self.client.chat.completions.create(
            model = self.model_name,
            messages=[
                {"role": "system", "content": "You are a professional Chinese cuisine gourmet."},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_data
                            },
                        },
                        {"type": "text", "text": self.quote},
                    ],
                },
            ],
            seed = 1
        )
        return chat_response

if __name__ == "__main__":
    test = OpenAITest('config/mllm_config.ini')
    image_path = r"D:\00-dataset\60_classss\0\wushicai_0731_0012.jpg"
    res = test.detect(image_path)
    print(res)