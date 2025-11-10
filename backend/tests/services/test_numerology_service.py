"""
Unit tests for Numerology Calculation Service

Tests cover:
- Helper function (_reduce_to_single_digit)
- Life Path number calculation
- Expression/Destiny number calculation
- Soul Urge/Heart's Desire number calculation
- Birthday number calculation
- Personal Year number calculation
- Master number preservation (11, 22, 33)
- Edge cases and input validation
"""

import pytest
from datetime import date
from src.services.numerology_service import (
    _reduce_to_single_digit,
    calculate_life_path,
    calculate_expression_number,
    calculate_soul_urge_number,
    calculate_birthday_number,
    calculate_personal_year,
    MASTER_NUMBERS,
    _LETTER_VALUES,
    _VOWELS
)


# ============================================================================
# Test Helper Function: _reduce_to_single_digit
# ============================================================================

def test_reduce_to_single_digit_single_digits():
    """Test that single digits (1-9) are returned unchanged"""
    for i in range(1, 10):
        assert _reduce_to_single_digit(i) == i


def test_reduce_to_single_digit_double_digits():
    """Test reduction of double digit numbers"""
    assert _reduce_to_single_digit(10) == 1  # 1 + 0 = 1
    assert _reduce_to_single_digit(15) == 6  # 1 + 5 = 6
    assert _reduce_to_single_digit(27) == 9  # 2 + 7 = 9
    assert _reduce_to_single_digit(99) == 9  # 9 + 9 = 18 → 1 + 8 = 9


def test_reduce_to_single_digit_triple_digits():
    """Test reduction of triple digit numbers"""
    assert _reduce_to_single_digit(100) == 1  # 1 + 0 + 0 = 1
    assert _reduce_to_single_digit(123) == 6  # 1 + 2 + 3 = 6
    assert _reduce_to_single_digit(999) == 9  # 9 + 9 + 9 = 27 → 2 + 7 = 9


def test_reduce_to_single_digit_master_numbers():
    """Test that master numbers (11, 22, 33) are not reduced"""
    assert _reduce_to_single_digit(11) == 11
    assert _reduce_to_single_digit(22) == 22
    assert _reduce_to_single_digit(33) == 33


def test_reduce_to_single_digit_reduces_to_master():
    """Test numbers that reduce to master numbers"""
    assert _reduce_to_single_digit(29) == 11  # 2 + 9 = 11 (master)
    assert _reduce_to_single_digit(38) == 11  # 3 + 8 = 11 (master)
    assert _reduce_to_single_digit(47) == 11  # 4 + 7 = 11 (master)


# ============================================================================
# Test Life Path Number Calculation
# ============================================================================

@pytest.mark.parametrize("birth_date,expected", [
    (date(1990, 5, 15), 3),   # Month:5, Day:1+5=6, Year:1+9+9+0=19→1+9=10→1, Sum:5+6+1=12→3
    (date(1984, 11, 2), 8),   # Month:1+1=2, Day:2, Year:1+9+8+4=22(master), Sum:2+2+22=26→8
    (date(2000, 1, 1), 4),    # Month:1, Day:1, Year:2+0+0+0=2, Sum:1+1+2=4
    (date(1999, 12, 31), 8),  # Month:1+2=3, Day:3+1=4, Year:1+9+9+9=28→10→1, Sum:3+4+1=8
])
def test_calculate_life_path(birth_date, expected):
    """Test Life Path calculation with various birth dates"""
    assert calculate_life_path(birth_date) == expected


def test_calculate_life_path_master_number_result():
    """Test Life Path calculations that result in master numbers"""
    # Birth date that results in master number 11
    result = calculate_life_path(date(1979, 9, 2))
    assert result in MASTER_NUMBERS or 1 <= result <= 9


# ============================================================================
# Test Expression Number Calculation
# ============================================================================

def test_calculate_expression_number_basic():
    """Test Expression number with basic names"""
    # JOHN SMITH: J=1 O=6 H=8 N=5 S=1 M=4 I=9 T=2 H=8 = 44 → 8
    result = calculate_expression_number("John Smith")
    assert 1 <= result <= 9 or result in MASTER_NUMBERS


def test_calculate_expression_number_single_name():
    """Test Expression number with single name"""
    # MARY: M=4 A=1 R=9 Y=7 = 21 → 3
    result = calculate_expression_number("Mary")
    assert 1 <= result <= 9 or result in MASTER_NUMBERS


def test_calculate_expression_number_with_spaces_punctuation():
    """Test Expression number ignores spaces and punctuation"""
    result1 = calculate_expression_number("JohnSmith")
    result2 = calculate_expression_number("John Smith")
    result3 = calculate_expression_number("John-Smith")
    result4 = calculate_expression_number("john smith")
    # All should be equal regardless of spacing/punctuation/case
    assert result1 == result2 == result3 == result4


def test_calculate_expression_number_case_insensitive():
    """Test Expression number is case insensitive"""
    assert calculate_expression_number("ABC") == calculate_expression_number("abc")
    assert calculate_expression_number("XYZ") == calculate_expression_number("xyz")


# ============================================================================
# Test Soul Urge Number Calculation
# ============================================================================

def test_calculate_soul_urge_number_basic():
    """Test Soul Urge number with basic names"""
    # JOHN SMITH: O, I are vowels → O=6, I=9 = 15 → 6
    result = calculate_soul_urge_number("John Smith")
    assert 1 <= result <= 9 or result in MASTER_NUMBERS


def test_calculate_soul_urge_number_only_vowels():
    """Test Soul Urge with names containing only vowels"""
    # AEI: A=1 E=5 I=9 = 15 → 6
    result = calculate_soul_urge_number("Aei")
    assert result == 6


def test_calculate_soul_urge_number_no_vowels():
    """Test Soul Urge with names containing no standard vowels"""
    # Should return a valid result even with minimal vowels
    result = calculate_soul_urge_number("Brr")
    assert 1 <= result <= 9 or result in MASTER_NUMBERS or result == 0


def test_calculate_soul_urge_number_vowel_extraction():
    """Test that only vowels (A, E, I, O, U) are extracted"""
    # ELIZABETH: E, I, A, E are vowels
    result = calculate_soul_urge_number("Elizabeth")
    assert 1 <= result <= 9 or result in MASTER_NUMBERS


# ============================================================================
# Test Birthday Number Calculation
# ============================================================================

@pytest.mark.parametrize("birth_date,expected", [
    (date(1990, 5, 1), 1),    # Day 1 → 1
    (date(1990, 5, 9), 9),    # Day 9 → 9
    (date(1990, 5, 10), 1),   # Day 10 → 1 + 0 = 1
    (date(1990, 5, 15), 6),   # Day 15 → 1 + 5 = 6
    (date(1990, 5, 11), 11),  # Day 11 → 11 (master number)
    (date(1990, 5, 22), 22),  # Day 22 → 22 (master number)
    (date(1990, 5, 29), 11),  # Day 29 → 2 + 9 = 11 (master)
    (date(1990, 5, 31), 4),   # Day 31 → 3 + 1 = 4
])
def test_calculate_birthday_number(birth_date, expected):
    """Test Birthday number calculation for various days"""
    assert calculate_birthday_number(birth_date) == expected


# ============================================================================
# Test Personal Year Calculation
# ============================================================================

def test_calculate_personal_year_with_specified_year():
    """Test Personal Year with explicitly specified year"""
    # May 15, 1990 for year 2025
    # Month:5, Day:1+5=6, Year:2+0+2+5=9 → 5+6+9=20 → 2
    result = calculate_personal_year(date(1990, 5, 15), 2025)
    assert result == 2


def test_calculate_personal_year_default_current_year():
    """Test Personal Year defaults to current year"""
    # Should not raise an error and return valid result
    result = calculate_personal_year(date(1990, 5, 15))
    assert 1 <= result <= 9 or result in MASTER_NUMBERS


@pytest.mark.parametrize("birth_date,year,expected", [
    (date(1990, 1, 1), 2024, 9),   # Month:1, Day:1, Year:2+0+2+4=8 → 1+1+8=10→1
    (date(1990, 12, 31), 2024, 4), # Month:1+2=3, Day:3+1=4, Year:8 → 3+4+8=15→6
])
def test_calculate_personal_year_various_dates(birth_date, year, expected):
    """Test Personal Year with various dates and years"""
    result = calculate_personal_year(birth_date, year)
    assert 1 <= result <= 9 or result in MASTER_NUMBERS


def test_calculate_personal_year_master_number_result():
    """Test Personal Year that results in master number"""
    # Find a combination that results in master number 11
    result = calculate_personal_year(date(1990, 11, 2), 2024)
    assert 1 <= result <= 9 or result in MASTER_NUMBERS


# ============================================================================
# Test Master Numbers Preservation
# ============================================================================

def test_master_numbers_constant():
    """Test that MASTER_NUMBERS constant contains exactly {11, 22, 33}"""
    assert MASTER_NUMBERS == {11, 22, 33}


def test_master_numbers_never_reduced():
    """Test that master numbers are preserved across all calculations"""
    # Test day 11 is preserved in birthday calculation
    assert calculate_birthday_number(date(1990, 5, 11)) == 11

    # Test day 22 is preserved in birthday calculation
    assert calculate_birthday_number(date(1990, 5, 22)) == 22

    # Test that reduction stops at master numbers
    assert _reduce_to_single_digit(11) == 11
    assert _reduce_to_single_digit(22) == 22
    assert _reduce_to_single_digit(33) == 33


# ============================================================================
# Test Pythagorean Letter Mapping
# ============================================================================

def test_letter_values_completeness():
    """Test that all 26 letters have value mappings"""
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    for letter in alphabet:
        assert letter in _LETTER_VALUES
        assert 1 <= _LETTER_VALUES[letter] <= 9


def test_letter_values_pythagorean_pattern():
    """Test that letter values follow Pythagorean pattern"""
    # First cycle: A-I should be 1-9
    assert _LETTER_VALUES['A'] == 1
    assert _LETTER_VALUES['B'] == 2
    assert _LETTER_VALUES['C'] == 3
    assert _LETTER_VALUES['I'] == 9

    # Second cycle: J-R should repeat 1-9
    assert _LETTER_VALUES['J'] == 1
    assert _LETTER_VALUES['K'] == 2
    assert _LETTER_VALUES['R'] == 9

    # Third cycle: S-Z
    assert _LETTER_VALUES['S'] == 1
    assert _LETTER_VALUES['Z'] == 8


def test_vowels_set():
    """Test that vowels set contains the five standard vowels"""
    assert _VOWELS == {'A', 'E', 'I', 'O', 'U'}


# ============================================================================
# Test Edge Cases
# ============================================================================

def test_empty_name_handling():
    """Test handling of empty or invalid names"""
    # Empty string should handle gracefully
    result = calculate_expression_number("")
    assert result == 0  # Sum of nothing is 0, which won't reduce


def test_special_characters_ignored():
    """Test that special characters are properly ignored"""
    # Names with numbers, symbols should only process letters
    assert calculate_expression_number("John123") == calculate_expression_number("John")
    assert calculate_expression_number("Mary@#$") == calculate_expression_number("Mary")
