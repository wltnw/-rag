from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import os

# 配置
API_KEY = "c1bb1a9460264bb4b3b0bfb16ca0fbd3.3jgWNTiHspW7ceqd"
os.environ["OPENAI_API_KEY"] = API_KEY
os.environ["OPENAI_API_BASE"] = "https://open.bigmodel.cn/api/paas/v4/"

# 读取文件
with open("knowledge.txt", "r", encoding="utf-8") as f:
    text = f.read()

# 分割文本
text_splitter = CharacterTextSplitter(
    separator="\n",
    chunk_size=150,
    chunk_overlap=30
)
chunks = text_splitter.split_text(text)

# 创建向量数据库
embeddings = OpenAIEmbeddings(model="embedding-2")
db = Chroma.from_texts(
    texts=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"
)

print(f"数据库初始化完成！共存入 {len(chunks)} 个文本块")