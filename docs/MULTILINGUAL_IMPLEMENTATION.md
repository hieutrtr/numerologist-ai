# Multilingual Implementation Guide: Vietnamese Voice Bot

## Overview

This document provides verified best practices for implementing Vietnamese language support in the Numerologist AI voice bot while maintaining reliable OpenAI function calling.

## ✅ Research Verified: English Functions + Vietnamese Prompts

**Status**: Recommended approach confirmed by:
- OpenAI Function Calling Documentation
- OpenAI Community discussions
- arXiv research paper: "Enhancing Function-Calling Capabilities in LLMs: Strategies for Multilingual Translation" (Dec 2024)
- Industry best practices from multilingual LLM implementations

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    User (Vietnamese)                     │
│              "Tính số đường đời của tôi"                │
└────────────────────────┬─────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────┐
│           Pipecat Voice Bot (Vietnamese)                 │
├──────────────────────────────────────────────────────────┤
│  System Prompt (Vietnamese):                             │
│  ├─ Role: "Nhà số học Pythagorean"                      │
│  ├─ Instructions: Entirely in Vietnamese                 │
│  ├─ User Context: Personalized in Vietnamese            │
│  └─ Conversation: All responses in Vietnamese           │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│     Function Calling (English JSON Schema)                │
├──────────────────────────────────────────────────────────┤
│  Functions (Story 4.3 - numerology_functions.py):       │
│  ├─ calculate_life_path                                  │
│  ├─ calculate_expression_number                          │
│  ├─ calculate_soul_urge_number                           │
│  └─ get_numerology_interpretation                        │
│                                                          │
│  ⚠️ All descriptions stay in English (required!)         │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│     Handler Functions (Story 4.4 - No Changes)            │
├──────────────────────────────────────────────────────────┤
│  function_handlers.py:                                   │
│  ├─ handle_calculate_life_path()                         │
│  ├─ handle_calculate_expression()                        │
│  ├─ handle_calculate_soul_urge()                         │
│  ├─ handle_get_interpretation()                          │
│  └─ handle_numerology_function() [router]                │
│                                                          │
│  Python implementation layer - no language changes      │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│      Response Back to User (Vietnamese)                    │
│  "Số đường đời của bạn là 7. Điều này có nghĩa..."       │
└────────────────────────────────────────────────────────────┘
```

## Key Implementation Decisions

### ✅ What Goes in Vietnamese (System Prompt)

**File**: `backend/src/voice_pipeline/system_prompts.py`
**Function**: `get_numerology_system_prompt(user: User) -> str`

**Content entirely in Vietnamese**:
- Role definition: "Bạn là một nhà số học Pythagorean..."
- Knowledge scope: "Số Đường Đời, Biểu Hiện, Thúc Đẩy Tâm Hồn..."
- Tool instructions: "Sử dụng calculate_life_path để..."
- Conversation style guidelines: "Nói chuyện tự nhiên..."
- Boundaries and guardrails: "Không đưa ra lời khuyên y tế..."
- User context: Name and birth date in Vietnamese format
- Opening greeting: "Chào mừng..."

**User Experience**:
- All visible text is Vietnamese
- Conversation feels natural in Vietnamese
- User never sees English prompts

### ⚠️ What MUST Stay in English (Function Definitions)

**File**: `backend/src/voice_pipeline/numerology_functions.py` (Story 4.3)
**Status**: DO NOT MODIFY or TRANSLATE

**Must remain in English**:
```json
{
  "type": "function",
  "function": {
    "name": "calculate_life_path",           // ← English
    "description": "Calculate the user's...", // ← English
    "parameters": {
      "type": "object",
      "properties": {
        "birth_date": {
          "type": "string",
          "description": "User's birth date..." // ← English
        }
      }
    }
  }
}
```

**Why English is Required**:
1. **Tokenization**: OpenAI models tokenize English more efficiently
2. **Function Calling Reliability**: Non-English function schemas increase hallucination risk
3. **Schema Compatibility**: JSON schemas work best with English technical terms
4. **No User Visibility**: Function definitions never appear to user

### ✅ Handler Functions Unchanged (Story 4.4)

**File**: `backend/src/voice_pipeline/function_handlers.py`
**Status**: NO CHANGES NEEDED

**Why**:
- Implementation layer (Python backend)
- Not user-facing
- Language-independent logic
- Already tested and working

## Translation Guide

### Vietnamese Translation Examples

**English System Prompt** → **Vietnamese System Prompt**

| Concept | English | Vietnamese |
|---------|---------|-----------|
| Role | Master Pythagorean numerologist | Nhà số học Pythagorean |
| Personality | Aria, warm and wise | Aria, ấm áp và khôn ngoan |
| Knowledge | Life Path, Expression, Soul Urge | Số Đường Đời, Biểu Hiện, Thúc Đẩy |
| Master Numbers | Master Numbers (11, 22, 33) | Các Số Chủ (11, 22, 33) |
| Tools section | Use calculate_life_path | Sử dụng calculate_life_path |
| Conversation style | Speak naturally | Nói chuyện tự nhiên |
| Boundaries | For entertainment only | Chỉ cho giải trí |
| Medical advice | Don't give medical advice | Không đưa ra lời khuyên y tế |

### Function Names Stay English

Even in Vietnamese prompt, function names remain English:

```
❌ WRONG:
"Sử dụng tính_số_đường_đời để..."

✅ CORRECT:
"Sử dụng calculate_life_path để..."
```

Function names are identifiers that must match the JSON schema exactly.

## User Experience Flow

```
User speaks in Vietnamese:
"Tính số đường đời của tôi, ngày sinh 1990-05-15"

↓ Pipecat STT (Vietnamese)

AI Understands: Vietnamese text + Vietnamese system prompt

↓ AI Decides to Call Function

AI Calls: calculate_life_path({"birth_date": "1990-05-15"})

↓ Handler Executes (English function, no problem)

Returns: {"life_path_number": 7}

↓ AI Generates Response (Vietnamese system prompt guides this)

AI Says (Vietnamese):
"Số đường đời của bạn là 7. Điều này có nghĩa rằng bạn là
một người sáng tạo và biểu hiện..."

↓ Pipecat TTS (Vietnamese)

User hears Vietnamese response about their numerology reading
```

## Implementation Checklist

### Story 4.5: System Prompt (Vietnamese)
- [ ] Create `backend/src/voice_pipeline/system_prompts.py`
- [ ] Implement `get_numerology_system_prompt(user: User) -> str`
- [ ] Generate entire prompt in Vietnamese
- [ ] Include user personalization (name, birth date in Vietnamese format)
- [ ] Include tool instructions (tool names stay English)
- [ ] Add comprehensive boundaries section
- [ ] Test with various users
- [ ] Verify all output is Vietnamese

### Story 4.3: Function Definitions (Already Done - DO NOT CHANGE)
- [x] Keep `numerology_functions.py` in English
- [x] All function names in English
- [x] All descriptions in English
- [x] JSON schema in English

### Story 4.4: Function Handlers (Already Done - NO CHANGES)
- [x] Keep `function_handlers.py` as-is
- [x] No language-related modifications needed
- [x] Implementation layer remains unchanged

### Pipecat Bot Integration
- [ ] Import Vietnamese system prompt function
- [ ] Pass User object to `get_numerology_system_prompt()`
- [ ] Set system message with Vietnamese prompt
- [ ] Register tools (English definitions from Story 4.3)
- [ ] Wire function handler (from Story 4.4)
- [ ] Test end-to-end with Vietnamese conversation

## Testing Strategy

### Unit Tests (Vietnamese Prompt Generation)
```python
def test_get_numerology_system_prompt_vietnamese():
    user = User(full_name="Nguyễn Văn A", birth_date=date(1990, 5, 15))
    prompt = get_numerology_system_prompt(user)

    # Verify Vietnamese content
    assert "nhà số học Pythagorean" in prompt
    assert "Nguyễn Văn A" in prompt
    assert "15/05/1990" in prompt  # Vietnamese date format
    assert "Aria" in prompt

    # Verify function names stay English
    assert "calculate_life_path" in prompt
    assert "get_numerology_interpretation" in prompt

    # Verify boundaries in Vietnamese
    assert "không đưa ra lời khuyên" in prompt
```

### Integration Tests (End-to-End)
1. Start conversation with Vietnamese-speaking user
2. User asks: "Tính số đường đời của tôi"
3. AI responds in Vietnamese with calculation
4. AI calls calculate_life_path function
5. AI explains result in Vietnamese
6. Verify no English text appears to user
7. Verify function calling works correctly

### Function Calling Tests
1. Verify calculate_life_path accepts same parameters
2. Verify handlers return same format
3. Verify no translation-related errors
4. Verify logging still works

## Troubleshooting

### Issue: AI responds in English instead of Vietnamese
**Solution**: Ensure system prompt is entirely in Vietnamese, including all example instructions.

### Issue: Function calling fails
**Solution**: Check that function definitions in `numerology_functions.py` were NOT modified and remain in English.

### Issue: Date format inconsistency
**Solution**: Use Vietnamese date format in prompt (15/05/1990) but pass ISO format to functions (1990-05-15).

### Issue: User sees English function names
**Solution**: This is expected and correct. Function names must stay English internally - users don't see them.

## References

- OpenAI Function Calling: https://platform.openai.com/docs/guides/function-calling
- OpenAI Community Discussion: "Function calling in different language than english"
- Research Paper: Yi-Chang Chen et al., "Enhancing Function-Calling Capabilities in LLMs: Strategies for Multilingual Translation" (arXiv:2412.01130)
- Pipecat Documentation: https://docs.pipecat.ai/
- Best Practice: English schemas for reliability, native language for user experience

## Summary

✅ **The Strategy Works Because**:
1. System prompts guide all user-facing output (Vietnamese)
2. Function definitions are implementation details (English schema)
3. GPT understands to use functions in English schema regardless of system prompt language
4. Users experience entirely Vietnamese conversation
5. Function calling remains reliable and predictable

**Implementation is straightforward**:
- Story 4.5 generates Vietnamese prompts
- Stories 4.3 and 4.4 remain unchanged
- Pipecat integration combines both
- Result: Authentic Vietnamese conversation with reliable function calling
