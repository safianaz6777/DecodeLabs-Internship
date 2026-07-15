"""
Real-time async pipeline.

- httpx-style async client (openai's AsyncOpenAI, pointed at Groq's free
  OpenAI-compatible endpoint by default) so a single slow request doesn't
  block the whole program.
- asyncio.Semaphore caps concurrent connections to avoid HTTP 429s.
- tenacity gives randomized exponential backoff on transient failures.
- asyncio.gather(..., return_exceptions=True) keeps result order aligned
  with input order and isolates per-job failures.

Free-tier note: Groq (https://console.groq.com/keys) needs no credit card
and is used here by default via GROQ_API_KEY + GROQ_BASE_URL. To use real
OpenAI models instead, set OPENAI_API_KEY/OPENAI_BASE_URL env vars and
switch _client below.
"""

import asyncio
import json
import os

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential

from .config import TOP_P_DEFAULT, temperature_for_tone
from .models import MarketingCopy
from .templates import build_master_prompt

MODEL_NAME = os.getenv("COPYWRITER_MODEL", "llama-3.3-70b-versatile")
MAX_CONCURRENT_REQUESTS = int(os.getenv("COPYWRITER_MAX_CONCURRENCY", "10"))

_client = AsyncOpenAI(
    api_key=os.getenv("GROQ_API_KEY", os.getenv("OPENAI_API_KEY")),
    base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
)
_semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)


@retry(wait=wait_random_exponential(min=1, max=30), stop=stop_after_attempt(5))
async def _call_model(prompt: str, temperature: float, top_p: float) -> MarketingCopy:
    schema_hint = json.dumps(MarketingCopy.model_json_schema())
    system_msg = (
        "You must reply with ONLY a single valid JSON object matching this "
        f"JSON schema, no extra text: {schema_hint}"
    )

    async with _semaphore:
        response = await _client.chat.completions.create(
            model=MODEL_NAME,
            temperature=temperature,
            top_p=top_p,
            max_tokens=500,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt},
            ],
        )
    raw = response.choices[0].message.content
    return MarketingCopy.model_validate_json(raw)


async def generate_copy(
    product_name: str,
    product_description: str,
    platform: str,
    tone: str,
) -> MarketingCopy:
    """Generate a single piece of marketing copy for one platform/tone."""
    prompt = build_master_prompt(product_name, product_description, platform, tone)
    temperature = temperature_for_tone(tone)
    return await _call_model(prompt, temperature, TOP_P_DEFAULT)


async def generate_bulk(jobs: list[dict]):
    """
    jobs: list of dicts with keys product_name, product_description,
    platform, tone.

    Uses asyncio.gather -> guaranteed result order matching `jobs`, with
    return_exceptions=True so one failed job doesn't kill the batch.
    """
    tasks = [
        generate_copy(
            j["product_name"], j["product_description"], j["platform"], j["tone"]
        )
        for j in jobs
    ]
    return await asyncio.gather(*tasks, return_exceptions=True)
