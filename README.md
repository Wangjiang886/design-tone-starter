# 设计定调助手 · design-tone-starter

**先把方向问清楚，再一步步找资料、看预览、改到合适。**

面向 OpenDesign Cloud / Local Codex 工作流的新手引导 skill。适合“有个想法或参考链接，但不知道从哪里开始”的人，用问答串起项目文件夹、定调、素材复核、可返工网页方案与最后的声音交接。

Beginner-friendly design direction and production guidance: ask focused questions, organize references, review real materials, iterate on silent web previews, and hand approved visuals to Doubao for audio.

版本：`0.1.0`。这是工作流首版；目录工具已提供本地行为检查，外部平台的完整协作效果需要在真实项目中验证。

[下载 v0.1.0 ZIP](https://github.com/Wangjiang886/design-tone-starter/releases/download/v0.1.0/design-tone-starter-v0.1.0.zip) · [GitHub 项目](https://github.com/Wangjiang886/design-tone-starter)

## 第一次怎么用

1. 自行下载所需桌面客户端：[官方下载](https://open-design.ai/zh/download/)；也可按需要选择 [OpenDesign Cloud](https://open-design.ai/cloud/)。
2. 解压本 skill，将**整个 `design-tone-starter` 文件夹**交给具有文件读取能力的 agent，或放入所用宿主支持的 skills 目录。宿主安装路径以其官方说明为准；无需安装时也可以明确让 agent 读取入口文件。
3. 把下面这段话发给它，附上真实的文件夹位置：

   ```text
   请读取这个文件夹里的 SKILL.md，使用“设计定调助手”带我开始。
   先和我确定项目目录，再问方向、参考链接和大致效果。
   每轮问少量问题，按步骤带我做。
   ```

   已被宿主识别为 skill 时，可以直接说：

   ```text
   使用 $design-tone-starter，帮我从一个想法开始做设计。
   ```

助手会先建项目分区，再询问思路。视频类推荐文案前置；网页无口播需求时跳过声音环节。

## 它会带你走什么流程

```text
建项目目录
  → 问方向、参考与想要的样子
  → 分析参考，写步骤与目标
  → 视频推荐先确认文案
  → 列需要收集的资料和用途
  → 素材入库、筛选
  → 第二个有视觉能力的 agent 看实际材料
  → 制作静音网页预览，按反馈返工
  → 用户确认最终视觉方案
  → 有声音需求时，交豆包做 TTS 与音效
```

新项目分为：核心分区、素材库、过滤库、制作区、最终方案、成品。原始资料留在素材库，过滤库保存采用意见和依据。每一步记下结果放哪里、接下来做什么，下次接着进度继续。

## 推荐分工

| 工作 | 使用方式 |
|---|---|
| 设计与制作 | Claude 优先；无法使用时选有本地工具能力的 DeepSeek agent |
| 审查、素材视觉复核 | Codex 或豆包，按当前入口实际视觉能力选择 |
| 文案 | Gemini 或豆包 |
| TTS、音效 | 固定交豆包，在视觉版本确认后处理 |

有现成连接器时按授权范围调用；没有时使用附带的交接模板，由用户转交材料和反馈。第二个 agent 真正回复后才记录复核结果，skill 本身不提供跨平台自动登录和自动传图服务。

## 预览和声音

常规生产交付可打开的网址与源码定位，视频先做可播放、暂停和重播的**静音网页视觉原型**。不默认导出 MP4，不在视觉制作阶段生成口播、音乐或音效。

本地浏览器可以走硬件加速展示；是否实际使用显卡需单独核验。本机 `localhost` 不能直接给远端豆包访问，声音交接需要实际可读的画面材料或用户认可的可访问链接。

## 可选的资料收集工具

核心流程支持用户手动提供资料，也可调用用户已有工具。

- [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness)：本地 agent 入口之一。
- [reverse-skill](https://github.com/zhaoxuya520/reverse-skill)：所提到“万能抓取”相关能力的上游工具包，范围包含浏览器自动化和逆向。按需求选用即可，它不是本 skill 的必装依赖，也不是 DeepSeek 官方抓取 skill。

详细接入与来源见 [工具与来源链接](references/tool-links.md)。本仓库没有复制用户本机的抓取技能、私人脚本、代理配置或登录资料。

## 目录工具与维护检查

只有目录辅助脚本需要 Python 3.10+，使用标准库，无第三方 Python 依赖。没有 Python 时，agent 可以按照项目约定手动建目录。

在 skill 文件夹里运行，路径含空格时保留引号：

```text
python scripts/init_project.py --root "./我的设计项目" --name "我的设计项目"
```

已明确类型时可加 `--type web` 或 `--type video`。默认 `undecided`，由问答决定。重复执行只补缺少的文件，保留已有简报、进度和素材；类型冲突或计划路径为符号链接/联接目录时停止并报告。

运行本地行为检查：

```text
python -B -m unittest discover -s tests -v
```

检查覆盖目录创建、中文与空格路径、重复运行保留进度和原件、缺失文件补齐、路径类型冲突和链接目录保护。它们不代替真实设计效果、第二 agent 回复或音频生成的验证。

## 文件入口

- [SKILL.md](SKILL.md)：给 agent 的执行入口。
- [项目与进度约定](references/project-contract.md)：目录、素材记录和阶段状态。
- [分阶段问法](references/questions.md)：面向新手的提问示例。
- [交接模板](references/handoffs.md)：素材、制作、审查与豆包声音交接。
- [两种走法示例](references/walkthroughs.md)：网页与视频的虚构流程演示。
- [来源与许可说明](NOTICE.md)：独立编写内容与外部项目边界。

如果这个流程帮你减少了不知道下一步做什么的困扰，欢迎给项目点一个 Star，也欢迎反馈卡住的具体步骤。
