import re
from parser_config import ParserConfig, PRESETS


class QuestionParser:
    """
    Generic parser driven entirely by ParserConfig.
    Replaces the hardcoded IllustrationParser.

    Usage:
        config = PRESETS["arihant_illustration"]
        parser = QuestionParser(config)
        questions = parser.parse(md_text)
    """

    def __init__(self, config: ParserConfig):
        self.config = config
        self._block_pattern = self._build_block_pattern()
        self._solution_pattern = self._build_solution_pattern()

    # ─────────────────────────────────────────
    #  PATTERN BUILDERS  (called once on init)
    # ─────────────────────────────────────────


    def _build_block_pattern(self) -> re.Pattern:
        """
        Build a regex that splits the document into question blocks
        based on config.question.prefixes.

        Handles two cases:
          - Heading-style:  "## ILLUSTRATION 7.57"
          - Inline-style:   "Q.1", "1.", "Q1"
        """

        escaped = [re.escape(p) for p in self.config.question.prefixes]
        prefix_group = '|'.join(escaped)

        if self.config.question.numbering == "decimal":
            number = r'\d+\.\d+(?!\d)'  # Fix 2: negative lookahead
        elif self.config.question.numbering == "integer":
            number = r'\d+'
        else:
            number = r''

        if number:
            block_start = rf'(?:#+\s*)?(?:{prefix_group})\s*{number}'  # Fix 1: optional ##
        else:
            block_start = rf'(?:#+\s*)?(?:{prefix_group})'

        pattern = rf'({block_start}.*?)(?={block_start}|\Z)'
        return re.compile(pattern, re.S)



    def _build_solution_pattern(self) -> re.Pattern:
        """
        Build a regex that matches the start of a solution section.
        Handles both inline ("Sol.") and heading ("## Sol.") forms.
        """
        escaped = [re.escape(p) for p in self.config.solution.prefixes]
        prefix_group = '|'.join(escaped)
        pattern = rf'\n(?:#+\s*)?(?:{prefix_group})'
        return re.compile(pattern, re.IGNORECASE)

    # ─────────────────────────────────────────
    #  CORE PARSING
    # ─────────────────────────────────────────

    def match(self, text: str) -> bool:
        """Quick check: does this file look like it contains questions?"""
        return bool(self._block_pattern.search(text))

    def normalize(self, text: str) -> str:
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def extract_blocks(self, text: str) -> list[str]:
        return self._block_pattern.findall(text)

    def extract_id(self, block: str) -> str:
        """Pull the question number out of the block's first line."""
        first_line = block.split('\n')[0]
        if self.config.question.numbering == "decimal":
            m = re.search(r'(\d+\.\d+)', first_line)
        else:
            m = re.search(r'(\d+)', first_line)
        return m.group(1) if m else "?"

    def split_question_solution(self, block: str) -> tuple[str, str]:
        """
        Split a block into (question_text, solution_text).
        Returns ("", "") for solution if none found or not present.
        """
        # Remove the heading line (first line)
        body = block.split('\n', 1)[1].strip() if '\n' in block else block

        if not self.config.solution.present:
            return body, ""

        parts = self._solution_pattern.split(body, maxsplit=1)
        question = parts[0].strip()
        solution = parts[1].strip() if len(parts) > 1 else ""
        return question, solution

    def extract_images(self, text: str) -> list[str]:
        return re.findall(r'!\[.*?\]\((.*?)\)', text)

    def has_math(self, text: str) -> bool:
        return bool(re.search(r'\$|\\[([]', text))

    def clean_math(self, text: str) -> str:
        """Strip LaTeX delimiters and convert to plain text."""
        text = re.sub(r'\$\$(.*?)\$\$', lambda m: self._latex_to_text(m.group(1)), text, flags=re.S)
        text = re.sub(r'\\\[(.*?)\\\]',  lambda m: self._latex_to_text(m.group(1)), text, flags=re.S)
        text = re.sub(r'\$(.*?)\$',      lambda m: self._latex_to_text(m.group(1)), text, flags=re.S)
        text = re.sub(r'\\\((.*?)\\\)',  lambda m: self._latex_to_text(m.group(1)), text, flags=re.S)
        return text

    def _latex_to_text(self, latex: str) -> str:
        t = latex.strip()
        t = re.sub(r'\^\{?(\w+)\}?C_\{?(\w+)\}?', r'\1C\2', t)
        t = re.sub(r'\^\{?(\w+)\}?P_\{?(\w+)\}?', r'\1P\2', t)
        t = re.sub(r'\\frac\{([^}]*)\}\{([^}]*)\}', r'(\1/\2)', t)
        t = re.sub(r'\^\{([^}]*)\}', r'^\1', t)
        t = re.sub(r'_\{([^}]*)\}',  r'_\1', t)
        replacements = [
            (r'\\times',             r'x'),
            (r'\\cdot',              r'.'),
            (r'\\leq',               r'<='),
            (r'\\geq',               r'>='),
            (r'\\neq',               r'!='),
            (r'\\approx',            r'~'),
            (r'\\infty',             r'inf'),
            (r'\\alpha',             r'alpha'),
            (r'\\beta',              r'beta'),
            (r'\\gamma',             r'gamma'),
            (r'\\theta',             r'theta'),
            (r'\\pi',                r'pi'),
            (r'\\sum',               r'sum'),
            (r'\\prod',              r'prod'),
            (r'\\sqrt\{([^}]*)\}',   r'sqrt(\1)'),
            (r'\\left',              r''),
            (r'\\right',             r''),
            (r'\\quad',              r' '),
            (r'\\text\{([^}]*)\}',   r'\1'),
            (r'\\begin\{[^}]*\}',    r''),
            (r'\\end\{[^}]*\}',      r''),
            (r'\\\\',                '\n'),
            (r'\\[a-zA-Z]+',         r''),
            (r'[{}]',                r''),
        ]
        for pattern, replacement in replacements:
            t = re.sub(pattern, replacement, t)
        return t.strip()

    def parse(self, text: str) -> list[dict]:
        text = self.normalize(text)
        blocks = self.extract_blocks(text)

        questions = []
        for block in blocks:
            question_id = self.extract_id(block)
            raw_q, raw_sol = self.split_question_solution(block)

            if not raw_q:
                continue

            mode = self.config.solution.mode
            if mode == "same_slide":
                slide_text = raw_q + "\n\n" + raw_sol
            else:
                slide_text = raw_q

            entry = {
                "question_id": question_id,
                "raw": slide_text,
                "images": self.extract_images(raw_q),
                "has_math": self.has_math(raw_q),
            }

            if mode == "next_slide" and raw_sol:
                entry["solution"] = raw_sol
            else:
                entry["solution"] = ""

            questions.append(entry)

        return questions