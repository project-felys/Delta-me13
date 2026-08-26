from collections.abc import Iterator

import pandas as pd

from pipeline.api.paragraph import Paragraph
from pipeline.loaders.turn_based_game_data import TurnBasedGameDataLoader


class TextOnlyFactory(TurnBasedGameDataLoader):
    def __init__(
        self, turn_based_game_data_dir: str, turn_based_game_data_language: str
    ):
        super().__init__(turn_based_game_data_dir, turn_based_game_data_language)

    def build_talk_sentence_config(self, name_hash: int) -> Iterator[Paragraph]:
        df = self.talk_sentence_config_table.fillna(None)
        name_hash_mask = df["textmap_talk_sentence_name"] == name_hash
        group_ids = set(df.loc[name_hash_mask, "group"])
        mask = df["group"].isin(group_ids)
        df = df[mask]

        for _, sub_df in df.groupby("group"):
            yield from self.__build_one_talk_sentence_config(sub_df, name_hash)

    def __build_one_talk_sentence_config(
        self, df: pd.DataFrame, assistant_name_hash: int
    ) -> Iterator[Paragraph]:
        fields = [
            "talk_sentence_id",
            "textmap_talk_sentence_name",
            "talk_sentence_text",
            "voice_id",
        ]
        df = df[fields]

        buffer = []
        for talk_sentence_id, name_hash, text_hash, voice_id in df.itertuples(
            index=False
        ):
            if name_hash == assistant_name_hash and pd.isna(voice_id):
                sentence = self.sentence_factory(talk_sentence_id, name_hash, text_hash)
                buffer.append(sentence)
            elif buffer:
                yield Paragraph(sentences=tuple(buffer))
                buffer.clear()

        if buffer:
            yield Paragraph(sentences=tuple(buffer))
