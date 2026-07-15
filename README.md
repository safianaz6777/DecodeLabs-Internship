# Project 2: Automated Copywriting & Tone Transformer
**DecodeLabs — Generative AI Industrial Training Kit (Batch 2026)**

Takes a raw product description and automatically generates professional
marketing copy tailored to LinkedIn, Instagram, or Email — with tunable
Temperature/Top_P per tone and both a real-time async pipeline and a
bulk OpenAI Batch API pipeline.

## Project Structure
```
project2-copywriter/
├── main.py                 # entry point (CLI -> pipeline router)
├── requirements.txt
├── .env.example
├── sample_products.csv     # demo data for bulk mode
└── src/
    ├── models.py           # Pydantic output schema
    ├── config.py           # platform constraints + temperature/top_p map
    ├── templates.py        # master instruction prompt compiler
    ├── generator.py        # real-time async pipeline (semaphore + retry)
    ├── batch_pipeline.py   # bulk pipeline via OpenAI Batch API
    └── cli.py               # argparse CLI
```

## 1. Setup

```bash
git clone <your-repo-url>
cd project2-copywriter

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# then open .env and paste your Groq API key
```

**Free option (no credit card):** get a key from
https://console.groq.com/keys — sign up with email/Google/GitHub, click
"Create API Key", done.

Set it as an environment variable before running:

```bash
export GROQ_API_KEY=gsk_xxxx        # Windows PowerShell: $env:GROQ_API_KEY="gsk_xxxx"
```

By default the real-time pipeline (`src/generator.py`) talks to Groq's
free, OpenAI-compatible endpoint using `llama-3.3-70b-versatile`. If you
later want real OpenAI models, set `OPENAI_API_KEY` and point
`generator.py`'s client at `api.openai.com` instead — note the `--batch`
bulk pipeline (`src/batch_pipeline.py`) always uses OpenAI's Batch API,
which is paid.

## 2. Running it

**Single product, single platform:**
```bash
python main.py --product-name "Aqua Pure Bottle" \
                --description "A self-cleaning water bottle with UV purification" \
                --platform instagram \
                --tone witty
```

**Single product, all 3 platforms at once** (custom `+a` flag):
```bash
python main.py -p "Aqua Pure Bottle" -d "A self-cleaning water bottle with UV purification" +a
```

**Bulk mode from CSV (real-time async, runs immediately):**
```bash
python main.py --csv sample_products.csv
```

**Bulk mode via OpenAI Batch API (cheaper, for large jobs, ~24h window):**
```bash
python main.py --csv sample_products.csv --batch
```
This prints a `batch_id`. Poll and fetch results later:
```python
from src.batch_pipeline import check_batch, fetch_batch_results
check_batch("batch_xxx")               # check status
fetch_batch_results("batch_xxx")       # once status == "completed"
```

## 3. How it works (mapped to the training deck)

| Deck concept | Where it lives |
|---|---|
| Master Instruction Template / f-string injection | `src/templates.py` |
| Platform-specific filtering (char limits) | `src/config.py` |
| Temperature / Top_P tuning per tone | `src/config.py` |
| Legacy vs reasoning model token param routing | `config.token_param_for_model()` |
| Async pipeline (`async def` / `await` / semaphore) | `src/generator.py` |
| `asyncio.gather` (ordered results, error isolation) | `generator.generate_bulk()` |
| Retry with exponential backoff + jitter | `tenacity` decorator in `generator.py` |
| Enterprise Batch API (50% cost cut, 24h window) | `src/batch_pipeline.py` |
| CLI / argparse / custom prefix flags | `src/cli.py` |
| Pydantic structured output schema | `src/models.py` |

## 4. Pushing this to your GitHub repository

If you already created an empty repo on GitHub, run these from inside
the `project2-copywriter` folder:

```bash
git init
git add .
git commit -m "Project 2: Automated Copywriting & Tone Transformer"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git push -u origin main
```

If the GitHub repo already has a README/license (not empty), pull first
to avoid conflicts:
```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

Never commit your real `.env` file — `.gitignore` already excludes it.
