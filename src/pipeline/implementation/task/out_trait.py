import json
from collections.abc import Iterator
from pathlib import Path
from typing import IO, Any

import tqdm

from pipeline.api.out_trait import OutTrait


def to_jsonl(
    iterable: Iterator[OutTrait], f: IO[str], **kwargs: Any
) -> Iterator[OutTrait]:
    for each in iterable:
        line = each.to_jsonl(**kwargs)
        json.dump(line, f, ensure_ascii=False)
        print(file=f)
        yield each


def num_tokens(iterable: Iterator[OutTrait]) -> Iterator[int]:
    for each in iterable:
        yield each.num_tokens


def emit(
    iterable: Iterator[OutTrait], output_path: Path, desc: str, **kwargs: Any
) -> list[int]:
    with open(output_path, "w+") as file:
        iterable = to_jsonl(iterable, file, **kwargs)
        iterable = num_tokens(iterable)
        metrics = list(tqdm.tqdm(iterable, desc=f"> {desc}"))
    return metrics
