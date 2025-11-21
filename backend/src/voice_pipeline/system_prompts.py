"""
Numerology System Prompt Generation

This module generates specialized system prompts for the numerology voice AI bot.
The system prompt defines the AI's role, knowledge boundaries, and conversation style
to create authentic, knowledgeable numerology interactions.

Strategy: Vietnamese System Prompt + English Function Definitions
- System prompt is 100% Vietnamese to provide authentic user experience
- Function definitions stay in English (verified OpenAI best practice for reliability)
- Handler functions language-agnostic (implementation layer)

This approach is based on:
- OpenAI Function Calling Documentation
- arXiv Research: "Enhancing Function-Calling Capabilities in LLMs: Strategies for Multilingual Translation" (2024)
- Industry best practices from multilingual voice AI implementations

Integration with Pipecat bot (Story 4.4 function handlers + Story 4.3 tool definitions):
- System prompt instructs AI when/how to use calculate_life_path, calculate_expression_number, etc.
- Tool definitions (English schemas) handle the technical interface
- Result: Perfect Vietnamese conversation with reliable function calling
"""

import logging
from pathlib import Path
from src.models.user import User

# Configure logger
logger = logging.getLogger(__name__)

# Path to the system prompt template
PROMPT_TEMPLATE_PATH = Path(__file__).parent / "prompts" / "aria_system_prompt.md"


def get_numerology_system_prompt(user: User) -> str:
    """
    Generate a Vietnamese system prompt for the numerology voice AI bot.

    This function creates a personalized system prompt that:
    1. Defines the AI's role as a master Pythagorean numerologist (Aria)
    2. Specifies knowledge scope (Life Path, Expression, Soul Urge, etc.)
    3. Instructs on when to use calculation functions
    4. Sets conversational style (natural, warm, knowledgeable)
    5. Establishes boundaries (no medical, legal, financial advice)
    6. Personalizes with user's name and birth date

    The prompt is loaded from a markdown template file and personalized with user data.
    Function names remain in English (required for OpenAI function calling reliability).

    Args:
        user (User): User object containing full_name and birth_date for personalization

    Returns:
        str: Complete Vietnamese system prompt for Pipecat LLM context

    Raises:
        No exceptions - handles missing data gracefully with fallbacks
    """
    try:
        # Format user's birth date in Vietnamese format (DD/MM/YYYY)
        if user.birth_date is not None:
            birth_date_formatted = user.birth_date.strftime('%d/%m/%Y')
        else:
            birth_date_formatted = 'Chưa cung cấp'

        # Handle None full_name
        user_name = user.full_name if user.full_name else 'bạn'

        # Load system prompt template from markdown file
        prompt_template = PROMPT_TEMPLATE_PATH.read_text(encoding='utf-8')

        # Substitute user-specific variables
        prompt = prompt_template.format(
            user_name=user_name,
            birth_date_formatted=birth_date_formatted
        )

        logger.info(f"Generated structured Vietnamese system prompt for user: {user_name}")
        return prompt

    except FileNotFoundError:
        logger.error(f"System prompt template not found at: {PROMPT_TEMPLATE_PATH}", exc_info=True)
        return _get_fallback_prompt()
    except Exception as e:
        logger.error(f"Error generating system prompt: {str(e)}", exc_info=True)
        return _get_fallback_prompt()


def _get_fallback_prompt() -> str:
    """
    Return a fallback system prompt if the main template cannot be loaded.

    Returns:
        str: Minimal but functional Vietnamese system prompt
    """
    fallback_prompt = """<agent name="Aria" role="Nhà Thần Số Học">

Tôi là Aria, một nhà thần số học Pythagorean. Tôi ấm áp, khôn ngoan, và thực sự quan tâm đến việc
giúp bạn hiểu biết về thần số học.

<knowledge>
- Life Path Number (Số Đường Đời): Tính từ ngày sinh
- Expression Number (Số Biểu Hiện): Tính từ họ tên
- Soul Urge Number (Số Khát Khao): Tính từ nguyên âm trong tên
- Master Numbers: 11, 22, 33
</knowledge>

<style>
Tôi nói chuyện tự nhiên, thân mật, và chậm rãi. Mỗi lần chỉ chia sẻ một ý tưởng, và luôn lắng nghe
phản hồi của bạn trước khi tiếp tục. Tôi đặt câu hỏi để hiểu sâu hơn về tình huống của bạn.
</style>

<tools>
- calculate_life_path(birth_date): Tính Số Đường Đời
- calculate_expression_number(full_name): Tính Số Biểu Hiện
- calculate_soul_urge_number(full_name): Tính Số Khát Khao
- get_numerology_interpretation(number_type, number_value): Lấy giải nghĩa
</tools>

<boundaries>
Thần số học là để giải trí và hướng dẫn tâm linh. Tôi không đưa ra lời khuyên về y tế, pháp lý,
hoặc tài chính. Nếu vấn đề nghiêm trọng, tôi khuyến khích bạn tìm trợ giúp chuyên nghiệp.
</boundaries>

Chào bạn! Mình là Aria. Hôm nay bạn muốn khám phá điều gì về bản thân qua thần số học nhỉ?

</agent>"""

    logger.warning("Using fallback prompt")
    return fallback_prompt
