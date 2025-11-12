"""
Unit Tests for Numerology System Prompt Module

Tests for backend/src/voice_pipeline/system_prompts.py

Coverage includes:
- System prompt generation with valid User objects
- Vietnamese language support and content validation
- User personalization (name and birth date)
- Edge cases (None birth_date, None full_name)
- Function names staying in English
- Boundaries enforcement in Vietnamese
- Unicode handling for Vietnamese names
"""

import pytest
from datetime import date
from unittest.mock import MagicMock, patch

from src.voice_pipeline.system_prompts import get_numerology_system_prompt
from src.models.user import User


class TestSystemPromptGeneration:
    """Test basic system prompt generation with valid User objects."""

    def test_generates_prompt_with_valid_user(self):
        """Test that system prompt is generated correctly with valid User."""
        user = User(
            id="test-user-1",
            email="test@example.com",
            full_name="John Michael Smith",
            birth_date=date(1990, 5, 15),
            hashed_password="hashed",
        )
        prompt = get_numerology_system_prompt(user)

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "nhà số học Pythagorean" in prompt
        assert "John Michael Smith" in prompt
        assert "15/05/1990" in prompt

    def test_prompt_contains_vietnamese_role_definition(self):
        """Test that Vietnamese role definition is present."""
        user = User(
            id="test-user-2",
            email="test@example.com",
            full_name="Test User",
            birth_date=date(1985, 3, 20),
            hashed_password="hashed",
        )
        prompt = get_numerology_system_prompt(user)

        assert "Aria" in prompt
        assert "ấm áp" in prompt  # warm
        assert "khôn ngoan" in prompt  # wise

    def test_prompt_contains_knowledge_section_in_vietnamese(self):
        """Test that KIẾN THỨC (Knowledge) section is in Vietnamese."""
        user = User(
            id="test-user-3",
            email="test@example.com",
            full_name="Test User",
            birth_date=date(1992, 7, 10),
            hashed_password="hashed",
        )
        prompt = get_numerology_system_prompt(user)

        assert "KIẾN THỨC:" in prompt
        assert "Số Đường Đời" in prompt
        assert "Biểu Hiện" in prompt
        assert "Thúc Đẩy Tâm Hồn" in prompt
        assert "Các Số Chủ" in prompt
        assert "11, 22, 33" in prompt

    def test_prompt_contains_tools_section_with_english_functions(self):
        """Test that CÔNG CỤ (Tools) section has English function names."""
        user = User(
            id="test-user-4",
            email="test@example.com",
            full_name="Test User",
            birth_date=date(1995, 12, 25),
            hashed_password="hashed",
        )
        prompt = get_numerology_system_prompt(user)

        # Tools section
        assert "CÔNG CỤ:" in prompt

        # Function names MUST stay in English
        assert "calculate_life_path" in prompt
        assert "calculate_expression_number" in prompt
        assert "get_numerology_interpretation" in prompt

    def test_prompt_contains_conversation_style_in_vietnamese(self):
        """Test that PHONG CÁCH HỘI THOẠI (Conversation Style) section is in Vietnamese."""
        user = User(
            id="test-user-5",
            email="test@example.com",
            full_name="Test User",
            birth_date=date(1988, 1, 1),
            hashed_password="hashed",
        )
        prompt = get_numerology_system_prompt(user)

        assert "PHONG CÁCH HỘI THOẠI:" in prompt
        assert "tự nhiên" in prompt
        assert "thân mật" in prompt
        assert "câu hỏi" in prompt

    def test_prompt_contains_boundaries_in_vietnamese(self):
        """Test that RANH GIỚI (Boundaries) section enforces guardrails in Vietnamese."""
        user = User(
            id="test-user-6",
            email="test@example.com",
            full_name="Test User",
            birth_date=date(1996, 6, 15),
            hashed_password="hashed",
        )
        prompt = get_numerology_system_prompt(user)

        assert "RANH GIỚI:" in prompt
        assert "giải trí" in prompt  # entertainment
        assert "y tế" in prompt  # medical
        assert "pháp lý" in prompt  # legal
        assert "tài chính" in prompt  # financial

    def test_prompt_contains_user_info_section(self):
        """Test that THÔNG TIN NGƯỜI DÙNG (User Info) section has proper format."""
        user = User(
            id="test-user-7",
            email="test@example.com",
            full_name="Nguyễn Văn A",
            birth_date=date(1990, 5, 15),
            hashed_password="hashed",
        )
        prompt = get_numerology_system_prompt(user)

        assert "THÔNG TIN NGƯỜI DÙNG:" in prompt
        assert "Tên:" in prompt
        assert "Nguyễn Văn A" in prompt
        assert "Ngày Sinh:" in prompt
        assert "15/05/1990" in prompt


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_handles_none_birth_date(self):
        """Test that None birth_date is handled gracefully."""
        user = User(
            id="test-user-edge-1",
            email="test@example.com",
            full_name="Test User",
            birth_date=None,
            hashed_password="hashed",
        )
        prompt = get_numerology_system_prompt(user)

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "Chưa cung cấp" in prompt  # "Not yet provided"
        assert "Test User" in prompt

    def test_handles_none_full_name(self):
        """Test that None full_name is handled gracefully."""
        user = User(
            id="test-user-edge-2",
            email="test@example.com",
            full_name=None,
            birth_date=date(1990, 5, 15),
            hashed_password="hashed",
        )
        prompt = get_numerology_system_prompt(user)

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        # Should use fallback "bạn" (you/them)
        assert "bạn" in prompt

    def test_handles_both_none_values(self):
        """Test that both None values are handled gracefully."""
        user = User(
            id="test-user-edge-3",
            email="test@example.com",
            full_name=None,
            birth_date=None,
            hashed_password="hashed",
        )
        prompt = get_numerology_system_prompt(user)

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "nhà số học Pythagorean" in prompt

    def test_handles_empty_string_full_name(self):
        """Test that empty string full_name is handled gracefully."""
        user = User(
            id="test-user-edge-4",
            email="test@example.com",
            full_name="",
            birth_date=date(1990, 5, 15),
            hashed_password="hashed",
        )
        prompt = get_numerology_system_prompt(user)

        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_no_exceptions_raised(self):
        """Test that no exceptions are raised for any input."""
        test_cases = [
            User(id="1", email="test@ex.com", full_name="Test", birth_date=date(1990, 1, 1), hashed_password="h"),
            User(id="2", email="test@ex.com", full_name=None, birth_date=None, hashed_password="h"),
            User(id="3", email="test@ex.com", full_name="", birth_date=date(1990, 1, 1), hashed_password="h"),
        ]

        for user in test_cases:
            # Should not raise any exception
            prompt = get_numerology_system_prompt(user)
            assert isinstance(prompt, str)


class TestVietnameseContent:
    """Test Vietnamese language support and content validation."""

    def test_entire_prompt_is_vietnamese(self):
        """Test that entire visible prompt is in Vietnamese."""
        user = User(
            id="test-user-vi-1",
            email="test@example.com",
            full_name="Trần Thị B",
            birth_date=date(1985, 3, 20),
            hashed_password="hashed",
        )
        prompt = get_numerology_system_prompt(user)

        # Check that Vietnamese content is present
        assert "Bạn là" in prompt
        assert "Aria" in prompt
        assert "KIẾN THỨC:" in prompt
        assert "CÔNG CỤ:" in prompt
        assert "PHONG CÁCH:" in prompt
        assert "RANH GIỚI:" in prompt
        assert "THÔNG TIN:" in prompt

    def test_date_format_vietnamese(self):
        """Test that date is formatted in Vietnamese style (DD/MM/YYYY)."""
        user = User(
            id="test-user-vi-2",
            email="test@example.com",
            full_name="Test User",
            birth_date=date(1990, 5, 15),
            hashed_password="hashed",
        )
        prompt = get_numerology_system_prompt(user)

        # Vietnamese date format: 15/05/1990 (not 05/15/1990 or 1990-05-15)
        assert "15/05/1990" in prompt
        assert "05/15/1990" not in prompt
        assert "1990-05-15" not in prompt

    def test_unicode_vietnamese_names_supported(self):
        """Test that Vietnamese names with special characters are supported."""
        vietnamese_names = [
            "Nguyễn Văn A",
            "Trần Thị B",
            "Lê Văn C",
            "Phạm Văn D",
            "Hoàng Thị E",
        ]

        for name in vietnamese_names:
            user = User(
                id=f"test-{name}",
                email="test@example.com",
                full_name=name,
                birth_date=date(1990, 5, 15),
                hashed_password="hashed",
            )
            prompt = get_numerology_system_prompt(user)

            assert isinstance(prompt, str)
            assert name in prompt


class TestFunctionCallingPreservation:
    """Test that function names remain in English for reliable function calling."""

    def test_function_names_in_english(self):
        """Test that all function names are in English."""
        user = User(
            id="test-user-func-1",
            email="test@example.com",
            full_name="Test User",
            birth_date=date(1990, 5, 15),
            hashed_password="hashed",
        )
        prompt = get_numerology_system_prompt(user)

        # Function names MUST be in English
        assert "calculate_life_path" in prompt
        assert "calculate_expression_number" in prompt
        assert "get_numerology_interpretation" in prompt

        # These should NOT be translated
        assert "tính_số_đường_đời" not in prompt
        assert "tính_số_biểu_hiện" not in prompt
        assert "lấy_diễn_giải_số_học" not in prompt

    def test_no_english_words_in_main_prompt(self):
        """Test that main visible prompt text doesn't contain English words."""
        user = User(
            id="test-user-func-2",
            email="test@example.com",
            full_name="Test User",
            birth_date=date(1990, 5, 15),
            hashed_password="hashed",
        )
        prompt = get_numerology_system_prompt(user)

        # These English words should NOT appear (except in function names)
        english_words = ["warm", "wise", "interested", "knowledgeable", "entertaining"]
        for word in english_words:
            # Check that these English words are NOT in the Vietnamese prompt
            # (except as part of function names)
            lines = prompt.split("\n")
            for line in lines:
                # Skip lines with function names
                if "calculate" not in line and "get_" not in line:
                    assert word not in line.lower()


class TestBoundaryEnforcement:
    """Test that safety boundaries are properly enforced in Vietnamese."""

    def test_medical_advice_boundary(self):
        """Test that medical advice boundary is present in Vietnamese."""
        user = User(
            id="test-user-boundary-1",
            email="test@example.com",
            full_name="Test User",
            birth_date=date(1990, 5, 15),
            hashed_password="hashed",
        )
        prompt = get_numerology_system_prompt(user)

        assert "y tế" in prompt or "y học" in prompt or "bác sĩ" in prompt

    def test_legal_advice_boundary(self):
        """Test that legal advice boundary is present in Vietnamese."""
        user = User(
            id="test-user-boundary-2",
            email="test@example.com",
            full_name="Test User",
            birth_date=date(1990, 5, 15),
            hashed_password="hashed",
        )
        prompt = get_numerology_system_prompt(user)

        assert "pháp lý" in prompt or "luật" in prompt or "luật sư" in prompt

    def test_financial_advice_boundary(self):
        """Test that financial advice boundary is present in Vietnamese."""
        user = User(
            id="test-user-boundary-3",
            email="test@example.com",
            full_name="Test User",
            birth_date=date(1990, 5, 15),
            hashed_password="hashed",
        )
        prompt = get_numerology_system_prompt(user)

        assert "tài chính" in prompt or "tiền" in prompt or "đầu tư" in prompt

    def test_entertainment_disclaimer(self):
        """Test that entertainment disclaimer is present."""
        user = User(
            id="test-user-boundary-4",
            email="test@example.com",
            full_name="Test User",
            birth_date=date(1990, 5, 15),
            hashed_password="hashed",
        )
        prompt = get_numerology_system_prompt(user)

        assert "giải trí" in prompt or "tâm linh" in prompt


class TestDeterminism:
    """Test that prompt generation is deterministic."""

    def test_same_user_generates_same_prompt(self):
        """Test that the same user always generates the same prompt."""
        user = User(
            id="test-user-deterministic",
            email="test@example.com",
            full_name="Consistent User",
            birth_date=date(1990, 5, 15),
            hashed_password="hashed",
        )

        prompt1 = get_numerology_system_prompt(user)
        prompt2 = get_numerology_system_prompt(user)

        assert prompt1 == prompt2


class TestReturnType:
    """Test return type and structure."""

    def test_returns_string(self):
        """Test that function returns a string."""
        user = User(
            id="test-user-return-1",
            email="test@example.com",
            full_name="Test User",
            birth_date=date(1990, 5, 15),
            hashed_password="hashed",
        )
        prompt = get_numerology_system_prompt(user)

        assert isinstance(prompt, str)

    def test_returns_non_empty_string(self):
        """Test that function returns non-empty string."""
        user = User(
            id="test-user-return-2",
            email="test@example.com",
            full_name="Test User",
            birth_date=date(1990, 5, 15),
            hashed_password="hashed",
        )
        prompt = get_numerology_system_prompt(user)

        assert len(prompt) > 100  # Should be substantial prompt

    def test_returns_complete_prompt_structure(self):
        """Test that returned prompt has all required sections."""
        user = User(
            id="test-user-return-3",
            email="test@example.com",
            full_name="Test User",
            birth_date=date(1990, 5, 15),
            hashed_password="hashed",
        )
        prompt = get_numerology_system_prompt(user)

        required_sections = [
            "Bạn là",  # Role definition start
            "KIẾN THỨC:",  # Knowledge section
            "CÔNG CỤ:",  # Tools section
            "PHONG CÁCH",  # Conversation style
            "RANH GIỚI:",  # Boundaries section
            "THÔNG TIN NGƯỜI DÙNG:",  # User info section
        ]

        for section in required_sections:
            assert section in prompt, f"Missing section: {section}"
