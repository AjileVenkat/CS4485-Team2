import argparse
from pathlib import Path

import openneuro as on


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download an OpenNeuro dataset into this backend workspace"
    )
    parser.add_argument(
        "--dataset",
        default="ds004504",
        help="OpenNeuro dataset accession number (default: ds004504)",
    )
    parser.add_argument(
        "--target-dir",
        default="ds004504",
        help="Target directory to store dataset files (default: ds004504)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    target_dir = Path(args.target_dir).resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    print(f"Downloading {args.dataset} into {target_dir} ...")
    print("If interrupted, re-run the same command to resume.")
    on.download(dataset=args.dataset, target_dir=str(target_dir))
    print("Download finished.")


if __name__ == "__main__":
    main()
