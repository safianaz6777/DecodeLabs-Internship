"""
CLI entry point config (argparse).

Includes the custom prefix_chars example from the deck: standard flags use
'-' / '--', while '+a' / '++all-platforms' is a custom action flag,
distinguished via prefix_chars="-+".
"""

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="copywriter",
        description="DecodeLabs Project 2 - Automated Copywriting & Tone Transformer",
        prefix_chars="-+",
    )

    parser.add_argument("--product-name", "-p", type=str, help="Name of the product")
    parser.add_argument(
        "--description", "-d", type=str, help="Raw product description"
    )
    parser.add_argument(
        "--platform",
        choices=["linkedin", "instagram", "email"],
        default="linkedin",
        help="Target platform for the copy",
    )
    parser.add_argument(
        "--tone",
        type=str,
        default="professional",
        help="Desired tone, e.g. witty, professional, playful, persuasive",
    )
    parser.add_argument(
        "--csv",
        type=str,
        help="Path to a CSV file for bulk generation "
        "(columns: product_name,description,platform,tone)",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Route CSV jobs through the OpenAI Batch API instead of the "
        "real-time async pipeline (cheaper, for large non-urgent jobs)",
    )
    parser.add_argument(
        "+a",
        "++all-platforms",
        dest="all_platforms",
        action="store_true",
        help="Generate copy for all three platforms at once for a single product",
    )

    return parser
