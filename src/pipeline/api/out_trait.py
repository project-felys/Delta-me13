import abc
from collections.abc import Mapping
from typing import Any


class OutTrait(abc.ABC):
    @property
    @abc.abstractmethod
    def num_tokens(self) -> int: ...

    @abc.abstractmethod
    def to_jsonl(self, **kwargs: Any) -> Mapping[str, Any]: ...
