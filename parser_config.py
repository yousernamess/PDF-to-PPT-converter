from dataclasses import dataclass, field


# ─────────────────────────────────────────
#  CONFIG SCHEMA
# ─────────────────────────────────────────

@dataclass
class QuestionConfig:
    """Describes how questions are marked in the MD file."""

    # The prefix pattern that starts a question block.
    # Examples: "Q.", "Q ", "## ILLUSTRATION", "Example", "Problem"
    prefixes: list[str] = field(default_factory=lambda: ["## ILLUSTRATION"])

    # Whether question numbers follow a pattern like 1.1, 7.57 (decimal)
    # or plain integers like 1, 2, 3
    numbering: str = "decimal"          # "decimal" | "integer" | "none"


@dataclass
class SolutionConfig:
    """Describes how solutions are marked in the MD file."""

    # Markers that indicate the start of a solution
    # Examples: ["Sol.", "Solution:", "Ans.", "Answer:"]
    prefixes: list[str] = field(default_factory=lambda: ["Sol.", "Solution", "Ans."])

    # Whether solutions exist in this file at all
    present: bool = True

    # What to do with solutions in the PPT
    # "none"       → strip solution, question only
    # "same_slide" → question + solution on one slide
    # "next_slide" → solution on the slide immediately after the question
    mode: str = "none"


@dataclass
class SlideConfig:
    """Controls what ends up on each slide."""

    # Include sub-parts like (i), (ii) or (a), (b) as part of the question text
    include_subparts: bool = True

    # Extract and show chapter/section heading on the slide
    show_chapter: bool = False


@dataclass
class ParserConfig:
    """
    Top-level config. One instance per parsing job.
    The UI collects these fields from the user and passes this
    object to QuestionParser.
    """
    question: QuestionConfig = field(default_factory=QuestionConfig)
    solution: SolutionConfig = field(default_factory=SolutionConfig)
    slide: SlideConfig = field(default_factory=SlideConfig)


# ─────────────────────────────────────────
#  PRESETS  (built-in defaults for known book formats)
# ─────────────────────────────────────────

PRESETS: dict[str, ParserConfig] = {

    # Arihant-style books (current format you're already handling)
    "arihant_illustration": ParserConfig(
        question=QuestionConfig(
            prefixes=["## ILLUSTRATION", "ILLUSTRATION", "ILLISTRATION"],  # ✅ added
            numbering="decimal",
        ),
        solution=SolutionConfig(
            prefixes=["Sol.", "## Sol.", "Solution"],
            present=True,
            mode="none",
        ),
    ),

    # Standard numbered questions: 1. 2. 3.
    "numbered": ParserConfig(
        question=QuestionConfig(
            prefixes=["1.", "2.", "3."],   # parser will generalise from these
            numbering="integer",
        ),
        solution=SolutionConfig(
            prefixes=["Ans.", "Answer:"],
            present=True,
            mode="none",
        ),
    ),

    # Q-prefixed: Q1. Q2. or Q. 1
    "q_prefix": ParserConfig(
        question=QuestionConfig(
            prefixes=["Q."],
            numbering="integer",
        ),
        solution=SolutionConfig(
            prefixes=["Sol.", "Ans."],
            present=True,
            mode="none",
        ),
    ),
}
