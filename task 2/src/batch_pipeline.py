"""
Bulk / enterprise-scale pipeline using OpenAI's Batch API.

Per the deck's "Strategic Mandate": when real-time UI streaming is not
needed, route generation through the Batch API instead of the live async
pipeline -- it runs on a separate rate-limit pool, costs ~50% less, and
completes within a 24h window.

This builds the batch .jsonl, uploads it, and creates the batch job.
Fetching/parsing results is done once OpenAI reports the batch as
"completed" (poll `check_batch`).
"""

import json
import os


from openai import OpenAI

from .config import TOP_P_DEFAULT, temperature_for_tone
from .models import MarketingCopy
from .templates import build_master_prompt

MODEL_NAME = os.getenv("COPYWRITER_MODEL", "gpt-4o")
_client = None


def _get_client() -> OpenAI:
    """Lazily create the OpenAI client only when batch mode is actually
    used, so importing this module doesn't crash when the person is only
    using the free Groq real-time pipeline (no OPENAI_API_KEY set)."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. The --batch pipeline requires a "
                "real (paid) OpenAI API key from https://platform.openai.com/api-keys "
                "-- it is not available on the free Groq tier."
            )
        _client = OpenAI(api_key=api_key)
    return _client


def build_batch_file(jobs: list[dict], path: str = "batch_input.jsonl") -> str:
    """Write one JSON line per job in the format the Batch API expects."""
    with open(path, "w") as f:
        for i, job in enumerate(jobs):
            prompt = build_master_prompt(
                job["product_name"],
                job["product_description"],
                job["platform"],
                job["tone"],
            )
            temperature = temperature_for_tone(job["tone"])

            request = {
                "custom_id": f"job-{i}",
                "method": "POST",
                "url": "/v1/responses",
                "body": {
                    "model": MODEL_NAME,
                    "input": prompt,
                    "temperature": temperature,
                    "top_p": TOP_P_DEFAULT,
                    "text": {
                        "format": {
                            "type": "json_schema",
                            "name": "MarketingCopy",
                            "schema": MarketingCopy.model_json_schema(),
                        }
                    },
                },
            }
            f.write(json.dumps(request) + "\n")
    return path


def submit_batch(path: str = "batch_input.jsonl") -> str:
    """Upload the batch file and kick off the job. Returns the batch id."""
    client = _get_client()
    uploaded = client.files.create(file=open(path, "rb"), purpose="batch")
    batch = client.batches.create(
        input_file_id=uploaded.id,
        endpoint="/v1/responses",
        completion_window="24h",
    )
    return batch.id


def check_batch(batch_id: str):
    """Poll batch status: validating | in_progress | completed | failed ..."""
    return _get_client().batches.retrieve(batch_id)


def fetch_batch_results(batch_id: str, output_path: str = "batch_output.jsonl"):
    """Once status == 'completed', download the results file."""
    client = _get_client()
    batch = client.batches.retrieve(batch_id)
    if batch.status != "completed":
        return None
    content = client.files.content(batch.output_file_id)
    with open(output_path, "wb") as f:
        f.write(content.read())
    return output_path
