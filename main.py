import argparse

from dotenv import load_dotenv

from spotify_playlist_creator import run


def _positive_int(value: str) -> int:
    n = int(value)
    if n <= 0:
        raise argparse.ArgumentTypeError(f"--limit must be a positive integer, got {n}")
    return n


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=_positive_int, default=None)
    parser.add_argument("--dry-run", action="store_true", default=False)
    args = parser.parse_args()
    run(limit=args.limit, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
