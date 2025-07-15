from pydantic import BaseModel, Field
from typing import List, Optional
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_redis import RedisChatMessageHistory
# from langchain_core.runnables import RunnableParallel
from langchain_core.runnables.history import RunnableWithMessageHistory 
from langchain_core.output_parsers import StrOutputParser # 导⼊字符串输出解析器
import os
from dotenv import load_dotenv
from dao import userDAO

# 加载环境变量
load_dotenv()
key = os.getenv("SILICONFLOW_API_KEY")
base = os.getenv("SILICONFLOW_API_BASE")

# 初始化DeepSeek模型
llm = ChatDeepSeek(
    model='deepseek-ai/DeepSeek-R1',
    temperature=0.3,  # 适当提高随机性，避免排序逻辑过于僵化
    api_key=key,
    api_base=base,
    timeout=180,
)

# llm = ChatDeepSeek(
#     model='deepseek-ai/DeepSeek-R1',
#     temperature=0,
#     api_key=key,
#     api_base=base,
#     timeout=180,#增加请求超时限制
# )

# 完整商品数据模型
class Product(BaseModel):
    name: str = Field(..., description="商品名称")
    price: float = Field(..., description="商品价格")
    deals: int = Field(..., description="销量")
    img_url: str = Field(..., description="商品图片URL")
    goods_url: str = Field(..., description="商品详情页URL")
    shop_url: str = Field(..., description="店铺URL")


class SortedProducts(BaseModel):
    sorted_products: List[Product] = Field(..., description="排序后的商品列表")
    sorting_rules: str = Field(..., description="排序规则说明，需明确说明排序依据")
    output_count: int = Field(..., description="实际输出的商品数量，需与用户指定或默认值一致")

class Project(BaseModel):
    name: str = Field(..., description="可能想要买的商品的名称，只用一个词描述想要的商品,可以带修饰词描述，如果商品有多个，请列出商品名并用|分隔")
    # description: str = Field(..., description="对于每个想要买的商品的描述，用|分隔")
    
class metamessage:
    def __init__(self, mestype:type, contents):
        self.type = mestype
        self.content = contents
def ai_get_history(session_id: str):
    history = RedisChatMessageHistory(
        redis_url="redis://47.98.143.59:6379",  # Redis 连接URL
        session_id=session_id,  # 会话ID
    )
    meshistory = []
    for message in history.messages:
        meshistory.append({
            'type':str(message.type), 
            'content':message.content,
            })
    return meshistory
# test
# print("历史消息：") # 显示当前历史消息
# for i in ai_get_history("user_1"):
#     print("说话对象：", i.type,"交流内容：" , i.content) # 打印每条消息的类型和内容

class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """内存聊天历史实现，增强消息类型校验"""
    messages: List[BaseMessage] = Field(default_factory=list)
    
    def add_messages(self, messages: List[BaseMessage]) -> None:
        """确保只添加BaseMessage类型，支持字符串自动转换为HumanMessage"""
        validated_messages = []
        for msg in messages:
            if not isinstance(msg, BaseMessage):
                if isinstance(msg, str):
                    msg = HumanMessage(content=msg)
                else:
                    raise ValueError(f"不支持的消息类型: {type(msg)}")
        self.messages.extend(validated_messages)
    def add_message(self, message):
        if str(message.type) == "human":
            self.messages.append(HumanMessage(content=message.content))
        elif str(message.type) == "ai":
            self.messages.append(AIMessage(content=message.content))
    def clear(self) -> None:
        self.messages = []

def ai_get_keywords(session_id:str, question: str):
    router_chain = (
        PromptTemplate.from_template("""
            你和另一人一同完成商品推荐的工作，
            请根据下面用户的问题，将用户的问题分类为'1'或'0'。
            若用户的问题涉及需要推荐商品或者继续细化之前提到的商品的特征，则分类为'1'。
            若用户的问题设计到讨论商品在价格、销量等方面的表现，则分类为'0'。
            只需要回复'0'或者'1'。
            <question>
            {question}
            </question>
            分类结果：""") | llm | StrOutputParser()
    )
    result = router_chain.invoke({"question": question}) # 调用路由链，获取问题类型
    
    print("问题类型：", result) # 打印问题类型
    if int(result) == 0: # 如果问题类型不是关于商品推荐
        return([], False) # 返回空列表和False
    
    # 实例化解析器、提示词模板
    parser = PydanticOutputParser(pydantic_object=Project)
    # 注意，提示词模板中需要部分格式化解析器的格式要求format_instructions 
    prompt = PromptTemplate(
        template="{history}\n回答⽤户的查询，查询出的商品名是关于日常商品的，如果结果有多个请用|分隔,商品描述如果有多个也请用|分隔.\n{format_instructions}\n{question}",
        input_variables=["history","question"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
     # 将提示模板与模型组合成⼀个处理链
    chain = prompt | llm | parser
    redis_history = RedisChatMessageHistory(
        redis_url = "redis://47.98.143.59:6379",# Redis 连接URL
        session_id = session_id, # 会话ID
    )
    # 转换函数
    # def get_session_history(session_id: str) -> BaseChatMessageHistory:
    #     temp = InMemoryHistory()
    #     for message in redis_history.messages:
    #         # print("说话对象：", message.type,"交流内容：" , message.content, "类型：", message.name)  # 打印每条消息的类型和内容
    #         temp.add_message(message)
    #     return temp
    def get_session_history(session_id: str) -> RedisChatMessageHistory:
        return redis_history
        
    # 创建⼀个带有消息历史的可运⾏对象
    chain_with_history  = RunnableWithMessageHistory(
        chain,# 基础链
        get_session_history,
        input_messages_key="question",  # 指定输⼊消息的键为"question"
        history_messages_key="history", # 指定历史消息的键为"history"
    )
    res = chain_with_history.invoke(
        {"question": question},
        config={"configurable": {"session_id": session_id}}  # 配置会话ID为"foo"
    )
    # # 向历史记录中添加消息
    redis_history.add_user_message(question)
    pro = res.name.split("|")
    ai_message = "我认为你可能需要的商品是"
    for i in pro:
        ai_message += i + "、"
    redis_history.add_ai_message(ai_message)
    # print("商品名称：",res.name.split("|"))
    # print("商品描述：",res.description.split("|"))
    return (pro, True)

def ai_delete_history(session_id:str):
    history = RedisChatMessageHistory(
        redis_url = "redis://47.98.143.59:6379",# Redis 连接URL
        session_id = session_id, # 会话ID
    )
    history.clear()  # 清除聊天历史

def ai_recommend(
    session_id: str,
    question: str,
    key: str,
    # products: List[dict],
    user_preferences: Optional[str] = None,
) -> List[Product]:
    """
    完整商品信息排序函数
    
    :param products: 包含完整商品信息的字典列表
    :return: 包含所有原始字段的Product对象列表
    """
    
    #  原始数据
    products = userDAO.find_goods(session_id=session_id, keyword=key)
    # print("原始数据：", products)
    
    # 数据校验
    required_fields = ["name", "price", "deals", "img_url", "goods_url", "shop_url"]
    for i, p in enumerate(products):
        missing = [f for f in required_fields if f not in p]
        if missing:
            raise ValueError(f"商品{i+1}缺少必要字段：{missing}")

    parser = PydanticOutputParser(pydantic_object=SortedProducts)

    # 构建提示词（简化版，重点在完整输出）
    prompt_template = """
    你是专业的商品排序助手，需根据商品信息和用户需求完成以下任务：
    1. 对商品进行排序（支持多轮调整，可参考历史偏好）
    2. 清晰说明排序规则（尤其是用户偏好的体现）

    商品列表：
    {products}
    
    {history_prompt}  # 多轮对话时引入历史偏好
    {current_preferences}  # 当前轮次的用户偏好
    用户的需求为：{question}

    
    排序参考维度（需综合或侧重）：
    - 价格（越低越优）
    - 销量（越高越优，反映大众认可度）
    - 用户明确偏好（如指定则优先满足）

    输出要求：
    - 排序规则需具体
    - 输出的商品数据要包含名字价格销量
    - 不需要输出全部的商品，只需要输出排序后的前几名

    {format_instructions}
    """
    
    # 4. 处理历史对话（支持追加偏好调整）
    redis_history = RedisChatMessageHistory(
        redis_url="redis://47.98.143.59:6379",
        session_id=session_id
    )
    history_prompt = ""
    if redis_history.messages:
        history_prompt = "历史偏好参考：用户之前提到过{}".format(
            "; ".join([m.content for m in redis_history.messages if "偏好" in m.content.lower()])
        )

    # 5. 处理当前偏好（无偏好时说明默认逻辑）
    current_preferences = ""
    if user_preferences:
        current_preferences = f"当前用户偏好：{user_preferences}（请优先满足）"
    else:
        current_preferences = "当前无特殊偏好，默认按销量越高越好，价格越低越好的综合排序"

    # 格式化商品信息（简略显示）
    products_str = "\n".join([
        f"{i+1}. {p['name']} | 价格：{p['price']} | 销量：{p['deals']}"
        for i, p in enumerate(products)
    ])
    
    # 构建处理链
    parser = PydanticOutputParser(pydantic_object=SortedProducts)
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["products", "history_prompt", "current_preferences", "question"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    chain = prompt | llm | parser
    def get_session_history(session_id: str) -> RedisChatMessageHistory:
        return redis_history

    chain_with_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="current_preferences",  # 绑定当前偏好为输入键
        history_messages_key="history_prompt"  # 绑定历史消息为历史键
    )

    # 调用模型
    try:
        print(1)
        result = chain_with_history.invoke(
            input={
                "products": products_str,
                "history_prompt": history_prompt,
                "current_preferences": current_preferences,
                "question": question,
            },
            config={"configurable": {"session_id": session_id}}
        )
    except Exception as e:
        raise RuntimeError(f"排序失败：{str(e)}")
    
    # 10. 保存本轮对话到历史（便于后续调整）
    user_msg = f"请求排序（），偏好：{user_preferences or '无'}"
    ai_msg = f"排序规则：{result.sorting_rules}（输出{len(result.sorted_products)}件）"
    redis_history.add_user_message(user_msg)
    redis_history.add_ai_message(ai_msg)
    
    # 将原始数据映射到结果中
    final_products = []
    name_to_original = {p["name"]: p for p in products}
    
    for sorted_p in result.sorted_products:
        original = name_to_original.get(sorted_p.name)
        if original:
            final_products.append(Product(
                name=original["name"],
                price=original["price"],
                deals=original["deals"],
                img_url=original["img_url"],
                goods_url=original["goods_url"],
                shop_url=original["shop_url"],
            ))
    
    
    res = []
    for i in final_products:
        res.append({
            "name": i.name,
            "price": i.price,
            "deals": i.deals,
            "img_url": i.img_url,
            "goods_url": i.goods_url,
            "shop_url": i.shop_url,
        })

    return res



# ------------------------------
# 测试用例（覆盖所有新功能）
# ------------------------------
# if __name__ == "__main__":
    # # 测试数据：更多商品（超过5个，测试top_n功能）
    # test_products = [
    #     {"name": "无线耳机", "price": 299, "rating": 4.5, "sales": 1200},
    #     {"name": "蓝牙音箱", "price": 199, "rating": 4.2, "sales": 800},
    #     {"name": "智能手表", "price": 599, "rating": 4.7, "sales": 1500},
    #     {"name": "手机支架", "price": 39, "rating": 4.0, "sales": 3000},
    #     {"name": "充电宝", "price": 89, "rating": 4.3, "sales": 2500},
    #     {"name": "蓝牙耳机", "price": 159, "rating": 4.4, "sales": 1800}  # 第6个商品
    # ]

    # # 测试1：默认排序（前5名，无偏好）
    # print("=== 测试1：默认排序（前5名，无偏好） ===")
    # sorted1 = ai_sort_products("test_user", test_products)
    # for i, p in enumerate(sorted1, 1):
    #     print(f"{i}. {p.name} - 评分：{p.rating}，价格：{p.price}，销量：{p.sales}")

    # # 测试2：指定输出前3名，带偏好
    # print("\n=== 测试2：指定前3名，偏好「高销量」 ===")
    # sorted2 = ai_sort_products("test_user", test_products, user_preferences="我想要销量高的", top_n=3)
    # for i, p in enumerate(sorted2, 1):
    #     print(f"{i}. {p.name} - 销量：{p.sales}")

    # 测试3：追加偏好调整（基于上一轮历史，新增「价格低于200」）
    # print("\n=== 测试3：追加偏好（销量高且价格低于200） ===")
    # sorted3 = ai_sort_products("test_user", test_products, user_preferences="销量高且价格低于200", top_n=3)
    # for i, p in enumerate(sorted3, 1):
    #     print(f"{i}. {p.name} - 价格：{p.price}，销量：{p.sales}")
    
    # # 测试4：回调测试
    # redis_history = RedisChatMessageHistory(
    #     redis_url="redis://47.98.143.59:6379",
    #     session_id="user_1"
    # )
    # def get_session_history(session_id: str) -> BaseChatMessageHistory:
    #     temp = InMemoryHistory()
    #     for message in redis_history.messages:
    #         print("说话对象：", message.type,"交流内容：" , message.content, "类型：", message.name)  # 打印每条消息的类型和内容
    #         temp.add_message(message)
    #     return temp
    # print("get_by_session_id:")  # 打印转换后的历史消息
    # for i in get_session_history("user_1").messages:
    #     print("说话对象：", i.type,"交流内容：" , i.content, "类型：", i.name)  # 打印每条消息的类型和内容
    
    # # 测试5：多轮调整（基于历史偏好）
    # ai_delete_history("user_1") # 清除历史记录
    # print("处理请求中。。。")
    # print(ai_get_keywords("user_1", "我想买个戴在手上的")) # 测试函数
    # print("处理请求中。。。")
    # print(ai_get_keywords("user_1", "最好是金色的"))
    # print("处理请求中。。。")
    # print("历史消息：") # 显示当前历史消息
    # for i in ai_get_history("user_1"):
    #     print("说话对象：", i.type,"交流内容：" , i.content) # 打印每条消息的类型和内容
    
    # # 测试6：完整商品信息排序
    # test_product = {
    #     'name': '【政府补贴15%】HONOR/荣耀200 5G手机 5200mAh青海湖电池5000万三主摄写真相机荣耀绿洲 护眼屏官方旗舰店100 5G 手机',
    #     'price': 1410.15,
    #     'deals': 70000,
    #     'img_url': 'https://g-search3.alicdn.com/img/bao/uploaded/i4/i4/1114511827/O1CN01pYspum1PMog8RZ6Ze_!!4611686018427386323-0-item_pic.jpg_580x580q90.jpg_.webp',
    #     'goods_url': '//detail.tmall.com/item.htm?priceTId=2147818d17521394102321658e1c75&utparam=%7B%22aplus_abtest%22%3A%2256498aa96c581f213f393002730bc35f%22%7D&id=789770187657&ns=1&abbucket=20&xxc=taobaoSearch&detail_redpacket_pop=true&query=%E6%89%8B%E6%9C%BA%205G&mi_id=MgoS6nP-gUWyQU8KRHWWoIOTsMQOKTczL27npuUTMCI_TYgNAvxxu0-4L-m6dG-ty-myroJvH9haNbjdX5Oy0jj7hogeQmFLiUV09xFRj-s&skuId=5890259858259&spm=a21n57.1.item.49',
    #     'shop_url': '//store.taobao.com/shop/view_shop.htm?appUid=RAzN8HWJa6UWaRALcQM7yQ91BruC69N5os3Q6hgqbEP6bxEp16h&spm=a21n57.1.item.49' 
    # }
    
    # # 模拟多个商品
    # test_products = [test_product, 
    #                 {**test_product, 'name': 'iPhone 15', 'price': 5999, 'deals': 50000},
    #                 {**test_product, 'name': '小米14', 'price': 3999, 'deals': 80000}]
    
    # ai_delete_history("test_session")
    # # print("history:\n",ai_get_history("test_session"))  # 打印当前历史消息
    # # 执行排序
    # sorted_results = ai_recommend(
    #     session_id="test_session", 
    #     question="请帮我推荐几款性价比高的手机",
    #     key="手机 5G",
    #     products=test_products)
    
    # # 打印完整结果
    # print(f"推荐结果:")
    # for i, product in enumerate(sorted_results, 1):
    #     print(f"\n=== 第{i}名 ===")
    #     print(f"名称: {product.name}")
    #     print(f"价格: {product.price}")
    #     print(f"销量: {product.deals}")
    #     print(f"图片: {product.img_url}")
    #     print(f"商品链接: {product.goods_url}")
    #     print(f"店铺链接: {product.shop_url}")
    
    # print("\n")
    # print("历史消息：") # 显示当前历史消息
    # for i in ai_get_history("test_session"):
    #     print("说话对象：", i.type,"交流内容：" , i.content) # 打印每条消息的类型和内容