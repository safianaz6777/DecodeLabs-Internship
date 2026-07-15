"""
Pydantic models define the STRICT output schema the model must return.
Used with OpenAI's structured outputs (text_format=MarketingCopy) so we
never have to hand-parse free text.
"""

from typing import List, Literal
from pydantic import BaseModel, Field


class MarketingCopy(BaseModel):
    platform: Literal["linkedin", "instagram", "email"]
    subject_or_headline: str = Field(
        description="Email subject line, or headline/hook for LinkedIn/Instagram"
    )
    body: str = Field(description="The main marketing copy body")
    call_to_action: str = Field(description="A short, punchy closing CTA line")
    hashtags: List[str] = Field(
        default_factory=list,
        description="Relevant hashtags. Leave empty for email.",
    )
    character_count: int = Field(
        description="Total character count of subject_or_headline + body + call_to_action"
    )
