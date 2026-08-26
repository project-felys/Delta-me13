import itertools
from collections.abc import Iterator
from pathlib import Path

from pipeline.api.paragraph import Paragraph
from pipeline.api.sentence import Sentence
from pipeline.factories.pt import PtFactory
from pipeline.factories.vendor import VendorFactory
from pipeline.implementation import auto_format, match_sub, token_counter
from pipeline.implementation.task.out_trait import emit


def __split_paragraphs(
    iterable: Iterator[Paragraph], max_token: int
) -> Iterator[Paragraph]:
    for each in iterable:
        yield from each.split(max_token)


def everything(
    output_dir: Path, turn_based_game_data_dir: Path, language: str
) -> list[int]:
    Sentence.global_config(
        auto_format=auto_format.get_retain_sentence_name(language),
        token_counter=token_counter.get_qwen3(),
        match_sub=match_sub.get_felysneko_all_fixed(language),
    )

    factory = PtFactory(turn_based_game_data_dir, language)
    iterable = itertools.chain(
        factory.build_talk_sentence_config(),
        factory.build_book_series_config(),
        factory.build_story_atlas(),
        factory.build_voice_atlas(),
        factory.build_noun_atlas(),
        factory.build_chronicle_conclusion(),
        factory.build_tarot_mails(),
        factory.build_tarot_book_sentence(),
        factory.build_tarot_wiki_data(),
    )
    iterable = __split_paragraphs(iterable, 4096)
    return emit(iterable, output_dir / f"{language}.jsonl", f"{language:>3}")


def amphoreus(
    output_dir: Path, turn_based_game_data_dir: Path, language: str
) -> list[int]:
    Sentence.global_config(
        auto_format=auto_format.get_retain_sentence_name(language),
        token_counter=token_counter.get_qwen3(),
        match_sub=match_sub.get_felysneko_all_fixed(language),
    )

    avatar_id_to_name_hash = {
        1402: 8347254212154585286,  # 阿格莱雅
        1403: 12286569378821401368,  # 缇宝
        1404: 12172129776731566058,  # 万敌
        1405: 7940279852062189396,  # 那刻夏
        1406: 8212064977546372217,  # 赛飞儿
        1407: 3884071463804277504,  # 遐蝶
        1408: 1410515507232658695,  # 白厄
        1409: 11373702895576004432,  # 风堇
        1410: 6101302014640441508,  # 海瑟音
        1412: 16138667287721516920,  # 刻律德菈
        1413: 6287657147795310895,  # 长夜月
        1414: 11464334189321098131,  # 丹恒
        1415: 2309313067306506373,  # 昔涟
    }
    extra_name_hashes = [
        11001695012879251917,  # 迷迷
        16450988707457331866,  # 来古士
    ]

    factory = PtFactory(turn_based_game_data_dir, language)
    iterable = itertools.chain(
        factory.build_talk_sentence_config(
            list(avatar_id_to_name_hash.values()) + extra_name_hashes
        ),
        factory.build_chronicle_conclusion(
            [
                104,  # 主线
                204,  # 支线
                803,  # 活动
            ]
        ),
        factory.build_story_atlas(avatar_id_to_name_hash.keys()),
        factory.build_voice_atlas(avatar_id_to_name_hash.keys()),
        factory.build_book_series_config(
            [
                5,  # 翁法罗斯
            ]
        ),
        factory.build_noun_atlas(),  # 智库（专有名词、星神、派系）
        factory.build_tarot_mails(),  # 邮箱.exe
        factory.build_tarot_book_sentence(),  # 翁法罗斯英雄纪.exe
        factory.build_tarot_wiki_data(),  # δ-me13.exe
    )
    iterable = __split_paragraphs(iterable, 4096)
    return emit(iterable, output_dir / f"{language}.jsonl", f"{language:>3}")


def vendor(output_dir: Path, vendor_dir: Path):
    Sentence.global_config(
        auto_format=None,
        token_counter=token_counter.get_qwen3(),
        match_sub=match_sub.get_felysneko_only(),
    )

    factory = VendorFactory(vendor_dir)
    named_metrics = {
        "miyoushe": emit(
            factory.build_miyoushe(), output_dir / "miyoushe.jsonl", "miyoushe"
        ),
        "coig": emit(factory.build_coig(), output_dir / "coig.jsonl", "coig"),
    }

    return named_metrics
