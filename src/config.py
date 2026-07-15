"""
Central configuration: platform constraints + the "Parameter Tuning Spectrum"
described in the training deck (Temperature/Top_P per tone, token-param
routing for legacy vs reasoning models).
"""

# ---- Platform-specific filtering (character limits & style) ----------------
PLATFORM_CONSTRAINTS = {
    "linkedin": {
        "max_chars": 3000,
        "style": "professional, thought-leadership tone, minimal emoji",
        "hashtags": True,
    },
    "instagram": {
        "max_chars": 2200,
        "style": "casual, visual, emoji-friendly, punchy short sentences",
        "hashtags": True,
    },
    "email": {
        "max_chars": 1500,
        "style": "direct, persuasive, formal structure with a clear subject line",
        "hashtags": False,
    },
}

# ---- Tone -> Temperature spectrum ------------------------------------------
# Low temperature (~0.2)  -> consistent, factual, professional (emails)
# High temperature (~0.8) -> diverse phrasing, witty hooks (social media)
TONE_TEMPERATURE_MAP = {
    "professional": 0.2,
    "formal": 0.2,
    "informative": 0.3,
    "persuasive": 0.5,
    "casual": 0.6,
    "friendly": 0.6,
    "witty": 0.8,
    "playful": 0.85,
    "bold": 0.85,
}
DEFAULT_TEMPERATURE = 0.5
TOP_P_DEFAULT = 0.9

# ---- Token-limit decision tree ---------------------------------------------
# Legacy models (gpt-4, gpt-3.5-turbo)   -> max_tokens        (50-500, safety buffer)
# Reasoning models (o1, gpt-4o family)   -> max_completion_tokens (150-300)
LEGACY_MODELS = {"gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"}
REASONING_MODELS = {"gpt-4o", "gpt-4o-mini", "o1", "o1-mini"}


def token_param_for_model(model_name: str) -> str:
    """Return the correct token-limit kwarg name for the given model family."""
    if model_name in REASONING_MODELS:
        return "max_completion_tokens"
    return "max_tokens"


def temperature_for_tone(tone: str) -> float:
    return TONE_TEMPERATURE_MAP.get(tone.lower().strip(), DEFAULT_TEMPERATURE)
