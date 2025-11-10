"""
Numerology Interpretation Model

Defines the NumerologyInterpretation database model for storing expert
numerology guidance. This model serves as the knowledge base for AI-powered
numerology readings during voice conversations.

Each entry provides interpretation content for a specific numerology number
(1-9, 11, 22, 33) across various categories (personality, strengths, challenges,
career, relationships, etc.).
"""

from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4


class NumerologyInterpretation(SQLModel, table=True):
    """
    Numerology interpretation knowledge base model.

    Stores comprehensive interpretations for all numerology number types across
    multiple categories. Used by AI to provide detailed, accurate guidance during
    voice conversations based on calculated numerology numbers.

    Number Types:
        - life_path: Core life purpose and journey
        - expression: Natural talents and abilities
        - soul_urge: Inner motivations and desires
        - birthday: Special characteristics from birth day
        - personal_year: Current year cycle themes

    Categories:
        - personality: Core personality traits
        - strengths: Natural abilities and gifts
        - challenges: Areas of growth and difficulty
        - career: Professional path guidance
        - relationships: Interpersonal dynamics
        - talents: Specific skills and abilities
        - abilities: Natural capabilities
        - purpose: Life purpose and mission
        - spiritual: Spiritual growth aspects

    Master Numbers:
        11, 22, 33 are spiritually significant and have unique interpretations
        that differ from their reduced forms (2, 4, 6).

    Example:
        Life Path 1 might have entries:
        - category="personality": "Natural-born leader with independence..."
        - category="strengths": "Initiative, courage, determination..."
        - category="challenges": "Can be overly aggressive or impatient..."
    """

    __tablename__ = "numerology_interpretation"

    # Primary key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the interpretation"
    )

    # Core fields
    number_type: str = Field(
        index=True,
        description="Type of numerology number (life_path, expression, soul_urge, birthday, personal_year)"
    )
    number_value: int = Field(
        index=True,
        description="The number value (1-9 or master numbers 11, 22, 33)"
    )
    category: str = Field(
        description="Interpretation category (personality, strengths, challenges, career, relationships, etc.)"
    )
    content: str = Field(
        description="The interpretation text (2-4 sentences, specific and actionable)"
    )

    # Metadata fields
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when interpretation was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when interpretation was last updated"
    )
