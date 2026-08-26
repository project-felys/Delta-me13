import argparse
from pathlib import Path

import tqdm

from pck.api import PckExtractor


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("audio"))
    args = parser.parse_args()

    all_sub_dirs = [entry for entry in args.input_dir.iterdir() if entry.is_dir()]
    name_width = max((len(d.name) for d in all_sub_dirs), default=0)

    for sub_dir in all_sub_dirs:
        wildcard_dot_pck = [
            entry for entry in sub_dir.iterdir() if entry.suffix == ".pck"
        ]

        output_dir = args.output_dir / sub_dir.name
        desc = f"> {sub_dir.name.rjust(name_width)}"
        for dot_pck in tqdm.tqdm(wildcard_dot_pck, desc=desc):
            PckExtractor(dot_pck).extract(output_dir)
