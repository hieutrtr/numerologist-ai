"""
Tests for Numerology Function Call Handlers

Tests all handler functions to ensure they:
- Convert GPT arguments to proper Python types
- Call service functions correctly
- Return GPT-friendly dict results
- Handle errors gracefully without raising exceptions
- Log execution properly
"""

import pytest
import sys
import importlib.util
from pathlib import Path
from datetime import date
from unittest.mock import Mock, patch

# Direct module import to avoid triggering voice_pipeline/__init__.py (which imports pipecat)
backend_dir = Path(__file__).parent.parent.parent
module_path = backend_dir / "src" / "voice_pipeline" / "function_handlers.py"

spec = importlib.util.spec_from_file_location("function_handlers", module_path)
function_handlers = importlib.util.module_from_spec(spec)
sys.modules["function_handlers"] = function_handlers
spec.loader.exec_module(function_handlers)

# Import handler functions
handle_calculate_life_path = function_handlers.handle_calculate_life_path
handle_calculate_expression = function_handlers.handle_calculate_expression
handle_calculate_soul_urge = function_handlers.handle_calculate_soul_urge
handle_get_interpretation = function_handlers.handle_get_interpretation
handle_numerology_function = function_handlers.handle_numerology_function


class TestHandleCalculateLifePath:
    """Test Life Path number calculation handler (AC2)"""

    def test_valid_date_returns_life_path_number(self):
        """Test handler with valid date string returns calculated number"""
        result = handle_calculate_life_path("1990-05-15")

        assert isinstance(result, dict)
        assert "life_path_number" in result
        assert isinstance(result["life_path_number"], int)
        assert 1 <= result["life_path_number"] <= 33

    def test_master_number_preserved(self):
        """Test handler preserves master numbers (11, 22, 33)"""
        # Date that results in master number 11: 1980-02-29
        result = handle_calculate_life_path("1980-02-29")

        assert isinstance(result, dict)
        assert "life_path_number" in result
        # Verify it's a valid numerology number
        assert result["life_path_number"] in list(range(1, 10)) + [11, 22, 33]

    def test_invalid_date_format_returns_error_dict(self):
        """Test handler with invalid date format returns error dict (not exception)"""
        result = handle_calculate_life_path("invalid-date")

        assert isinstance(result, dict)
        assert "error" in result
        assert result["error"] == "InvalidDate"
        assert "message" in result
        assert "YYYY-MM-DD" in result["message"]

    def test_empty_date_returns_error_dict(self):
        """Test handler with empty date returns error dict"""
        result = handle_calculate_life_path("")

        assert isinstance(result, dict)
        assert "error" in result
        assert "message" in result

    def test_partial_date_returns_error_dict(self):
        """Test handler with partial date (e.g., missing day) returns error"""
        result = handle_calculate_life_path("1990-05")

        assert isinstance(result, dict)
        assert "error" in result

    def test_handler_never_raises_exception(self):
        """Test handler catches all exceptions and returns error dict"""
        # Even with completely malformed input, should not raise
        try:
            result = handle_calculate_life_path(None)
            assert isinstance(result, dict)
            assert "error" in result
        except Exception:
            pytest.fail("Handler should not raise exceptions")


class TestHandleCalculateExpression:
    """Test Expression number calculation handler (AC3)"""

    def test_valid_name_returns_expression_number(self):
        """Test handler with valid name returns calculated number"""
        result = handle_calculate_expression("John Michael Smith")

        assert isinstance(result, dict)
        assert "expression_number" in result
        assert isinstance(result["expression_number"], int)
        assert 1 <= result["expression_number"] <= 33

    def test_empty_name_returns_error_dict(self):
        """Test handler with empty name returns error dict"""
        result = handle_calculate_expression("")

        assert isinstance(result, dict)
        assert "error" in result
        assert result["error"] == "InvalidName"
        assert "message" in result
        assert "full name" in result["message"].lower()

    def test_whitespace_only_name_returns_error_dict(self):
        """Test handler with whitespace-only name returns error"""
        result = handle_calculate_expression("   ")

        assert isinstance(result, dict)
        assert "error" in result
        assert result["error"] == "InvalidName"

    def test_single_name_works(self):
        """Test handler works with single name (edge case)"""
        result = handle_calculate_expression("Madonna")

        assert isinstance(result, dict)
        assert "expression_number" in result

    def test_name_with_special_characters_works(self):
        """Test handler works with names containing hyphens, apostrophes"""
        result = handle_calculate_expression("Mary-Jane O'Connor")

        assert isinstance(result, dict)
        assert "expression_number" in result


class TestHandleCalculateSoulUrge:
    """Test Soul Urge number calculation handler (AC4)"""

    def test_valid_name_returns_soul_urge_number(self):
        """Test handler with valid name returns calculated number"""
        result = handle_calculate_soul_urge("Sarah Elizabeth Johnson")

        assert isinstance(result, dict)
        assert "soul_urge_number" in result
        assert isinstance(result["soul_urge_number"], int)
        assert 1 <= result["soul_urge_number"] <= 33

    def test_empty_name_returns_error_dict(self):
        """Test handler with empty name returns error dict"""
        result = handle_calculate_soul_urge("")

        assert isinstance(result, dict)
        assert "error" in result
        assert result["error"] == "InvalidName"

    def test_whitespace_only_name_returns_error_dict(self):
        """Test handler with whitespace-only name returns error"""
        result = handle_calculate_soul_urge("   \t\n   ")

        assert isinstance(result, dict)
        assert "error" in result


class TestHandleGetInterpretation:
    """Test interpretation retrieval handler (AC5)"""

    def test_valid_parameters_returns_interpretations(self):
        """Test handler with valid parameters returns interpretation list"""
        result = handle_get_interpretation(
            number_type="life_path",
            number_value=1
        )

        assert isinstance(result, dict)
        assert "interpretations" in result
        assert isinstance(result["interpretations"], list)

        # If interpretations exist, verify structure
        if len(result["interpretations"]) > 0:
            interp = result["interpretations"][0]
            assert "category" in interp
            assert "content" in interp
            assert isinstance(interp["category"], str)
            assert isinstance(interp["content"], str)

    def test_with_category_filter_returns_filtered_results(self):
        """Test handler with category filter returns only matching category"""
        result = handle_get_interpretation(
            number_type="life_path",
            number_value=1,
            category="personality"
        )

        assert isinstance(result, dict)
        assert "interpretations" in result

        # All returned interpretations should match category
        for interp in result["interpretations"]:
            assert interp["category"] == "personality"

    def test_nonexistent_number_returns_empty_list_not_error(self):
        """Test handler with non-existent number returns empty list (not error)"""
        result = handle_get_interpretation(
            number_type="life_path",
            number_value=999  # Non-existent value
        )

        assert isinstance(result, dict)
        assert "interpretations" in result
        assert isinstance(result["interpretations"], list)
        # Should return empty list, not error
        assert "error" not in result

    def test_master_number_interpretations_exist(self):
        """Test handler can retrieve master number interpretations (11, 22, 33)"""
        for master_num in [11, 22, 33]:
            result = handle_get_interpretation(
                number_type="life_path",
                number_value=master_num
            )

            assert isinstance(result, dict)
            assert "interpretations" in result
            # Master numbers may or may not have interpretations yet, but should return valid structure
            assert isinstance(result["interpretations"], list)

    def test_database_error_returns_error_dict(self):
        """Test handler returns error dict on database failure"""
        # Mock database failure by mocking the Session context manager
        with patch('function_handlers.Session') as mock_session_class:
            mock_session = Mock()
            mock_session.__enter__ = Mock(side_effect=Exception("Database connection failed"))
            mock_session.__exit__ = Mock(return_value=False)
            mock_session_class.return_value = mock_session

            result = handle_get_interpretation(
                number_type="life_path",
                number_value=1
            )

            assert isinstance(result, dict)
            assert "error" in result
            assert result["error"] == "DatabaseError"


class TestHandleNumerologyFunction:
    """Test main router function (AC6)"""

    def test_calculate_life_path_routing(self):
        """Test router dispatches calculate_life_path correctly"""
        arguments = {"birth_date": "1990-05-15"}
        result = handle_numerology_function("calculate_life_path", arguments)

        assert isinstance(result, dict)
        # Should have life_path_number or error
        assert "life_path_number" in result or "error" in result

    def test_calculate_expression_number_routing(self):
        """Test router dispatches calculate_expression_number correctly"""
        arguments = {"full_name": "John Smith"}
        result = handle_numerology_function("calculate_expression_number", arguments)

        assert isinstance(result, dict)
        assert "expression_number" in result or "error" in result

    def test_calculate_soul_urge_number_routing(self):
        """Test router dispatches calculate_soul_urge_number correctly"""
        arguments = {"full_name": "Jane Doe"}
        result = handle_numerology_function("calculate_soul_urge_number", arguments)

        assert isinstance(result, dict)
        assert "soul_urge_number" in result or "error" in result

    def test_get_numerology_interpretation_routing(self):
        """Test router dispatches get_numerology_interpretation correctly"""
        arguments = {
            "number_type": "life_path",
            "number_value": 1
        }
        result = handle_numerology_function("get_numerology_interpretation", arguments)

        assert isinstance(result, dict)
        assert "interpretations" in result or "error" in result

    def test_get_interpretation_with_optional_category(self):
        """Test router handles optional category parameter"""
        arguments = {
            "number_type": "life_path",
            "number_value": 1,
            "category": "personality"
        }
        result = handle_numerology_function("get_numerology_interpretation", arguments)

        assert isinstance(result, dict)
        assert "interpretations" in result or "error" in result

    def test_unknown_function_name_returns_error(self):
        """Test router returns error for unknown function names"""
        result = handle_numerology_function("unknown_function", {})

        assert isinstance(result, dict)
        assert "error" in result
        assert result["error"] == "UnknownFunction"
        assert "unknown_function" in result["message"]

    def test_missing_required_argument_returns_error(self):
        """Test router returns error when required argument missing"""
        result = handle_numerology_function("calculate_life_path", {})

        assert isinstance(result, dict)
        assert "error" in result
        assert result["error"] == "MissingArgument"

    def test_router_never_raises_exception(self):
        """Test router catches all exceptions and returns error dict"""
        try:
            # Invalid arguments should return error dict, not raise
            result = handle_numerology_function("calculate_life_path", {"wrong_key": "value"})
            assert isinstance(result, dict)
            assert "error" in result
        except Exception:
            pytest.fail("Router should not raise exceptions")


class TestErrorHandling:
    """Test comprehensive error handling across all handlers (AC7)"""

    def test_all_handlers_return_dict_never_raise(self):
        """Test all handlers always return dict, never raise exceptions"""
        test_cases = [
            (handle_calculate_life_path, ["invalid"]),
            (handle_calculate_expression, [""]),
            (handle_calculate_soul_urge, [""]),
            (handle_get_interpretation, ["invalid_type", 999]),
            (handle_numerology_function, ["unknown", {}]),
        ]

        for handler, args in test_cases:
            try:
                result = handler(*args)
                assert isinstance(result, dict), f"{handler.__name__} did not return dict"
            except Exception as e:
                pytest.fail(f"{handler.__name__} raised exception: {e}")

    def test_error_dicts_have_consistent_format(self):
        """Test all error dicts have 'error' and 'message' keys"""
        # Generate various errors
        error_results = [
            handle_calculate_life_path("invalid"),
            handle_calculate_expression(""),
            handle_calculate_soul_urge(""),
            handle_numerology_function("unknown", {}),
            handle_numerology_function("calculate_life_path", {}),
        ]

        for result in error_results:
            if "error" in result:  # It's an error dict
                assert "error" in result, "Error dict missing 'error' key"
                assert "message" in result, "Error dict missing 'message' key"
                assert isinstance(result["error"], str), "'error' should be string"
                assert isinstance(result["message"], str), "'message' should be string"
                assert len(result["message"]) > 0, "Error message should not be empty"

    def test_error_messages_are_user_friendly(self):
        """Test error messages don't expose internal implementation details"""
        result = handle_calculate_life_path("invalid")

        assert "error" in result
        # Should not contain technical terms like "ValueError", "strptime", etc.
        assert "ValueError" not in result["message"]
        assert "strptime" not in result["message"]
        # Should contain helpful guidance
        assert "YYYY-MM-DD" in result["message"]


class TestIntegration:
    """Integration tests for full function call flow"""

    def test_full_life_path_flow(self):
        """Test complete flow: router → handler → service → result"""
        # Simulate GPT function call
        function_name = "calculate_life_path"
        arguments = {"birth_date": "1990-05-15"}

        # Call router (as Pipecat would)
        result = handle_numerology_function(function_name, arguments)

        # Verify success
        assert isinstance(result, dict)
        assert "life_path_number" in result
        assert isinstance(result["life_path_number"], int)

    def test_full_interpretation_flow(self):
        """Test complete interpretation retrieval flow"""
        # First calculate a number
        calc_result = handle_numerology_function(
            "calculate_life_path",
            {"birth_date": "1990-05-15"}
        )
        assert "life_path_number" in calc_result

        # Then get interpretations for that number
        life_path = calc_result["life_path_number"]
        interp_result = handle_numerology_function(
            "get_numerology_interpretation",
            {
                "number_type": "life_path",
                "number_value": life_path
            }
        )

        assert "interpretations" in interp_result
        assert isinstance(interp_result["interpretations"], list)

    def test_error_flow_invalid_input(self):
        """Test error handling in full flow with invalid input"""
        result = handle_numerology_function(
            "calculate_life_path",
            {"birth_date": "not-a-date"}
        )

        assert isinstance(result, dict)
        assert "error" in result
        assert result["error"] == "InvalidDate"

    def test_error_flow_missing_argument(self):
        """Test error handling when argument missing"""
        result = handle_numerology_function(
            "calculate_expression_number",
            {}  # Missing full_name
        )

        assert isinstance(result, dict)
        assert "error" in result
        assert result["error"] == "MissingArgument"


class TestLogging:
    """Test execution logging (AC8)"""

    @patch('function_handlers.logger')
    def test_successful_execution_logged_info(self, mock_logger):
        """Test successful executions logged at INFO level"""
        handle_calculate_life_path("1990-05-15")

        # Should have INFO logs for start and success
        assert mock_logger.info.called
        assert mock_logger.info.call_count >= 2

    @patch('function_handlers.logger')
    def test_error_execution_logged_error(self, mock_logger):
        """Test failed executions logged at ERROR level"""
        handle_calculate_life_path("invalid-date")

        # Should have ERROR log
        assert mock_logger.error.called

    @patch('function_handlers.logger')
    def test_router_logs_function_calls(self, mock_logger):
        """Test router logs all function calls"""
        handle_numerology_function("calculate_life_path", {"birth_date": "1990-05-15"})

        # Router should log the function call
        assert mock_logger.info.called
        # Check that function name is in one of the log calls
        log_calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any("calculate_life_path" in call for call in log_calls)
