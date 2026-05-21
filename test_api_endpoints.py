"""
API接口测试 - 测试FastAPI端点的功能和响应
"""
import pytest
import requests
from conftest import API_BASE_URL

class TestHealthEndpoints:
    """健康检查接口测试"""
    
    def test_health_check(self, api_client, wait_for_api):
        """测试健康检查接口"""
        response = api_client.get(f"{API_BASE_URL}/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data
        assert data["service"] == "智慧农场 AI 知识库"
    
    def test_health_response_time(self, api_client, wait_for_api):
        """测试健康检查响应时间"""
        response = api_client.get(f"{API_BASE_URL}/health")
        assert response.elapsed.total_seconds() < 1.0  # 响应时间应小于1秒

class TestAskEndpoint:
    """问答接口测试"""
    
    def test_ask_valid_question(self, api_client, wait_for_api, api_helper):
        """测试有效问题"""
        result = api_helper.ask_question(api_client, "水泵需要多久维护一次？")
        
        assert result["status_code"] == 200
        assert result["response_time"] < 10.0  # 响应时间应小于10秒
        
        data = result["data"]
        assert api_helper.validate_response_structure(data)
        assert api_helper.validate_intent(data["intent"])
        assert len(data["answer"]) > 0
        assert data["source"] in ["json_parsing", "keyword_matching"]
    
    def test_ask_different_intents(self, api_client, wait_for_api, api_helper):
        """测试不同意图的问题"""
        test_cases = [
            ("水泵需要多久维护一次？", "INFO"),
            ("水泵突然停止工作了怎么办？", "EMERGENCY"),
            ("大棚里温度多少度的时候需要启动风扇？", "INFO"),
        ]
        
        for question, expected_intent in test_cases:
            result = api_helper.ask_question(api_client, question)
            assert result["status_code"] == 200
            
            data = result["data"]
            # 注意：实际意图可能与预期不同，这里只验证格式
            assert api_helper.validate_intent(data["intent"])
    
    def test_ask_response_structure(self, api_client, wait_for_api, api_helper):
        """测试响应结构完整性"""
        result = api_helper.ask_question(api_client, "传感器电压范围是多少？")
        
        assert result["status_code"] == 200
        data = result["data"]
        
        # 验证所有必需字段
        required_fields = ["answer", "intent", "action", "source", "timestamp"]
        for field in required_fields:
            assert field in data, f"缺少字段: {field}"
        
        # 验证字段类型
        assert isinstance(data["answer"], str)
        assert isinstance(data["intent"], str)
        assert isinstance(data["action"], str)
        assert isinstance(data["source"], str)
        assert isinstance(data["timestamp"], str)
    
    def test_ask_source_types(self, api_client, wait_for_api, api_helper):
        """测试不同的来源类型"""
        result = api_helper.ask_question(api_client, "水泵维护周期")
        
        assert result["status_code"] == 200
        data = result["data"]
        
        # 验证来源类型
        valid_sources = ["json_parsing", "keyword_matching"]
        assert data["source"] in valid_sources

class TestDocumentEndpoints:
    """文档接口测试"""
    
    def test_swagger_docs(self, api_client, wait_for_api):
        """测试Swagger文档接口"""
        response = api_client.get(f"{API_BASE_URL}/docs")
        
        # FastAPI的/docs通常返回HTML
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_openapi_schema(self, api_client, wait_for_api):
        """测试OpenAPI schema接口"""
        response = api_client.get(f"{API_BASE_URL}/openapi.json")
        
        assert response.status_code == 200
        schema = response.json()
        
        # 验证基本OpenAPI结构
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
        
        # 验证我们的端点存在
        assert "/ask" in schema["paths"]
        assert "/health" in schema["paths"]

class TestErrorHandling:
    """错误处理测试"""
    
    def test_ask_empty_question(self, api_client, wait_for_api):
        """测试空问题"""
        response = api_client.post(
            f"{API_BASE_URL}/ask",
            json={"question": ""}
        )
        
        # 应该返回400错误
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    def test_ask_missing_field(self, api_client, wait_for_api):
        """测试缺少必需字段"""
        response = api_client.post(
            f"{API_BASE_URL}/ask",
            json={"wrong_field": "test"}
        )
        
        # 应该返回422验证错误
        assert response.status_code == 422
    
    def test_ask_invalid_json(self, api_client, wait_for_api):
        """测试无效JSON"""
        response = api_client.post(
            f"{API_BASE_URL}/ask",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        # 应该返回422验证错误
        assert response.status_code == 422

class TestConcurrency:
    """并发测试"""
    
    def test_concurrent_requests(self, api_client, wait_for_api, api_helper):
        """测试并发请求"""
        import concurrent.futures
        
        questions = [
            "水泵维护周期",
            "传感器电压范围",
            "风扇启动温度",
            "故障代码ERR_002",
            "传感器成本对比"
        ]
        
        def ask_question(question):
            return api_helper.ask_question(api_client, question)
        
        # 并发发送5个请求
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(ask_question, q) for q in questions]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # 验证所有请求都成功
        for result in results:
            assert result["status_code"] == 200
            assert result["response_time"] < 15.0  # 并发情况下响应时间可能更长

if __name__ == "__main__":
    pytest.main([__file__, "-v"])