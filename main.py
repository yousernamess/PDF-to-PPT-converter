import sys
from question_parser import QuestionParser
from parser_config import PRESETS, ParserConfig, QuestionConfig, SolutionConfig, SlideConfig
from ppt_generator import create_ppt


def main():
    # Load markdown
    try:
        with open("output/sample.md", "r", encoding="utf-8") as f:
            md_text = f.read()
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)

    # Pick a config — right now hardcoded, later this comes from your UI
    config = PRESETS["arihant_illustration"]

    # Or build a custom one manually:
    # config = ParserConfig(
    #     question=QuestionConfig(prefixes=["Q."], numbering="integer"),
    #     solution=SolutionConfig(prefixes=["Ans."], present=True, mode="none"),
    # )

    # Parse
    parser = QuestionParser(config)
    if not parser.match(md_text):
        print("No questions found — check the file or config")
        sys.exit(1)

    questions = parser.parse(md_text)
    print(f"Extracted {len(questions)} questions")

    if not questions:
        print("No questions parsed — check the markdown file")
        sys.exit(1)

    # Generate PPT
    create_ppt(questions, "output/questions2.pptx")


if __name__ == "__main__":
    main()



#OLD
#-----------------------------------------------------------------------
# import sys
# from md_parser import IllustrationParser, load_markdown
# from ppt_generator import create_ppt


# def main():
#     # Step 1: Load markdown
#     try:
#         md_text = load_markdown("output/sample.md")
#     except FileNotFoundError as e:
#         print(e)
#         sys.exit(1)

#     # Step 2: Parse questions
#     parser = IllustrationParser()

#     if not parser.match(md_text):
#         print("No matching parser found")
#         sys.exit(1)

#     questions = parser.parse(md_text)
#     print(f"Extracted {len(questions)} questions")

#     if not questions:
#         print("No questions parsed — check the markdown file")
#         sys.exit(1)

#     # Step 3: Generate PPT
#     create_ppt(questions, "output/questions2.pptx")


# if __name__ == "__main__":
#     main()



