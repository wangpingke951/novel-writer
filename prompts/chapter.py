CHAPTER_SYSTEM_PROMPT = """你是一位资深网络小说作家，擅长创作引人入胜的网文章节。

你需要根据小说大纲和当前章节信息，撰写出完整的章节正文。

写作要求：
1. 字数：3000-5000字，内容充实，不要灌水
2. 语言风格：符合网文特点，对话生动自然，描写细腻有画面感，节奏张弛有度
3. 严格遵循大纲中该章的摘要，但可以适当发挥细节和对话
4. 保持与前文的连贯性——人物性格、情节线索、世界观设定要前后一致
5. 每章要有完整的起承转合，结尾留钩子吸引读者继续
6. 适度运用网文爽点技巧（打脸、装逼、反转、悬念等），但要自然不刻意
7. 对话和内心独白要有人物特色，不要让所有角色说话风格相同

输出格式：直接输出章节正文（Markdown格式），以章节标题开头。"""


def chapter_user_prompt(outline_text: str, chapter_info: dict, prev_chapter_text: str = "") -> str:
    lines = [
        "请根据以下小说大纲和章节信息，撰写本章正文：",
        "",
        "---",
        "# 完整大纲",
        outline_text,
        "",
        "---",
    ]

    if prev_chapter_text:
        lines += [
            "# 前一章原文（供剧情和风格参考）",
            prev_chapter_text,
            "",
            "---",
        ]

    lines += [
        "# 当前待写章节",
        f"卷: {chapter_info['volume']}",
        f"章号: 第{chapter_info['number']}章",
        f"标题: {chapter_info['title']}",
        f"摘要: {chapter_info['summary']}",
        "",
        "请直接输出本章正文（3000-5000字）。",
    ]

    return "\n".join(lines)


CHAPTER_REVISION_PROMPT = """你是一位资深网络小说编辑。用户对之前撰写的章节正文提出了一些修改建议，请根据建议修改。

注意：
1. 只修改用户提到的部分，保留其他未提及的内容
2. 保持相同的输出格式
3. 保持与大纲的一致性
4. 修改后章节长度保持合理（3000-5000字）"""


def chapter_revision_user_prompt(
    original_text: str, chapter_info: dict, feedback: str
) -> str:
    return f"""以下是原始章节正文：

{original_text}

---

章节信息：
- 卷: {chapter_info['volume']}
- 章号: 第{chapter_info['number']}章
- 标题: {chapter_info['title']}

修改建议：

{feedback}

---

请输出修改后的完整章节正文。"""
