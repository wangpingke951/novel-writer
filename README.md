# Novel Writer - 自动写小说 Agent

基于 DeepSeek API 的 AI 网文写作助手，从一句话创意到逐章正文，全流程辅助创作。

## 功能

- **故事方向脑爆** — 输入一句话梗概，生成 3-5 个不同侧重的故事方向（书名/题材/风格/卖点/梗概），支持"换一批"
- **完整大纲生成** — 选定方向后自动生成含分卷、章节标题和摘要的详细大纲，支持多轮修改
- **逐章正文写作** — 沿大纲逐章撰写 3000-5000 字正文，保持人物和剧情连贯
- **断点续写** — 支持从已有大纲文件直接开始写章节，无需重新走大纲流程
- **Streaming 输出** — 所有 LLM 调用实时流式展示，零等待体验

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
cp .env.example .env
# 编辑 .env，填入你的 DeepSeek API Key
```

### 3. 运行

```bash
# 方式一：交互式菜单
python main.py

# 方式二：直接创建大纲
python main.py generate-outline

# 方式三：从已有大纲续写章节
python main.py write-chapters
```

### 启动脚本（可选）

**macOS / Linux:**
```bash
chmod +x novel
# 将项目目录加入 PATH，或创建软链接
./novel
```

**Windows:**
将项目目录加入 PATH 后，在 CMD 中直接输入 `novel` 即可运行。

## 命令说明

| 命令 | 说明 |
|------|------|
| `python main.py` | 交互式菜单 |
| `python main.py generate-outline` | 从创意生成大纲 |
| `python main.py generate-outline --premise "你的创意"` | 带创意参数直接生成 |
| `python main.py write-chapters` | 从已有大纲续写（交互选择文件） |
| `python main.py write-chapters --outline output/xxx.md` | 指定大纲文件续写 |

## 工作流

```
输入创意 → 选择故事方向 → 生成大纲 → 修改迭代 → 逐章写作
                                                      ↓
                                         每章: 写 → 审 → 改/通过 → 下一章
```

章节写作时的交互操作：
- **回车** — 保存当前章节，继续写下一章
- **输入修改建议** — 根据反馈修改当前章节
- **jump N** — 跳到第 N 章
- **list** — 列出所有章节及状态
- **quit** — 保存当前章节并退出

## 配置

所有配置通过 `.env` 文件管理：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | — |
| `DEEPSEEK_BASE_URL` | API 地址 | `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | 模型名称 | `deepseek-v4-flash` |
| `TEMPERATURE` | 生成温度 | `0.7` |
| `MAX_TOKENS` | 最大输出 token | `8192` |
| `THINKING_LEVEL` | 思考模式 (enabled/adaptive/disabled) | `enabled` |

## 输出结构

```
output/
├── outline_xxx.md          # 大纲文件
└── chapters/
    ├── ch0001_章节标题.md   # 第1章正文
    ├── ch0002_章节标题.md   # 第2章正文
    └── ...
```

## 技术栈

- Python 3.12+
- DeepSeek API (OpenAI SDK 兼容)
- Streaming + Thinking 模式

## License

MIT
