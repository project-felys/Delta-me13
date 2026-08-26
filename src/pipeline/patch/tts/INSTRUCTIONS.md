# TTS 补丁说明

补丁按角色分目录存放：`patch/tts/<角色>/<Language>.jsonl`（角色目录名与 `audio --dataset` 的取值一致，如 `cyrene`）。运行时由 `pipeline.patch.tts.load_patch(character, language)` 读入，`get_patch` 按 `Sentence.text_hash` 查表，将语料文本替换为补丁文本；目录或文件缺失时返回空映射，视为无补丁。

新增角色：在本目录新建子目录，放入各语言的 `<Language>.jsonl`，并仿照下文「cyrene」「aglaea」一节追加该角色的说明。

## 通用

### 任务背景

游戏配音时配音演员无法得知 `{NICKNAME}` 的实际值，因此会用「伙伴 / 她 / 你 / friend / 파트너」等替代。TTS 补丁任务把语料中含 `{NICKNAME}` 的条目，依据 ASR 实际念法处理成可读文本，供 TTS 训练使用。

### 文件格式

每行一条 JSON 记录，三个字段：

```json
{"audio": "chapter4_77_cyrene_229_f.wav", "hash": 4076366899179991993, "patch": "「而在你的心里，我一定会得到最喜欢的，你给我的名字。」"}
```

- `audio` — 音频文件名（来自 corpora，仅用于溯源）
- `hash` — 游戏内文本哈希（`TalkSentenceConfig.json` 中的哈希，运行时查表键）
- `patch` — 最终文本（`{NICKNAME}` 位已按实际念法替换）

> 生成过程中的中间产物曾采用四字段记录：`audio` / `text`（原始字幕，保留 `{NICKNAME}`）/ `asr`（ASR 听写结果）/ `patch`（规则修正后文本）。最终入库时 `hash` 由 `text` 在游戏数据中反查得到，`text` / `asr` 字段不再保留。

### 处理规则

#### 一、总则

1. **只动 `{NICKNAME}` 一处**，其余文本以原文为准，不照抄 ASR 的错字 / 标点 / 漏字。
2. 专有名词以原文为准，ASR 错识不照搬：`白厄`≠白垩、`识刻锚`≠食刻矛、`哀丽秘榭`≠艾利蜜榭、`神悟树庭`≠神物树亭、`丹恒`≠单恒、`Cyrene`≠Sereni、`Aedes Elysiae`≠…、`파트너`≠파티나/파티노、`단항`≠다낭、`셉터`≠세타、`앰포리어스`≠엠포리아스/엠포리우스、`엘리사이 에데스`≠엘리사의 에데스 等。
3. 非空格空白符用脚本核实：韩文 key/value 均用 **NBSP（U+00A0）** 分词，肉眼难辨，务必 `repr()` / `hex(ord(c))` 核查。

#### 二、`{NICKNAME}` 位的处理方式

1. **替换**：换成 ASR 听到的词（`{NICKNAME}`→`伙伴` / `파트너` / `friend`）；写法以官方文本为准，核验方法见下文「称呼写法的官方文本核音法」。
2. **删除**：配音时被删则一并删除，连带清掉呼语附属标点。
   - `{NICKNAME}，还记得…`→`还记得…`（呼语逗号同删）
   - `接下来，{NICKNAME}就要…`→`接下来，就要…`（结构性逗号保留）
   - `…我也不知道，{NICKNAME}。`→`…我也不知道。`（句末呼语删，前句号留作句末）
3. **复杂替换**：照搬 ASR 念法（`{NICKNAME}`→`我的伙伴` / `天外的救世主` / `the Deliverer beyond the sky` / `우리 파트너` / `천의 구세주` 等多字表述）。
4. **填充词替代**：配音用「嗯 / Ugh / 음 / 어 / 응 / 와」等语气词代替称呼时，`{NICKNAME}`→该填充词。
5. **第三人称代词默认用「她」（重要）**：`{NICKNAME}` 位被念成第三人称「ta」时（中 `他/她/它`、英 `he/she/it/his/her`、韩 `그/그녀`），**一律取「她 / she / her / 그녀」**，即使 ASR 写成「他 / he」也改回。仅限 `{NICKNAME}` 位；非 `{NICKNAME}` 位的代词按原文不动。
6. **乱码 / 装饰条目**：如 `{NICKNAME}▀▄抓紧▄█我▄▀▄`，删 `{NICKNAME}`，装饰符与可读词保留（→`▀▄抓紧▄█我▄▀▄`）；ASR 整条乱码（如 `화투나 팔아야겠다`）则忽略 ASR，回退到 key 结构去 `{NICKNAME}`。
7. **ASR 严重错识回退**：整段乱码（如韩文 `왜? 조시매`、`기린네 바트너`）回退到语法标准形（→`파트너, 조심해`、`키레네, 파트너`）。
8. **英文主语人称切换**带动词一致：`{NICKNAME} is`→`you're`/`she is`；`returns`→`return`、`talks`→`talk`。两句因删 `{NICKNAME}` 合并时后句首字母大写→小写（`No surprise, {NICKNAME}. You shine…`→`No surprise, you shine…`）；反之，句首呼语删除后余句升为句首，首字母小写→大写（`{NICKNAME}, what form…`→`What form…`）。

#### 三、标点 / 语气词细节

- **照搬 ASR 的标点风格**（句末 `。`/`.`/`?`、`……`→`.` 等），但 `「」`《》`""` 等书名 / 引号括号按原文保留（中文 / 日文）。
- 远离 `{NICKNAME}` 的句首语气词（`ふふっ、` / `흐음,` / `헤,` / `후훗,` / `히히` 等）即使 ASR 漏识也补回（TTS 表演信息）。
- 数字照搬 ASR 念法：`3천만`→`삼천만`、`33,550,337`→`삼천삼백오십오만 삼백삼십칠`。
- 词间粘连 / 拆分照搬 ASR（如 `보안 검사`→`보안검사`、`기억해 둬`→`기억해둬`、`천 년`→`천년`）。

### 称呼写法的官方文本核音法

ASR 对人名 / 爱称的拼写极不稳定（Greyfry / Grief / Greyfri 三变、灰鱼儿 / 霍雨儿 同音异字、회색 물고기 / 해생물 거기 / 회생물고기 三变），`{NICKNAME}` 位的替换词**不能照抄 ASR 写法**，须用官方文本核实。

**原理**：游戏文本中该角色对玩家的爱称大量**原生出现**（旁白转述、其他角色对话、命名场景），这些行的写法即官方拼写；`{NICKNAME}` 占位行的实读音（ASR）决定「念什么」，原生行决定「怎么写」。

**数据源**：`corpora/sft/amphoreus/<lang>.jsonl`（剧情 + 图鉴文本，与 TTS 语料同源）。注意两点：

- sft 语料的 `{NICKNAME}` 位已被默认昵称替换（`银河猫猫侠` / `FelysNeko`），**搜不到占位符**，能搜到的是原生写法。
- 各语言**行数不同、行号不对齐**（chs 3859 行 / en 3867 行），禁止按行号对齐，只能用内容锚点。

**操作**：

1. **粗搜**：用 ASR 听音的音译多拼法初搜（中：同音字组多试几组；英 `-i` 大小写不敏感 + 拆写 / 连写都试；韩：疑似词形逐一试），`rg -o -c` 先看计数，上百行即基本坐实。
2. **确权**：看命中行的上下文是否为该角色的称呼习惯，优先采信「命名 / 说明场景」（如 `灰宝？丹宝？\n是昵称！怎么样，可爱吧？`）与系列昵称连带证据（`세븐둥이`（三月七）/ `청룡둥이`（丹恒）→ `회색둥이` 同族）。
3. **跨语言定形**：英 / 韩写法用 zh 原生行的高区分度同现词做锚点（如 `小海兔`→`sea hare`）定位同一对话的译文行，读出 `{NICKNAME}` 位的官方词形——大小写、连写、冠词（`the little gray fry`）全以译文为准。
4. **实读与文本不一致时取实读**：官方存在多词形时（`Little Gray` 与裸 `Gray` 并存），按 ASR 实读择形并记录证据行（ASR 三处均无 little → 取裸 `Gray`）；ASR 读音在官方文本无任何原生行佐证时，取最接近官方命名风格的拼写，并在该角色小节标注待复核。

判例：`灰鱼儿`（hysilens，原生 12 行）→ `gray fry`（`The little gray fry and pink sea hare`）→ `회색 물고기`（kr 64 行）；`灰宝`（hyacine，原生 203 行）→ `Gray`（裸形 `Gray's eyes are so sharp!`）→ `회색둥이`（kr 202 行）。

## cyrene

### 数据上游

`corpora/tts/cyrene/<Language>.jsonl`（每行 `{audio, text}`，各 1828 行）+ 同目录 `<Language>/` 音频文件夹。

> 生成过程中的中间文件（`patch/asr/*.json` 的 ASR 结果、`patch/llm/*.json` 的人工修正结果）已删除，其内容已并入最终 `.jsonl` 的 `hash` / `patch` 字段。

### 条目范围

**只保留含 `{NICKNAME}` 的条目**（asr/patch 非 null）；不含 `{NICKNAME}` 的普通行已剔除。条目数：中 160、英 158、日 7、韩 158（corpora 中重复 text 自动复用同一条 asr/patch；含英雄纪接入后新增的 05_01 献书两句：中/英/韩各 +2）。

合并脚本要点：按 corpora 原顺序遍历，`text` 同时作为 key 查 asr/llm 两个 dict，命中则填入，否则两项为 null（后过滤掉）。

### 各语言注意点

- **中文**：呼语逗号删 / 留判断最多；非 `{NICKNAME}` 位「她/他/它」按原文。
- **英文**：动词时态 / 主谓一致 / 缩写（`'s`/`'re`/`'d`）；`"` 转义保留；英文 ASR 的 `he/his` 均为原文指代反派（非 `{NICKNAME}` 位），保持不动。
- **日文**：`「」`、`…`、`♪` 保留；条目最少（7 条），多为 `{NICKNAME}`→`あなた`/`あの子`/`彼女`。
- **韩文**：key/value 均用 NBSP 分词；助词形 `{NICKNAME}은(는)`/`이(가)`/`을(를)`/`와(과)`/`(이)가`/`(이)랑`，括号内为备用助词；策略为「ASR 清晰照搬、乱码回退标准形」混合；专有名词统一（파트너 / 단항 / 셉터 / 앰포리어스 / 엘리사이 에데스 / 헤르타 / 카이사르 等）。

### 验证清单（针对 `.jsonl` 产物）

- 每行 JSON 合法：`python3 -c "import json;[json.loads(l) for l in open(...)]"`
- 三字段齐全：`audio` / `hash` / `patch` 均存在
- 条目数：中 160、英 158、日 7、韩 158
- 残留 `{NICKNAME}`：`patch` 字段中不得出现
- 韩文 NBSP：`patch` 字段中不得残留普通空格（`' ' in v` 应为空）
- `hash` 应能在游戏数据 `TalkSentenceConfig.json` 中找到（查表键来源一致）

### 复现流程（脚本未入库，需自行实现）

整个数据集的构建分三步：

1. **筛选**：从 `corpora/tts/cyrene/<Language>.jsonl`（每行 `{audio, text}`）中筛出 `text` 含 `{NICKNAME}` 的条目，按 `text` 去重（同一字幕复用同一段音频的听写），得到「字幕 → 音频」映射。四语共约 460 条唯一文本。

2. **听写**：用语音识别服务对每条音频做转写，得到配音演员实际念出的内容（含 `{NICKNAME}` 位的替代念法）。本数据集使用阿里云百炼（DashScope）US 区的 `qwen3-asr-flash-us` 模型，开启逆文本归一化（ITN），按语言传入提示（中 `zh` / 英 `en` / 日 `ja` / 韩 `ko`）。该模型 US 区限流约 100 RPM，建议低并发（4 左右）配合限流退避重试，并支持断点续跑与增量落盘。输出为「原始字幕 → 听写文本」的对照表。

3. **修正**：对照听写结果，按「通用 › 处理规则」逐条判断，产出最终文本——`{NICKNAME}` 位按实际念法替换并遵循默认「她」等规则，其余文本以原文为准、不照抄识别误差。该步可借助语言模型（把处理规则作为提示词，逐条喂入「原始字幕 + 听写文本」让其输出修正文本），但须人工复核。输出为「原始字幕 → 修正文本」的对照表。

最后把两张对照表与原语料合并：按 corpora 顺序遍历，以 `text` 为键分别查两张表填入 `asr` / `patch` 字段，丢弃两者皆空（即不含 `{NICKNAME}`）的行；再以 `text` 在游戏数据 `TalkSentenceConfig.json` 中反查哈希，整理为本目录下的 `cyrene/<Language>.jsonl`。

## aglaea

### 数据上游

`corpora/tts/aglaea/<Language>.jsonl`（每行 `{name, text}`，各 954 行）+ 同目录 `<Language>/` 音频文件夹。语料含三类来源：剧情（chapter4）、英雄纪（vo_syss）、语音图鉴（archive / Ev_archive）。

中间产物以 `<Language>.transcribed.jsonl` 形式与本目录 `*.jsonl` 并置：`patch` 字段为原始字幕（保留 `{NICKNAME}`），`transcript` 字段为 ASR 听写结果；修正后的最终文本回填 `*.jsonl` 的 `patch` 字段。

### 条目范围

只保留含 `{NICKNAME}` 的条目。条目数：中 19、英 19、日 2、韩 19（hash 去重后无同文本合并；全部来自 chapter4 剧情线）。`hash` 直接取自流水线 `Sentence.text_hash`（源表哈希），无需文本反查。

### 各语言注意点

- **称谓实读随语境变化，须逐条按 ASR**：中 `阁下 / 开拓者阁下 / 贵客`；英 `you / Miss Trailblazer / Esteemed one / the Trailblazer / the distinguished guest`；韩 `개척자님 / 당신 / 손님`。
- **第三人称默认「她」**照例适用：中 `她`、英 `her`、日 `彼女`。
- **英文**：句首呼语删除后余句升为句首，首字母小写→大写；主谓一致（`{NICKNAME} is here`→`you are here`）。
- **韩文**：`{NICKNAME} 씨` 被实读称谓吞并时，助词随新词变形（`씨를→당신을`、`씨와→개척자님과`、`님도→당신도`）；实读称谓已含敬语（`개척자님`）时不得保留 `씨`，以免双敬语。
- **配音偶有整段省略**：「{NICKNAME}与丹恒——」整段未读（中/英删除收尾、句末标点照搬 ASR；韩按实读收为 `전사 두 분.`）。填充词替代一处位于 `{NICKNAME}` 位（`You're here. Hmm.`，保留）；另一处句首 "Hmm." 不在 `{NICKNAME}` 位（未采纳）。
- **专有名词错识清单（不照搬，回退原文）**：霞蝶→遐蝶、奥赫马→奥赫玛、玄风城→悬锋城、埃利密谢→哀丽秘榭、白垩→白厄、万迪→万敌、巫师/无事→吾师；Castram Kremnos→Castrum Kremnos、Finan→Phainon、Ides Elizei→Aedes Elysiae、Mighty→Mydei、Akima→Okhema、Orinix→Oronyx、Castorus→Castorice、Trinan→Trinnon；오르닉스→오로닉스。

### 验证清单（针对 `.jsonl` 产物）

- 每行 JSON 合法：`python3 -c "import json;[json.loads(l) for l in open(...)]"`
- 三字段齐全：`audio` / `hash` / `patch` 均存在
- 条目数：中 19、英 19、日 2、韩 19
- 残留 `{NICKNAME}`：`patch` 字段中不得出现
- 韩文 NBSP：`patch` 字段中不得残留普通空格（`' ' in v` 应为空）
- `hash` 与语料条目的 `Sentence.text_hash` 一致；`load_patch("aglaea", language)` 应全部命中（重跑 `delta-me13 audio --dataset aglaea` 生效）

## hysilens

### 数据上游

`corpora/tts/hysilens/<Language>.jsonl`（每行 `{name, text}`，各 432 行）+ 同目录 `<Language>/` 音频文件夹。语料含三类来源：剧情（chapter4 / side4 / vo_ambient）、英雄纪（vo_syss）、语音图鉴（archive / Ev_archive）。

中间产物以 `<Language>.transcribed.jsonl` 形式与本目录 `*.jsonl` 并置（同 aglaea）：`patch` 字段为原始字幕（保留 `{NICKNAME}`），`transcript` 字段为 ASR 听写结果；修正后的最终文本回填 `*.jsonl` 的 `patch` 字段。

### 条目范围

只保留含 `{NICKNAME}` 的条目。条目数：中 4、英 4、日 0（日文文本无 `{NICKNAME}`）、韩 4（hash 去重后无同文本合并；全部来自 chapter4_64 / 65 剧情线）。`hash` 直接取自流水线 `Sentence.text_hash`，无需文本反查。

### 各语言注意点

- **称呼实读三语一致，均为海瑟音对玩家的爱称「灰鱼儿」**（冥河主题）：
  - 中 `灰鱼儿`：ASR 一处写作 `霍雨儿`，同音归一；游戏原生文本即有 `灰鱼儿 / 小灰鱼儿` 称呼（side4_shitang、chapter4_53/56/57/58/64/65/73 共 12 行），可直接互证。
  - 英 `gray fry`：**官方本地化写法**（sft 语料原生行 `The little gray fry and pink sea hare` / `Gray fry? Little sea hare?` 可证）——小写普通名词、美式拼写，不得仿 ASR 拼法造专名（ASR 出现 Greyfriars / Grief / Greyfri 等多种不稳定写法）。句中一律小写，仅句首呼格大写。
  - 韩 `회색 물고기`：官方写法（kr sft 语料 64 行可证）；助词单元随替换一并落定（`{NICKNAME}은(는)`→`회색 물고기는`、`{NICKNAME}을(를)`→`회색 물고기를`），NBSP 照例。
- **动词位不在 `{NICKNAME}` 处不动**：EN 一条 ASR 听到 `lies`（原文 `is`），按只动一处保留原文。

### 验证清单（针对 `.jsonl` 产物）

- 每行 JSON 合法：`python3 -c "import json;[json.loads(l) for l in open(...)]"`
- 三字段齐全：`audio` / `hash` / `patch` 均存在
- 条目数：中 4、英 4、日 0、韩 4
- 残留 `{NICKNAME}`：`patch` 字段中不得出现
- 韩文 NBSP：`patch` 字段中不得残留普通空格（`' ' in v` 应为空）
- `hash` 与语料条目的 `Sentence.text_hash` 一致；`load_patch("hysilens", language)` 应全部命中（重跑 `delta-me13 audio --dataset hysilens` 生效）

## hyacine

### 数据上游

`corpora/tts/hyacine/<Language>.jsonl`（每行 `{name, text}`，各 797 行）+ 同目录 `<Language>/` 音频文件夹。语料含三类来源：剧情（chapter4 / side4 / vo_ambient，含 hyacinetitan 泰坦形态标签）、英雄纪（vo_syss，书 owner 为 `hyacinthus`）、语音图鉴（archive / Ev_archive）。

中间产物以 `<Language>.transcribed.jsonl` 形式与本目录 `*.jsonl` 并置（同 aglaea）。

### 条目范围

只保留含 `{NICKNAME}` 的条目。条目数：中 6、英 5、日 0（日文文本自带称呼，无 `{NICKNAME}`）、韩 5。`hash` 直接取自流水线 `Sentence.text_hash`；story + tarot 共 5 个唯一文本之外，还有语音图鉴行 `archive_hyacine_24`（三语含 `{NICKNAME}`）——批次枚举必须含 `build_voice_atlas` 路线。

### 各语言注意点

- **称呼实读三语同源，为风堇对玩家的「灰」系爱称**：
  - 中 `灰宝`：原生文本 203 行互证（含命名场景「灰宝？丹宝？是昵称！怎么样，可爱吧？」）；ASR 一处写作 `徽宝`，同音归一。
  - 英 `Gray`：官方 `Little Gray` 与裸 `Gray` 并存（`Little Gray and Dannie are such good peop...` / `Gray's eyes are so sharp!`）；ASR 三处均未听到 little，取裸形。
  - 韩 `회색둥이`：原生文本 202 行互证（多带 `씨`）；与 `세븐둥이`（三月七）、`청룡둥이`（丹恒）、`카스둥이` 同系列。
- **第三人称默认「她 / her」**照例：中 `他`→`她` ×2（ASR 写「他」）、英 `her` ×2。
- **KO 吸收型助词判例**：`{NICKNAME} 씨가`→`그분께서`、`{NICKNAME} 씨에게`→`그분께`（实读为敬语 `그분`，씨 被吞并；按 cyrene 复杂替换照搬实读，不取 `그녀` 默认）；其余 `{NICKNAME} 씨` 仅换名词、씨 保留。
- **整段未读判例**：中「你肯定有办法指导`{NICKNAME}`他们吧？」ASR 听成「知道他们」——判定 `{NICKNAME}` 未读出（删除），`知道`为`指导`之误听（回退原文）。
- **专有名词错识清单（不照搬，回退原文）**：担保→丹宝、克莱特鲁斯→克拉特鲁斯、烛火→逐火、Denny→Dannie、Aqualad→Aquila、Amphorius→Amphoreus、Mister Crateros→Mr. Krateros、Sevi→Sevie、Grie→Gray。

### 验证清单（针对 `.jsonl` 产物）

- 每行 JSON 合法：`python3 -c "import json;[json.loads(l) for l in open(...)]"`
- 三字段齐全：`audio` / `hash` / `patch` 均存在
- 条目数：中 6、英 5、日 0、韩 5
- 残留 `{NICKNAME}`：`patch` 字段中不得出现
- 韩文 NBSP：`patch` 字段中不得残留普通空格（`' ' in v` 应为空）
- `hash` 与语料条目的 `Sentence.text_hash` 一致；`load_patch("hyacine", language)` 应全部命中（重跑 `delta-me13 audio --dataset hyacine` 生效）

## castorice

### 数据上游

`corpora/tts/castorice/<Language>.jsonl`（每行 `{name, text}`，各 1627 行）+ 同目录 `<Language>/` 音频文件夹。语料含三类来源：剧情（chapter4 / side4 / **chapterfate02 命运篇** / vo_ambient，含 castoricehy 变体与 castoricetitan 泰坦形态标签）、英雄纪（vo_syss，本音仅 4 条——她的书 90 条中 83 条为旁白代读）、语音图鉴（archive / Ev_archive）。

中间产物以 `<Language>.transcribed.jsonl` 形式与本目录 `*.jsonl` 并置（同 aglaea）。

### 条目范围

只保留含 `{NICKNAME}` 的条目。条目数：中 76、英 76、日 7、韩 70。`hash` 直接取自流水线 `Sentence.text_hash`；atlas 文本四语均无 `{NICKNAME}`（已复查）。

### 各语言注意点

- **删除主导型数据集**：遐蝶从不念爱称——中 63/76 条 `{NICKNAME}` 直接不读（保留其惯用敬语「阁下」，即 `{NICKNAME}阁下`→`阁下`）；英 55/76（保留 `Miss`）；韩 35/70（**连 `님` 一并删除**——韩语无 bare 님 称呼，与中英保留敬语的行为相反）；日文基本全替换。
- **第三人称默认「她 / her / 彼女」**照例：中 `他`→`她` ×7、英 `her`（含 `{NICKNAME}'s`→`her` 吞 's）、日 `彼女` ×5。
- **韩文实读称谓**：`그분`（敬语，씨/님 被吞并：`{NICKNAME} 님은`→`그분은`）、`이분`、`당신`、`그녀`、`부하님`（fuse）、`개척자님`（fuse）；`님` 随替换被吞时助词随新词变形（`님께서`→`당신이`）。
- **英文判例**：`Looks like {NICKNAME} is`→`they are`（实读 they，主谓一致随动；未按默认改 she——待复核）；`saving Miss {NICKNAME}'s life`→`Miss's life`（实读 Missus's，取规范拼写）；`took care of dromases with {NICKNAME}`→`the Trailblazer`。
- **韩文整行填充词判例**：`{NICKNAME} 님……`→`아.`（实读仅语气词）。
- **句尾标点照搬 ASR**（删除型高频）：원문无句号/`……` 而实读为 `.` 时补/替换；`——` 保留（dash 非句末标点）。
- **专有名词错识清单（不照搬，回退原文）**：Denny→Dannie、Aklya→Aglaea、Treby/Trehan/Trinan→Tribbie/Trianne/Trinnon、Hyacinth→Hyacine、Dromasus→dromases、Toshaka→Tohsaka；티타니→티탄이、유네→윤회、오로닉스 실연→오로닉스 시련。

### 验证清单（针对 `.jsonl` 产物）

- 每行 JSON 合法：`python3 -c "import json;[json.loads(l) for l in open(...)]"`
- 三字段齐全：`audio` / `hash` / `patch` 均存在
- 条目数：中 76、英 76、日 7、韩 70
- 残留 `{NICKNAME}`：`patch` 字段中不得出现
- 韩文 NBSP：`patch` 字段中不得残留普通空格（`' ' in v` 应为空）
- `hash` 与语料条目的 `Sentence.text_hash` 一致；`load_patch("castorice", language)` 应全部命中（重跑 `delta-me13 audio --dataset castorice` 生效）

## cipher

### 数据上游

`corpora/tts/cipher/<Language>.jsonl`（每行 `{name, text}`，各 629 行）+ 同目录 `<Language>/` 音频文件夹。语料含三类来源：剧情（chapter4 / side4 / vo_ambient）、英雄纪（vo_syss，书 owner 为真名 `cifera`，本音 21 条）、语音图鉴（archive / Ev_archive）。

> `shaocipher`（少女形态）音色与本音差异明显，已排除：story 52 条 + 书内本音 2 条，不计入语料。

### 条目范围

**全线零 `{NICKNAME}`**（story / tarot / atlas 三路线 × 四语言逐一核实，atlas Voice_M 文本亦为 0）——无需 ASR 批次与补丁修正，系迄今唯一无补丁内容的角色。`patch/tts/cipher/` 四语 `.jsonl` 为空文件占位：`load_patch("cipher", language)` 返回空映射兜底；若后续版本更新引入含 `{NICKNAME}` 的行，按本文件通用规则补录即可。

### 验证清单（针对 `.jsonl` 产物）

- 四语 `.jsonl` 均为空（0 条）
- 重跑 `delta-me13 audio --dataset cipher` 生效；语料 `{NICKNAME}` 残留应为 0

## cerydra

### 数据上游

`corpora/tts/cerydra/<Language>.jsonl`（每行 `{name, text}`，各 385 行）+ 同目录 `<Language>/` 音频文件夹。语料含三类来源：剧情（chapter4 / side4 / vo_ambient）、英雄纪（vo_syss，本音 24 条——自家书 18 + huangdi 皇帝书 4 + hysilens 书 2）、语音图鉴（archive / Ev_archive）。

中间产物以 `<Language>.transcribed.jsonl` 形式与本目录 `*.jsonl` 并置（同 aglaea）。

### 条目范围

只保留含 `{NICKNAME}` 的条目。条目数：中 1、英 1、日 0（日文文本直接略去名字只称「救世主」）、韩 1。`hash` 直接取自流水线 `Sentence.text_hash`。

### 各语言注意点

- **礼仪宣告句的呼语整段跳读**：唯一一条（「岁月」神谕宣告）中 `{NICKNAME}` 三语均未读出——中/英删除呼语及其随附逗号（`「救世主」，{NICKNAME}，已从`→`「救世主」，已从`；`"Time," {NICKNAME}, has`→`"Time," has`，引号内逗号属原文保留）。
- **韩文助词并合判例**：`「구세주」, {NICKNAME}이(가) 천외에서 왔다` 实读为「구세주가 천외에서 왔다」——主格助词 `이(가)` 并入前词（`구세주`+`가`），呼语逗号同删（→`「구세주」가 천외에서 왔다`，待复核）。
- ASR 噪声不照搬：神域→神谕、皆是→揭示、满意之碑→满溢之杯、천에 서왔다→천외에서 왔다、깨뜨리고→깨트리고。

### 验证清单（针对 `.jsonl` 产物）

- 每行 JSON 合法：`python3 -c "import json;[json.loads(l) for l in open(...)]"`
- 三字段齐全：`audio` / `hash` / `patch` 均存在
- 条目数：中 1、英 1、日 0、韩 1
- 残留 `{NICKNAME}`：`patch` 字段中不得出现
- 韩文 NBSP：`patch` 字段中不得残留普通空格（`' ' in v` 应为空）
- `hash` 与语料条目的 `Sentence.text_hash` 一致；`load_patch("cerydra", language)` 应全部命中（重跑 `delta-me13 audio --dataset cerydra` 生效）
