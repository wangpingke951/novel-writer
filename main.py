import argparse
import sys
from config import Config
from outline_generator import OutlineGenerator


def cmd_generate_outline(args):
    Config.validate()

    premise = args.premise

    if not premise:
        print("请输入一句话创意（输入完成后回车）:")
        premise = input().strip()

    if not premise:
        print("错误：创意不能为空")
        sys.exit(1)

    generator = OutlineGenerator()
    genre = args.genre
    style = args.style

    if not genre or not style:
        print(f"\n创意: {premise[:100]}{'...' if len(premise) > 100 else ''}")
        print("正在分析题材和风格...")
        info = generator.classify(premise)
        genre = genre or info.get("genre", "玄幻")
        style = style or info.get("style", "热血升级流")
        title = info.get("title", "")
        print(f"识别结果 → 题材: {genre} | 风格: {style}")
        if title:
            print(f"建议书名: {title}")
    else:
        print(f"\n题材: {genre}")
        print(f"风格: {style}")
        print(f"创意: {premise[:80]}{'...' if len(premise) > 80 else ''}")

    print("\n正在生成大纲，请稍候...\n")

    content = generator.generate(genre, style, premise)
    filepath = generator.save(content)

    print(f"大纲已保存到: {filepath}")
    print("=" * 60)
    print(content)

    # Interactive revision loop
    revision_count = 0
    while True:
        print("\n" + "-" * 40)
        feedback = input("输入修改建议（直接回车结束）: ").strip()

        if not feedback:
            print("大纲已定稿，结束。")
            break

        revision_count += 1
        print(f"\n正在根据建议修改大纲（第 {revision_count} 次修改）...\n")
        content = generator.revise(content, feedback)
        filepath = generator.save(content)

        print(f"修改后大纲已保存到: {filepath}")
        print("=" * 60)
        print(content)


def main():
    parser = argparse.ArgumentParser(description="自动写小说 Agent - MVP")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    outline_parser = subparsers.add_parser("generate-outline", help="生成小说大纲")
    outline_parser.add_argument("--genre", type=str, help="题材，留空自动识别")
    outline_parser.add_argument("--style", type=str, help="风格，留空自动识别")
    outline_parser.add_argument("--premise", type=str, help="一句话创意（核心卖点）")
    outline_parser.set_defaults(func=cmd_generate_outline)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
