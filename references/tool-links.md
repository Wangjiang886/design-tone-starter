# 工具接入与来源链接

链接核对日期：2026-10-18。具体安装方法、模型和接口以当前官方页面与实际可用工具为准。本 skill 只提供流程和接入说明，不捆绑这些工具的源码或客户端。

## 设计环境：由使用者自行下载

- [官方桌面下载](https://open-design.ai/zh/download/)
- [上游源码、接入说明与 Releases 入口](https://github.com/nexu-io/open-design)
- [OpenDesign Cloud](https://open-design.ai/cloud/)

首次确认用户采用的入口和可用 agent。这里的推荐分工是用户选择的工作方式，不是不同模型效果的排行榜：Claude 制作，无法使用时由 DeepSeek 替代；Codex 或豆包审查；Gemini 或豆包写文案；豆包负责 TTS 和音效。

本机浏览器预览是 Local Codex 路径中的一种展示方式；Claude 或 DeepSeek 的制作接入要按当前客户端实际支持情况选择，不将 Local Codex 的设置原样套给其他 agent。

## 平台提供工具时

以下是接口用途说明，不是假定每个宿主都有这些工具：

1. 续作用户当前项目时可读 `get_active_context` 或使用工具默认的活动上下文；明确要求新项目时才新建。匹配到意外项目先核对，避免改到别的工作。
2. 读可编辑设计优先 `get_artifact` 获取入口与关联文件。入口缺失时先 `list_files` 找实际 HTML/JSX 文件；只有图片或元数据时记录缺少入口。
3. 新设计先 `collect_brief`，复用前面已知答案并让用户完成必要选择，之后 `confirm_brief`。工具返回的内部关联值只用于协议，不让新手复制或理解它们。
4. 使用 OpenDesign Cloud 时按当前工具检查登录状态；需要登录时交用户完成。使用本地 agent 时先 `list_agents`，只传其真实返回的 ID，不猜 `claude` 或其他运行时名称。
5. 平台负责生成的任务走其现有运行流程；同一次动作在响应丢失时复用原请求标识并检查原运行状态。仍在生成时不重复启动，不以直接覆盖文件替代正在运行的生成任务。
6. 完成后取得真实预览入口与源码位置。平台本身的能力范围、导出参数和资源限制按当前版本，不在本 skill 写死旧上限。

没有这些工具时，助手在自身获准的本地文件范围内准备简报、素材索引和制作交接，由用户在已安装客户端使用。不能报告一次没有发生的调用。

## DeepSeek 资料收集：可选接入

- [DeepSeek Harness 官方项目](https://github.com/deepseek-ai/deepseek-harness)：有本地工具能力的 agent 入口之一。应按其当前文档安装；仅打开 DeepSeek 聊天网页，不等于具备本地抓取能力。
- [reverse-skill 上游](https://github.com/zhaoxuya520/reverse-skill)：本次所说“万能抓取”相关浏览器自动化、JS 与协议能力的上游来源。它是范围更广的逆向和工具路由包，适合按实际需求选择，不是本 skill 的必装依赖，也不是 DeepSeek 官方抓取工具。
- [yt-dlp 上游](https://github.com/yt-dlp/yt-dlp)：需要下载参考视频时可由资料工具按当前支持情况选用。

若用户已有 `video-downloader`、`douyin-cdp-pipeline` 等本机技能，先检查实际文件和包外依赖，沿用用户已选择的通道。不要假定这些名称都有统一公共仓库；不要将个人盘符、代理、登录态、旧端口或项目规则写成所有用户的默认配置。

资料工具输出的原件、来源和可读摘要按项目清单入库。资料收集可由用户手动完成，核心定调流程不因此停用。需要安装或接管真实浏览器时，按当前任务授权操作，不能因用户只要方案就启动抓包。

## 文案与声音入口

- [Gemini](https://gemini.google.com/)：文案推荐入口之一。
- [豆包](https://www.doubao.com/)：素材视觉复核、文案以及最终声音交接的推荐入口；实际附件、音频生成和导出能力以选定入口为准。
- [Claude Code 技能文档](https://code.claude.com/docs/en/skills)：若要作为该宿主的已安装 skill 使用，按官方目录规范安装。

这些工具保持各自的版权与条款。主 skill 的 MIT 许可仅覆盖仓库内独立编写的流程、模板和代码，不改变所链接项目的许可。
