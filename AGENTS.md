# AGENTS.md

Dataset generation pipeline for **Cyrene** (text + audio). Python 3.12, `uv` + `hatchling`. Package: `src/pipeline`.

## Critical: this repo is not runnable from a clean checkout

The pipeline depends on inputs that are **deliberately not in this repo**:

- An unnamed external **game-data repository** → passed as `--turn-based-game-data-dir`. Required for `multilingual` and `audio`.
- The **game's `.pck` audio banks** → required for `audio` (unpack with `delta-me13-pck` first).
- **`vgmstream-cli`** binary → converts `.wem`→`.wav`. Put on `PATH` or `export VGMSTREAM=/path/to/vgmstream-cli`. The binary at repo root is gitignored; a fresh checkout won't have it.

`corpora/` and `audio/` are generated output (gitignored). `vendor/` holds supplementary game-wiki/LeetCode data used by the `vendor` command.

## Commands

```bash
uv sync                          # install (editable dev setup)
uv run ruff check src            # lint (rules: E F W I UP, line-length 88, py312)
uv run ruff format src           # format
python -m pipeline ...           # run CLI (entrypoints: delta-me13, delta-me13-pck)
```

No test suite, no CI. Verification = running the pipeline end-to-end (requires the external inputs above).

Two entrypoints (pyproject `[project.scripts]`):

- `delta-me13 multilingual|vendor|audio ...`
- `delta-me13-pck --input-dir <dir-of-pck-files>` → unpacks `.pck` banks to `.wem` + a JSON manifest into `audio/` (default).

See `README.md` for full per-command flags.

## Architecture (`src/pipeline/`)

Layered by purpose — the names are not self-explanatory:

- `cli.py` — argparse dispatcher over the three subcommands.
- `api/` — pydantic data models (`Sentence`, `Audio`, `Conversation`, ...). `Sentence` carries **global mutable config** set via the classmethod `Sentence.global_config(auto_format=, match_sub=, token_counter=)`; each task calls it once before processing.
- `loaders/` — read raw game data / unpacked audio / vendor sources into pandas tables (`TurnBasedGameDataLoader`, `UnpackedAudioLanguageLoader`, vendor).
- `factories/` — orchestration; classes **multi-inherit from loaders** (e.g. `TtsFactory(UnpackedAudioLanguageLoader, TurnBasedGameDataLoader)`). Per output type: `pt`, `sft`, `tts`, `vendor`.
- `implementation/` — config wiring + the actual pipeline functions the CLI calls:
  - `task/{pt,sft,tts}.py` — functions invoked from `cli.py` (e.g. `pt.amphoreus`, `sft.cyrene`, `tts.cyrene`).
  - `auto_format.py`, `match_sub.py`, `token_counter.py` — factories that build the callables passed to `Sentence.global_config`.
  - `tokenizer/` — **shipped Qwen3 tokenizer** (local-only) used for token counts in `pt`/`sft` (TTS sets `token_counter=None`). Included in the wheel via `force-include`.
- `patch/` — shipped data, not code:
  - `patch/tts/<Language>.jsonl` — TTS text patches keyed by text hash, loaded by `patch/tts.py` (also `force-include`d in the wheel).
  - `patch/tts/INSTRUCTIONS.md` — documents how those patches were produced. The generation scripts are **not in the repo**; only the final `.jsonl` artifacts are.
- `pck.py` — standalone binary parser for Wwise `.pck` containers (separate `delta-me13-pck` entrypoint).
- `fnv1.py` — FNV-1 32/64-bit hashing used to map voice paths / audio events to in-game IDs.

### Do not "deduplicate" these pairs

- `match_sub.py` (core `MatchSub` class, runs regex substitutions) vs `implementation/match_sub.py` (factory functions configuring it) — intentional split.
- `{NICKNAME}` is the game's player-name placeholder. `MatchSub` replaces it; default nickname is `银河猫猫侠` (zh) / `FelysNeko`. Many hashes/whitelists in `auto_format.py` hardcode speaker identity for the Cyrene dataset.

## Conventions

- **Two different language-code styles**: text tasks use short codes (`chs cht de en es fr id jp kr pt ru th vi`, see `cli.TEXT_LANGUAGES`); audio/voiceover uses full names (`Chinese(PRC) English Japanese Korean`, see `cli.VOICEOVER_LANGUAGES`). `factories/tts.py` `LANGUAGE_ABBREVIATION_MAP` bridges them.
- `cli.py` sets `os.environ["TRANSFORMERS_VERBOSITY"] = "error"` at import time (silences HF logs).
- Tasks parallelize via `multiprocessing.Pool` (text, one proc per language) or `ThreadPoolExecutor` (audio wem→wav conversion).
- Hash-keyed patches: TTS patches and speaker whitelists are matched on FNV-1 text/name hashes (`sentence.text_hash`, `name_hash`), not on raw strings — text in `patch/tts/*.jsonl` is looked up by hash.
