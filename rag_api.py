from fastapi import FastAPI
from pydantic import BaseModel
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
import os

# ================= 1. 全局配置 =================
# 务必填入你真实、安全的英文字母 API Key
API_KEY = "c1bb1a9460264bb4b3b0bfb16ca0fbd3.3jgWNTiHspW7ceqd"  
os.environ["OPENAI_API_KEY"] = API_KEY
os.environ["OPENAI_API_BASE"] = "https://open.bigmodel.cn/api/paas/v4/"

# ================= 2. 唤醒“农场大脑” =================
print("⏳ 正在加载智慧农场知识库...")

# 直接加载我们之前建好的 farm_db
embeddings = OpenAIEmbeddings(model="embedding-2")
vectorstore = Chroma(persist_directory="./farm_db", embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

# 初始化大模型
llm = ChatOpenAI(model="glm-4-flash", temperature=0.1)

# 设定严谨的技术专家提示词
prompt_template = ChatPromptTemplate.from_template("""
你是一个资深的【智慧农场技术专家】。请严格根据下面的【农场操作手册】来回答问题。
如果资料中没有答案，请直接回复：“抱歉，操作手册中未查找到相关信息”，禁止编造。

【农场操作手册】：
{context}

管理员提问：{question}
""")

rag_chain = prompt_template | llm

# ================= 3. 组装 FastAPI 接口 =================
app = FastAPI()

# 定义请求格式
class AskRequest(BaseModel):
    question: str

@app.post("/api/ask")
async def ask_farm_bot(request: AskRequest):
    # 1. 检索：去数据库找相关的手册片段
    docs = retriever.invoke(request.question)
    context_text = "\n\n".join([doc.page_content for doc in docs])
    
    # 2. 生成：让大模型结合资料给出答案
    response = rag_chain.invoke({
        "context": context_text,
        "question": request.question
    })
    
    # 3. 返回：把答案发给前端（或者你的 Java 系统）
    return {
        "question": request.question,
        "answer": response.content,
        "source_found": len(docs) > 0
    }

print("✅ 农场 AI 服务已就绪！")