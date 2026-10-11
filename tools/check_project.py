"""Check key files, Python syntax, and relative Markdown links."""

import ast
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    "README.md", "CONTRIBUTING.md", ".gitignore", "requirements.txt",
    "docs/project-brief.md", "docs/requirements.md", "docs/architecture.md",
    "docs/calculations.md", "docs/decision-log.md", "docs/development-log.md",
    "docs/portfolio.md", "docs/safety.md", "docs/flight-test-plan.md",
    "hardware/bom.md", "firmware/README.md", "simulation/README.md",
    "software/README.md", "data/example_design.json", "data/example_mass_budget.csv",
    "analysis/calculations.py", "analysis/run_analysis.py",
    "tests/test_calculations.py", "tests/test_analysis.py",
    "reports/example/summary.md", "reports/example/power_sensitivity.png",
]


def main():
    errors = []
    for name in REQUIRED_FILES:
        if not (ROOT / name).is_file():
            errors.append(f"Missing required file: {name}")
    for path in ROOT.rglob("*.py"):
        if ".venv" in path.parts or "work" in path.relative_to(ROOT).parts:
            continue
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, UnicodeError) as error:
            errors.append(str(error))
    for path in ROOT.rglob("*.md"):
        if ".venv" in path.parts or "work" in path.relative_to(ROOT).parts:
            continue
        content = path.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^\s)]+)\)", content):
            if re.match(r"^[a-zA-Z]+:", target) or target.startswith("#"):
                continue
            target_path = target.split("#", 1)[0]
            if target_path and not (path.parent / target_path).exists():
                errors.append(f"Broken link in {path.relative_to(ROOT)}: {target}")
    if errors:
        for error in errors:
            print(error)
        return 1
    print("Required files, Python syntax, and relative documentation links checked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
