import os, jieba, json, random, re
import string

prompt_list = [
    "图中存在哪些食材，没有食材就返回“无”，请简短回答无需输出无关字符。",
    "图片中有哪些食材？若没有食材请返回“无”。",
    "请列出图中所有食材，若无则回复“无”。",
    "图中包含哪些食材？若无，请简单回复“无”。",
    "请识别图片里的食材，没有食材则回复“无”。",
    "图中食材有哪些？如没有，请返回“无”。",
    "请分析图中是否有食材，如无则返回“无”。",
    "请确认图片中有哪些食材，如无食材请返回“无”。",
    "识别图中的食材，没有食材则简单返回“无”。",
    "请列出图中的所有食材，若无则返回“无”即可。",
    "图中有哪些食材成分？无则回复“无”。",
    "请识别图中的食材内容，无食材则返回“无”。",
    "请问图中有什么食材？如无食材请返回“无”。",
    "图片中含有哪些食材？没有食材则返回“无”。",
    "请检查图片是否有食材，如无则回复“无”。",
    "识别图中存在哪些食材，若无食材则简单返回“无”。",
    "请分析图中的食材种类，没有则返回“无”。",
    "列出图片中所有的食材，若无食材则返回“无”。",
    "请问图中存在哪些食材成分？如无，请返回“无”。",
    "请识别图中的所有食材，如无请返回“无”。",
    "图中有哪些食材？如无食材请回复“无”。",
    "请列出图中的食材内容，若无食材则返回“无”。",
    "请确认图中的食材种类，若无则回复“无”。",
    "请识别图片里包含的食材，如无食材则返回“无”。",
    "图中有食材吗？如无请回复“无”。",
    "请检查图中是否含有食材，如无请返回“无”。",
    "请列出图片中所有的食材，如果没有食材，请返回“无”，无需输出其他内容。",
    "请识别图片中的食材种类，若没有食材存在，请直接返回“无”即可。",
    "请查看图中有哪些食材，如无食材请简短回复“无”，无需其他描述。",
    "图片中有哪些食材？如果没有食材，请简单返回“无”，不必输出多余信息。",
    "请检查图片中是否有食材存在，若无食材请直接回复“无”即可。",
    "请确认图中是否有食材，如果没有，请返回“无”，无需其他字符。",
    "图中包含哪些食材？若无食材，请回复“无”，请保持回答简洁。",
    "请识别图中的食材成分，若无食材请返回“无”，无需输出其他信息。",
    "请列出图中存在哪些食材，若没有任何食材，请返回“无”。",
    "请分析图中是否含有食材，如没有任何食材存在，请直接返回“无”。",
    "请告诉我图中有哪些食材，若没有食材存在，请直接回复“无”即可。",
    "图片中是否有食材？若没有任何食材存在，请回复“无”。",
    "请确认图片中是否有食材，如无，请直接返回“无”，无需额外信息。",
    "请查看图片中的食材，如果没有食材，请返回“无”，不需要多余字符。",
    "请分析图中的食材内容，如果没有任何食材，请直接返回“无”即可。",
    "请列出图中所有的食材，如没有任何食材，请简短回复“无”。",
    "请识别图中的食材成分，如无食材存在，请简单返回“无”即可。",
    "请确认图中是否含有任何食材，如果没有，请返回“无”。",
    "图片中有哪些食材？如无任何食材，请回复“无”，不需其他字符。",
    "请列出图片里所有的食材，若无食材存在，请返回“无”，无需其他信息。",
    "请检查图片中的食材，如没有食材，请直接返回“无”，不必多余描述。",
    "请确认图片是否包含食材，若无食材存在，请简短返回“无”。",
    "请查看图片中的所有食材，若没有食材存在，请简短返回“无”即可。",
    "请列出图中所有食材，若没有任何食材，请直接回复“无”即可。",
    "图中是否有食材存在？如无食材，请回复“无”，无需额外信息。",
    "请告诉我图片中的食材，若无食材存在，请直接返回“无”即可。",
    "请分析图中是否有食材，若无食材存在，请简短回复“无”即可。",
    "请查看图中包含哪些食材，若没有食材，请直接返回“无”即可。",
    "图中有哪些食材？如果没有食材存在，请简短回复“无”，不必输出其他信息。",
    "请列出图中所有食材，若没有食材存在，请简短返回“无”即可。",
    "请确认图片中存在哪些食材，若无食材存在，请直接返回“无”即可。",
    "请检查图片中的食材种类，若没有食材，请返回“无”，无需其他描述。",
    "请分析图中含有哪些食材，如无任何食材存在，请直接回复“无”即可。",
    "请识别图中的所有食材，若没有食材，请简短返回“无”即可。",
    "图中存在哪些食材？如果没有食材存在，请简短返回“无”，无需其他描述。",
    "请查看图片中是否有食材，如无任何食材，请直接返回“无”即可。",
    "请列出图中的食材内容，若无食材，请简短返回“无”，不需其他描述。",
    "请确认图中含有哪些食材，若无任何食材存在，请直接返回“无”即可。",
    "图中有哪些食材？若没有任何食材，请回复“无”，无需其他字符。",
]

des_list = [
    "描述一下图像",
    '请详细描绘这幅图片的内容',
    '请对这张图片进行视觉分析',
    '请尝试用文字描绘这张图片',
    '请描述这张图片'
]

food_list = [
    "图中存在哪些食材，没有食材就返回“无”，请简短回答无需输出无关字符。"
]


def splite(res_text):
    words = [word for word in jieba.cut(res_text) if word.strip() and word not in string.punctuation and word not in '，。、！？：；“”‘’（）《》【】' and not word.isdigit()]
    return words


def generate_sharegpt_data(data_content, image_path, label_func):    
    if data_content == "":
        return None    
    
    if label_func == 0:
        random_number = random.randint(0, len(prompt_list)-1)
        res_string = prompt_list[random_number]
    elif label_func == 1:
        random_number = random.randint(0, len(des_list)-1)
        res_string = des_list[random_number]
    elif label_func == 2:
        random_number = random.randint(0, len(food_list)-1)
        res_string = food_list[random_number]
    
    data = [{
        "消息": [
            {"role": "user" , "content": f"<image>{res_string}"},
            {"role": "助手" , "content": data_content},
        ],
        "图片":[
            image_path
        ]
    }]
    return data


def is_linux_folder_path(path):
    """
    判断路径是Linux文件夹地址还是本地Windows文件夹地址
    :param path: 文件夹路径
    :return: True 如果是Linux路径，False 如果是Windows路径
    """
    return not ':' in path

def parse_mllm_result(mllm_output, func_index):
    if func_index == 0:
        filter_parse =  ["图", "存在", "以下", "下"]
        data_list = splite(mllm_output)
        data_list = [item for item in data_list if not any(keyword in item for keyword in filter_parse)]
        res_string = '，'.join(data_list)
    elif func_index == 1:
        res_string = mllm_output
    elif func_index == 2:
        res_string = mllm_output
    
    return res_string

        
def parse_json_data(json_data, func_index):
    if json_data is None:
        return ''
    
    if func_index == 0:
        filter_parse =  ["图", "存在", "以下", "下"]
        data = json_data[0]['消息'][1]['content']
        data_list = splite(data)
        data_list = [item for item in data_list if not any(keyword in item for keyword in filter_parse)]
        res_string = '，'.join(data_list)
    elif func_index == 1:
        res_string = json_data[0]['消息'][1]['content']
    elif func_index == 2:
        res_string = json_data[0]['消息'][1]['content']
    
    return res_string


def writeJson(save_path, data):
    try:
        with open(save_path, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"数据已成功保存到 {save_path}")
    except Exception as e:
        print(f"保存数据到 {save_path} 失败，错误信息: {e}")


def get_image_dict(file_folder):
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
    image_dict = {}
    nameList = os.listdir(file_folder)
    
    for path in nameList:
        if not any(path.lower().endswith(ext) for ext in image_extensions):
            continue
        image_dict[path.split('.')[0]] = os.path.join(file_folder, path)
    return image_dict


def read_json(file_path):
    """
    远程读取保存的json文件。
    :param file_path: 要读取的json文件路径。
    :return: 读取的json数据。
    """
    try:
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'r') as f:
            json_data = json.load(f)
        return json_data
    except Exception as e:
        print(f"读取JSON文件{file_path}失败，{e}")
        return None

if __name__ == "__main__":
    conversation = [
        "The capital of France is Paris.",
        "D:/haha.jpg"
    ]
    
    # generate_sharegpt_data(conversation)    
    
    a = "jjfjff.qq"
    
    print(a.endswith('q'))