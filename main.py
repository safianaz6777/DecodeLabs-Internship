"""
Entry point.

Flow: CLI input -> prompt compiler (src.templates) -> router ->
      real-time async pipeline (src.generator)  OR
      bulk Batch API pipeline (src.batch_pipeline)
"""

import asyncio
import csv
import json

from src.batch_pipeline import build_batch_file, submit_batch
from src.cli import build_parser
from src.generator import generate_bulk


def read_csv_jobs(path: str) -> list[dict]:
    jobs = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            jobs.append(
                {
                    "product_name": row["product_name"],
                    "product_description": row["description"],
                    "platform": row["platform"],
                    "tone": row["tone"],
                }
            )
    return jobs


def print_result(result):
    if isinstance(result, Exception):
        print(f"FAILED: {result}")
    else:
        print(json.dumps(result.model_dump(), indent=2))
        print("-" * 60)


def main():
    parser = build_parser()
    args = parser.parse_args()

    # ---- Bulk mode: CSV input ----------------------------------------
    if args.csv:
        jobs = read_csv_jobs(args.csv)

        if args.batch:
            path = build_batch_file(jobs)
            batch_id = submit_batch(path)
            print(f"Batch submitted successfully. Batch ID: {batch_id}")
            print(
                "This can take up to 24h. Poll status with "
                "src.batch_pipeline.check_batch(batch_id), then download "
                "with fetch_batch_results(batch_id) once status is 'completed'."
            )
        else:
            results = asyncio.run(generate_bulk(jobs))
            for result in results:
                print_result(result)
        return

    # ---- Single product mode ------------------------------------------
    if not args.product_name or not args.description:
        parser.error(
            "--product-name and --description are required unless --csv is used"
        )

    platforms = (
        ["linkedin", "instagram", "email"] if args.all_platforms else [args.platform]
    )
    jobs = [
        {
            "product_name": args.product_name,
            "product_description": args.description,
            "platform": p,
            "tone": args.tone,
        }
        for p in platforms
    ]

    results = asyncio.run(generate_bulk(jobs))
    for result in results:
        print_result(result)


if __name__ == "__main__":
    main()
