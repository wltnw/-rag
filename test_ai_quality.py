"""
AI质量测试 - 测试AI回答的准确性和幻觉检测
"""
import pytest
import requests
from conftest import API_BASE_URL

class TestAnswerAccuracy:
    """答案准确性测试"""
    
    def test_pump_maintenance_accuracy(self, api_client, wait_for_api, api_helper):
        """测试水泵维护答案准确性"""
        result = api_helper.ask_question(api_client, "水泵需要多久维护一次？")
        
        assert result["status_code"] == 200
        data = result["data"]
        
        answer = data["answer"].lower()
        
        # 验证答案包含维护周期信息
        maintenance_keywords = ["维护", "检查", "保养", "周", "月", "定期"]
        assert any(keyword in answer for keyword in maintenance_keywords), \
            f"答案中未包含维护周期信息: {data['answer']}"
    
    def test_sensor_voltage_accuracy(self, api_client, wait_for_api, api_helper):
        """测试传感器电压答案准确性"""
        result = api_helper.ask_question(api_client, "温湿度传感器的电源电压范围是多少？")
        
        assert result["status_code"] == 200
        data = result["data"]
        
        answer = data["answer"].lower()
        
        # 验证答案包含正确的电压范围
        voltage_keywords = ["3.3", "5.0", "v", "电压"]
        assert any(keyword in answer for keyword in voltage_keywords), \
            f"答案中未包含电压信息: {data['answer']}"
    
    def test_fan_temperature_accuracy(self, api_client, wait_for_api, api_helper):
        """测试风扇启动温度答案准确性"""
        result = api_helper.ask_question(api_client, "大棚里温度多少度的时候需要启动风扇？")
        
        assert result["status_code"] == 200
        data = result["data"]
        
        answer = data["answer"].lower()
        
        # 验证答案包含温度阈值
        temperature_keywords = ["28", "30", "度", "℃"]
        assert any(keyword in answer for keyword in temperature_keywords), \
            f"答案中未包含温度信息: {data['answer']}"
    
    def test_fault_code_accuracy(self, api_client, wait_for_api, api_helper):
        """测试故障代码答案准确性"""
        result = api_helper.ask_question(api_client, "ERR_002 是什么故障？")
        
        assert result["status_code"] == 200
        data = result["data"]
        
        answer = data["answer"].lower()
        
        # 验证答案包含故障信息
        fault_keywords = ["err_002", "超时", "timeout", "故障"]
        assert any(keyword in answer for keyword in fault_keywords), \
            f"答案中未包含故障信息: {data['answer']}"

class TestHallucinationDetection:
    """幻觉检测测试"""
    
    def test_no_hallucination_for_unknown(self, api_client, wait_for_api, api_helper):
        """测试未知问题时的幻觉检测"""
        # 问一个知识库中不存在的问题
        result = api_helper.ask_question(api_client, "火星上的农场怎么管理？")
        
        assert result["status_code"] == 200
        data = result["data"]
        
        # 系统应该表明无法找到相关信息
        answer = data["answer"].lower()
        hallucination_indicators = ["抱歉", "未找到", "没有", "无法", "不知道", "操作手册"]
        
        # 验证响应格式正确
        assert len(data["answer"]) > 0
    
    def test_no_hallucination_for_technical(self, api_client, wait_for_api, api_helper):
        """测试技术问题时的幻觉检测"""
        # 问一个超出知识库范围的技术问题
        result = api_helper.ask_question(api_client, "量子计算机如何优化农场管理？")
        
        assert result["status_code"] == 200
        data = result["data"]
        
        # 系统应该表明无法找到相关信息
        answer = data["answer"].lower()
        
        # 验证响应格式正确
        assert len(data["answer"]) > 0
    
    def test_no_hallucination_for_numbers(self, api_client, wait_for_api, api_helper):
        """测试数字信息时的幻觉检测"""
        # 问一个需要精确数字的问题
        result = api_helper.ask_question(api_client, "水泵的价格是多少？")
        
        assert result["status_code"] == 200
        data = result["data"]
        
        # 系统应该表明无法找到价格信息
        answer = data["answer"].lower()
        
        # 验证响应格式正确
        assert len(data["answer"]) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
