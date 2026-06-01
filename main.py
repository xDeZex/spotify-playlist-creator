import argparse

from spotify_playlist_creator import run


def _positive_int(value: str) -> int:
    n = int(value)
    if n <= 0:
        raise argparse.ArgumentTypeError(f"--limit must be a positive integer, got {n}")
    return n


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=_positive_int, default=None)
    args = parser.parse_args()
    run(limit=args.limit)


if __name__ == "__main__":
    main()
