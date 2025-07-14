import requests, json

def send_get(url: str, params: dict = None) -> None:
    """
    发送 GET 请求并打印结果
    
    Args:
        url: 请求的完整 URL (例如: "http://localhost:8080/student")
        params: 请求参数 (字典形式)
    """
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # 检查请求是否成功
        print(f"GET 请求到 {url} 成功:")
        
        dict=response.json()
        print(dict.get('code'))
        print(dict.get('message'))
        print(dict.get('result'))
        print(dict.get('reason'))
    except requests.exceptions.RequestException as e:
        print(f"GET 请求失败: {e}")
        dict=response.json()
        print(dict)

def send_post(url: str, data: dict = None, json: dict = None) -> None:
    """
    发送 POST 请求并打印结果
    
    Args:
        url: 请求的完整 URL
        data: 表单数据 (字典形式)
        json: JSON 数据 (字典形式)
    """
    try:
        response = requests.post(url, data=data, json=json)
        response.raise_for_status()  # 检查请求是否成功
        
        print(f"POST 请求到 {url} 成功:")
        dict=response.json()
        print(dict.get('code'))
        print(dict.get('message'))
        print(dict.get('result'))
        print(dict.get('reason'))
    except requests.exceptions.RequestException as e:
        print(f"POST 请求失败: {e}")
        dict=response.json()
        print(dict)

# 示例调用
if __name__ == "__main__":
    # 发送 GET 请求示例
    send_get("http://localhost:8080/keywords/xDJTomato_0001/我想要买点饮料，可以给我推荐什么牌子吗")
    # send_get("http://localhost:8080/test")
