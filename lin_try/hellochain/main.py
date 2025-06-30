import os
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek

load_dotenv()

def main():
    print("Hello from hellochain!")
    key = os.getenv("SILICONFLOW_API_KEY")
    base = os.getenv("SILICONFLOW_API_BASE")
    print(f"KEY: {key}")
    model = ChatDeepSeek(
        model='deepseek-ai/DeepSeek-R1-0528-Qwen3-8B',
        temperature=0,
        api_key=key,
        api_base=base
    )
    res = model.invoke("introduce yourself in Chinese briefly")
    print(res)

if __name__ == "__main__":
    main()
