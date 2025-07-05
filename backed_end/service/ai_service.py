from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from langchain_core.runnables import RunnableWithMessageHistory, RunnablePassthrough
from langchain_openai import ChatOpenAI
import os
session_id= "arknights_session"
def gethistory(session_id:str) -> RedisChatMessageHistory:
    RedisUrl = "redis://localhost:6379/0"
    return RedisChatMessageHistory(session_id,url=RedisUrl,ttl=60*10)
def trimming(input_data: dict) -> list:
    """从 Redis 历史记录中提取最近两条消息"""
    # 获取完整的 Redis 历史记录
    history = gethistory(session_id)
    messages = history.messages

    # 只取最后两条消息
    if len(messages) >= 5:
        return messages[-5:]  # 返回最后两条消息
    elif len(messages) > 0:
        return messages  # 如果不足两条但至少有一条，返回所有
    else:
        return []  # 如果没有消息，返回空列表


def aiResponse(question: str) -> str:
    """
    This function is a placeholder for AI response generation.
    It currently returns a static response.
    """
    llm = ChatOpenAI(
        api_key=os.getenv("OPEN_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model="deepseek-r1",
        temperature=0.5
    )
    session_id = "arknights_session"
    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{text}")

    ])
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    history = gethistory(session_id)
    with_massage_history = RunnableWithMessageHistory(
        chain,
        gethistory,
        input_messages_key="text",
        history_messages_key="history"
    )
    # 同步调用获取完整结果

    chat_with_trimming = RunnablePassthrough.assign(history=lambda x: trimming(x)) | with_massage_history
    result = chat_with_trimming.invoke({"text": question.question}, config={"configurable": {"session_id": session_id}})
    return result