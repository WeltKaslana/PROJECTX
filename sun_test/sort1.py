from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_redis import RedisChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory 
import os
from dotenv import load_dotenv
import mysql.connector  # 导入MySQL驱动
from mysql.connector import Error  # 用于捕获数据库错误

# 加载环境变量
load_dotenv()
key = os.getenv("SILICONFLOW_API_KEY")
base = os.getenv("SILICONFLOW_API_BASE")

# 初始化DeepSeek模型
llm = ChatDeepSeek(
    model='deepseek-ai/DeepSeek-R1',
    temperature=0.3,
    api_key=key,
    api_base=base,
    timeout=180,
)

# 完整商品数据模型
class Product(BaseModel):
    name: str = Field(..., description="商品名称")
    price: float = Field(..., description="商品价格")
    deals: int = Field(..., description="销量")
    img_url: str = Field(..., description="商品图片URL")
    goods_url: str = Field(..., description="商品详情页URL")
    shop_url: str = Field(..., description="店铺URL")

class SortedProducts(BaseModel):
    sorted_products: List[Product] = Field(..., description="排序后的完整商品列表")
    sorting_rules: str = Field(..., description="排序规则说明")
    output_count: int = Field(..., description="实际输出数量")

class metamessage:
    def __init__(self, mestype:type, contents):
        self.type = mestype
        self.content = contents

def ai_get_history(session_id: str):
    history = RedisChatMessageHistory(
        redis_url="redis://47.98.143.59:6379",
        session_id=session_id,
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
    """修复消息添加逻辑的内存历史"""
    messages: List[BaseMessage] = Field(default_factory=list)
    
    def add_messages(self, messages: List[BaseMessage]) -> None:
        """修复：正确处理验证后的消息，确保添加到列表"""
        validated_messages = []
        for msg in messages:
            if not isinstance(msg, BaseMessage):
                if isinstance(msg, str):
                    msg = HumanMessage(content=msg)
                else:
                    raise ValueError(f"不支持的消息类型: {type(msg)}")
            validated_messages.append(msg)  # 之前漏了这行，导致消息未被添加
        self.messages.extend(validated_messages)

    def clear(self) -> None:
        self.messages = []

def ai_sort_products(
    session_id: str,
    question: str,
    key: str,
    products: List[dict],
    user_preferences: Optional[str] = None,
) -> List[Product]:
    """
    完整商品信息排序函数
    
    :param products: 包含完整商品信息的字典列表
    :return: 包含所有原始字段的Product对象列表
    """
    
    #  原始数据
    # products = find_goods(session_id, key)
    
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
    - 输出数据要完整全面

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
    
    return final_products


def ai_delete_history(session_id:str):
    history = RedisChatMessageHistory(
        redis_url = "redis://47.98.143.59:6379",# Redis 连接URL
        session_id = session_id, # 会话ID
    )
    history.clear()  # 清除聊天历史

# 使用示例
if __name__ == "__main__":
    test_product = {
        'name': '【政府补贴15%】HONOR/荣耀200 5G手机 5200mAh青海湖电池5000万三主摄写真相机荣耀绿洲 护眼屏官方旗舰店100 5G 手机',
        'price': 1410.15,
        'deals': 70000,
        'img_url': 'https://g-search3.alicdn.com/img/bao/uploaded/i4/i4/1114511827/O1CN01pYspum1PMog8RZ6Ze_!!4611686018427386323-0-item_pic.jpg_580x580q90.jpg_.webp',
        'goods_url': '//detail.tmall.com/item.htm?priceTId=2147818d17521394102321658e1c75&utparam=%7B%22aplus_abtest%22%3A%2256498aa96c581f213f393002730bc35f%22%7D&id=789770187657&ns=1&abbucket=20&xxc=taobaoSearch&detail_redpacket_pop=true&query=%E6%89%8B%E6%9C%BA%205G&mi_id=MgoS6nP-gUWyQU8KRHWWoIOTsMQOKTczL27npuUTMCI_TYgNAvxxu0-4L-m6dG-ty-myroJvH9haNbjdX5Oy0jj7hogeQmFLiUV09xFRj-s&skuId=5890259858259&spm=a21n57.1.item.49',
        'shop_url': '//store.taobao.com/shop/view_shop.htm?appUid=RAzN8HWJa6UWaRALcQM7yQ91BruC69N5os3Q6hgqbEP6bxEp16h&spm=a21n57.1.item.49' 
    }
    
    # 模拟多个商品
    test_products = [test_product, 
                    {**test_product, 'name': 'iPhone 15', 'price': 5999, 'deals': 50000},
                    {**test_product, 'name': '小米14', 'price': 3999, 'deals': 80000}]
    
    ai_delete_history("test_session")
    # print("history:\n",ai_get_history("test_session"))  # 打印当前历史消息
    # 执行排序
    sorted_results = ai_sort_products(
        session_id="test_session", 
        question="请帮我推荐几款性价比高的手机",
        key="手机 5G",
        products=test_products)
    
    # 打印完整结果
    # for i, product in enumerate(sorted_results, 1):
    #     print(f"\n=== 第{i}名 ===")
    #     print(f"名称: {product.name}")
    #     print(f"价格: {product.price}")
    #     print(f"销量: {product.deals}")
    #     print(f"图片: {product.img_url}")
    #     print(f"商品链接: {product.goods_url}")
    #     print(f"店铺链接: {product.shop_url}")
    
    print("历史消息：") # 显示当前历史消息
    for i in ai_get_history("test_session"):
        print("说话对象：", i.type,"交流内容：" , i.content) # 打印每条消息的类型和内容

