import os, inspect, json
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.prompts import StringPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
from langchain import hub
from langsmith import Client
from pydantic import BaseModel,Field,model_validator
from langchain_core.output_parsers import PydanticOutputParser, XMLOutputParser
from langchain_core.output_parsers import StrOutputParser
from langchain.output_parsers import RetryOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_core.runnables import RunnableParallel, chain, ConfigurableField
from langchain_core.runnables import RunnableLambda, RunnablePassthrough, ConfigurableFieldSpec
from langchain.runnables.hub import HubRunnable
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_redis import RedisChatMessageHistory
from operator import itemgetter
from typing import Iterator, List
from pydantic import BaseModel, Field

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
    ).configurable_fields(
        temperature=ConfigurableField(
            id="model_temperature",
            name="模型温度",
            description="The temperature to use for the model."
        ),
    )
    # res = model.invoke("introduce yourself in Chinese briefly")
    # print(res)

    #code1  字符串模版
    def code1():
        prompt = PromptTemplate.from_template("你是⼀个{name}，帮我起⼀个具有{country}特⾊的{sex}名字")
        prompts = prompt.format(name="算命⼤师", country="中国", sex="⼥孩")
        print(prompts)

    #code2 对话模版
    def code2():
        chat_template = ChatPromptTemplate.from_messages(
            [
                {"role": "system", "content": "你是⼀个起名⼤师，你的名字叫{name}"},
                {"role": "human", "content": "你好{name}，你感觉如何？ "},
                {"role": "ai", "content": "你好！我状态⾮常好！ "},
                {"role": "human", "content": "你叫什么名字呢？ "},
                {"role": "ai", "content": "你好！我叫{name}"},
                {"role": "human", "content": "{user_input}"},
            ]
        )
        chats = chat_template.format_messages(name="吕半仙⼉", user_input="你的爷爷是谁呢？ ")
        print(chats)

    #code3  占位符模版
    def code3():
        prompt_template = ChatPromptTemplate(
            [
                {"role": "system", "content": "你是⼀个超级⼈⼯智能助⼿"},
                #MessagesPlaceholder("msgs")
                {"role":"placeholder","content" :"{msgs}"}
            ]
        )
        result = prompt_template.invoke({"msgs":[HumanMessage("请帮我写⼀个关于机器学习的⽂章")]})
        print(result)

    #code4 使用Message组合模版
    def code4():
        sys = SystemMessage(
            content="你是⼀个起名⼤师",
            additional_kwargs = {"⼤师姓名": "吕半仙⼉"}
        )
        human = HumanMessage(
            content="请问⼤师叫什么名字？ "
        )
        ai = AIMessage(
            content="我叫吕半仙⼉"
        )
        mesg = [sys,human,ai]
        print(mesg)

    #code5 自定义模版
    def code5():
        def hello_world(abc):
            print("Hello World!")
            return abc
        
        PROMPT = """\
        你是⼀个⾮常有经验和天赋的程序员，现在给你如下函数名称，你会按照如下格式，输出这段代码的名称、源代码、中⽂解释。
        函数名称： {function_name}
        函数源代码:\n{source_code}
        代码解释：
        """
        def get_source_code(function_name):
            #获得源代码
            return inspect.getsource(function_name)
        #⾃定义模板class
        class CustomPromptTemplate(StringPromptTemplate):
            def format(self, **kwargs) -> str:
                # 获取源代码
                source_code = get_source_code(kwargs["function_name"])
                #⽣成提示词模板
                prompt = PROMPT.format(
                    function_name=kwargs["function_name"].__name__,
                    source_code=source_code,
                )
                return prompt
        #使⽤⾃定义的提示词模板，⽽并⾮类似度化提示词模板
        a = CustomPromptTemplate(input_variables=["function_name"])
        pm = a.format(function_name= hello_world)
        print("格式化之后的提示词为=======>")
        print(pm)

    #code6 push、pull自定义模版模版
    def code6():
        client=Client(api_key=langsmith_key)
        # 使⽤ from_messages 构造多轮对话结构
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a super intelligent assistant"),
                ("human", "{question}"),
            ]
        )
        project_name = "test1_langsmith"
        # 推送提示词到 LangSmith，并指定所属项⽬
        try: #如果未更新模版就push会报错
            client.push_prompt(project_name, object=prompt)
        except Exception as e:
            print(e)
        # pro = client.pull_prompt(project_name)
        # print(pro.invoke({"question":"What is the capital of France?"}))
        # res = model.invoke(pro.invoke({"question":"What is the capital of France?"}))
        # print(res)

    #code7 调用公共的hub模版
    def code7():
        client=Client(api_key=langsmith_key)
        pro=client.pull_prompt("rlm/rag-prompt")
        # print(pro)
        res = model.invoke(pro.invoke({
            "context": "China is a great country. It is a country of peace and love.",
            "question":"Who is the current leader of China?"}))
        print(res)
    
    #code8 模型输出解析、重试
    def code8():
        class Joke(BaseModel):
            setup: str = Field(..., description="笑话中的铺垫问题，必须以？结尾")
            punchline: str = Field(..., description="笑话中回答铺垫问题的部分，通常是⼀种抖包袱⽅式回答铺垫问题，例如谐⾳、会错意等")
            # # 可以根据⾃⼰的数据情况进⾏⾃定义验证器
            @model_validator(mode="before")
            @classmethod
            def check_setup_and_punchline(cls, values:dict) -> dict:
                setup = values.get("setup")
                punchline = values.get("punchline")
                if setup and punchline and (setup.endswith("? ") or setup.endswith("？")):
                    return values
                else:
                    raise ValueError("setup and punchline must be provided and setup must end with'?'")
        parser = PydanticOutputParser(pydantic_object=Joke)

        # parser = XMLOutputParser()
        # parser = XMLOutputParser(tags = ["setup", "punchline"])

        # 注意，提示词模板中需要部分格式化解析器的格式要求format_instructions
        prompt = PromptTemplate(
            template="回答⽤户的查询.\n{format_instructions}\n{query}",
            input_variables=["query"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        # print("pydanticoutparser的格式要求为=======>")
        # print(parser.get_format_instructions())
        chain = prompt | model 
        prompt_value=prompt.format_prompt(query="请写一个笑话")
        output = chain.invoke(prompt_value)
        print(type(output))
        res = output.content
        res = {
            "setup": "hello",
            "punchline": "world",
        }

        res=json.dumps(res)
        print(type(res))

        try:
            parser.parse(res)
            print(res)
        except Exception as e:
            # print(e)
            retry = RetryOutputParser.from_llm(parser=parser, llm=model)
            retry_res = retry.parse_with_prompt(res, prompt_value)
            print(retry_res)
    
    # code9 并行chain运行大模型
    def code9():
        joke_prompt =ChatPromptTemplate.from_template("tell me a joke about {topic1}")
        story_prompt = ChatPromptTemplate.from_template("tell me a short story about {topic2}")
        # joke_chain = joke_prompt | model | StrOutputParser()
        joke_chain = joke_prompt.pipe(model).pipe(StrOutputParser())
        story_chain = story_prompt | model | StrOutputParser()
        
        map_chain = RunnableParallel(joke = joke_chain, topic = story_chain)
        print(map_chain.invoke({"topic1": "football","topic2": "programming"}))

    #code10 利用@chain修饰符将函数转为chain
    def code10():
        prompt1 = ChatPromptTemplate.from_template("tell me a joke about {topic}")
        prompt2 = ChatPromptTemplate.from_template("tell me the subject of this joke: {joke}")

        @chain
        def defchain(text):
            joke_prompt = prompt1.invoke({"topic":text})
            joke = model.invoke(joke_prompt)
            output1 = StrOutputParser().parse(joke)
            print(output1)

            chain2 = prompt2 | model | StrOutputParser()
            print(chain2.invoke({"joke":output1}))
        defchain.invoke("football")
    
    #code 11 lamba函数\stream输出\chain中自定义函数
    def code11():
        def length_function(text):
            return len(text)
        def _multiple_length_function(text1,text2):
            return len(text1) * len(text2)
        def multiple_length_function(_dict):
            return _multiple_length_function(_dict["text1"],_dict["text2"])
        prompt = ChatPromptTemplate.from_template("What is the sum of {a} and {b}?")
        chain =(
            {"a": itemgetter("foo") | RunnableLambda(length_function),
            "b": {"text1": itemgetter("foo"), "text2": itemgetter("bar")}
            | RunnableLambda(multiple_length_function)
            }
            | prompt | model | StrOutputParser()
        )
        def func(input: Iterator) -> Iterator[List]:
            buffer = ""
            for chunk in input:
                buffer += chunk
                while "," in buffer:
                    comma_index = buffer.index(",")
                    yield [buffer[:comma_index].strip()]
                    buffer = buffer[comma_index + 1:]
            yield [buffer.strip()]

        chain = chain | func
        for i in chain.stream({"foo": "hello", "bar": "world"}):
            print(i, end="", flush=True)
    
    #code 12 runnablePassThrough
    def code12():
        runnable = RunnableParallel(
            passed = RunnablePassthrough(),
            moddified = lambda x: x["num"] + 2,
        )
        res = runnable.invoke({"num": 1})
        print(res)
    
    #code 13 动态加载模型配置、提示词
    def code13():
        prompt = HubRunnable("rlm/rag-prompt").configurable_fields(
            owner_repo_commit=ConfigurableField(
                id="hub_commit",
                name="Hub Commit",
                description="The Hub commit to pull from."
            ),
        )
        prompt = prompt.with_config(configurable = {"hub_commit":"rlm/rag-prompt"})
        prompt = prompt.invoke({"question":"foo","context":"bar"})
        res = model.invoke(prompt, config={"temperature":1})
        res = StrOutputParser().parse(res)
        print(res)
    
    #code 14 内存内记忆、短期记忆
    def code14():
        class InMemoryChatMessageHistory(BaseChatMessageHistory, BaseModel):
            messages: List[BaseMessage] = Field(default_factory=list)
            def add_messages(self, messages: List[BaseMessage]):
                self.messages.extend(messages)
            def clear(self):
                self.messages = []
        stored_history={}
        # 索引为用户
        def get_history(session_id: str) -> BaseChatMessageHistory:
            if session_id not in stored_history:
                stored_history[session_id] = InMemoryChatMessageHistory()
            return stored_history[session_id]
        #索引为用户+对话ID
        def get_session(user_id: str, conversation_id: str)->BaseChatMessageHistory:
            if (user_id, conversation_id) not in stored_history:
                stored_history[(user_id, conversation_id)] = InMemoryChatMessageHistory()
            return stored_history[(user_id, conversation_id)]
        history = get_history("1")
        history.add_messages([AIMessage(content="Hello! 我是Deepseek")])
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个擅长{ability}的助手"), # 系统角色提示,使用ability变量定义助手专长
            MessagesPlaceholder(variable_name="history"), # 放置历史消息的占位符
            ("human", "{question}"), # 用户问题的占位符
        ])
        chain = prompt | model | StrOutputParser()
        # 创建带历史消息的链，索引为用户id
        # chain_with_history = RunnableWithMessageHistory(
        #     chain,
        #     get_session_history=get_history,
        #     input_messages_key="question", # 指定输入消息的键名
        #     history_messages_key="history", # 指定历史消息的键名
        # )
        # print(chain_with_history.invoke(
        #     {"ability": "写笑话", "question": "请写一个笑话"},
        #     config={"configurable": {"session_id": "1"}}
        # ))
        # print(chain_with_history.invoke(
        #     {"ability": "写笑话", "question": "上面笑话的主题是什么？"},
        #     config={"configurable": {"session_id": "1"}}
        # ))
        
        #创建一个带历史消息的链，索引为用户id+会话id
        with_message_history = RunnableWithMessageHistory(
            chain,
            get_session_history=get_session,
            input_messages_key="question", # 输入消息的键名
            history_messages_key="history", # 历史消息的键名
            history_factory_config=[ # 历史记录工厂配置
                ConfigurableFieldSpec(
                    id="user_id", # 配置字段ID
                    annotation=str, # 类型注解
                    name="用户ID", # 字段名称
                    description="用户的唯一标识符", # 字段描述
                    default="", # 默认值
                    is_shared=True, # 是否在多个调用间共享
                ),
                ConfigurableFieldSpec(
                    id="conversation_id", # 配置字段ID
                    annotation=str, # 类型注解
                    name="对话ID", # 字段名称
                    description="对话的唯一标识符", # 字段描述
                    default="", # 默认值
                    is_shared=True, # 是否在多个调用间共享
                ),
            ],
        )
        with_message_history.invoke(
            {"ability": "写笑话", "question": "请写一个笑话"},
            config={"configurable": {"user_id": "1", "conversation_id": "1"}}
        )
        with_message_history.invoke(
            {"ability": "写笑话", "question": "上面笑话的主题是什么？"},
            config={"configurable": {"user_id": "1", "conversation_id": "1"}}
        )
        print(stored_history)
    
    #code 15 长期记忆
    def code15():
        def get_history(session_id: str) -> RedisChatMessageHistory:
            return RedisChatMessageHistory(
                session_id=session_id,
                redis_url="redis://127.0.0.1:8888",
            )
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个擅长{ability}的助手"), # 系统角色提示,使用ability变量定义助手专长
            MessagesPlaceholder(variable_name="history"), # 放置历史消息的占位符
            ("human", "{question}"), # 用户问题的占位符
        ])
        chain = prompt | model
        with_history = RunnableWithMessageHistory(
            chain,
            get_session_history=get_history,
            input_messages_key="question", # 输入消息的键名
            history_messages_key="history", # 历史消息的键名
        )
        history = get_history("uesr1")
        history.clear()
        with_history.invoke(
            { "ability":"写笑话", "question": "请写一个笑话"},
            config={"configurable": {"session_id": "uesr1"}}
        )
        with_history.invoke(
            { "ability":"写笑话","question": "上面笑话的主题是什么？"},
            config={"configurable": {"session_id": "uesr1"}}
        )
        print("聊天历史： ")
        for message in history.messages:
            # 打印每条消息的类型和内容
            print(f"{type(message).__name__}: {message.content}")
    
    #code 16 自定义路由链
    def code16 ():
        chain = (
            PromptTemplate.from_template(
                """根据下面的用户问题， 将其分类为 `LangChain`、 `Anthropic` 或 `Other`。
                请只回复一个词作为答案。
                <question>
                {question}
                </question>
                分类结果:"""
                ) | model | StrOutputParser() 
        )
        langchain_chain = PromptTemplate.from_template(
            """你将扮演一位LangChain专家。 请以他的视角回答问题。 \
            你的回答必须以"正如Harrison Chase告诉我的"开头， 否则你会受到惩罚。 \
            请回答以下问题:
            问题: {question}
            回答:"""
            ) | model
        anthropic_chain = PromptTemplate.from_template(
            """你将扮演一位一位Anthropic专家。 请以他的视角回答问题。 \
            你的回答必须以"正如Dario Amodei告诉我的"开头， 否则你会受到惩罚。 \
            请回答以下问题:
            问题: {question}
            回答:"""
            ) | model
        general_chain = PromptTemplate.from_template(
            """请回答以下问题:
            问题: {question}
            回答:"""
            ) | model
        
        def route(info):
            print(info)
            if "anthropic" in info["topic"].lower():
                print("claude")
                return anthropic_chain
            elif "langchain" in info["topic"].lower():
                print("langchain")
                return langchain_chain
            else:
                print("general")
                return general_chain
            
        fall_chain={
            "topic":chain, "question": lambda x:x["question"]
        } | RunnableLambda(route) | StrOutputParser()

        res = fall_chain.invoke({"question":"我该如何使用langchain?"})
        print(res)
    

if __name__ == "__main__":
    # chat_template = ChatPromptTemplate.from_messages(
    #     [
    #         {"role": "system", "content": "你是⼀个熟知各种二次元的助手，请以这个身份给出购买二次元产品建议"},
    #         {"role": "human", "content": "我想购买一些{name}的立牌，可以给出一些产品建议并附上网购链接吗？"},
    #     ]
    # )
    # key = os.getenv("SILICONFLOW_API_KEY")
    # base = os.getenv("SILICONFLOW_API_BASE")
    # model = ChatDeepSeek(
    #     model='deepseek-ai/DeepSeek-R1-0528-Qwen3-8B',
    #     temperature=0,
    #     api_key=key,
    #     api_base=base,
    # )
    # chain = chat_template | model | StrOutputParser()
    # res = chain.invoke({"name": "爱莉希雅"})
    # print(res)
    main()
