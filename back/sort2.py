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
import concurrent.futures
import time
from dao import userDAO

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
    # 其他原始字段保留
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="原始数据")

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
    top_n: int = 5
) -> List[Product]:
    """
    完整商品信息排序函数
    
    :param products: 包含完整商品信息的字典列表
    :return: 包含所有原始字段的Product对象列表
    """
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
    2. 仅输出前{top_n}名商品
    3. 清晰说明排序规则（尤其是用户偏好的体现）

    商品列表：
    {products}
    
    {history_prompt}  # 多轮对话时引入历史偏好
    {current_preferences}  # 当前轮次的用户偏好

    
    排序参考维度（需综合或侧重）：
    1. 性价比（评分/价格比值）
    2. 用户明确偏好（如指定则优先满足）
    3. 必须保留所有原始字段
    4. 销量（越高越优，反映大众认可度）

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
        current_preferences = "当前无特殊偏好，默认按「销量*0.6 + 性价比*0.4」综合排序"

    # 格式化商品信息（简略显示）
    products_str = "\n".join([
        f"{i+1}. {p['name']} | 价格：{p['price']} | 销量：{p['deals']}"
        for i, p in enumerate(products)
    ])
    
    # 构建处理链
    parser = PydanticOutputParser(pydantic_object=SortedProducts)
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["products", "history_prompt", "current_preferences", "top_n"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

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

    # 调用模型
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
                raw_data=original  # 保留所有原始数据
            ))
    
    return final_products[:top_n]
def parallel_sort_goods(
    session_id: str,
    goods_list: List[Dict[str, Any]],
    user_preferences: Optional[str] = None,
    top_n: int = 5,
    max_workers: int = 5
) -> List[List[Dict[str, Any]]]:
    """
    对多个商品列表进行并行排序
    
    :param session_id: 会话ID
    :param goods_list: 商品字典列表的列表，每个子列表代表一组要排序的商品
    :param user_preferences: 用户偏好，用于AI排序
    :param top_n: 每组返回的商品数量
    :param max_workers: 最大并行线程数
    :return: 排序后的商品列表的列表
    """
    # 验证输入
    if not isinstance(goods_list, list) or not all(isinstance(g, list) for g in goods_list):
        raise ValueError("goods_list必须是商品字典列表的列表")
    
    results = []
    
    # 使用线程池实现并行排序
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有排序任务
        future_to_index = {
            executor.submit(
                ai_sort_products, 
                f"{session_id}_{i}",  # 使用不同的session_id避免冲突
                goods, 
                user_preferences, 
                top_n
            ): i 
            for i, goods in enumerate(goods_list)
        }
        
        # 收集结果
        for future in concurrent.futures.as_completed(future_to_index):
            index = future_to_index[future]
            try:
                # 获取排序结果并转换为字典列表
                sorted_products = future.result()
                sorted_goods = [p.dict() for p in sorted_products]
                results.append((index, sorted_goods))
            except Exception as e:
                print(f"Error sorting group {index}: {str(e)}")
                results.append((index, []))  # 出错时返回空列表
    
    # 按原始顺序排序结果
    results.sort(key=lambda x: x[0])
    return [r[1] for r in results]

# 使用示例
if __name__ == "__main__":
    session_id = "user_123"  # 示例会话ID
    keyword = "手机"         # 示例搜索关键词
    user_dao = userDAO()
    result = user_dao.find_goods(session_id, keyword)  # 调用函数
    # # 模拟多个商品组
    # test_product = {
    #     'name': '【政府补贴15%】HONOR/荣耀200 5G手机',
    #     'price': 1410.15,
    #     'deals': 70000,
    #     'img_url': 'https://example.com/image.jpg',
    #     'goods_url': 'https://example.com/product',
    #     'shop_url': 'https://example.com/store'
    # }
    
    # # 创建3个商品组，每个组有不同的商品
    # goods_groups = [
    #     [test_product, 
    #      {**test_product, 'name': 'iPhone 15', 'price': 5999, 'deals': 50000},
    #      {**test_product, 'name': '小米14', 'price': 3999, 'deals': 80000}],
        
    #     [test_product, 
    #      {**test_product, 'name': '三星Galaxy S23', 'price': 4999, 'deals': 60000},
    #      {**test_product, 'name': '华为Mate 60', 'price': 5499, 'deals': 75000}],
        
    #     [test_product, 
    #      {**test_product, 'name': 'OPPO Find X7', 'price': 4499, 'deals': 45000},
    #      {**test_product, 'name': 'vivo X100', 'price': 3999, 'deals': 55000}]
    # ]
    
    # 并行排序所有商品组
    start_time = time.time()
    sorted_groups = parallel_sort_goods("test_session", result, "性价比优先", 2, max_workers=3)
    end_time = time.time()
    
    print(f"并行排序耗时: {end_time - start_time:.2f}秒")
    
    # 打印每个商品组的排序结果
    for i, sorted_goods in enumerate(sorted_groups):
        print(f"\n=== 商品组 {i+1} 的排序结果 ===")
        for j, product in enumerate(sorted_goods, 1):
            print(f"\n  === 第{j}名 ===")
            print(f"  名称: {product['name']}")
            print(f"  价格: {product['price']}")
            print(f"  销量: {product['deals']}")