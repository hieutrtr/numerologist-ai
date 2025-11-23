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
from typing import List, Dict
from datetime import datetime

try:
    import tiktoken
except ImportError:
    tiktoken = None
    logging.warning("tiktoken not available - token counting will be estimated")

from src.models.user import User

# Configure logger
logger = logging.getLogger(__name__)

# Path to the system prompt template
PROMPT_TEMPLATE_PATH = Path(__file__).parent / "prompts" / "aria_system_prompt.md"


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Count tokens in text using tiktoken.

    Provides accurate token counting for OpenAI models to ensure
    context stays within model limits.

    Args:
        text: Text content to count tokens for
        model: Model name for encoding (default: "gpt-4")

    Returns:
        int: Number of tokens in the text

    Note:
        If tiktoken is not available, estimates tokens as ~4 chars per token
    """
    if tiktoken is None:
        # Fallback estimation: roughly 4 characters per token
        estimated = len(text) // 4
        logger.debug(f"Estimated {estimated} tokens (tiktoken unavailable)")
        return estimated

    try:
        encoding = tiktoken.encoding_for_model(model)
        token_count = len(encoding.encode(text))
        logger.debug(f"Counted {token_count} tokens in text ({len(text)} chars)")
        return token_count
    except Exception as e:
        logger.warning(f"Error counting tokens: {e} - falling back to estimation")
        return len(text) // 4


def format_conversation_history(
    conversations: List[Dict],
    max_tokens: int = 500
) -> str:
    """
    Format conversation summaries for system prompt with token limits.

    Creates a concise summary of past conversations optimized for LLM context.
    If the formatted context exceeds max_tokens, progressively reduces the
    number of conversations until it fits.

    Args:
        conversations: List of conversation dicts with keys:
            - date: ISO 8601 timestamp string
            - topic: Main topic discussed
            - insights: Key insights (truncated to 100 chars)
            - numbers: Numbers discussed (comma-separated)
        max_tokens: Maximum tokens allowed for context (default: 500)

    Returns:
        Formatted conversation history string ready for system prompt.
        Returns empty string if no conversations provided.

    Example:
        conversations = [
            {
                "date": "2025-11-23T10:30:00Z",
                "topic": "Life Path Number",
                "insights": "User resonates with leadership",
                "numbers": "1, 11"
            }
        ]
        context = format_conversation_history(conversations)
        # Returns: "Previous conversations with this user:\\n1. Nov 23: Life Path Number..."
    """
    if not conversations:
        return ""

    def _format_conversations(convs: List[Dict]) -> str:
        """Inner function to format a specific number of conversations."""
        parts = ["Previous conversations with this user:"]

        for i, conv in enumerate(convs, 1):
            try:
                # Parse and format date
                date_obj = datetime.fromisoformat(conv["date"].replace("Z", "+00:00"))
                date_str = date_obj.strftime("%b %d")
            except (ValueError, KeyError):
                date_str = "Recent"

            topic = conv.get("topic", "General discussion")
            insights = conv.get("insights", "")[:100]  # Truncate to 100 chars
            numbers = conv.get("numbers", "")

            # Build conversation entry
            entry = f"{i}. {date_str}: {topic}."
            if numbers:
                entry += f" Discussed numbers: {numbers}."
            if insights:
                entry += f" Key insight: {insights}"

            parts.append(entry)

        return "\n".join(parts)

    # Try formatting all conversations
    context = _format_conversations(conversations)
    token_count = count_tokens(context)

    # If within limit, return as-is
    if token_count <= max_tokens:
        logger.debug(
            f"Formatted {len(conversations)} conversations "
            f"({token_count} tokens, under {max_tokens} limit)"
        )
        return context

    # Progressively reduce conversations until under limit
    for reduced_count in range(len(conversations) - 1, 0, -1):
        context = _format_conversations(conversations[:reduced_count])
        token_count = count_tokens(context)

        if token_count <= max_tokens:
            logger.info(
                f"Reduced to {reduced_count} conversations to fit token limit "
                f"({token_count} tokens)"
            )
            return context

    # If even 1 conversation is too long, return minimal context
    minimal = f"User has {len(conversations)} previous conversations about numerology."
    logger.warning(
        f"Could not fit any full conversations in {max_tokens} tokens - "
        f"returning minimal context"
    )
    return minimal


def get_numerology_system_prompt(user: User, conversation_history: str = "") -> str:
    """
    Generate a Vietnamese system prompt for the numerology voice AI bot with conversation context.

    This function creates a personalized system prompt that:
    1. Defines the AI's role as a master Pythagorean numerologist (Aria)
    2. Specifies knowledge scope (Life Path, Expression, Soul Urge, etc.)
    3. Instructs on when to use calculation functions
    4. Sets conversational style (natural, warm, knowledgeable)
    5. Establishes boundaries (no medical, legal, financial advice)
    6. Personalizes with user's name and birth date
    7. **NEW:** Includes previous conversation context for continuity

    The prompt is loaded from a markdown template file and personalized with user data.
    Function names remain in English (required for OpenAI function calling reliability).

    Args:
        user (User): User object containing full_name and birth_date for personalization
        conversation_history (str): Formatted conversation history context from previous sessions.
                                   If provided, enables AI to reference past discussions naturally.

    Returns:
        str: Complete Vietnamese system prompt for Pipecat LLM context with conversation history

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

        # Append conversation history if provided
        if conversation_history:
            prompt += f"\n\n{conversation_history}\n\n"
            prompt += """
## Tận dụng lịch sử trò chuyện (Using Conversation History)

Bạn đã có lịch sử trò chuyện với người dùng này. Hãy sử dụng thông tin đó một cách tự nhiên và chân thành:

**Khi chào hỏi:**
- Chào hỏi ấm áp và nhắc đến chủ đề đã thảo luận trước đó
- Ví dụ: "Chào {user_name}! Rất vui được gặp lại bạn. Lần trước chúng ta đã nói về [chủ đề]..."
- Thể hiện sự quan tâm thực sự đến hành trình của họ

**Khi trả lời câu hỏi:**
- Liên hệ với những gì đã biết từ cuộc trò chuyện trước
- Ví dụ: "Như mình đã chia sẻ lần trước, [số] của bạn cho thấy [đặc điểm]. Hôm nay chúng ta có thể đào sâu hơn về..."
- Xây dựng dựa trên những insight đã có thay vì lặp lại

**Khi khám phá sâu hơn:**
- Nhận ra các mẫu hình (patterns) xuyên suốt các cuộc trò chuyện
- Ví dụ: "Bạn có nhớ lần trước mình nói về [đặc điểm]? Điều bạn đang chia sẻ hôm nay phản ánh đúng bản chất đó..."
- Giúp người dùng thấy sự liên kết giữa các khía cạnh numerology khác nhau

**Khi người dùng hỏi lại:**
- Nếu họ hỏi về thông tin đã thảo luận, hãy tóm tắt ngắn gọn và đề nghị đào sâu thêm
- Ví dụ: "Đúng rồi, số [X] của bạn... Lần này bạn muốn khám phá khía cạnh nào của nó?"

**Nguyên tắc quan trọng:**
- Đừng lặp lại y hệt những gì đã nói trước đó
- Luôn mang đến giá trị mới trong mỗi cuộc trò chuyện
- Thể hiện sự tiến triển và hiểu biết sâu hơn về người dùng
- Giữ không khí thân thiện, ấm áp như gặp lại người bạn thân

Hãy làm cho người dùng cảm thấy được nhớ đến, được hiểu, và mỗi cuộc trò chuyện đều có ý nghĩa riêng.
"""
            logger.info(
                f"Generated system prompt with enhanced conversation history guidance for user: {user_name} "
                f"({len(conversation_history)} chars of context)"
            )
        else:
            logger.info(f"Generated system prompt (no conversation history) for user: {user_name}")

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
