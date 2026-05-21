"""
测试配置文件 - 提供测试fixtures和通用工具
"""
import pytest
import requests
import time
from typing import Dict, Any

# 测试配置
API_BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 10  # 秒

@pytest.fixture(scope="session")
def api_base_url():
    """API基础URL"""
    return API_BASE_URL

@pytest.fixture(scope="session")
def api_client():
    """API客户端会话"""
    session = requests.Session()
    # 禁用代理，避免502错误
    session.trust_env = False
    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json"
    })
    yield session
    session.close()

@pytest.fixture(scope="session")
def wait_for_api():
    """等待API服务启动"""
    max_retries = 30
    retry_interval = 1
    
    for i in range(max_retries):
        try:
            # 禁用代理，避免502错误
            response = requests.get(f"{API_BASE_URL}/health", timeout=5, proxies={})
            if response.status_code == 200:
                print(f"✅ API服务已就绪 (尝试 {i+1}/{max_retries})")
                return True
        except requests.exceptions.ConnectionError:
            print(f"⏳ 等待API服务启动... (尝试 {i+1}/{max_retries})")
            time.sleep(retry_interval)
    
    pytest.skip("API服务未启动，跳过测试")

@pytest.fixture
def sample_questions():
    """示例问题集"""
    return [
        "水泵需要多久维护一次？",
        "大棚里温度多少度的时候需要启动风扇？",
        "那个温湿度传感器的电源电压范围是多少？",
        "DHT22 传感器的温度测量精度是多少？",
        "ERR_002 是什么故障？应该怎么处理？",
        "DHT22 和 SHT31 这两个传感器成本差多少？"
    ]

@pytest.fixture
def emergency_questions():
    """紧急情况问题集"""
    return [
        "水泵突然停止工作了怎么办？",
        "传感器显示异常数据",
        "大棚温度过高报警",
        "设备出现故障代码ERR_001"
    ]

@pytest.fixture
def boundary_questions():
    """边界条件问题集"""
    return [
        "",  # 空问题
        "a" * 1000,  # 超长问题
        "   ",  # 空白问题
        "!@#$%^&*()",  # 特殊字符
        "1234567890",  # 纯数字
    ]

class APITestHelper:
    """API测试辅助类"""
    
    @staticmethod
    def ask_question(client: requests.Session, question: str, timeout: int = TEST_TIMEOUT) -> Dict[str, Any]:
        """提问并返回响应"""
        response = client.post(
            f"{API_BASE_URL}/ask",
            json={"question": question},
            timeout=timeout
        )
        return {
            "status_code": response.status_code,
            "response_time": response.elapsed.total_seconds(),
            "data": response.json() if response.status_code == 200 else None,
            "raw_text": response.text
        }
    
    @staticmethod
    def check_health(client: requests.Session) -> bool:
        """检查API健康状态"""
        try:
            response = client.get(f"{API_BASE_URL}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    @staticmethod
    def validate_response_structure(data: Dict[str, Any]) -> bool:
        """验证响应结构"""
        required_fields = ["answer", "intent", "action", "source", "timestamp"]
        return all(field in data for field in required_fields)
    
    @staticmethod
    def validate_intent(intent: str) -> bool:
        """验证意图值是否有效"""
        valid_intents = ["INFO", "EMERGENCY", "ACTION_REQUIRED"]
        return intent in valid_intents

@pytest.fixture
def api_helper():
    """API测试辅助工具"""
    return APITestHelper()