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
    
    # 执行排序
    sorted_results = ai_sort_products("test_session", test_products, "性价比优先", 2)
    
    # 打印完整结果
    for i, product in enumerate(sorted_results, 1):
        print(f"\n=== 第{i}名 ===")
        print(f"名称: {product.name}")
        print(f"价格: {product.price}")
        print(f"销量: {product.deals}")
        print(f"图片: {product.img_url}")
        print(f"商品链接: {product.goods_url}")
        print(f"店铺链接: {product.shop_url}")
        # 如需访问原始数据:
        # print("原始数据:", product.raw_data)

# def get_db_connection():
#     """建立数据库连接"""
#     try:
#         connection = mysql.connector.connect(
#             host='你的数据库主机地址',  # 如：localhost 或 127.0.0.1
#             database='你的数据库名称',  # 存储商品信息的数据库
#             user='你的数据库用户名',    # 如：root
#             password='你的数据库密码'   # 数据库密码
#         )
#         if connection.is_connected():
#             return connection
#     except Error as e:
#         raise RuntimeError(f"数据库连接失败：{str(e)}")

# def fetch_products_from_db(query: str = None) -> List[dict]:
#     """
#     从数据库查询商品信息并转换为程序所需格式
    
#     :param query: 自定义查询SQL（可选，默认查询所有商品）
#     :return: 符合要求的商品字典列表（包含name/price/deals等字段）
#     """
#     # 1. 定义默认查询SQL（根据你的表结构调整字段和表名）
#     if not query:
#         query = """
#         SELECT 
#             product_name AS name,  # 商品名称（映射到程序的name字段）
#             price,                 # 商品价格（映射到price）
#             sales AS deals,        # 销量（映射到deals）
#             image_url AS img_url,  # 商品图片URL（映射到img_url）
#             product_url AS goods_url,  # 商品详情页URL（映射到goods_url）
#             shop_url               # 店铺URL（映射到shop_url）
#         FROM 
#             products  # 你的商品表名（需替换为实际表名）
#         """  # 可根据需要添加WHERE条件（如筛选在售商品）

#     # 2. 连接数据库并执行查询
#     connection = None
#     products = []
#     try:
#         connection = get_db_connection()
#         cursor = connection.cursor(dictionary=True)  # 以字典形式返回结果
#         cursor.execute(query)
#         records = cursor.fetchall()  # 获取所有查询结果

#         # 3. 转换查询结果为程序所需格式（确保字段匹配）
#         for record in records:
#             # 检查必要字段是否存在（与程序中的required_fields对应）
#             product = {
#                 "name": record.get("name"),
#                 "price": float(record.get("price")),  # 确保为float类型
#                 "deals": int(record.get("deals")),    # 确保为int类型
#                 "img_url": record.get("img_url"),
#                 "goods_url": record.get("goods_url"),
#                 "shop_url": record.get("shop_url")
#             }
#             products.append(product)

#         return products

#     except Error as e:
#         raise RuntimeError(f"数据库查询失败：{str(e)}")
#     finally:
#         # 4. 关闭连接（避免资源泄露）
#         if connection and connection.is_connected():
#             cursor.close()
#             connection.close()

# if __name__ == "__main__":
#     # 从数据库读取商品信息（可自定义查询条件）
#     try:
#         # 示例：查询价格低于2000的商品（自定义SQL）
#         custom_query = """
#         SELECT 
#             product_name AS name,
#             price,
#             sales AS deals,
#             image_url AS img_url,
#             product_url AS goods_url,
#             shop_url
#         FROM 
#             products 
#         WHERE 
#             price < 2000  # 筛选条件：价格低于2000
#         """
#         # 调用函数从数据库获取商品数据
#         test_products = fetch_products_from_db(query=custom_query)
#         print(f"成功从数据库读取 {len(test_products)} 条商品信息")
#     except Exception as e:
#         print(f"读取商品数据失败：{str(e)}")
#         exit(1)

#     # 执行排序（使用数据库读取的商品数据）
#     sorted_results = ai_sort_products(
#         session_id="test_session",
#         products=test_products,  # 传入数据库数据
#         user_preferences="性价比优先",
#         top_n=2
#     )

#     # 打印排序结果（同之前逻辑）
#     for i, product in enumerate(sorted_results, 1):
#         print(f"\n=== 第{i}名 ===")
#         print(f"名称: {product.name}")
#         print(f"价格: {product.price}")
#         print(f"销量: {product.deals}")
#         print(f"图片: {product.img_url}")
#         print(f"商品链接: {product.goods_url}")
#         print(f"店铺链接: {product.shop_url}")