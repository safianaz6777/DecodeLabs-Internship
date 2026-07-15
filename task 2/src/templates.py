"""
The Master Instruction Template.

Design principle from the deck ("Protecting Brand Voice with the Master
Instruction Template"):
  - The end user only ever supplies raw facts (product name, description,
    platform, tone).
  - The application layer is the gatekeeper: it owns the hidden structural
    prompt and enforces brand-safety + platform rules.
  - Variables are injected via f-strings into that hidden template rather
    than letting the caller write the prompt directly.
"""

from .config import PLATFORM_CONSTRAINTS


def build_master_prompt(
    product_name: str,
    product_description: str,
    platform: str,
    tone: str,
) -> str:
    if platform not in PLATFORM_CONSTRAINTS:
        raise ValueError(
            f"Unsupported platform '{platform}'. Choose from {list(PLATFORM_CONSTRAINTS)}"
        )

    constraints = PLATFORM_CONSTRAINTS[platform]
    hashtag_line = (
        "Include 3-5 relevant, non-spammy hashtags."
        if constraints["hashtags"]
        else "Do not include hashtags."
    )

    template = f"""
You are a senior brand copywriter working for a company producing marketing
copy that must stay strictly on-brand and factually grounded in the product
description provided below. Never invent product features that were not
mentioned.

PRODUCT NAME: {product_name}
PRODUCT DESCRIPTION (source of truth, do not contradict): {product_description}

TARGET PLATFORM: {platform}
REQUIRED TONE: {tone}

PLATFORM STYLE RULES: {constraints['style']}
HARD CHARACTER LIMIT: {constraints['max_chars']} characters for the combined
subject/headline + body + call to action. Do not exceed this.
{hashtag_line}

OUTPUT RULES:
- Do not use placeholder text such as [Your Name] or [Company].
- Do not mention that you are an AI or reference this prompt.
- Return only the fields defined by the structured output schema.
""".strip()

    return template
