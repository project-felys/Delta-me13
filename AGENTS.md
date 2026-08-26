# AGENTS.md

Dataset-generation pipeline (text + audio corpora) for Cyrene and several other Amphoreus characters. Python 3.12, `uv` + `uv_build` build backend (not hatchling). Packages: `pipeline` (`src/pipeline`) and `pck` (`src/pck`).

## Critical: this repo is not runnable from a clean checkout

The pipeline depends on inputs that are **deliberately not in this repo**:

- An unnamed external **game-data repository** → passed as `--turn-based-game-data-dir`. Required for `multilingual` and `audio`.
- The **game's `.pck` audio banks** → required for `audio` (unpack with `delta-me13-unpack` first).
- **`vgmstream-cli`** binary → converts `.wem`→`.wav`. Put on `PATH` or `export VGMSTREAM=/path/to/vgmstream-cli`. The binary at repo root is gitignored; a fresh checkout won't have it.

`corpora/` and `audio/` are generated output (gitignored, except `corpora/**/*.json` metrics). `vendor/` holds supplementary game-wiki (`vendor/miyoushe/*.md`) and LeetCode (`vendor/coig/`) data used by the `vendor` command.

## Commands

```bash
uv sync                          # install; puts the console scripts in .venv/bin
uv run ruff check src            # lint (rules: E F W I UP, line-length 88, py312)
uv run ruff format src           # format
uv run delta-me13 --help         # CLI (entrypoints: delta-me13, delta-me13-unpack)
```

No test suite, no CI. Verification = running the pipeline end-to-end (requires the external inputs above).

## Entrypoints and dispatch

- `delta-me13` → `pipeline.build:main` — argparse dispatcher over `multilingual | vendor | audio`.
- `delta-me13-unpack` → `pck.unpack:main` — `--input-dir <dir-of-pck-files>` (default `--output-dir audio/`), one subdir at a time, sequential with tqdm.

**`pipeline/build.py` is the single source of truth** for what runs. Its `match` dispatch tables list every supported `(namespace, dataset)` / `audio dataset` combo. The `--namespace`/`--dataset` argparse `choices` are **wider** than what the dispatch handles — unsupported combos die with `parser.error("Unsupported: ...")`. Adding a dataset means: add a module-level task function `f(output_dir, …, language) -> list[int]` in `implementation/task/*.py`, plus a new `case` in `build.py` (and a `patch/tts/<dataset>/` dir for TTS).

Current surface (all in `build.py`):

- `multilingual --namespace pt|sft|textonly`: pt `everything|amphoreus`, sft `everything|amphoreus|cyrene`, textonly `cyrene|aglaea|cipher|castorice|hyacine|hysilens|cerydra`.
- `audio --dataset cyrene|aglaea|hysilens|hyacine|castorice|cipher|cerydra`.
- `vendor --vendor-dir vendor`.

Output layout: `corpora/<namespace|tts>/<dataset>/<language>.jsonl` (+ `.wav` next to audio lines for `tts`); per-dataset token metrics JSON at `corpora/<ns>/<dataset>.json`.

## Architecture (`src/pipeline/`)

Layered by purpose — the names are not self-explanatory:

- `api/` — pydantic data models (`Sentence`, `Paragraph`, `Conversation`, `Audio`, `OutTrait`). `Sentence` carries **global mutable config** set via the classmethod `Sentence.global_config(auto_format=, match_sub=, token_counter=)`; defaults are identity/`len`. **Each task function must call `global_config` itself at entry** — it does not persist between tasks, and workers run in separate `mp` processes (do not set it once in `main()`).
- `loaders/` — read raw game data / unpacked audio / vendor sources into pandas tables (`TurnBasedGameDataLoader`, `UnpackedAudioLanguageLoader`, `VendorLoader`).
- `factories/` — orchestration; `TtsFactory(UnpackedAudioLanguageLoader, TurnBasedGameDataLoader)` is the only multi-inherit case. Per output type: `pt`, `sft`, `textonly`, `tts`, `vendor`. Methods like `build_talk_sentence_config`, `build_voice_atlas` expose specific content sources.
- `implementation/` — config wiring + the functions the CLI calls:
  - `task/{pt,sft,textonly,tts}.py` — one function per dataset (e.g. `pt.amphoreus`, `sft.cyrene`, `textonly.aglaea`, `tts.aglaea`); these call `global_config`, then stream via `task/out_trait.py` `emit(...)` (writes JSONL + tqdm + returns per-line token counts).
  - `auto_format.py`, `match_sub.py`, `token_counter.py` — factories building the callables passed to `Sentence.global_config`.
  - `tokenizer/` — **shipped Qwen3 tokenizer** (~22 MB, several big JSON/txt files, tracked in git). Loaded with `AutoTokenizer.from_pretrained(..., local_files_only=True)` so it never touches the network. Do not move or prune it. Used for token counts in pt/sft/textonly; TTS passes `token_counter=None` (falls back to `len`).
- `patch/` — shipped data, not code:
  - `patch/tts/<dataset>/<Language>.jsonl` — TTS text patches per dataset (`cyrene`, `aglaea`, ...). Loaded by `patch/tts.py` `load_patch(character, language)`. A missing character/language file falls back to an empty mapping — note some languages exist as **0-byte placeholder files** (e.g. `cipher/*.jsonl`). Entries map a text hash → patched text; `auto_format.get_patch` applies `patch_mapping.get(sentence.text_hash, sentence.text)`.
  - `patch/tts/INSTRUCTIONS.md` — documents how those patches were produced: shared rules first, then one section per dataset. The generation scripts are **not in the repo**; only the final `.jsonl` artifacts are.
- `pck/` — standalone Wwise `.pck` parser + `unpack` entrypoint. Each `.pck` extracts to numbered `.wem` files **plus a `<stem>.json` manifest** (the parsed bank header) under `audio/`. `UnpackedAudioLanguageLoader` re-reads those manifests to map `voice_path`/`audio_event` → wem files — do not change the naming scheme without updating it.
- `fnv1.py` — FNV-1 32/64-bit hashing used to map voice paths / audio events / names to in-game IDs (`fnv1_64(wem_path.lower())`, etc.). Hashes appear hardcoded all over the task files and `auto_format.py`.

### Caveats

- `{NICKNAME}` is the game's player-name placeholder; substitution happens in `match_sub.py` (default `银河猫猫侠` for chs/cht, else `FelysNeko`). TTS uses `get_all_fixed_no_line_break`, which does **not** substitute nickname and replaces newlines per-language (`""` zh/ja, `\u00a0` kr, `" "` otherwise).
- Speaker identity is selected by **hardcoded name-hash / avatar-id maps** duplicated across `task/*.py`, `auto_format.py` whitelists, and TTS voice-path regexes in `task/tts.py`. E.g. `avatar_id 1415 = 昔涟`, and the same `avatar_id_to_name_hash` dict is copy-pasted in `pt.amphoreus` and `sft.amphoreus`. Adding/fixing a character means touching several coordinated places.
- Code comments name characters/items in Chinese (e.g. `# 昔涟`), while string content is localized per language.

## Conventions

- **Two different language-code styles**: text tasks use short codes (`chs cht de en es fr id jp kr pt ru th vi`, `build.TEXT_LANGUAGES`); audio/voiceover uses full names (`Chinese(PRC) English Japanese Korean`, `build.VOICEOVER_LANGUAGES`). `factories/tts.py` `LANGUAGE_ABBREVIATION_MAP` bridges them. Patch files use the voiceover-style names as filenames.
- `build.py` sets `os.environ["TRANSFORMERS_VERBOSITY"] = "error"` at import time (silences HF logs).
- Parallelism: `multilingual`/`audio` fan out one task per language over `multiprocessing.Pool` (text `--num-proc`, default 4; audio always `len(VOICEOVER_LANGUAGES)` = 4). Audio wem→wav conversion inside each worker uses `ThreadPoolExecutor(max_workers=--num-threads, default 8)`.
- Hash-keyed matching everywhere: TTS patches, `auto_format` whitelists, and `match_sub` lookups key on FNV-1 hashes (`sentence.text_hash`, `sentence.name_hash`), never raw strings — but `Sentence.text` is the real localized string.
