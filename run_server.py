#!/usr/bin/env python
"""直接启动 FastAPI 服务器"""
import os
import sys

# 设置路径
os.chdir(r'C:\Users\23284\python\111')

try:
    import rag_api_improved
    import uvicorn
    
    print("✅ 模块导入成功")
    print(f"   app: {rag_api_improved.app}")
    
    print("\n🚀 启动 FastAPI 服务器...")
    uvicorn.run(
        rag_api_improved.app,
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )
except Exception as e:
    print(f"❌ 启动失败：{e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
