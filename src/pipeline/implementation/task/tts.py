import itertools
import os
import re
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from pipeline.api.audio import Audio
from pipeline.api.sentence import Sentence
from pipeline.factories.tts import TtsFactory
from pipeline.implementation import auto_format, match_sub
from pipeline.implementation.task.out_trait import emit


def __convert_audio(
    iterable: Iterator[Audio], output_dir: Path, num_threads: int
) -> Iterator[Audio]:
    def worker(audio: Audio) -> Audio:
        audio.wem_to_wav_by_vgmstream(output_dir)
        return audio

    with ThreadPoolExecutor(max_workers=num_threads) as ex:
        yield from ex.map(worker, iterable)


def __ensure_dir_exist(output_dir: Path) -> None:
    os.makedirs(output_dir, exist_ok=True)


def cyrene(
    output_dir: Path,
    unpacked_audio_dir: Path,
    turn_based_game_data_dir: Path,
    language: str,
    num_threads: int,
) -> list[int]:
    Sentence.global_config(
        auto_format=auto_format.get_patch("cyrene", language),
        token_counter=None,
        match_sub=match_sub.get_all_fixed_no_line_break(language),
    )

    unpacked_audio_language_dir = unpacked_audio_dir / language
    audio_dir = output_dir / language
    __ensure_dir_exist(unpacked_audio_language_dir)
    __ensure_dir_exist(audio_dir)

    voice_path_regex = re.compile(
        r"(?:(?:chapter4|side4)_[^_]+|vo_ambient_w4_\w+_\w+)"
        r"_(?:cyrene|cyrenejiyi|cyrenely|wangxi|zuozhe)_\d+"
    )
    tarot_book_voice_path_regex = re.compile(
        r"vo_syss_(?!cyrene_02_)\w+_\d+_\d+_cyrene_\d+"
    )

    factory = TtsFactory(unpacked_audio_language_dir, turn_based_game_data_dir)

    iterable = itertools.chain(
        factory.build_talk_sentence_config(voice_path_regex),
        factory.build_tarot_book_sentence(tarot_book_voice_path_regex),
        factory.build_voice_atlas(1415),
    )
    iterable = __convert_audio(iterable, audio_dir, num_threads)
    return emit(iterable, output_dir / f"{language}.jsonl", f"{language:>12}")


def aglaea(
    output_dir: Path,
    unpacked_audio_dir: Path,
    turn_based_game_data_dir: Path,
    language: str,
    num_threads: int,
) -> list[int]:
    Sentence.global_config(
        auto_format=auto_format.get_patch("aglaea", language),
        token_counter=None,
        match_sub=match_sub.get_all_fixed_no_line_break(language),
    )

    unpacked_audio_language_dir = unpacked_audio_dir / language
    audio_dir = output_dir / language
    __ensure_dir_exist(unpacked_audio_language_dir)
    __ensure_dir_exist(audio_dir)

    voice_path_regex = re.compile(
        r"(?:(?:chapter4|side4)_[^_]+|vo_ambient_w4_\w+_\w+)"
        r"_(?:aglaea|aglaeahy)_\d+"
    )
    tarot_book_voice_path_regex = re.compile(r"vo_syss_\w+_\d+_\d+_aglaea_\d+")

    factory = TtsFactory(unpacked_audio_language_dir, turn_based_game_data_dir)

    iterable = itertools.chain(
        factory.build_talk_sentence_config(voice_path_regex),
        factory.build_tarot_book_sentence(tarot_book_voice_path_regex),
        factory.build_voice_atlas(1402),
    )
    iterable = __convert_audio(iterable, audio_dir, num_threads)
    return emit(iterable, output_dir / f"{language}.jsonl", f"{language:>12}")


def hysilens(
    output_dir: Path,
    unpacked_audio_dir: Path,
    turn_based_game_data_dir: Path,
    language: str,
    num_threads: int,
) -> list[int]:
    Sentence.global_config(
        auto_format=auto_format.get_patch("hysilens", language),
        token_counter=None,
        match_sub=match_sub.get_all_fixed_no_line_break(language),
    )

    unpacked_audio_language_dir = unpacked_audio_dir / language
    audio_dir = output_dir / language
    __ensure_dir_exist(unpacked_audio_language_dir)
    __ensure_dir_exist(audio_dir)

    voice_path_regex = re.compile(
        r"(?:(?:chapter4|side4)_[^_]+|vo_ambient_w4_\w+_\w+)"
        r"_(?:hysilens|helektra)_\d+"
    )
    tarot_book_voice_path_regex = re.compile(r"vo_syss_\w+_\d+_\d+_hysilens_\d+")

    factory = TtsFactory(unpacked_audio_language_dir, turn_based_game_data_dir)

    iterable = itertools.chain(
        factory.build_talk_sentence_config(voice_path_regex),
        factory.build_tarot_book_sentence(tarot_book_voice_path_regex),
        factory.build_voice_atlas(1410),
    )
    iterable = __convert_audio(iterable, audio_dir, num_threads)
    return emit(iterable, output_dir / f"{language}.jsonl", f"{language:>12}")


def hyacine(
    output_dir: Path,
    unpacked_audio_dir: Path,
    turn_based_game_data_dir: Path,
    language: str,
    num_threads: int,
) -> list[int]:
    Sentence.global_config(
        auto_format=auto_format.get_patch("hyacine", language),
        token_counter=None,
        match_sub=match_sub.get_all_fixed_no_line_break(language),
    )

    unpacked_audio_language_dir = unpacked_audio_dir / language
    audio_dir = output_dir / language
    __ensure_dir_exist(unpacked_audio_language_dir)
    __ensure_dir_exist(audio_dir)

    voice_path_regex = re.compile(
        r"(?:(?:chapter4|side4)_[^_]+|vo_ambient_w4_\w+_\w+)"
        r"_(?:hyacine|hyacinetitan)_\d+"
    )
    tarot_book_voice_path_regex = re.compile(r"vo_syss_\w+_\d+_\d+_hyacine_\d+")

    factory = TtsFactory(unpacked_audio_language_dir, turn_based_game_data_dir)

    iterable = itertools.chain(
        factory.build_talk_sentence_config(voice_path_regex),
        factory.build_tarot_book_sentence(tarot_book_voice_path_regex),
        factory.build_voice_atlas(1409),
    )
    iterable = __convert_audio(iterable, audio_dir, num_threads)
    return emit(iterable, output_dir / f"{language}.jsonl", f"{language:>12}")


def castorice(
    output_dir: Path,
    unpacked_audio_dir: Path,
    turn_based_game_data_dir: Path,
    language: str,
    num_threads: int,
) -> list[int]:
    Sentence.global_config(
        auto_format=auto_format.get_patch("castorice", language),
        token_counter=None,
        match_sub=match_sub.get_all_fixed_no_line_break(language),
    )

    unpacked_audio_language_dir = unpacked_audio_dir / language
    audio_dir = output_dir / language
    __ensure_dir_exist(unpacked_audio_language_dir)
    __ensure_dir_exist(audio_dir)

    voice_path_regex = re.compile(
        r"(?:(?:chapter4|side4|chapterfate02)_[^_]+|vo_ambient_w4_\w+_\w+)"
        r"_(?:castorice|castoricehy|castoricetitan)_\d+"
    )
    tarot_book_voice_path_regex = re.compile(r"vo_syss_\w+_\d+_\d+_castorice_\d+")

    factory = TtsFactory(unpacked_audio_language_dir, turn_based_game_data_dir)

    iterable = itertools.chain(
        factory.build_talk_sentence_config(voice_path_regex),
        factory.build_tarot_book_sentence(tarot_book_voice_path_regex),
        factory.build_voice_atlas(1407),
    )
    iterable = __convert_audio(iterable, audio_dir, num_threads)
    return emit(iterable, output_dir / f"{language}.jsonl", f"{language:>12}")


def cipher(
    output_dir: Path,
    unpacked_audio_dir: Path,
    turn_based_game_data_dir: Path,
    language: str,
    num_threads: int,
) -> list[int]:
    Sentence.global_config(
        auto_format=auto_format.get_patch("cipher", language),
        token_counter=None,
        match_sub=match_sub.get_all_fixed_no_line_break(language),
    )

    unpacked_audio_language_dir = unpacked_audio_dir / language
    audio_dir = output_dir / language
    __ensure_dir_exist(unpacked_audio_language_dir)
    __ensure_dir_exist(audio_dir)

    voice_path_regex = re.compile(
        r"(?:(?:chapter4|side4)_[^_]+|vo_ambient_w4_\w+_\w+)"
        r"_(?:cipher|cifera)_\d+"
    )
    tarot_book_voice_path_regex = re.compile(
        r"vo_syss_\w+_\d+_\d+_(?:cipher|cifera)_\d+"
    )

    factory = TtsFactory(unpacked_audio_language_dir, turn_based_game_data_dir)

    iterable = itertools.chain(
        factory.build_talk_sentence_config(voice_path_regex),
        factory.build_tarot_book_sentence(tarot_book_voice_path_regex),
        factory.build_voice_atlas(1406),
    )
    iterable = __convert_audio(iterable, audio_dir, num_threads)
    return emit(iterable, output_dir / f"{language}.jsonl", f"{language:>12}")


def cerydra(
    output_dir: Path,
    unpacked_audio_dir: Path,
    turn_based_game_data_dir: Path,
    language: str,
    num_threads: int,
) -> list[int]:
    Sentence.global_config(
        auto_format=auto_format.get_patch("cerydra", language),
        token_counter=None,
        match_sub=match_sub.get_all_fixed_no_line_break(language),
    )

    unpacked_audio_language_dir = unpacked_audio_dir / language
    audio_dir = output_dir / language
    __ensure_dir_exist(unpacked_audio_language_dir)
    __ensure_dir_exist(audio_dir)

    voice_path_regex = re.compile(
        r"(?:(?:chapter4|side4)_[^_]+|vo_ambient_w4_\w+_\w+)"
        r"_cerydra_\d+"
    )
    tarot_book_voice_path_regex = re.compile(r"vo_syss_\w+_\d+_\d+_cerydra_\d+")

    factory = TtsFactory(unpacked_audio_language_dir, turn_based_game_data_dir)

    iterable = itertools.chain(
        factory.build_talk_sentence_config(voice_path_regex),
        factory.build_tarot_book_sentence(tarot_book_voice_path_regex),
        factory.build_voice_atlas(1412),
    )
    iterable = __convert_audio(iterable, audio_dir, num_threads)
    return emit(iterable, output_dir / f"{language}.jsonl", f"{language:>12}")
