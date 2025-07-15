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
        # dict=response.json()
        # print(dict)

# 示例调用
if __name__ == "__main__":
    # 发送 GET 请求示例
    send_get("http://localhost:8080/register/test/abc123456")
    print('-'*50)
    send_get("http://localhost:8080/login/test/abc123456")
    print('-'*50)
    send_get("http://localhost:8080/historycount/test")
    print('-'*50)
    send_get("http://localhost:8080/new")
    print('-'*50)
    send_get("http://localhost:8080/keywords/xDJTomato_0001/我想要买点手上戴的饰品")
    print('-'*50)
    send_get("http://localhost:8080/result/xDJTomato_0001/我想要买点手上戴的饰品/手镯_手环")
