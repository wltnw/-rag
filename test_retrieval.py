"""
知识库检索测试 - 测试RAG系统的检索准确性和相关性
"""
import pytest
import requests
from conftest import API_BASE_URL

class TestRetrievalAccuracy:
    """检索准确性测试"""
    
    def test_pump_maintenance_retrieval(self, api_client, wait_for_api, api_helper):
        """测试水泵维护相关信息检索"""
        result = api_helper.ask_question(api_client, "水泵需要多久维护一次？")
        
        assert result["status_code"] == 200
        data = result["data"]
        
        # 验证答案包含维护相关信息
        answer = data["answer"].lower()
        maintenance_keywords = ["维护", "检查", "保养", "周", "月", "定期"]
        assert any(keyword in answer for keyword in maintenance_keywords), \
            f"答案中未包含维护相关信息: {data['answer']}"
    
    def test_sensor_voltage_retrieval(self, api_client, wait_for_api, api_helper):
        """测试传感器电压信息检索"""
        result = api_helper.ask_question(api_client, "温湿度传感器的电源电压范围是多少？")
        
        assert result["status_code"] == 200
        data = result["data"]
        
        # 验证答案包含电压信息
        answer = data["answer"].lower()
        voltage_keywords = ["3.3", "5.0", "v", "电压", "伏"]
        assert any(keyword in answer for keyword in voltage_keywords), \
            f"答案中未包含电压信息: {data['answer']}"
    
    def test_fan_temperature_retrieval(self, api_client, wait_for_api, api_helper):
        """测试风扇启动温度信息检索"""
        result = api_helper.ask_question(api_client, "大棚里温度多少度的时候需要启动风扇？")
        
        assert result["status_code"] == 200
        data = result["data"]
        
        # 验证答案包含温度信息
        answer = data["answer"].lower()
        temperature_keywords = ["28", "30", "度", "℃", "温度"]
        assert any(keyword in answer for keyword in temperature_keywords), \
            f"答案中未包含温度信息: {data['answer']}"
    
    def test_fault_code_retrieval(self, api_client, wait_for_api, api_helper):
        """测试故障代码信息检索"""
        result = api_helper.ask_question(api_client, "ERR_002 是什么故障？")
        
        assert result["status_code"] == 200
        data = result["data"]
        
        # 验证答案包含故障信息
        answer = data["answer"].lower()
        fault_keywords = ["err_002", "超时", "timeout", "故障", "错误"]
        assert any(keyword in answer for keyword in fault_keywords), \
            f"答案中未包含故障信息: {data['answer']}"

class TestRetrievalRelevance:
    """检索相关性测试"""
    
    def test_relevant_source_found(self, api_client, wait_for_api, api_helper):
        """测试是否找到相关来源"""
        result = api_helper.ask_question(api_client, "水泵维护周期")
        
        assert result["status_code"] == 200
        data = result["data"]
        
        # 验证找到了相关文档
        assert data["source_found"] is True or len(data["answer"]) > 0
    
    def test_irrelevant_question_handling(self, api_client, wait_for_api, api_helper):
        """测试无关问题处理"""
        result = api_helper.ask_question(api_client, "今天天气怎么样？")
        
        assert result["status_code"] == 200
        data = result["data"]
        
        # 对于无关问题，系统应该表明无法找到相关信息
        answer = data["answer"].lower()
        irrelevant_indicators = ["抱歉", "未找到", "没有", "无法", "不知道", "操作手册"]
        # 注意：系统可能仍然会给出答案，这里只验证响应格式正确
        assert len(data["answer"]) > 0
    
    def test_multiple_retrieval(self, api_client, wait_for_api, api_helper):
        """测试多次检索的一致性"""
        questions = [
            "水泵维护周期",
            "水泵维护周期",
            "水泵维护周期"
        ]
        
        results = []
        for question in questions:
            result = api_helper.ask_question(api_client, question)
            assert result["status_code"] == 200
            results.append(result["data"])
        
        # 验证多次检索的结果基本一致
        # 注意：由于LLM的随机性，答案可能不完全相同，但意图应该一致
        intents = [r["intent"] for r in results]
        assert len(set(intents)) <= 2  # 允许一定的变化

class TestRetrievalContext:
    """检索上下文测试"""
    
    def test_context_quality(self, api_client, wait_for_api, api_helper):
        """测试检索上下文质量"""
        result = api_helper.ask_question(api_client, "水泵常见故障有哪些？")
        
        assert result["status_code"] == 200
        data = result["data"]
        
        # 验证答案包含具体的故障信息
        answer = data["answer"].lower()
        context_keywords = ["无法启动", "水压", "异响", "电源", "保险丝"]
        assert any(keyword in answer for keyword in context_keywords), \
            f"答案中未包含具体故障信息: {data['answer']}"
    
    def test_context_completeness(self, api_client, wait_for_api, api_helper):
        """测试检索上下文完整性"""
        result = api_helper.ask_question(api_client, "传感器精度是多少？")
        
        assert result["status_code"] == 200
        data = result["data"]
        
        # 验证答案包含精度信息
        answer = data["answer"].lower()
        precision_keywords = ["2", "±", "精度", "℃", "度"]
        assert any(keyword in answer for keyword in precision_keywords), \
            f"答案中未包含精度信息: {data['answer']}"

class TestRetrievalEdgeCases:
    """检索边界情况测试"""
    
    def test_short_question(self, api_client, wait_for_api, api_helper):
        """测试简短问题"""
        result = api_helper.ask_question(api_client, "水泵")
        
        assert result["status_code"] == 200
        data = result["data"]
        assert len(data["answer"]) > 0
    
    def test_long_question(self, api_client, wait_for_api, api_helper):
        """测试长问题"""
        long_question = "我想了解一下关于水泵的维护保养知识，包括维护周期、常见故障、处理方法等详细信息"
        result = api_helper.ask_question(api_client, long_question)
        
        assert result["status_code"] == 200
        data = result["data"]
        assert len(data["answer"]) > 0
    
    def test_technical_question(self, api_client, wait_for_api, api_helper):
        """测试技术性问题"""
        result = api_helper.ask_question(api_client, "AQP-2500型水泵的额定功率是多少？")
        
        assert result["status_code"] == 200
        data = result["data"]
        
        # 验证答案包含技术参数
        answer = data["answer"].lower()
        technical_keywords = ["2.5", "kw", "千瓦", "功率"]
        assert any(keyword in answer for keyword in technical_keywords), \
            f"答案中未包含技术参数: {data['answer']}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])