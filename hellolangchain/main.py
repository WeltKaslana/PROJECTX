import os
from langchain_deepseek import ChatDeepSeek
from dotenv import load_dotenv

load_dotenv()

def main():
    llm = ChatDeepSeek(
        model="deepseek-ai/DeepSeek-R1-0528-Qwen3-8B",
        temperature=0,
        api_key=os.environ.get("SILICONFLOW_API_KEY"),
        api_base=os.environ.get("SILICONFLOW_API_BASE"),
    )
    resp = llm.invoke("介绍你自己")
    print(resp.usage_metadata)

if __name__ == "__main__":
    main()
