from pathlib import Path

from pipeline.api.sentence import Sentence
from pipeline.factories.textonly import TextOnlyFactory
from pipeline.implementation import match_sub, token_counter
from pipeline.implementation.task.out_trait import emit


def aglaea(
    output_dir: Path, turn_based_game_data_dir: Path, language: str
) -> list[int]:
    Sentence.global_config(
        auto_format=None,
        token_counter=token_counter.get_qwen3(),
        match_sub=match_sub.get_felysneko_all_fixed(language),
    )

    factory = TextOnlyFactory(turn_based_game_data_dir, language)
    iterable = factory.build_talk_sentence_config(8347254212154585286)
    return emit(iterable, output_dir / f"{language}.jsonl", f"{language:>3}")


def cyrene(
    output_dir: Path, turn_based_game_data_dir: Path, language: str
) -> list[int]:
    Sentence.global_config(
        auto_format=None,
        token_counter=token_counter.get_qwen3(),
        match_sub=match_sub.get_felysneko_all_fixed(language),
    )

    factory = TextOnlyFactory(turn_based_game_data_dir, language)
    iterable = factory.build_talk_sentence_config(2309313067306506373)
    return emit(iterable, output_dir / f"{language}.jsonl", f"{language:>3}")


def cipher(
    output_dir: Path, turn_based_game_data_dir: Path, language: str
) -> list[int]:
    Sentence.global_config(
        auto_format=None,
        token_counter=token_counter.get_qwen3(),
        match_sub=match_sub.get_felysneko_all_fixed(language),
    )

    factory = TextOnlyFactory(turn_based_game_data_dir, language)
    iterable = factory.build_talk_sentence_config(8212064977546372217)
    return emit(iterable, output_dir / f"{language}.jsonl", f"{language:>3}")


def castorice(
    output_dir: Path, turn_based_game_data_dir: Path, language: str
) -> list[int]:
    Sentence.global_config(
        auto_format=None,
        token_counter=token_counter.get_qwen3(),
        match_sub=match_sub.get_felysneko_all_fixed(language),
    )

    factory = TextOnlyFactory(turn_based_game_data_dir, language)
    iterable = factory.build_talk_sentence_config(3884071463804277504)
    return emit(iterable, output_dir / f"{language}.jsonl", f"{language:>3}")


def hyacine(
    output_dir: Path, turn_based_game_data_dir: Path, language: str
) -> list[int]:
    Sentence.global_config(
        auto_format=None,
        token_counter=token_counter.get_qwen3(),
        match_sub=match_sub.get_felysneko_all_fixed(language),
    )

    factory = TextOnlyFactory(turn_based_game_data_dir, language)
    iterable = factory.build_talk_sentence_config(11373702895576004432)
    return emit(iterable, output_dir / f"{language}.jsonl", f"{language:>3}")


def hysilens(
    output_dir: Path, turn_based_game_data_dir: Path, language: str
) -> list[int]:
    Sentence.global_config(
        auto_format=None,
        token_counter=token_counter.get_qwen3(),
        match_sub=match_sub.get_felysneko_all_fixed(language),
    )

    factory = TextOnlyFactory(turn_based_game_data_dir, language)
    iterable = factory.build_talk_sentence_config(6101302014640441508)
    return emit(iterable, output_dir / f"{language}.jsonl", f"{language:>3}")


def cerydra(
    output_dir: Path, turn_based_game_data_dir: Path, language: str
) -> list[int]:
    Sentence.global_config(
        auto_format=None,
        token_counter=token_counter.get_qwen3(),
        match_sub=match_sub.get_felysneko_all_fixed(language),
    )

    factory = TextOnlyFactory(turn_based_game_data_dir, language)
    iterable = factory.build_talk_sentence_config(16138667287721516920)
    return emit(iterable, output_dir / f"{language}.jsonl", f"{language:>3}")
