# Question Extractor

Extracts questions from PDF textbooks and generates PowerPoint presentations.

## What it does

1. Converts a PDF to Markdown using the Mathpix API (`md_generator.py`)
2. Parses questions from the Markdown (`question_parser.py`)
3. Generates a `.pptx` with one question per slide (`ppt_generator.py`)

## Setup

1. Clone the repo
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory:
   ```
   app_id="your_mathpix_app_id"
   app_key="your_mathpix_app_key"
   ```

## Usage

First, convert your PDF to Markdown:
```bash
python md_generator.py
```

Then generate the PowerPoint:
```bash
python main.py
```

Output will be saved to the `output/` folder.

## Configuration

`parser_config.py` contains presets for different question formats:
- `arihant_illustration` — Arihant-style books with `## ILLUSTRATION` headings
- `numbered` — Standard numbered questions (1. 2. 3.)
- `q_prefix` — Q-prefixed questions (Q1. Q2.)

You can also build a custom `ParserConfig` manually — see `main.py` for an example.
