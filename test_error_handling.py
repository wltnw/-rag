"""
异常和边界测试 - 测试系统的异常处理能力和边界条件
"""
import pytest
import requests
from conftest import API_BASE_URL

class TestInputValidation:
    """输入验证测试"""
    
    def test_empty_question(self, api_client, wait_for_api):
        """测试空问题"""
        response = api_client.post(
            f"{API_BASE_URL}/ask",
            json={"question": ""}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    def test_whitespace_question(self, api_client, wait_for_api):
        """测试空白问题"""
        response = api_client.post(
            f"{API_BASE_URL}/ask",
            json={"question": "   "}
        )
        
        # 系统可能接受空白问题或拒绝
        assert response.status_code in [200, 400]
    
    def test_missing_question_field(self, api_client, wait_for_api):
        """测试缺少question字段"""
        response = api_client.post(
            f"{API_BASE_URL}/ask",
            json={"wrong_field": "test"}
        )
        
        assert response.status_code == 422
    
    def test_null_question(self, api_client, wait_for_api):
        """测试null问题"""
        response = api_client.post(
            f"{API_BASE_URL}/ask",
            json={"question": None}
        )
        
        assert response.status_code == 422
    
    def test_extra_fields(self, api_client, wait_for_api):
        """测试额外字段"""
        response = api_client.post(
            f"{API_BASE_URL}/ask",
            json={"question": "水泵维护", "extra_field": "value"}
        )
        
        # 系统应该忽略额外字段
        assert response.status_code == 200

class TestBoundaryConditions:
    """边界条件测试"""
    
    def test_very_long_question(self, api_client, wait_for_api):
        """测试超长问题"""
        long_question = "水泵" * 500  # 1000个字符
        response = api_client.post(
            f"{API_BASE_URL}/ask",
            json={"question": long_question}
        )
        
        # 系统应该能处理长问题或返回适当错误
        assert response.status_code in [200, 400, 413]
    
    def test_special_characters(self, api_client, wait_for_api):
        """测试特殊字符"""
        special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        response = api_client.post(
            f"{API_BASE_URL}/ask",
            json={"question": special_chars}
        )
        
        # 系统应该能处理特殊字符
        assert response.status_code in [200, 400]
    
    def test_unicode_characters(self, api_client, wait_for_api):
        """测试Unicode字符"""
        unicode_question = "水泵维护🔧💡📊"
        response = api_client.post(
            f"{API_BASE_URL}/ask",
            json={"question": unicode_question}
        )
        
        # 系统应该能处理Unicode字符
        assert response.status_code in [200, 400]
    
    def test_numbers_only(self, api_client, wait_for_api):
        """测试纯数字问题"""
        response = api_client.post(
            f"{API_BASE_URL}/ask",
            json={"question": "1234567890"}
        )
        
        # 系统应该能处理纯数字
        assert response.status_code in [200, 400]
    
    def test_mixed_language(self, api_client, wait_for_api):
        """测试混合语言问题"""
        mixed_question = "水泵maintenance周期は？"
        response = api_client.post(
            f"{API_BASE_URL}/ask",
            json={"question": mixed_question}
        )
        
        # 系统应该能处理混合语言
        assert response.status_code in [200, 400]

class TestErrorRecovery:
    """错误恢复测试"""
    
    def test_rapid_requests(self, api_client, wait_for_api):
        """测试快速连续请求"""
        responses = []
        for i in range(10):
            response = api_client.post(
                f"{API_BASE_URL}/ask",
                json={"question": f"测试问题 {i}"}
            )
            responses.append(response)
        
        # 验证所有请求都得到响应
        for response in responses:
            assert response.status_code in [200, 400, 429, 500]
    
    def test_invalid_json_format(self, api_client, wait_for_api):
        """测试无效JSON格式"""
        response = api_client.post(
            f"{API_BASE_URL}/ask",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_wrong_content_type(self, api_client, wait_for_api):
        """测试错误的Content-Type"""
        response = api_client.post(
            f"{API_BASE_URL}/ask",
            data="question=test",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # 系统应该返回适当的错误
        assert response.status_code in [400, 415, 422]

class TestTimeoutHandling:
    """超时处理测试"""
    
    def test_request_timeout(self, api_client, wait_for_api):
        """测试请求超时"""
        try:
            response = api_client.post(
                f"{API_BASE_URL}/ask",
                json={"question": "水泵维护"},
                timeout=0.001  # 极短超时
            )
            # 如果请求成功，验证状态码
            assert response.status_code in [200, 408, 504]
        except requests.exceptions.Timeout:
            # 超时异常是预期的
            pass
    
    def test_long_processing(self, api_client, wait_for_api):
        """测试长时间处理"""
        complex_question = "请详细分析水泵系统的所有可能故障，并提供完整的维护方案"
        response = api_client.post(
            f"{API_BASE_URL}/ask",
            json={"question": complex_question},
            timeout=30  # 30秒超时
        )
        
        # 系统应该在合理时间内响应
        assert response.status_code in [200, 408, 504]

class TestDataIntegrity:
    """数据完整性测试"""
    
    def test_response_encoding(self, api_client, wait_for_api):
        """测试响应编码"""
        response = api_client.post(
            f"{API_BASE_URL}/ask",
            json={"question": "水泵维护"}
        )
        
        assert response.status_code == 200
        # 验证响应是有效的UTF-8
        data = response.json()
        assert isinstance(data["answer"], str)
    
    def test_json_structure(self, api_client, wait_for_api):
        """测试JSON结构完整性"""
        response = api_client.post(
            f"{API_BASE_URL}/ask",
            json={"question": "水泵维护"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证必需字段存在
        required_fields = ["answer", "intent", "action", "source", "timestamp"]
        for field in required_fields:
            assert field in data, f"缺少字段: {field}"
    
    def test_intent_values(self, api_client, wait_for_api):
        """测试意图值有效性"""
        response = api_client.post(
            f"{API_BASE_URL}/ask",
            json={"question": "水泵维护"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证意图值在有效范围内
        valid_intents = ["INFO", "EMERGENCY", "ACTION_REQUIRED"]
        assert data["intent"] in valid_intents

if __name__ == "__main__":
    pytest.main([__file__, "-v"])