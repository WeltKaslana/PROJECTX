from pydantic import BaseModel, Field
from typing import List, Optional
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_redis import RedisChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory 
import os
from dotenv import load_dotenv

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


# 数据模型定义
class Product(BaseModel):
    name: str = Field(..., description="商品名称")
    price: float = Field(..., description="商品价格，数值类型")
    rating: float = Field(..., description="用户评分，1-5之间的数值")
    sales: int = Field(..., description="销量，整数类型")
    # 可扩展其他属性：品牌、库存等


class SortedProducts(BaseModel):
    sorted_products: List[Product] = Field(..., description="排序后的商品列表")
    sorting_rules: str = Field(..., description="排序规则说明，需明确说明排序依据")
    output_count: int = Field(..., description="实际输出的商品数量，需与用户指定或默认值一致")

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
        meshistory.append(metamessage(type(message), message.content))
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

    def clear(self) -> None:
        self.messages = []


def ai_sort_products(
    session_id: str,
    products: List[dict],
    user_preferences: Optional[str] = None,
    top_n: int = 5  # 新增：默认输出前五名
) -> List[Product]:
    """
    对商品列表进行智能排序，支持指定输出数量和追加偏好调整
    
    :param session_id: 会话ID（用于存储历史，支持多轮调整）
    :param products: 商品列表（含name, price, rating, sales等字段）
    :param user_preferences: 用户偏好（可选，如"更看重性价比"）
    :param top_n: 输出的商品数量（默认5，用户可指定）
    :return: 排序后的商品列表（前N名）
    """
    # 1. 数据校验：确保商品属性完整
    required_fields = ["name", "price", "rating", "sales"]
    for i, p in enumerate(products):
        missing = [f for f in required_fields if f not in p]
        if missing:
            raise ValueError(f"商品{i+1}缺少必要字段：{missing}")

    # 2. 构建输出解析器（严格约束格式）
    parser = PydanticOutputParser(pydantic_object=SortedProducts)

    # 3. 构建提示词模板（增强多轮调整和数量控制）
    prompt_template = """
    你是专业的商品排序助手，需根据商品信息和用户需求完成以下任务：
    1. 对商品进行排序（支持多轮调整，可参考历史偏好）
    2. 仅输出前{top_n}名商品
    3. 清晰说明排序规则（尤其是用户偏好的体现）

    商品信息：
    {products}

    {history_prompt}  # 多轮对话时引入历史偏好
    {current_preferences}  # 当前轮次的用户偏好

    排序参考维度（需综合或侧重）：
    - 性价比（评分/价格比值）
    - 用户评分（越高越优）
    - 销量（越高越优，反映大众认可度）
    - 用户明确偏好（如指定则优先满足）

    输出要求：
    - 严格返回前{top_n}名商品，不可多不可少
    - 排序规则需具体（例如："因用户看重性价比，按评分/价格降序排列"）
    - 若商品总数不足{top_n}，则全部返回并说明

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
        current_preferences = "当前无特殊偏好，默认按「评分*0.4 + 销量*0.3 + 性价比*0.3」综合排序"

    # 6. 格式化提示词
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["products", "history_prompt", "current_preferences", "top_n"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    # 7. 商品信息格式化（避免长文本冗余）
    products_str = "\n".join([
        f"{i+1}. 名称：{p['name']}，价格：{p['price']}，评分：{p['rating']}，销量：{p['sales']}"
        for i, p in enumerate(products)
    ])

    # 8. 构建带历史的处理链
    chain = prompt | llm | parser

    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        temp = InMemoryHistory()
        temp.add_messages(redis_history.messages)
        return temp

    chain_with_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="current_preferences",  # 绑定当前偏好为输入键
        history_messages_key="history_prompt"  # 绑定历史消息为历史键
    )

    # 9. 调用模型获取排序结果
    try:
        result = chain_with_history.invoke(
            input={
                "products": products_str,
                "history_prompt": history_prompt,
                "current_preferences": current_preferences,
                "top_n": top_n
            },
            config={"configurable": {"session_id": session_id}}
        )
    except Exception as e:
        raise RuntimeError(f"排序失败：{str(e)}")

    # 10. 保存本轮对话到历史（便于后续调整）
    user_msg = f"请求排序（前{top_n}名），偏好：{user_preferences or '无'}"
    ai_msg = f"排序规则：{result.sorting_rules}（输出{len(result.sorted_products)}件）"
    redis_history.add_user_message(user_msg)
    redis_history.add_ai_message(ai_msg)

    return result.sorted_products


# ------------------------------
# 测试用例（覆盖所有新功能）
# ------------------------------
if __name__ == "__main__":
    # 测试数据：更多商品（超过5个，测试top_n功能）
    test_products = [
        {"name": "无线耳机", "price": 299, "rating": 4.5, "sales": 1200},
        {"name": "蓝牙音箱", "price": 199, "rating": 4.2, "sales": 800},
        {"name": "智能手表", "price": 599, "rating": 4.7, "sales": 1500},
        {"name": "手机支架", "price": 39, "rating": 4.0, "sales": 3000},
        {"name": "充电宝", "price": 89, "rating": 4.3, "sales": 2500},
        {"name": "蓝牙耳机", "price": 159, "rating": 4.4, "sales": 1800}  # 第6个商品
    ]

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
    print("\n=== 测试3：追加偏好（销量高且价格低于200） ===")
    sorted3 = ai_sort_products("test_user", test_products, user_preferences="销量高且价格低于200", top_n=3)
    for i, p in enumerate(sorted3, 1):
        print(f"{i}. {p.name} - 价格：{p.price}，销量：{p.sales}")