import argparse
import glob
import os
import re
import sys
from chapter_writer import ChapterWriter
from config import Config
from outline_generator import OutlineGenerator


def _stream_print(chunk: str) -> None:
    print(chunk, end="", flush=True)


def cmd_generate_outline(args):
    Config.validate()

    premise = args.premise
    if not premise:
        print("请输入核心创意（一句话或一段描述）:")
        premise = input().strip()

    if not premise:
        print("错误：创意不能为空")
        sys.exit(1)

    generator = OutlineGenerator()

    # ── Phase 1: 故事方向选择（支持换一批） ──
    selected_idea = None
    while selected_idea is None:
        print(f"\n核心创意: {premise[:120]}{'...' if len(premise) > 120 else ''}")
        print("\n正在脑爆故事方向...\n")

        ideas = generator.generate_ideas(premise, on_chunk=_stream_print)
        print()  # newline after streaming

        if not ideas:
            print("生成失败，请重试。\n")
            continue

        print("=" * 60)
        for i, idea in enumerate(ideas, 1):
            title = idea.get("title", "未命名")
            genre = idea.get("genre", "?")
            style = idea.get("style", "?")
            hook = idea.get("hook", "")
            summary = idea.get("summary", "")
            print(f"  [{i}] {title}")
            print(f"      题材: {genre}  |  风格: {style}")
            print(f"      卖点: {hook}")
            print(f"      梗概: {summary[:160]}{'...' if len(summary) > 160 else ''}")
            print()

        while True:
            print("-" * 60)
            choice = input(
                f"请选择故事方向（输入 1-{len(ideas)}，"
                f"或输入「换一批」重新生成）: "
            ).strip()

            if choice == "换一批":
                print("\n--- 重新生成新的故事方向 ---\n")
                break

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(ideas):
                    selected_idea = ideas[idx]
                    break
                else:
                    print(f"编号超出范围，请输入 1-{len(ideas)}。")
            except ValueError:
                print(f"输入无效，请输入 1-{len(ideas)} 或「换一批」。")

    # ── Phase 2: 生成详细大纲 ──
    print(f"\n已选定: {selected_idea['title']}")
    print(f"题材: {selected_idea['genre']}  |  风格: {selected_idea['style']}")
    print("\n正在生成详细大纲...\n")

    content = generator.generate(premise, selected_idea, on_chunk=_stream_print)
    safe_title = re.sub(r'[\\/*?:"<>|]', "", selected_idea.get("title", ""))
    filepath = generator.save(content, title_hint=safe_title)

    print(f"\n\n大纲已保存到: {filepath}")
    print("=" * 60)

    # ── Phase 3: 修改循环 ──
    revision_count = 0
    while True:
        print("\n" + "-" * 40)
        feedback = input("输入修改建议（直接回车结束）: ").strip()
        if not feedback:
            print("大纲已定稿。")
            break

        revision_count += 1
        print(f"\n正在根据建议修改大纲（第 {revision_count} 次修改）...\n")
        content = generator.revise(content, feedback, on_chunk=_stream_print)
        filepath = generator.save(content, title_hint=safe_title)
        print(f"\n\n修改后大纲已保存到: {filepath}")
        print("=" * 60)

    # ── Phase 4: 逐章写作 ──
    _run_chapter_writing(content)


def _run_chapter_writing(outline_text: str) -> None:
    """Run the chapter-by-chapter writing loop given an outline text."""
    writer = ChapterWriter()
    chapters = writer.parse_outline(outline_text)

    if not chapters:
        print("未能从大纲中解析到章节，无法进行章节写作。")
        return

    print(f"\n共 {len(chapters)} 章，开始逐章写作。")
    print("操作：回车=继续下一章 | 输入建议=修改本章 | jump N=跳到第N章 | list=列表 | quit=退出\n")

    chapter_texts: dict[int, str] = {}  # ch_num -> full text
    idx = 0
    while idx < len(chapters):
        ch = chapters[idx]
        prev_text = ""
        if idx > 0:
            prev_text = chapter_texts.get(chapters[idx - 1]["number"], "")

        print(f"\n{'=' * 60}")
        print(f"正在撰写 第{ch['number']}章: {ch['title']}")
        print(f"所属: {ch['volume']}")
        if ch["summary"]:
            print(f"摘要: {ch['summary']}")
        print(f"{'=' * 60}\n")

        ch_text = writer.write_chapter(
            outline_text, ch, prev_chapter_text=prev_text, on_chunk=_stream_print
        )
        print()  # newline after streaming

        while True:
            print("-" * 40)
            action = input(
                f"第{ch['number']}章已生成。"
                f"回车继续下一章 / 输入修改建议 / jump N / list / quit: "
            ).strip()

            if not action:
                chapter_texts[ch["number"]] = ch_text
                filepath = writer.save(ch_text, ch)
                print(f"第{ch['number']}章已保存到: {filepath}")
                idx += 1
                break

            if action.lower() == "quit":
                chapter_texts[ch["number"]] = ch_text
                writer.save(ch_text, ch)
                print(f"第{ch['number']}章已保存，退出章节写作。")
                return

            if action.lower() == "list":
                _print_chapter_list(chapters, idx)
                continue

            jump_match = re.match(r"^jump\s+(\d+)$", action, re.IGNORECASE)
            if jump_match:
                target = int(jump_match.group(1))
                found = False
                for i, c in enumerate(chapters):
                    if c["number"] == target:
                        chapter_texts[ch["number"]] = ch_text
                        writer.save(ch_text, ch)
                        idx = i
                        found = True
                        print(f"已跳到第{target}章。")
                        break
                if not found:
                    print(f"未找到第{target}章，请检查编号。")
                break

            print(f"\n正在修改第{ch['number']}章...\n")
            ch_text = writer.revise_chapter(
                ch_text, ch, action, on_chunk=_stream_print
            )
            print()

    print(f"\n全部 {len(chapters)} 章写作完成！")


def _print_chapter_list(chapters: list[dict], current_idx: int) -> None:
    for i, ch in enumerate(chapters):
        marker = " ← 当前" if i == current_idx else ""
        status = "  [已写]" if i < current_idx else ""
        print(
            f"  [{i + 1}] 第{ch['number']}章 {ch['title']}"
            f"  ({ch['volume']}){status}{marker}"
        )


def cmd_write_chapters(args):
    Config.validate()

    outline_path = args.outline
    if outline_path:
        if not os.path.isfile(outline_path):
            print(f"错误：文件不存在 - {outline_path}")
            sys.exit(1)
    else:
        # List existing outline files and let user pick
        pattern = os.path.join("output", "outline_*.md")
        files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
        if not files:
            print(f"未找到已有大纲文件（搜索路径: {pattern}）")
            print("请先运行 generate-outline 创建大纲。")
            sys.exit(1)

        print("已有大纲文件:")
        for i, f in enumerate(files, 1):
            mtime = os.path.getmtime(f)
            import datetime
            dt = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            print(f"  [{i}] {f}  ({dt})")

        while True:
            choice = input(f"\n请选择大纲文件（1-{len(files)}）: ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(files):
                    outline_path = files[idx]
                    break
                else:
                    print(f"编号超出范围，请输入 1-{len(files)}。")
            except ValueError:
                print(f"输入无效，请输入 1-{len(files)}。")

    with open(outline_path, "r", encoding="utf-8") as f:
        outline_text = f.read()

    print(f"\n已加载大纲: {outline_path}")
    _run_chapter_writing(outline_text)


def _interactive_menu() -> None:
    """Show interactive menu when no subcommand is given."""
    print("=" * 40)
    print("  自动写小说 Agent")
    print("=" * 40)
    print("  [1] 创建新大纲（从创意开始）")
    print("  [2] 从已有大纲续写章节")
    print("  [0] 退出")
    print("=" * 40)

    while True:
        choice = input("\n请选择: ").strip()
        if choice == "1":
            cmd_generate_outline(argparse.Namespace(premise=None))
            break
        elif choice == "2":
            cmd_write_chapters(argparse.Namespace(outline=None))
            break
        elif choice == "0":
            print("再见！")
            break
        else:
            print("输入无效，请输入 0-2。")


def main():
    parser = argparse.ArgumentParser(description="自动写小说 Agent - MVP")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    outline_parser = subparsers.add_parser(
        "generate-outline",
        help="根据创意生成3-5个故事方向供选择，再生成完整大纲",
    )
    outline_parser.add_argument(
        "--premise", type=str, help="核心创意（一句话或一段描述），留空则交互式输入"
    )
    outline_parser.set_defaults(func=cmd_generate_outline)

    write_parser = subparsers.add_parser(
        "write-chapters",
        help="从已有大纲文件开始逐章写作",
    )
    write_parser.add_argument(
        "--outline", type=str, help="大纲文件路径，留空则从output/目录选择"
    )
    write_parser.set_defaults(func=cmd_write_chapters)

    args = parser.parse_args()

    if args.command is None:
        _interactive_menu()
        return

    args.func(args)


if __name__ == "__main__":
    main()
