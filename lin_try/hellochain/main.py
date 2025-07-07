from langchain import hub
from langsmith import Client
from langchain_deepseek import ChatDeepSeek
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.prompts import StringPromptTemplate, MessagesPlaceholder

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage

from langchain_core.output_parsers import PydanticOutputParser, XMLOutputParser
from langchain_core.output_parsers import StrOutputParser
from langchain.output_parsers import RetryOutputParser
from langchain_core.exceptions import OutputParserException

from langchain_core.runnables import RunnableParallel, chain, ConfigurableField
from langchain_core.runnables import RunnableLambda, RunnablePassthrough, ConfigurableFieldSpec
from langchain_core.runnables.history import RunnableWithMessageHistory

from langchain_core.chat_history import BaseChatMessageHistory

from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.vectorstores import FAISS

from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document

from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_community.document_loaders import TextLoader, UnstructuredExcelLoader
from langchain_community.document_loaders.csv_loader import CSVLoader

from langchain_text_splitters import CharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain.runnables.hub import HubRunnable
from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from langchain_unstructured import UnstructuredLoader
from langchain_pinecone import PineconeVectorStore
from langchain_redis import RedisChatMessageHistory

import asyncio, base64, io, fitz, bs4, getpass, time, inspect, json, os
from PIL import Image
from dotenv import load_dotenv
from uuid import uuid4
from operator import itemgetter
from typing import Iterator, List, AsyncIterator
from pydantic import BaseModel, Field, model_validator
from IPython.display import Image as IPImage
from IPython.display import display
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

class CustomDocumentLoader(BaseLoader):
    """逐行读取文件的文档加载器示例"""
    def __init__(self, file_path: str) -> None:
        """使用文件路径初始化加载器
        参数:file_path: 要加载的文件路径
        """
        self.file_path = file_path

    def lazy_load(self) -> Iterator[Document]:
        """逐行读取文件的惰性加载器
        当实现惰性加载方法时,你应该使用生成器
        一次生成一个文档
        """
        with open(self.file_path, encoding="utf-8") as f:
            line_number = 0
            for line in f:
                yield Document(
                    page_content=line,
                    metadata={"line_number": line_number, "source": self.file_path},
                )
                line_number += 1

    # alazy_load 是可选的
    # 如果不实现它,将使用一个默认实现,该实现会委托给 lazy_load!
    async def alazy_load(
        self,
    ) -> AsyncIterator[Document]:  # <-- 不接受任何参数
        """逐行读取文件的异步惰性加载器"""
        # 需要 aiofiles (通过 pip 或 uv 安装)
        # https://github.com/Tinche/aiofiles
        import aiofiles

        async with aiofiles.open(self.file_path, encoding="utf-8") as f:
            line_number = 0
            async for line in f:
                yield Document(
                    page_content=line,
                    metadata={"line_number": line_number, "source": self.file_path},
                )
                line_number += 1

def main():
    key = os.getenv("SILICONFLOW_API_KEY")
    base = os.getenv("SILICONFLOW_API_BASE")
    langsmith_key = os.getenv("LANGSMITH_API_KEY") #模版网站的api_key
    model = ChatDeepSeek(
        model='deepseek-ai/DeepSeek-R1-0528-Qwen3-8B',
        temperature=0,
        api_key=key,
        api_base=base,
    ).configurable_fields(
        temperature=ConfigurableField(
            id="temperature",
            name="模型温度",
            description="The temperature to use for the model."
        ),
    )

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
                redis_url="redis://47.98.143.59:6379",
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
    # code15()
    
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
    
    #异步加载pdf
    async def load_pdf():
        file_path = "1.pdf"
        loader=PyPDFLoader(file_path)
        pages = []
        async for page in loader.alazy_load():
            pages.append(page)
        
        for page in pages:
            print(page.metadata)
            print(page.page_content)

    #读取pdf中图片
    def pdf_page_to_base64(page_number: int):
        pdf_document= fitz.open("E:\\1.pdf")
        page = pdf_document.load_page(page_number - 1) # input is one-indexed
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    
    #多模态
    def code17():
        query = "What is the subject of picture?"
        message = HumanMessage(
            content=[
                {"type": "text", "text": query},
                {
                    "type": "image_url",
                    "image _url": {"url": f"data: image/jpeg;base64,{pdf_page_to_base64(1)}"}
                }
            ]
        )
        model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE")
        )
        print(1)
        res = model.invoke([message])
        print(res)
    
    page_url = "https://python.langchain.com/docs/how_to/chatbots_memory/"
    #加载网址
    async def loadweb(page_url):
        loader = WebBaseLoader(web_paths=[page_url])
        docs =[]
        async for doc in loader.alazy_load():
            docs.append(doc)
        assert len(docs) == 1
        doc = docs[0]
        print(f"{doc.metadata}\n")
        print(doc.page_content[:500].strip())
    # asyncio.run(loadweb(page_url))
    
    #加载部分网页
    async def loadwebPart(page_url,page_num):
        loader = WebBaseLoader(
            web_paths=[page_url],
            bs_kwargs={
                "parse_only": bs4.SoupStrainer(class_="theme-doc-markdow markdown"),
            },
            bs_get_text_kwargs={"separator": " | ", "strip": True},
        )
        docs=[]
        async for doc in loader.alazy_load():
            docs.append(doc)
        assert len(docs) == 1
        doc = docs[page_num]
        print(f"{doc.metadata}\n")
        print(doc.page_content[:500])
    # asyncio.run(loadwebPart(page_url,0))

    #不熟悉网页结构时解析网页
    def loadweb_parse(page_url):
        try:
            loader = UnstructuredLoader(web_url=page_url)
            print(0)
            docs = list(loader.load())
            print(1)
            for doc in docs[:5]:
                print(f"{doc.metadata}\n")
                print(doc.page_content[:500])
        except Exception as e:
            print(e)
    # loadweb_parse("https://example.com")

    csv_path = "lin_try/hellochain/info.csv"
    #加载csv文件
    def loadcsv(file_path):
        loader = CSVLoader(file_path=file_path, encoding="utf-8")
        data = loader.load()
        for record in data[:2]:
            print(record)

        # 指定⼀列来标识⽂档
        loader = CSVLoader(file_path=file_path, source_column="邮箱", encoding="utf-8")
        data = loader.load()
        for record in data[:2]:
            print(record)
    # loadcsv(csv_path)

    xlsx_path = "lin_try/hellochain/scores.xlsx"
    # 加载excel文件
    def loadexcel(xlsx_path):
        # 加载所有工作表
        loader = UnstructuredExcelLoader(
            xlsx_path,
            mode="elements",
            process_multiple_sheets=True
        )
        documents = loader.load()
        print(f"Loaded {len(documents)} documents from {xlsx_path}")
        for doc in documents:
            print(f"Metadata: {doc.metadata}")
            print(f"Content: {doc.page_content[:500]}...")  # Print first 500 characters of content
            print("-" * 80)
    # loadexcel(xlsx_path)

    def loadcustom():
        with open("lin_try/hellochain/meow.txt", "w", encoding="utf-8") as f:
            quality_content = "meow meow🐱 \n meow meow🐱 \n meow😻😻"
            f.write(quality_content)

        loader = CustomDocumentLoader("lin_try/hellochain/meow.txt")

        ## 测试懒加载
        for doc in loader.lazy_load():
            print()
            print(type(doc))
            print(doc)
    # loadcustom()
    
    def split():
        file_path = "lin_try/hellochain/deepseek.pdf"
        loader = PyPDFLoader(file_path)
        pages =[]
        for page in loader.load():
            pages.append(page)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=0)
        texts = text_splitter.split_text(pages[1].page_content)
        print(texts)
        print("-"*50)

        text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
            encoding_name="cl100k_base", chunk_size=50, chunk_overlap=10
        )
        texts = text_splitter.split_text(pages[1].page_content)
        print(texts)
        print( "= " * 50)
        docs = text_splitter.create_documents([pages[2].page_content,pages[3].page_content])
        print(docs)
    # split()

    #FAISS缓存
    def embed():
        embeddings_model = OpenAIEmbeddings(
            openai_api_key=key, 
            openai_api_base=base, 
            model="BAAI/bge-m3"
        )
        embeddings = embeddings_model.embed_documents(
            [
                "Hi there!",
                "Oh, hello!",
                "What's your name?",
                "My friends call me World",
                "Hello World!"
            ]
        )
        # embed_query
        query_embedding = embeddings_model.embed_query("What is the meaning of life?")
        # print(query_embedding)
        store = LocalFileStore("lin_try/hellochain/cache")
        cached_embedder = CacheBackedEmbeddings.from_bytes_store(
            embeddings_model, store, namespace=embeddings_model.model
        )
        print(list(store.yield_keys()))
        print("-"*50)
        raw_documents = TextLoader("lin_try/hellochain/meow.txt").load()
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        documents = text_splitter.split_documents(raw_documents)
        # 创建向量存储
        db = FAISS.from_documents(documents, cached_embedder)

        # 再次创建将会读取缓存，从而加快速度降低成本
        db2 = FAISS.from_documents(documents, cached_embedder)
        # 查看缓存
        print(list(store.yield_keys())[:5])
    # embed()

    # 将vector存储到内存中
    def vector():
        embeddings_model = OpenAIEmbeddings(
            openai_api_key = key, 
            openai_api_base = base, 
            model="BAAI/bge-m3"
        )
        vector_store = InMemoryVectorStore(embedding=embeddings_model)
        document_1 = Document(
            page_content="今天在抖音学会了一个新菜：锅巴土豆泥！看起来简单，实际炸了厨房，连猫都嫌弃地走开了。",
            metadata={"source": "社交媒体"},
        )
        document_2 = Document(
            page_content="小区遛狗大爷今日播报：广场舞大妈占领健身区，遛狗群众纷纷撤退。现场气氛诡异，BGM已循环播放《最炫民族风》两小时。",
            metadata={"source": "社区新闻"},
        )
        documents=[document_1, document_2]
        result = vector_store.add_documents(documents=documents, ids=["doc1", "doc2"])
        # ids为可选项
        print(f"add {result}")
        print("-"*50)
        query = "遛狗"
        # 直接相似性查询
        docs = vector_store.similarity_search(query=query)
        print(docs[0].page_content)
        print("-"*50)
        # 使用向量模型将查询转换为向量，再利用向量进行相似性查询
        embeddings_vector = embeddings_model.embed_query(query)
        docs = vector_store.similarity_search_by_vector(embeddings_vector)
        print(docs[0].page_content)
        print("-"*50)

        # 删除向量
        vector_store.delete(ids=["doc2"])
        docs = vector_store.similarity_search_by_vector(embeddings_vector)
        print(docs[0].page_content)
        print("-"*50)
    # vector()

    # 利用pinecone存储向量
    def vector2():
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"),)
        index_name="test-index"
        existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
        if index_name not in existing_indexes:
            # 初始化向量数据库
            pc.create_index(
                name=index_name,
                dimension=4096, #注意维度要一致
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
            while not pc.describe_index(index_name).status["ready"]:
                time.sleep(1)
        # 查询pinecone数据信息
        index_info = pc.describe_index(index_name)
        print(f"dimension: {index_info}")
        index = pc.Index(index_name)
        print(f"index = {index}")

        embeddings_model = OpenAIEmbeddings(
            openai_api_key = key, 
            openai_api_base = base, 
            model="Qwen/Qwen3-Embedding-8B"
        )
        vector_store = PineconeVectorStore(index=index, embedding=embeddings_model)
        # 测试数据
        document_1 = Document(
            page_content="今天早餐吃了老王家的生煎包，馅料实在得快从褶子里跳出来了！这才是真正的上海味道！",
            metadata={"source": "tweet"},
        )
        document_2 = Document(
            page_content="明日天气预报：北京地区将出现大范围雾霾，建议市民戴好口罩，看不见脸的时候请不要慌张。",
            metadata={"source": "news"},
        )
        document_3 = Document(
            page_content="终于搞定了AI聊天机器人！我问它'你是谁'，它回答'我是你爸爸'，看来还需要调教...",
            metadata={"source": "tweet"},
        )
        document_4 = Document(
            page_content="震惊！本市一男子在便利店抢劫，只因店员说'扫码支付才有优惠'，现已被警方抓获。",
            metadata={"source": "news"},
        )
        document_5 = Document(
            page_content="刚看完《流浪地球3》，特效简直炸裂！就是旁边大妈一直问'这是在哪拍的'有点影响观影体验。",
            metadata={"source": "tweet"},
        )
        document_6 = Document(
            page_content="新发布的小米14Ultra值不值得买？看完这篇测评你就知道为什么李老板笑得合不拢嘴了。",
            metadata={"source": "website"},
        )
        document_7 = Document(
            page_content="2025年中超联赛十大最佳球员榜单新鲜出炉，第一名居然是他？！",
            metadata={"source": "website"},
        )
        document_8 = Document(
            page_content="用LangChain开发的AI助手太神奇了！问它'人生的意义'，它给我推荐了一份外卖优惠券...",
            metadata={"source": "tweet"},
        )
        document_9 = Document(
            page_content="A股今日暴跌，分析师称原因是'大家都在抢着卖'，投资者表示很有道理。",
            metadata={"source": "news"},
        )
        document_10 = Document(
            page_content="感觉我马上要被删库跑路了，祝我好运 /(ㄒoㄒ)/~~",
            metadata={"source": "tweet"},
        )
        documents = [
            document_1,
            document_2,
            document_3,
            document_4,
            document_5,
            document_6,
            document_7,
            document_8,
            document_9,
            document_10,
        ]
        uuids = [str(uuid4()) for _ in range(len(documents))]
        vector_store.add_documents(documents=documents, ids=uuids)
        results = vector_store.similarity_search(
            "看电影", #搜索词
            k=1, # 返回结果数
            filter={"source": "tweet"}, # 筛选
        )
        for res in results:
            print(f"* {res.page_content} [{res.metadata}]")
        print("-"*50)

        vector_store.delete(ids=[uuids[-1]]) #删除

        results = vector_store.similarity_search_with_score(
            "明天热吗?", k=1, filter={"source": "news"}
        )
        for res, score in results:
            print(f"* [SIM={score:3f}] {res.page_content} [{res.metadata}]")
        print("-"*50)

        results = vector_store.max_marginal_relevance_search(
            query="新手机",
            k=1,
            lambda_val=0.8,
            filter={"source": "website"},
        )
        for res in results:
            print(f"*{res.page_content} [{res.metadata}]")
        print("-"*50)
    # vector2()


if __name__ == "__main__":
    main()
