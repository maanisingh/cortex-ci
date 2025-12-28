#!/bin/bash
# Backend Quality Check Script
# Runs all quality tools and generates a comprehensive report

set -e

REPORT_DIR="../.quality-reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="$REPORT_DIR/backend_quality_report_$TIMESTAMP.md"

mkdir -p "$REPORT_DIR"

echo "# Backend Quality Report" > "$REPORT_FILE"
echo "Generated: $(date)" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Function to run check and capture output
run_check() {
    local name=$1
    local cmd=$2
    echo "Running $name..."
    echo "## $name" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    if eval "$cmd" >> "$REPORT_FILE" 2>&1; then
        echo "✅ $name passed"
        echo '```' >> "$REPORT_FILE"
        echo "**Status: PASSED**" >> "$REPORT_FILE"
    else
        echo "❌ $name found issues"
        echo '```' >> "$REPORT_FILE"
        echo "**Status: ISSUES FOUND**" >> "$REPORT_FILE"
    fi
    echo "" >> "$REPORT_FILE"
}

cd "$(dirname "$0")/.."

echo "=== Backend Quality Check ==="
echo ""

# 1. Vulture (Dead Code)
run_check "Vulture (Dead Code)" "vulture app --min-confidence 80"

# 2. Ruff (Linting)
run_check "Ruff (Linting)" "ruff check app"

# 3. Ruff (Formatting)
run_check "Ruff (Formatting)" "ruff format --check app"

# 4. Pyright (Type Checking)
run_check "Pyright (Type Checking)" "pyright app"

# 5. Bandit (Security)
run_check "Bandit (Security)" "bandit -r app -c pyproject.toml -f txt"

# 6. Interrogate (Docstrings)
run_check "Interrogate (Docstrings)" "interrogate -v app"

# 7. Radon (Complexity)
echo "## Radon (Code Complexity)" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
echo "Running Radon..."
radon cc app -a -s >> "$REPORT_FILE" 2>&1 || true
echo '```' >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 8. Pytest with Coverage
echo "## Pytest (Tests + Coverage)" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
echo "Running Tests..."
if pytest --cov=app --cov-report=term-missing -v >> "$REPORT_FILE" 2>&1; then
    echo "✅ Tests passed"
    echo '```' >> "$REPORT_FILE"
    echo "**Status: PASSED**" >> "$REPORT_FILE"
else
    echo "❌ Tests failed"
    echo '```' >> "$REPORT_FILE"
    echo "**Status: FAILED**" >> "$REPORT_FILE"
fi
echo "" >> "$REPORT_FILE"

# 9. Safety (Dependency Vulnerabilities)
run_check "Safety (Dependencies)" "safety check -r requirements.txt --output text || true"

echo ""
echo "=== Quality Report Generated ==="
echo "Report: $REPORT_FILE"
echo ""

# Summary
echo "## Summary" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "| Check | Tool | Status |" >> "$REPORT_FILE"
echo "|-------|------|--------|" >> "$REPORT_FILE"

cat "$REPORT_FILE"
