import re


class IllustrationParser:

    def match(self, text: str) -> bool:
        return "ILLUSTRATION" in text

    def normalize(self, text: str) -> str:
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def extract_blocks(self, text: str) -> list[str]:
        """Extract ONLY illustration blocks."""
        pattern = r'(## ILLUSTRATION \d+\.\d+.*?)(?=## ILLUSTRATION \d+\.\d+|\Z)'
        return re.findall(pattern, text, re.S)

    def extract_id(self, block: str) -> str:
        """Extract actual illustration number e.g. '7.57' from heading."""
        match = re.search(r'## ILLUSTRATION (\d+\.\d+)', block)
        return match.group(1) if match else "unknown"

    def clean_block(self, block: str) -> str:
        """Keep only text AFTER heading and BEFORE solution marker."""
        # Remove heading
        block = re.sub(r'## ILLUSTRATION \d+\.\d+', '', block).strip()

        # Stop at solution marker — handles both inline "Sol." and heading "## Sol."
        block = re.split(
            r'\n(?:##\s*)?(?:Sol\.|Solution[\s:.]|Ans\.)',
            block,
            flags=re.IGNORECASE
        )[0]

        return block.strip()

    def extract_images(self, text: str) -> list[str]:
        return re.findall(r'!\[.*?\]\((.*?)\)', text)

    def has_math(self, text: str) -> bool:
        return bool(re.search(r'\$|\\[([]', text))

    def clean_math(self, text: str) -> str:
        """Strip LaTeX delimiters and convert to plain text for PowerPoint."""
        # Display math first: $$...$$ and \[...\]
        text = re.sub(r'\$\$(.*?)\$\$', lambda m: self._latex_to_text(m.group(1)), text, flags=re.S)
        text = re.sub(r'\\\[(.*?)\\\]',  lambda m: self._latex_to_text(m.group(1)), text, flags=re.S)

        # Inline math: $...$ and \(...\)
        text = re.sub(r'\$(.*?)\$',      lambda m: self._latex_to_text(m.group(1)), text, flags=re.S)
        text = re.sub(r'\\\((.*?)\\\)',  lambda m: self._latex_to_text(m.group(1)), text, flags=re.S)

        return text

    def _latex_to_text(self, latex: str) -> str:
        t = latex.strip()

        # nCr / nPr — before generic super/subscript handling
        t = re.sub(r'\^\{?(\w+)\}?C_\{?(\w+)\}?', r'\1C\2', t)
        t = re.sub(r'\^\{?(\w+)\}?P_\{?(\w+)\}?', r'\1P\2', t)

        # \frac{a}{b} -> (a/b)
        t = re.sub(r'\\frac\{([^}]*)\}\{([^}]*)\}', r'(\1/\2)', t)

        # Superscripts and subscripts: ^{abc} -> ^abc, _{abc} -> _abc
        t = re.sub(r'\^\{([^}]*)\}', r'^\1', t)
        t = re.sub(r'_\{([^}]*)\}',  r'_\1', t)

        # Common symbols
        replacements = [
            (r'\\times',                r'x'),
            (r'\\cdot',                 r'.'),
            (r'\\leq',                  r'<='),
            (r'\\geq',                  r'>='),
            (r'\\neq',                  r'!='),
            (r'\\approx',               r'~'),
            (r'\\infty',                r'inf'),
            (r'\\alpha',                r'alpha'),
            (r'\\beta',                 r'beta'),
            (r'\\gamma',                r'gamma'),
            (r'\\theta',                r'theta'),
            (r'\\pi',                   r'pi'),
            (r'\\sum',                  r'sum'),
            (r'\\prod',                 r'prod'),
            (r'\\sqrt\{([^}]*)\}',      r'sqrt(\1)'),
            (r'\\left',                 r''),
            (r'\\right',                r''),
            (r'\\quad',                 r' '),
            (r'\\text\{([^}]*)\}',      r'\1'),
            (r'\\begin\{[^}]*\}',       r''),
            (r'\\end\{[^}]*\}',         r''),
            (r'\\\\',                   r'\n'),
            (r'\\[a-zA-Z]+',            r''),   # strip remaining unknown commands
            (r'[{}]',                   r''),   # strip leftover braces
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
            clean_q = self.clean_block(block)
            images = self.extract_images(clean_q)

            if not clean_q:
                continue

            questions.append({
                "question_id": question_id,
                "raw": self.clean_math(clean_q),
                "images": images,
                "has_math": self.has_math(clean_q),  # flagged before math is stripped
            })

        return questions


# =========================
# MAIN EXECUTION
# =========================

def load_markdown(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Markdown file not found: {file_path}")


def main():
    md_text = load_markdown("output/sample.md")

    parser = IllustrationParser()

    if not parser.match(md_text):
        print("No matching parser found")
        return

    questions = parser.parse(md_text)

    for q in questions:
        print(q["question_id"])
        print(q["raw"][:200])
        print("Images:", q["images"])
        print("Math:", q["has_math"])
        print("-----")


if __name__ == "__main__":
    main()
