# GitHub Machine Beacon 中文说明

这是一个 GitHub 机器浏览触发实验项目。目标是让仓库对搜索引擎、GitHub 内部索引、代码搜索、AI agent、LLM 抓取器、链接预览 bot、归档工具和引用工具都更容易发现、更容易解析、更容易复访。

核心原则：公开、透明、可复现，不刷量、不伪装、不堆无关关键词。

## 实验思路

普通 GitHub 仓库大多只靠 README 被理解。这个项目把“机器读者”当成第一类读者来设计：

- README 负责 GitHub 页面和代码搜索理解。
- GitHub Pages 负责通用网页爬虫入口。
- `llms.txt` 和 `llms-full.txt` 负责 LLM/agent 读者。
- `crawler-manifest.json` 负责结构化机器索引。
- `keyword-index.json` 负责把关键词按意图分组，避免变成无意义堆砌。
- `sitemap.xml` 和 `feed.xml` 负责发现和复访。
- `docs/measurement.md` 负责记录 GitHub traffic 指标。

## 该做什么

1. 修改 [`data/beacon.json`](data/beacon.json) 里的用户名、仓库地址和 Pages 地址。
2. 运行生成脚本，让 sitemap、manifest、feed、llms 文件同步。
3. 推送到 GitHub。
4. 开启 GitHub Pages。
5. 添加 [`docs/github-topics.txt`](docs/github-topics.txt) 里的主题标签。
6. 按 [`docs/measurement.md`](docs/measurement.md) 每天记录浏览数据。

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
