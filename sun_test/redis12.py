 # 使⽤Redis 构建⻓期记忆
from langchain_redis import RedisChatMessageHistory
# from langchain_core.runnables.history import RunnableWithMessageHistory
# from langchain_core.chat_history import BaseChatMessageHistory
# from langchain_core.messages import AIMessage, HumanMessage
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_deepseek import ChatDeepSeek
# import os
 
 # 初始化Redis 聊天消息历史记录
history= RedisChatMessageHistory(
 redis_url= "redis://47.98.143.59:6379",# Redis 连接URL
 session_id="user_1", # 会话ID
)
history.clear() # 清空历史记录,
# # 向历史记录中添加消息
history.add_user_message("你好，AI助⼿")
history.add_ai_message("你好！我今天能为你提供什么帮助呢？") # 添加AI助⼿的回复
# 检索并显示历史消息
print("历史消息：") # 显示当前历史消息
for message in history.messages:
 # 打印每条消息的类型和内容
    print(f"{type(message)}: {message.content}")