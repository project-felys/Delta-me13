import re
from collections.abc import Callable

__NICKNAME_STR: str = "{NICKNAME}"


def __sub_nickname(s: str, nickname: str) -> str:
    s = s.replace(__NICKNAME_STR, nickname)
    return s


__REMOVE_PARTS: tuple[str, ...] = (
    r"<[^>]+>",
    r"\{RUBY_B#[^}]*\}",
    r"\{RUBY_E#\}",
    r"\{F#\{M#\}\}",
    r"\{Img(#| )\d+\}",
    r"\{LAYOUT_CONTROLLER#[^}]+\}",
    r"\{LAYOUT_KEYBOARD#[^}]+\}",
)
__HELIOBI_COUNT_STR: str = "{MCV#8015162#OldValue_1}"
__SPACE_STR: str = "{SPACE}"
__REMOVE_PATTERN: re.Pattern[str] = re.compile("|".join(__REMOVE_PARTS))
__LAYOUT_MOBILE_PATTERN: re.Pattern[str] = re.compile(r"\{LAYOUT_MOBILE#([^}]*)\}")
__MALE_PATTERN: re.Pattern[str] = re.compile(r"\{M#([^}]*)\}")
__FEMALE_PATTERN: re.Pattern[str] = re.compile(r"\{F#([^}]*)\}")


def __fix_common_pattern(s: str) -> str:
    s = s.replace(__HELIOBI_COUNT_STR, "3")
    s = s.replace(__SPACE_STR, " ")

    s = __REMOVE_PATTERN.sub("", s)
    s = __LAYOUT_MOBILE_PATTERN.sub(r"\1", s)

    s = __FEMALE_PATTERN.sub(r"\1", s)
    s = __MALE_PATTERN.sub("", s)
    return s


def __line_break_handler(s: str, new: str) -> str:
    s = s.replace("\n", new)
    return s


__WARNING_PATTERN: re.Pattern[str] = re.compile(r"\{[^}]*\}")
__SKIP_WARNING: set[str] = {"{大地獣,\xa0ネクタール,\xa0数学}"}


def __check_warning_and_print(s: str) -> None:
    raw_warning = __WARNING_PATTERN.findall(s)
    warning = [w for w in raw_warning if w not in __SKIP_WARNING]
    if warning:
        print(warning)


def get_felysneko_all_fixed(language: str) -> Callable[[str], str]:
    nickname = "银河猫猫侠" if language.lower() in ["chs", "cht"] else "FelysNeko"

    def match_sub(s: str) -> str:
        s = __sub_nickname(s, nickname)
        s = __fix_common_pattern(s)
        __check_warning_and_print(s)
        return s

    return match_sub


def get_felysneko_only() -> Callable[[str], str]:
    def match_sub(s: str) -> str:
        s = __sub_nickname(s, "银河猫猫侠")
        return s

    return match_sub


def get_all_fixed_no_line_break(language: str) -> Callable[[str], str]:
    spacing = {"Chinese(PRC)": "", "Japanese": "", "Korean": "\u00a0"}.get(
        language, " "
    )

    def match_sub(s: str) -> str:
        s = __fix_common_pattern(s)
        s = __line_break_handler(s, spacing)
        return s

    return match_sub
