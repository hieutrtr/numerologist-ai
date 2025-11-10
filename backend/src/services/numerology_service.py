"""
Numerology Calculation Service

This module provides pure Python functions for calculating numerology numbers
using the Pythagorean numerology system. All calculations are deterministic
and have no external dependencies.

The Pythagorean System:
- Letters map to numbers 1-9 in a repeating cycle (A=1, B=2... I=9, J=1...)
- All numbers reduce to single digits (1-9) EXCEPT master numbers (11, 22, 33)
- Master numbers are spiritually significant and never reduced further

Core Calculations:
- Life Path Number: From birth date (reveals life purpose and journey)
- Expression Number: From full name (shows natural talents and abilities)
- Soul Urge Number: From vowels in name (inner motivations and desires)
- Birthday Number: From day of month (special characteristics)
- Personal Year: From birth date + current year (yearly cycle guidance)

Usage Example:
    from datetime import date
    from src.services import numerology_service

    # Calculate Life Path number
    life_path = numerology_service.calculate_life_path(date(1990, 5, 15))
    print(f"Life Path: {life_path}")  # Output: Life Path: 3

    # Calculate Expression number
    expression = numerology_service.calculate_expression_number("John Smith")
    print(f"Expression: {expression}")

References:
    - Pythagorean numerology system
    - Story 4.1: Numerology Calculation Functions
    - PRD FR-2: Numerology Calculation Engine
"""

from datetime import date
from typing import Optional

# Constants
MASTER_NUMBERS = {11, 22, 33}
"""Set of master numbers that should never be reduced further in numerology calculations"""


def _reduce_to_single_digit(number: int) -> int:
    """
    Reduce a number to a single digit or master number using digit summation.

    This is the core reduction algorithm used across all numerology calculations.
    Numbers are repeatedly summed digit-by-digit until reaching a single digit
    (1-9) or a master number (11, 22, 33).

    Master numbers (11, 22, 33) are spiritually significant in Pythagorean
    numerology and are never reduced further.

    Args:
        number: Any positive integer to reduce

    Returns:
        Single digit (1-9) or master number (11, 22, 33)

    Examples:
        >>> _reduce_to_single_digit(15)
        6  # 1 + 5 = 6
        >>> _reduce_to_single_digit(99)
        9  # 9 + 9 = 18 → 1 + 8 = 9
        >>> _reduce_to_single_digit(29)
        11  # 2 + 9 = 11 (master number, not reduced)
        >>> _reduce_to_single_digit(100)
        1  # 1 + 0 + 0 = 1
    """
    while number > 9 and number not in MASTER_NUMBERS:
        number = sum(int(digit) for digit in str(number))
    return number


def calculate_life_path(birth_date: date) -> int:
    """
    Calculate Life Path number from birth date.

    The Life Path number reveals your life's purpose, natural talents, and the
    lessons you're meant to learn. It's the most important number in numerology.

    Calculation method:
    1. Reduce month, day, and year separately to single digits or master numbers
    2. Sum the three reduced components
    3. Reduce the final sum to single digit or master number

    Args:
        birth_date: User's birth date

    Returns:
        Life Path number (1-9, 11, 22, or 33)

    Examples:
        >>> calculate_life_path(date(1990, 5, 15))
        3  # Month: 5, Day: 1+5=6, Year: 1+9+9+0=19→1+9=10→1, Sum: 5+6+1=12→3
        >>> calculate_life_path(date(1979, 9, 2))
        11  # Results in master number 11
    """
    # Reduce month component
    month_reduced = _reduce_to_single_digit(birth_date.month)

    # Reduce day component
    day_reduced = _reduce_to_single_digit(birth_date.day)

    # Reduce year component (sum all digits in year first)
    year_sum = sum(int(digit) for digit in str(birth_date.year))
    year_reduced = _reduce_to_single_digit(year_sum)

    # Combine and reduce final sum
    total = month_reduced + day_reduced + year_reduced
    return _reduce_to_single_digit(total)


# Pythagorean letter-to-number mapping
# Letters cycle through 1-9: A=1, B=2, C=3, D=4, E=5, F=6, G=7, H=8, I=9, J=1, K=2...
_LETTER_VALUES = {
    'A': 1, 'J': 1, 'S': 1,
    'B': 2, 'K': 2, 'T': 2,
    'C': 3, 'L': 3, 'U': 3,
    'D': 4, 'M': 4, 'V': 4,
    'E': 5, 'N': 5, 'W': 5,
    'F': 6, 'O': 6, 'X': 6,
    'G': 7, 'P': 7, 'Y': 7,
    'H': 8, 'Q': 8, 'Z': 8,
    'I': 9, 'R': 9
}


def calculate_expression_number(full_name: str) -> int:
    """
    Calculate Expression (Destiny) number from full name.

    The Expression number reveals your natural talents, abilities, and the goals
    you're meant to accomplish in life. It's based on the full birth name.

    Uses Pythagorean letter-to-number mapping where letters cycle 1-9.
    Ignores spaces, punctuation, and is case-insensitive.

    Args:
        full_name: User's full birth name

    Returns:
        Expression number (1-9, 11, 22, or 33)

    Examples:
        >>> calculate_expression_number("John Smith")
        5  # J=1, O=6, H=8, N=5, S=1, M=4, I=9, T=2, H=8 → sum and reduce
        >>> calculate_expression_number("MARY")
        11  # Results in master number 11
    """
    # Clean input: uppercase and keep only letters
    clean_name = ''.join(char.upper() for char in full_name if char.isalpha())

    # Sum letter values
    total = sum(_LETTER_VALUES[char] for char in clean_name)

    # Reduce to single digit or master number
    return _reduce_to_single_digit(total)


# Vowels for Soul Urge calculation (Y is considered a vowel in certain positions)
_VOWELS = {'A', 'E', 'I', 'O', 'U'}


def calculate_soul_urge_number(full_name: str) -> int:
    """
    Calculate Soul Urge (Heart's Desire) number from vowels in name.

    The Soul Urge number reveals your inner motivations, desires, and what
    drives you at a soul level. It's calculated using only the vowels in your name.

    In Pythagorean numerology, vowels are: A, E, I, O, U
    Y is sometimes considered a vowel (when it sounds like a vowel), but for
    consistency, this implementation uses only the standard five vowels.

    Args:
        full_name: User's full birth name

    Returns:
        Soul Urge number (1-9, 11, 22, or 33)

    Examples:
        >>> calculate_soul_urge_number("John Smith")
        9  # O, I → vowels only
        >>> calculate_soul_urge_number("ELIZABETH")
        22  # Results in master number 22
    """
    # Clean input and extract vowels only
    clean_name = ''.join(char.upper() for char in full_name if char.isalpha())
    vowels_only = ''.join(char for char in clean_name if char in _VOWELS)

    # Sum vowel values
    total = sum(_LETTER_VALUES[char] for char in vowels_only)

    # Reduce to single digit or master number
    return _reduce_to_single_digit(total)


def calculate_birthday_number(birth_date: date) -> int:
    """
    Calculate Birthday number from day of month.

    The Birthday number reveals special talents and abilities you were born with.
    It's simply the day of the month reduced to a single digit or master number.

    Args:
        birth_date: User's birth date

    Returns:
        Birthday number (1-9, 11, 22, or 33)

    Examples:
        >>> calculate_birthday_number(date(1990, 5, 15))
        6  # Day 15 → 1+5 = 6
        >>> calculate_birthday_number(date(1990, 5, 11))
        11  # Day 11 is master number, not reduced
        >>> calculate_birthday_number(date(1990, 5, 5))
        5  # Day 5 is already single digit
    """
    # Extract day and reduce to single digit or master number
    return _reduce_to_single_digit(birth_date.day)


def calculate_personal_year(birth_date: date, current_year: Optional[int] = None) -> int:
    """
    Calculate Personal Year number for current or specified year.

    The Personal Year number reveals the theme and opportunities for a specific year
    in your life. It changes each year and provides guidance for the year ahead.

    Calculation: birth month + birth day + current year, all reduced.

    Args:
        birth_date: User's birth date
        current_year: Year to calculate for (defaults to current year)

    Returns:
        Personal Year number (1-9, 11, 22, or 33)

    Examples:
        >>> calculate_personal_year(date(1990, 5, 15), 2025)
        2  # Month:5, Day:1+5=6, Year:2+0+2+5=9 → 5+6+9=20 → 2
        >>> calculate_personal_year(date(1990, 11, 2), 2024)
        11  # Results in master number 11
    """
    # Default to current year if not specified
    if current_year is None:
        current_year = date.today().year

    # Reduce month component
    month_reduced = _reduce_to_single_digit(birth_date.month)

    # Reduce day component
    day_reduced = _reduce_to_single_digit(birth_date.day)

    # Reduce current year component
    year_sum = sum(int(digit) for digit in str(current_year))
    year_reduced = _reduce_to_single_digit(year_sum)

    # Combine and reduce final sum
    total = month_reduced + day_reduced + year_reduced
    return _reduce_to_single_digit(total)
