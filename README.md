# δ-me13

δ-me13 generates text and audio datasets for Cyrene, and can be extended to support a wider range of characters. Feel free to [chat](https://felys.dev/en/chat) with Cyrene or hear her [voice](https://felys.dev/en/voice).

**Note: this project does not contain any game assets, nor does it reverse engineer any encrypted files.**

## Setup

The project isn't published to a package index, so install it directly from git.

```bash
pip install git+https://github.com/project-felys/delta-me13.git
```

However, since upstream dependencies can be extremely fragile, I recommend cloning the repository and patching it as needed. You can set it up with `pip install -e .` or `uv sync`. Feel free to ask an LLM for help, as some of the data mapping is complicated.

## Large-Language-Model

The corpus generation scripts depend on an external game data repository, which I will not name here. If you find that repository, clone it and replace `/path/to/game-data-repository` with its path. The following commands build the dataset in [standard](https://swift.readthedocs.io/en/latest/Customization/Custom-dataset.html#standard-dataset-format) format for all 13 languages.

```bash
repo=/path/to/game-data-repository

# Pre-training: everything, amphoreus
delta-me13 multilingual \
    --turn-based-game-data-dir $repo \
    --namespace pt \
    --dataset amphoreus \
    --num-proc 13

# Supervised Fine-tuning: everything, amphoreus, cyrene
delta-me13 multilingual \
    --turn-based-game-data-dir $repo \
    --namespace sft \
    --dataset cyrene
```

The vendor data includes the official game [wiki](https://bbs.mihoyo.com/sr/wiki/content/5851/detail) and LeetCode problems from [COIG](https://huggingface.co/datasets/BAAI/COIG/blob/main/leetcode_instructions.jsonl).

```bash
# Pre-training
delta-me13 vendor --vendor-dir vendor
```

## Text-to-Speech

Generating the audio dataset requires both the external repository (see the previous [section](#large-language-model)) and the game itself. You will need to unpack the audio files first. Replace `/path/to/persistent/audio/audio-package/windows` with the game's audio directory.

```bash
pck=/path/to/persistent/audio/audio-package/windows

# Unpack *.pck
delta-me13-unpack --input-dir $pck
```

Once all `.pck` files have been unpacked, the command-line interface can process the corpus and generate `.wav` files. Make sure `vgmstream-cli` is in your `PATH`, or run `export VGMSTREAM=/path/to/vgmstream-cli`. Refer to [vgmstream](https://github.com/vgmstream/vgmstream) for installation guidance.

```bash
repo=/path/to/game-data-repository

# Text-to-Speech: cyrene, aglaea, hysilens, hyacine, castorice, cipher, cerydra
delta-me13 audio \
    --turn-based-game-data-dir $repo \
    --unpacked-audio-dir audio \
    --dataset cyrene
```

## Bias

Please be aware that corpus generation hard-codes my nickname `FelysNeko` and only considers the female perspective (i.e., Stelle). Pronouns are not a major issue, as models are generally robust enough to handle them. However, this bias matters if you want characters to recognize your name or to use male conventions for the voiceover (especially in Japanese). I don't plan to fix this — just good to know.

## License

Distributed under the terms of the [LICENSE](LICENSE).

## Copyright

© All rights reserved by FelysNeko.
