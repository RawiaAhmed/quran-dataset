"""`quran-dataset build` downloads and writes data/; `quran-dataset stats` prints the chunking table."""

from __future__ import annotations

import argparse
from pathlib import Path

from .build import build, read_jsonl, write_jsonl
from .chunk import STRATEGIES, stats

COLUMNS = ["chunks", "verses_mean", "words_en_mean", "words_en_median", "words_en_max", "words_ar_mean", "under_10_words_en"]


def markdown_table(rows: dict[str, dict]) -> str:
    lines = ["| strategy | " + " | ".join(COLUMNS) + " |", "|---" * (len(COLUMNS) + 1) + "|"]
    for name, row in rows.items():
        lines.append(f"| {name} | " + " | ".join(str(row[c]) for c in COLUMNS) + " |")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(prog="quran-dataset")
    parser.add_argument("command", choices=["build", "stats"])
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    args = parser.parse_args()

    verses_path = args.data_dir / "verses.jsonl"
    if args.command == "build" or not verses_path.exists():
        verses = build(args.data_dir)
        print(f"wrote {len(verses)} verses to {verses_path}")
    else:
        verses = read_jsonl(verses_path)

    table = {}
    for name, fn in STRATEGIES.items():
        chunks = fn(verses)
        write_jsonl(chunks, args.data_dir / "chunks" / f"{name}.jsonl")
        table[name] = stats(chunks)
    print(markdown_table(table))


if __name__ == "__main__":
    main()
