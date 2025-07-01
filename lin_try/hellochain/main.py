import os
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langchain_core.messages import SystemMessage, AIMessage
from langchain_core.prompts import StringPromptTemplate
import inspect
from langchain import hub
from langsmith import Client
from pydantic import BaseModel,Field,model_validator
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.output_parsers import XMLOutputParser
from langchain.output_parsers import RetryOutputParser
from langchain_core.exceptions import OutputParserException
import json

load_dotenv()

def main():
    # print("Hello from hellochain!")
    key = os.getenv("SILICONFLOW_API_KEY")
    base = os.getenv("SILICONFLOW_API_BASE")
    langsmith_key = os.getenv("LANGSMITH_API_KEY") #模版网站的api_key
    # print(f"KEY: {key}")
    model = ChatDeepSeek(
        model='deepseek-ai/DeepSeek-R1-0528-Qwen3-8B',
        temperature=0,
        api_key=key,
        api_base=base,
    )
    # res = model.invoke("introduce yourself in Chinese briefly")
    # print(res)

    #code1  字符串模版
    # prompt = PromptTemplate.from_template("你是⼀个{name}，帮我起⼀个具有{country}特⾊的{sex}名字")
    # prompts = prompt.format(name="算命⼤师", country="中国", sex="⼥孩")
    # print(prompts)

    #code2 对话模版
    # chat_template = ChatPromptTemplate.from_messages(
    #     [
    #         {"role": "system", "content": "你是⼀个起名⼤师，你的名字叫{name}"},
    #         {"role": "human", "content": "你好{name}，你感觉如何？ "},
    #         {"role": "ai", "content": "你好！我状态⾮常好！ "},
    #         {"role": "human", "content": "你叫什么名字呢？ "},
    #         {"role": "ai", "content": "你好！我叫{name}"},
    #         {"role": "human", "content": "{user_input}"},
    #     ]
    # )
    # chats = chat_template.format_messages(name="吕半仙⼉", user_input="你的爷爷是谁呢？ ")
    # print(chats)

    #code3  占位符模版
    # prompt_template = ChatPromptTemplate(
    #     [
    #         {"role": "system", "content": "你是⼀个超级⼈⼯智能助⼿"},
    #         #MessagesPlaceholder("msgs")
    #         {"role":"placeholder","content" :"{msgs}"}
    #     ]
    # )
    # result = prompt_template.invoke({"msgs":[HumanMessage("请帮我写⼀个关于机器学习的⽂章")]})
    # print(result)

    #code4 使用Message组合模版
    # sys = SystemMessage(
    #     content="你是⼀个起名⼤师",
    #     additional_kwargs = {"⼤师姓名": "吕半仙⼉"}
    # )
    # human = HumanMessage(
    #     content="请问⼤师叫什么名字？ "
    # )
    # ai = AIMessage(
    #     content="我叫吕半仙⼉"
    # )
    # mesg = [sys,human,ai]
    # print(mesg)

    #code5
    # def hello_world(abc):
    #     print("Hello World!")
    #     return abc
    
    # PROMPT = """\
    # 你是⼀个⾮常有经验和天赋的程序员，现在给你如下函数名称，你会按照如下格式，输出这段代码的名称、源代码、中⽂解释。
    # 函数名称： {function_name}
    # 函数源代码:\n{source_code}
    # 代码解释：
    # """
    # def get_source_code(function_name):
    #     #获得源代码
    #     return inspect.getsource(function_name)
    # #⾃定义模板class
    # class CustomPromptTemplate(StringPromptTemplate):
    #     def format(self, **kwargs) -> str:
    #         # 获取源代码
    #         source_code = get_source_code(kwargs["function_name"])
    #         #⽣成提示词模板
    #         prompt = PROMPT.format(
    #             function_name=kwargs["function_name"].__name__,
    #             source_code=source_code,
    #         )
    #         return prompt
    # #使⽤⾃定义的提示词模板，⽽并⾮类似度化提示词模板
    # a = CustomPromptTemplate(input_variables=["function_name"])
    # pm = a.format(function_name= hello_world)
    # print("格式化之后的提示词为=======>")
    # print(pm)

    #code6 push、pull自定义模版模版
    # client=Client(api_key=langsmith_key)
    # # 使⽤ from_messages 构造多轮对话结构
    # prompt = ChatPromptTemplate.from_messages(
    #     [
    #         ("system", "You are a super intelligent assistant"),
    #         ("human", "{question}"),
    #     ]
    # )
    # project_name = "test1_langsmith"
    # # 推送提示词到 LangSmith，并指定所属项⽬
    # try: #如果未更新模版就push会报错
    #     client.push_prompt(project_name, object=prompt)
    # except Exception as e:
    #     print(e)
    # # pro = client.pull_prompt(project_name)
    # # print(pro.invoke({"question":"What is the capital of France?"}))
    # # res = model.invoke(pro.invoke({"question":"What is the capital of France?"}))
    # # print(res)

    #code7 调用公共的hub模版
    # client=Client(api_key=langsmith_key)
    # pro=client.pull_prompt("rlm/rag-prompt")
    # # print(pro)
    # res = model.invoke(pro.invoke({
    #     "context": "China is a great country. It is a country of peace and love.",
    #     "question":"Who is the current leader of China?"}))
    # print(res)


    #code8
    # class Joke(BaseModel):
    #     setup: str = Field(..., description="笑话中的铺垫问题，必须以？结尾")
    #     punchline: str = Field(..., description="笑话中回答铺垫问题的部分，通常是⼀种抖包袱⽅式回答铺垫问题，例如谐⾳、会错意等")
    #     # # 可以根据⾃⼰的数据情况进⾏⾃定义验证器
    #     @model_validator(mode="before")
    #     @classmethod
    #     def check_setup_and_punchline(cls, values:dict) -> dict:
    #         setup = values.get("setup")
    #         punchline = values.get("punchline")
    #         if setup and punchline and (setup.endswith("? ") or setup.endswith("？")):
    #             return values
    #         else:
    #             raise ValueError("setup and punchline must be provided and setup must end with'?'")
    # parser = PydanticOutputParser(pydantic_object=Joke)

    # # parser = XMLOutputParser()
    # # parser = XMLOutputParser(tags = ["setup", "punchline"])

    # # 注意，提示词模板中需要部分格式化解析器的格式要求format_instructions
    # prompt = PromptTemplate(
    #     template="回答⽤户的查询.\n{format_instructions}\n{query}",
    #     input_variables=["query"],
    #     partial_variables={"format_instructions": parser.get_format_instructions()}
    # )
    # # print("pydanticoutparser的格式要求为=======>")
    # # print(parser.get_format_instructions())
    # chain = prompt | model 
    # prompt_value=prompt.format_prompt(query="请写一个笑话")
    # output = chain.invoke(prompt_value)
    # print(type(output))
    # res = output.content
    # res = {
    #     "setup": "hello",
    #     "punchline": "world",
    # }

    # res=json.dumps(res)
    # print(type(res))

    # try:
    #     parser.parse(res)
    #     print(res)
    # except Exception as e:
    #     # print(e)
    #     retry = RetryOutputParser.from_llm(parser=parser, llm=model)
    #     retry_res = retry.parse_with_prompt(res, prompt_value)
    #     print(retry_res)
    

if __name__ == "__main__":
    main()
