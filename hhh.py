from nacos import NacosClient
import yaml


def get_nacos_params(user_name, password):
    client = NacosClient(
        server_addresses = "http://nacos.myroki.com:8848",
        namespace = "adfc3ec2-a1ea-4b31-9b1a-fafb4228c8ca",
        username = user_name,
        password = password
    )
    config = client.get_config(group = "ROKI_AI_GROUP",
        data_id = "roki-ai-food-identifier")

    parameter = yaml.safe_load(config)
    return parameter



if __name__ == "__main__":
    username = "roki-ai-test"
    password = "Q65ILEBfsAmqnPbJqcSig"
    param = get_nacos_params(username, password)
    print(param)