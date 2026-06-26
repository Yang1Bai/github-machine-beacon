# GitHub Machine Beacon 中文说明

这是一个 GitHub 机器浏览触发实验项目。目标是让仓库对搜索引擎、GitHub 内部索引、代码搜索、AI agent、LLM 抓取器、链接预览 bot、归档工具和引用工具都更容易发现、更容易解析、更容易复访。

[![Cloudflare 实时访问量](https://beacon.ybliterature.com/traffic-card.svg?v=0.6.0)](https://beacon.ybliterature.com/)

实时主页：[https://beacon.ybliterature.com/](https://beacon.ybliterature.com/)

GitHub Pages 镜像：[https://yang1bai.github.io/github-machine-beacon/](https://yang1bai.github.io/github-machine-beacon/)
机器/人拆分 JSON：[cloudflare-traffic.json](https://beacon.ybliterature.com/cloudflare-traffic.json)
机器地理位置聚合 JSON：[geo-traffic.json](https://beacon.ybliterature.com/geo-traffic.json)
流量类型拆分 JSON：[traffic-classes.json](https://beacon.ybliterature.com/traffic-classes.json)
AI 阅读入口 JSON：[ai-readers.json](https://beacon.ybliterature.com/ai-readers.json)
AI 阅读上下文：[ai-reader-context.txt](https://beacon.ybliterature.com/ai-reader-context.txt)

核心原则：公开、透明、可复现，不刷量、不伪装、不堆无关关键词。

## 第二版增强

我把项目从“可发布实验”升级成“可引用资源库”。现在它不只是有机器入口，还提供了一组真实有用的页面：

- [Machine-Readable Repository Checklist](https://beacon.ybliterature.com/machine-readable-repository-checklist.html)
- [Crawler Surface Map](https://beacon.ybliterature.com/crawler-surface-map.html)
- [AI Agent Entrypoints](https://beacon.ybliterature.com/ai-agent-entrypoints.html)
- [Experiment Protocol](https://beacon.ybliterature.com/experiment-protocol.html)
- [Standards and Sources](https://beacon.ybliterature.com/standards-and-sources.html)
- [Crawlability Audit](https://beacon.ybliterature.com/crawlability-audit.html)
- [Results Log](https://beacon.ybliterature.com/results-log.html)

## 首页访问量显示

首页现在有一个大号实时流量面板，主数据来自 Cloudflare Worker：

- `total requests`、`machine visits`、`human visits` 和 `unknown` 来自 [`cloudflare-traffic.json`](https://beacon.ybliterature.com/cloudflare-traffic.json)。
- 机器访问会在 [`traffic-classes.json`](https://beacon.ybliterature.com/traffic-classes.json) 中拆成 `ai_reader`、`security_scanner` 和 `generic_machine`。
- Cloudflare 已识别的 `AI Crawler`、`AI Search`、`AI Assistant` 会计入 `ai_reader`；敏感文件探测路径仍优先归为 `security_scanner`。
- 机器访问地理位置来自 [`geo-traffic.json`](https://beacon.ybliterature.com/geo-traffic.json)，按国家、地区、城市、Cloudflare colo 和 ASN 组织聚合。
- README 顶部访问量卡片由 Worker 动态生成：[`traffic-card.svg`](https://beacon.ybliterature.com/traffic-card.svg)。
- GitHub 官方 `views`、`unique visitors` 和 `clones` 仍然保留在 [`traffic.json`](traffic.json)，但它是较慢刷新的官方快照。
- `.github/workflows/update-traffic.yml` 会定时刷新 GitHub API 快照，数据变化时自动重新发布 Pages。

自动刷新需要配置一个名为 `TRAFFIC_TOKEN` 的仓库 secret，并授予读取 repository traffic 的权限。没有这个 secret 时，定时 workflow 会安全跳过，首页显示最后一次已提交的官方快照。

机器/人拆分现在由 Cloudflare Worker 统计：经过 `https://beacon.ybliterature.com/` 的请求会按 user-agent 和请求头启发式分类。`/.env`、`/.git/config`、`wp-login.php`、`xmlrpc.php`、`phpinfo.php` 这类敏感文件或漏洞探测路径会优先归为 `security_scanner`，不再算作 AI reader。

地理位置是近似值，代表请求出口或云节点位置，不等于 AI 公司真实位置。Worker 只保存聚合计数，不保存原始 IP 或经纬度。

## 实验思路

普通 GitHub 仓库大多只靠 README 被理解。这个项目把“机器读者”当成第一类读者来设计：

- README 负责 GitHub 页面和代码搜索理解。
- GitHub Pages 负责通用网页爬虫入口。
- `ai-readers.json` 和 `ai-reader-context.txt` 负责给 AI readers 一个更直接的入口。
- `llms.txt` 和 `llms-full.txt` 负责 LLM/agent 读者。
- `crawler-manifest.json` 负责结构化机器索引。
- `keyword-index.json` 负责把关键词按意图分组，避免变成无意义堆砌。
- `resources.json` 负责把所有资源页和机器入口统一成结构化索引。
- `traffic.json` 负责给首页大号访问量面板提供公开流量快照。
- `sitemap.xml` 和 `feed.xml` 负责发现和复访。
- `docs/measurement.md` 负责记录 GitHub traffic 指标。

## 该做什么

1. 修改 [`data/beacon.json`](data/beacon.json) 里的用户名、仓库地址和 Pages 地址。
2. 运行生成脚本，让 sitemap、manifest、feed、llms 文件同步。
3. 运行校验脚本，检查 JSON/XML、内部链接、占位符和关键入口。
4. 推送到 GitHub。
5. 开启 GitHub Pages。
6. 添加 [`docs/github-topics.txt`](docs/github-topics.txt) 里的主题标签。
7. 按 [`docs/measurement.md`](docs/measurement.md) 每天记录浏览数据。

## 不该做什么

- 不运行刷访问量脚本。
- 不使用代理流量。
- 不伪装成热门项目。
- 不隐藏关键词。
- 不添加不相关热门关键词。
- 不收集个人数据。

## 判断是否成功

优先看：

- GitHub repository views
- unique visitors
- referrers
- popular content
- clones
- unique cloners

其次看：

- 搜索结果中是否出现项目名
- 是否有外部链接和引用
- 是否有人或 agent 在 issue/discussion 里提到项目
- 发布 GitHub Pages 和 release 后，访问曲线是否发生变化

## 项目定位

这个项目最有价值的地方不是“骗机器来访问”，而是测试：当一个开源项目把机器可读性做到足够完整时，平台和爬虫会不会更频繁、更准确地发现它。
