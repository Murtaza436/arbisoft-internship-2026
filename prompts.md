# prompts.md — AI Interaction Log

## Week 1: AI/ML Foundations

### 2026-06-23
**Prompt:** "Explain the full week 1 and week 2 assignments from my Arbisoft internship roadmap in detail so I can explain to my mentor what I am doing — what each file does, where each function is, and what each function does."
**Model:** Claude (claude.ai)
**Result:** Received a complete breakdown of the project structure, every file purpose, and a function-by-function explanation of data_prep.py, train.py, evaluate.py, main.py, and the test file. Used this as the conceptual foundation before writing any code.

### 2026-06-23
**Prompt:** "uv init week1-ml is giving access denied error in PowerShell."
**Model:** Claude (claude.ai)
**Result:** Learned that PowerShell was running inside C:\WINDOWS\System32, a protected directory. Fix was to navigate to the Desktop first before running uv init.

### 2026-06-23
**Prompt:** "pytest is giving ModuleNotFoundError: No module named src when running tests."
**Model:** Claude (claude.ai)
**Result:** Two fixes required: create empty __init__.py files inside src/ and tests/ so Python treats them as packages, and add pythonpath to pyproject.toml so pytest resolves imports from the project root.

### 2026-06-23
**Prompt:** "pyproject.toml is giving TOML parse error: key with no value."
**Model:** Claude (claude.ai)
**Result:** The section header was accidentally split across multiple lines. TOML requires the entire header on one line as [tool.pytest.ini_options]. Fixed by overwriting the file using PowerShell Set-Content command.

### 2026-06-23
**Prompt:** "src/__init__.py is giving SyntaxError — the PowerShell New-Item command text was written into the file instead of creating an empty file."
**Model:** Claude (claude.ai)
**Result:** Fixed by running Set-Content src\__init__.py and Set-Content tests\__init__.py to overwrite both files with empty content.

### 2026-06-23
**Prompt:** "ruff check is returning 6 errors: W292 no newline at end of file and F401 pandas imported but unused."
**Model:** Claude (claude.ai)
**Result:** All 6 errors were auto-fixable. Ran ruff check with --fix flag. W292 means files must end with a blank newline. F401 means unused import — ruff removed the unused pandas import from the test file.
