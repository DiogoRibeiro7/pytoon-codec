"""Simple perf_counter-based benchmarks for pytoon-codec."""

from __future__ import annotations

from collections.abc import Callable
from time import perf_counter

from benchmarks.generate_payloads import generate_events, generate_metrics
from pytoon_codec import ToonCodec

PayloadBuilder = Callable[[int], dict]


def _run_suite(name: str, builder: PayloadBuilder, codec: ToonCodec) -> None:
    print(f"== {name} ==")
    print(f"{'rows':>8} | {'encode (s)':>10} | {'decode (s)':>10} | {'total (s)':>10}")
    print("-" * 48)

    for n_rows in (100, 1_000, 10_000):
        payload = builder(n_rows)

        start = perf_counter()
        toon = codec.encode(payload)
        encode_time = perf_counter() - start

        start = perf_counter()
        decoded = codec.decode(toon)
        decode_time = perf_counter() - start

        assert decoded == payload, "Benchmark round-trip failed"

        total = encode_time + decode_time
        print(f"{n_rows:8d} | {encode_time:10.4f} | {decode_time:10.4f} | {total:10.4f}")

    print()


def main() -> None:
    codec = ToonCodec()
    _run_suite("Time-series metrics", generate_metrics, codec)
    _run_suite("Nested events", generate_events, codec)

    # TODO: Add CLI flags to control sizes, repeat counts, and JSON output for CI ingestion.


if __name__ == "__main__":
    main()
