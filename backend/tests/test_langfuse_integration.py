"""
Tests for Langfuse integration
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.langchain_personas import LangChainPersonaAgent, Settings
from app.evaluators import (
    evaluate_response_length,
    evaluate_empathy_compliance,
    evaluate_role_consistency,
    evaluate_specificity,
    evaluate_overall_quality
)


class TestLangfuseCallback:
    """Test Langfuse callback handler creation"""
    
    def test_create_langfuse_handler_enabled(self):
        """Test creating Langfuse handler when enabled"""
        settings = Settings(
            openai_api_key="test-key",
            langfuse_enabled=True,
            langfuse_public_key="pk-test",
            langfuse_secret_key="sk-test"
        )
        
        persona_data = {
            "id": "test",
            "name": "Test Persona",
            "role": "Tester",
            "company": "Test Co",
            "empathy_map": {}
        }
        
        with patch('app.langchain_personas.LANGFUSE_AVAILABLE', True):
            with patch('app.langchain_personas.CallbackHandler') as mock_handler:
                agent = LangChainPersonaAgent(persona_data, settings, Mock())
                handler = agent._create_langfuse_handler(
                    session_id="test-session",
                    feature="chat"
                )
                
                # Verify handler was created
                mock_handler.assert_called_once()
                call_kwargs = mock_handler.call_args[1]
                assert call_kwargs['public_key'] == "pk-test"
                assert call_kwargs['secret_key'] == "sk-test"
                assert call_kwargs['session_id'] == "test-session"
                assert 'persona_id' in call_kwargs['metadata']
                assert 'chat' in call_kwargs['tags']
    
    def test_create_langfuse_handler_disabled(self):
        """Test that handler is None when Langfuse is disabled"""
        settings = Settings(
            openai_api_key="test-key",
            langfuse_enabled=False
        )
        
        persona_data = {
            "id": "test",
            "name": "Test Persona",
            "role": "Tester",
            "company": "Test Co",
            "empathy_map": {}
        }
        
        agent = LangChainPersonaAgent(persona_data, settings, Mock())
        handler = agent._create_langfuse_handler()
        
        assert handler is None
    
    def test_create_langfuse_handler_no_keys(self):
        """Test that handler is None when keys are missing"""
        settings = Settings(
            openai_api_key="test-key",
            langfuse_enabled=True,
            langfuse_public_key="",
            langfuse_secret_key=""
        )
        
        persona_data = {
            "id": "test",
            "name": "Test Persona",
            "role": "Tester",
            "company": "Test Co",
            "empathy_map": {}
        }
        
        agent = LangChainPersonaAgent(persona_data, settings, Mock())
        handler = agent._create_langfuse_handler()
        
        assert handler is None


class TestEvaluators:
    """Test custom evaluators"""
    
    def test_evaluate_response_length_optimal(self):
        """Test response length evaluator with optimal length"""
        response = " ".join(["word"] * 200)  # 200 words
        result = evaluate_response_length(response)
        
        assert result['score'] == 1.0
        assert result['status'] == "optimal"
        assert result['word_count'] == 200
    
    def test_evaluate_response_length_too_short(self):
        """Test response length evaluator with too short response"""
        response = " ".join(["word"] * 50)  # 50 words
        result = evaluate_response_length(response)
        
        assert result['score'] == 0.5
        assert result['status'] == "too_short"
        assert result['word_count'] == 50
    
    def test_evaluate_response_length_too_long(self):
        """Test response length evaluator with too long response"""
        response = " ".join(["word"] * 400)  # 400 words
        result = evaluate_response_length(response)
        
        assert result['score'] == 0.5
        assert result['status'] == "too_long"
        assert result['word_count'] == 400
    
    def test_evaluate_empathy_compliance_strong(self):
        """Test empathy evaluator with strong empathy markers"""
        response = "I think this is important. I feel concerned about the risks. I see the value. We should implement this."
        result = evaluate_empathy_compliance(response)
        
        assert result['score'] == 1.0
        assert result['status'] == "strong_empathy"
        assert result['dimensions_present'] >= 3
    
    def test_evaluate_empathy_compliance_weak(self):
        """Test empathy evaluator with weak empathy markers"""
        response = "This is a feature. It does something."
        result = evaluate_empathy_compliance(response)
        
        assert result['score'] <= 0.6
        assert result['dimensions_present'] <= 1
    
    def test_evaluate_role_consistency_trading(self):
        """Test role consistency for trading role"""
        response = "As a trader, I need uptime and SLA guarantees. Provider performance is critical for our trading operations."
        result = evaluate_role_consistency(response, "Head of Trading")
        
        assert result['score'] >= 0.6
        assert result['matches'] > 0
        assert result['status'] in ["strong_consistency", "good_consistency", "moderate_consistency"]
    
    def test_evaluate_role_consistency_product(self):
        """Test role consistency for product role"""
        response = "From a product perspective, user experience and feature design are key priorities."
        result = evaluate_role_consistency(response, "Product Owner")
        
        assert result['score'] >= 0.6
        assert result['matches'] > 0
    
    def test_evaluate_specificity_high(self):
        """Test specificity evaluator with specific response"""
        response = "Last week, we saw 99.9% uptime. For example, BetMax uses this feature daily. Our team of 15 analysts reviewed the data."
        result = evaluate_specificity(response)
        
        assert result['score'] >= 0.8
        assert result['status'] in ["highly_specific", "moderately_specific"]
        assert result['specificity_count'] >= 2
    
    def test_evaluate_specificity_low(self):
        """Test specificity evaluator with generic response"""
        response = "This is good. We like it. It works well."
        result = evaluate_specificity(response)
        
        assert result['score'] <= 0.6
        assert result['specificity_count'] <= 1
    
    def test_evaluate_overall_quality(self):
        """Test overall quality evaluator"""
        response = "I think this feature is valuable. I feel it addresses our concerns. " + " ".join(["word"] * 180)
        result = evaluate_overall_quality(
            response=response,
            persona_role="Product Owner"
        )
        
        assert 'overall_score' in result
        assert 0.0 <= result['overall_score'] <= 1.0
        assert 'evaluations' in result
        assert 'length' in result['evaluations']
        assert 'empathy' in result['evaluations']
        assert 'specificity' in result['evaluations']


class TestFeedbackEndpoint:
    """Test feedback endpoint"""
    
    @pytest.mark.asyncio
    async def test_feedback_endpoint_success(self):
        """Test successful feedback submission"""
        from app.routes.feedback import log_feedback, FeedbackRequest
        
        request = FeedbackRequest(
            trace_id="test-trace-123",
            score=1.0,
            persona_id="alex",
            persona_name="Alex"
        )
        
        with patch('app.routes.feedback.LANGFUSE_AVAILABLE', True):
            with patch('app.routes.feedback.Langfuse') as mock_langfuse:
                mock_instance = MagicMock()
                mock_langfuse.return_value = mock_instance
                
                result = await log_feedback(request)
                
                assert result['status'] == 'success'
                assert result['trace_id'] == 'test-trace-123'
                assert result['score'] == 1.0
                mock_instance.score.assert_called_once()
                mock_instance.flush.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_feedback_endpoint_langfuse_unavailable(self):
        """Test feedback endpoint when Langfuse is unavailable"""
        from app.routes.feedback import log_feedback, FeedbackRequest
        from fastapi import HTTPException
        
        request = FeedbackRequest(
            trace_id="test-trace-123",
            score=1.0
        )
        
        with patch('app.routes.feedback.LANGFUSE_AVAILABLE', False):
            with pytest.raises(HTTPException) as exc_info:
                await log_feedback(request)
            
            assert exc_info.value.status_code == 503
            assert "not available" in str(exc_info.value.detail)


class TestMetadataTracking:
    """Test metadata tracking in traces"""
    
    def test_metadata_includes_persona_info(self):
        """Test that trace metadata includes persona information"""
        settings = Settings(
            openai_api_key="test-key",
            langfuse_enabled=True,
            langfuse_public_key="pk-test",
            langfuse_secret_key="sk-test"
        )
        
        persona_data = {
            "id": "alex",
            "name": "Alex",
            "role": "Head of Trading",
            "company": "BetMax",
            "empathy_map": {}
        }
        
        with patch('app.langchain_personas.LANGFUSE_AVAILABLE', True):
            with patch('app.langchain_personas.CallbackHandler') as mock_handler:
                agent = LangChainPersonaAgent(persona_data, settings, Mock())
                handler = agent._create_langfuse_handler(
                    session_id="test-session",
                    feature="debate",
                    metadata={"round_number": 3}
                )
                
                call_kwargs = mock_handler.call_args[1]
                metadata = call_kwargs['metadata']
                
                assert metadata['persona_id'] == 'alex'
                assert metadata['persona_name'] == 'Alex'
                assert metadata['persona_role'] == 'Head of Trading'
                assert metadata['persona_company'] == 'BetMax'
                assert metadata['feature'] == 'debate'
                assert metadata['round_number'] == 3
    
    def test_tags_include_feature_and_persona(self):
        """Test that tags include feature and persona ID"""
        settings = Settings(
            openai_api_key="test-key",
            langfuse_enabled=True,
            langfuse_public_key="pk-test",
            langfuse_secret_key="sk-test"
        )
        
        persona_data = {
            "id": "nina",
            "name": "Nina",
            "role": "Product Owner",
            "company": "SportsBet",
            "empathy_map": {}
        }
        
        with patch('app.langchain_personas.LANGFUSE_AVAILABLE', True):
            with patch('app.langchain_personas.CallbackHandler') as mock_handler:
                agent = LangChainPersonaAgent(persona_data, settings, Mock())
                handler = agent._create_langfuse_handler(
                    feature="chat"
                )
                
                call_kwargs = mock_handler.call_args[1]
                tags = call_kwargs['tags']
                
                assert 'persona' in tags
                assert 'nina' in tags
                assert 'chat' in tags


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
