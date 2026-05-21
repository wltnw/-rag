"""
改进版本的智慧农场 RAG API（折衷方案 C：JSON Mode + 关键词降级）

关键改进：
1. AI 返回结构化 JSON（包含答案、意图、建议动作）
2. 客户端解析失败时自动降级到关键词匹配
3. 完整的异常处理和日志记录
4. 与 Java 后端完美兼容
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
import os
import json
import re
import logging
from datetime import datetime

# ================= 日志配置 =================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ================= 环境变量配置 =================
# 智谱大模型API配置（临时）
API_KEY = os.getenv("OPENAI_API_KEY", "c1bb1a9460264bb4b3b0bfb16ca0fbd3.3jgWNTiHspW7ceqd")
API_BASE = os.getenv("OPENAI_API_BASE", "https://open.bigmodel.cn/api/paas/v4/")

os.environ["OPENAI_API_KEY"] = API_KEY
os.environ["OPENAI_API_BASE"] = API_BASE

# ================= 全局变量 =================
vectorstore = None
retriever = None
rag_chain = None

# ================= 数据模型定义 =================
class AskRequest(BaseModel):
    """用户提问请求"""
    question: str

class AskResponse(BaseModel):
    """API 返回的标准响应"""
    answer: str
    intent: str  # INFO, EMERGENCY, ACTION_REQUIRED
    action: str  # 建议的操作，或 NONE
    source: str  # json_parsing 或 keyword_matching
    timestamp: str

# ================= 意图识别器（折衷方案 C）=================
def parse_ai_response(response_text):
    """
    【核心创新】：智能解析 AI 响应
    
    优先级 1：尝试解析 JSON（JSON Mode）
    优先级 2：关键词匹配（容错降级）
    
    这样既充分利用 LLM 的推理能力，也确保系统稳定性
    """
    
    logger.info(f"开始解析 AI 响应，长度：{len(response_text)}")
    
    # ===== 优先级 1：尝试 JSON 解析 =====
    try:
        # 查找 JSON 片段（可能被 ``` 包围）
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            result = json.loads(json_str)
            
            # 验证必需字段
            if "answer" in result:
                logger.info("✅ 成功解析 JSON，来源：JSON Mode")
                return {
                    "answer": result.get("answer", ""),
                    "intent": result.get("intent", "INFO"),
                    "action": result.get("action", "NONE"),
                    "source": "json_parsing"
                }
    except json.JSONDecodeError as e:
        logger.warning(f"⚠️ JSON 解析失败：{e}，准备启动降级方案")
    except Exception as e:
        logger.warning(f"⚠️ 意外错误：{e}，准备启动降级方案")
    
    # ===== 优先级 2：关键词匹配（容错降级）=====
    logger.info("启动关键词匹配降级方案...")
    
    # 识别紧急情况的关键词
    emergency_keywords = ["故障", "崩溃", "异常", "断电", "停止", "失败", "错误"]
    action_keywords = {
        "TURN_ON_FAN": ["打开", "启动", "开启", "风扇", "降温"],
        "STOP_PUMP": ["关闭", "停止", "停", "泵"],
        "CHECK_SENSOR": ["检查", "校准", "传感器"]
    }
    
    # 判断紧急程度
    if any(kw in response_text for kw in emergency_keywords):
        intent = "EMERGENCY"
        logger.warning("检测到紧急意图")
    else:
        intent = "INFO"
    
    # 判断推荐动作
    action = "NONE"
    for action_name, keywords in action_keywords.items():
        if any(kw in response_text for kw in keywords):
            action = action_name
            logger.info(f"检测到动作：{action}")
            break
    
    logger.info(f"✅ 降级方案返回：intent={intent}, action={action}")
    
    return {
        "answer": response_text,
        "intent": intent,
        "action": action,
        "source": "keyword_matching"
    }

# ================= FastAPI 应用 =================
app = FastAPI(
    title="智慧农场 AI 知识库 API",
    description="基于 RAG + Agent 意图识别的农业决策系统",
    version="2.0"
)

# ================= 启动事件：初始化知识库 =================
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化向量数据库和 LLM"""
    global vectorstore, retriever, rag_chain
    
    try:
        logger.info("=" * 50)
        logger.info("🚀 智慧农场大脑启动中...")
        logger.info("=" * 50)
        
        # 加载已有的向量数据库
        logger.info("📚 加载向量数据库...")
        embeddings = OpenAIEmbeddings(model="embedding-2")
        vectorstore = Chroma(
            persist_directory="./chroma_db",
            embedding_function=embeddings
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
        logger.info("✅ 向量数据库加载完成")
        
        # 初始化大模型
        logger.info("🤖 初始化大语言模型...")
        llm = ChatOpenAI(model="glm-4-flash", temperature=0.1)
        
        # ===== 核心改进：新的 Prompt 模板 =====
        # 加入 JSON 输出指令，让 AI 返回结构化数据
        prompt_template = ChatPromptTemplate.from_template("""
你是一个资深的【智慧农场技术专家】和【智能控制决策器】。

你的职责：
1. 严格根据【农场操作手册】回答用户问题
2. 判断用户的意图（普通咨询、紧急问题、还是需要控制设备）
3. 如果是紧急情况，建议相应的控制动作

【农场操作手册】：
{context}

用户问题：{question}

【输出格式要求】：
你必须输出一个有效的 JSON 对象，包含以下三个字段，不能有任何多余的解释文字：
{{
    "answer": "你的专业解答（基于手册内容）",
    "intent": "INFO | EMERGENCY | ACTION_REQUIRED 之一",
    "action": "如需控制设备，输入动作名称（如 TURN_ON_FAN），否则输入 NONE"
}}

【意图定义】：
- INFO: 用户只是普通咨询
- EMERGENCY: 用户报告了故障或异常
- ACTION_REQUIRED: 系统判断需要立即控制设备

【重要】：
- 如果手册中没有相关信息，在 "answer" 字段中说明
- 绝对禁止编造信息
- 输出必须是合法的 JSON 格式
""")
        
        rag_chain = prompt_template | llm
        logger.info("✅ 大语言模型初始化完成")
        
        logger.info("=" * 50)
        logger.info("✅ 智慧农场大脑已就绪！")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"❌ 启动失败：{e}")
        raise

# ================= 健康检查端点 =================
@app.get("/health")
async def health_check():
    """健康检查，用于确认 API 是否运行"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "智慧农场 AI 知识库"
    }

# ================= 核心端点：提问 =================
@app.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """
    用户提问接口
    
    请求示例：
    {
      "question": "温度太高了怎么办？"
    }
    
    返回示例：
    {
      "answer": "建议打开风扇...",
      "intent": "ACTION_REQUIRED",
      "action": "TURN_ON_FAN",
      "source": "json_parsing",
      "timestamp": "2026-04-27T10:30:00"
    }
    """
    
    try:
        logger.info(f"📥 收到提问：{request.question}")
        
        # 输入验证
        if not request.question or len(request.question.strip()) == 0:
            logger.warning("❌ 提问为空")
            raise HTTPException(status_code=400, detail="问题不能为空")
        
        # 第 1 步：从向量库检索相关文档
        logger.info("🔍 正在从知识库检索...")
        docs = retriever.invoke(request.question)
        context_text = "\n\n".join([doc.page_content for doc in docs])
        logger.info(f"✅ 检索到 {len(docs)} 个相关文档段落")
        
        # 第 2 步：调用 LLM 生成回答
        logger.info("🤖 正在调用大模型...")
        response = rag_chain.invoke({
            "context": context_text,
            "question": request.question
        })
        logger.info("✅ LLM 返回结果")
        
        # 第 3 步：解析 AI 响应（核心创新点）
        logger.info("🔍 解析 AI 响应...")
        parsed_result = parse_ai_response(response.content)
        
        logger.info(f"✅ 解析完成 - 意图：{parsed_result['intent']}, 来源：{parsed_result['source']}")
        
        # 返回结构化响应
        return AskResponse(
            answer=parsed_result["answer"],
            intent=parsed_result["intent"],
            action=parsed_result["action"],
            source=parsed_result["source"],
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 处理请求失败：{e}")
        raise HTTPException(status_code=500, detail="处理请求失败")

# ================= 调试端点：获取 API 文档 =================
@app.get("/docs")
async def get_docs():
    """FastAPI 会自动生成 Swagger 交互式文档"""
    pass

# ================= 主程序 =================
if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 启动 FastAPI 服务器...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
