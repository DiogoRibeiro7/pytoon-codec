"""Simple perf_counter-based benchmarks for pytoon-codec."""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from time import perf_counter
from typing import Any

from benchmarks.generate_payloads import generate_events, generate_metrics
from pytoon_codec import ToonCodec

PayloadBuilder = Callable[[int], dict[str, Any]]


def _measure_suite(
    name: str,
    builder: PayloadBuilder,
    codec: ToonCodec,
    sizes: list[int],
    repeats: int,
) -> dict[str, Any]:
    results = []

    for n_rows in sizes:
        encode_times: list[float] = []
        decode_times: list[float] = []

        for _ in range(repeats):
            payload = builder(n_rows)

            start = perf_counter()
            toon = codec.encode(payload)
            encode_times.append(perf_counter() - start)

            start = perf_counter()
            decoded = codec.decode(toon)
            decode_times.append(perf_counter() - start)

            assert decoded == payload, "Benchmark round-trip failed"

        avg_encode = sum(encode_times) / repeats
        avg_decode = sum(decode_times) / repeats

        results.append(
            {
                "rows": n_rows,
                "encode_seconds": avg_encode,
                "decode_seconds": avg_decode,
                "total_seconds": avg_encode + avg_decode,
            }
        )

    return {"name": name, "results": results}


def _print_table(summary: dict[str, Any]) -> None:
    print(f"== {summary['name']} ==")
    print(f"{'rows':>8} | {'encode (s)':>10} | {'decode (s)':>10} | {'total (s)':>10}")
    print("-" * 48)
    for row in summary["results"]:
        print(
            f"{row['rows']:8d} | "
            f"{row['encode_seconds']:10.4f} | "
            f"{row['decode_seconds']:10.4f} | "
            f"{row['total_seconds']:10.4f}"
        )
    print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark ToonCodec encode/decode")
    parser.add_argument(
        "--sizes",
        type=int,
        nargs="+",
        default=[100, 1_000, 10_000],
        help="row counts to benchmark (default: 100 1000 10000)",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="number of times to repeat each measurement (default: 1)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit JSON summary instead of tables (useful for CI ingestion)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.repeat <= 0:
        raise ValueError("--repeat must be positive")

    codec = ToonCodec()
    suites = [
        _measure_suite(
            "Time-series metrics", generate_metrics, codec, args.sizes, args.repeat
        ),
        _measure_suite(
            "Nested events", generate_events, codec, args.sizes, args.repeat
        ),
    ]

    if args.json:
        print(json.dumps(suites, indent=2))
    else:
        for summary in suites:
            _print_table(summary)


if __name__ == "__main__":
    main()
