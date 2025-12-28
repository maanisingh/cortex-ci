#!/bin/bash
# Comprehensive Quality Check Script for CORTEX
# Runs all quality tools on both backend and frontend

set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
REPORT_DIR="$PROJECT_ROOT/.quality-reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$REPORT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

log_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

log_check() {
    local name=$1
    local status=$2
    if [ "$status" -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC} - $name"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC} - $name"
        ((FAILED++))
    fi
}

log_warning() {
    echo -e "${YELLOW}⚠️  WARNING${NC} - $1"
    ((WARNINGS++))
}

# Initialize report
REPORT_FILE="$REPORT_DIR/quality_report_$TIMESTAMP.md"
echo "# CORTEX Quality Report" > "$REPORT_FILE"
echo "**Generated:** $(date)" >> "$REPORT_FILE"
echo "**Commit:** $(git rev-parse --short HEAD 2>/dev/null || echo 'N/A')" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

##############################################
# BACKEND CHECKS
##############################################
log_header "BACKEND QUALITY CHECKS"
echo "## Backend" >> "$REPORT_FILE"

cd "$PROJECT_ROOT/backend"

# Check if venv exists, if not create it
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate venv and install deps
source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate 2>/dev/null || true
pip install -q -r requirements-dev.txt 2>/dev/null || pip install -q -r requirements.txt

# 1. Ruff Linting
echo "### Ruff (Linting)" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
if ruff check app --output-format=text >> "$REPORT_FILE" 2>&1; then
    log_check "Ruff Linting" 0
    echo '```' >> "$REPORT_FILE"
    echo "**Status: PASSED**" >> "$REPORT_FILE"
else
    log_check "Ruff Linting" 1
    echo '```' >> "$REPORT_FILE"
    echo "**Status: ISSUES FOUND**" >> "$REPORT_FILE"
fi
echo "" >> "$REPORT_FILE"

# 2. Ruff Formatting
echo "### Ruff (Formatting)" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
if ruff format --check app >> "$REPORT_FILE" 2>&1; then
    log_check "Ruff Formatting" 0
    echo '```' >> "$REPORT_FILE"
    echo "**Status: PASSED**" >> "$REPORT_FILE"
else
    log_check "Ruff Formatting" 1
    echo '```' >> "$REPORT_FILE"
    echo "**Status: NEEDS FORMATTING**" >> "$REPORT_FILE"
fi
echo "" >> "$REPORT_FILE"

# 3. Pyright Type Checking
echo "### Pyright (Type Checking)" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
if pyright app >> "$REPORT_FILE" 2>&1; then
    log_check "Pyright Type Checking" 0
    echo '```' >> "$REPORT_FILE"
    echo "**Status: PASSED**" >> "$REPORT_FILE"
else
    log_check "Pyright Type Checking" 1
    echo '```' >> "$REPORT_FILE"
    echo "**Status: TYPE ERRORS**" >> "$REPORT_FILE"
fi
echo "" >> "$REPORT_FILE"

# 4. Bandit Security
echo "### Bandit (Security)" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
if bandit -r app -c pyproject.toml -f txt >> "$REPORT_FILE" 2>&1; then
    log_check "Bandit Security" 0
    echo '```' >> "$REPORT_FILE"
    echo "**Status: PASSED**" >> "$REPORT_FILE"
else
    log_check "Bandit Security" 1
    echo '```' >> "$REPORT_FILE"
    echo "**Status: SECURITY ISSUES**" >> "$REPORT_FILE"
fi
echo "" >> "$REPORT_FILE"

# 5. Vulture Dead Code
echo "### Vulture (Dead Code)" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
VULTURE_OUTPUT=$(vulture app --min-confidence 80 2>&1)
if [ -z "$VULTURE_OUTPUT" ]; then
    log_check "Vulture Dead Code" 0
    echo "No dead code found" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    echo "**Status: PASSED**" >> "$REPORT_FILE"
else
    log_warning "Vulture found potential dead code"
    echo "$VULTURE_OUTPUT" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    echo "**Status: DEAD CODE DETECTED**" >> "$REPORT_FILE"
fi
echo "" >> "$REPORT_FILE"

# 6. Pytest with Coverage
echo "### Pytest (Tests + Coverage)" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
if pytest tests/ --cov=app --cov-report=term-missing -v --tb=short >> "$REPORT_FILE" 2>&1; then
    log_check "Pytest Tests" 0
    echo '```' >> "$REPORT_FILE"
    echo "**Status: PASSED**" >> "$REPORT_FILE"
else
    log_check "Pytest Tests" 1
    echo '```' >> "$REPORT_FILE"
    echo "**Status: TESTS FAILED**" >> "$REPORT_FILE"
fi
echo "" >> "$REPORT_FILE"

# 7. Interrogate Docstrings
echo "### Interrogate (Docstrings)" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
interrogate -v app >> "$REPORT_FILE" 2>&1 || true
log_warning "Docstring coverage check complete"
echo '```' >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 8. Radon Complexity
echo "### Radon (Complexity)" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
radon cc app -a -s >> "$REPORT_FILE" 2>&1 || true
echo '```' >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 9. Safety Dependencies
echo "### Safety (Dependency Vulnerabilities)" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
safety check -r requirements.txt --output text >> "$REPORT_FILE" 2>&1 || log_warning "Safety check found vulnerabilities"
echo '```' >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

##############################################
# FRONTEND CHECKS
##############################################
log_header "FRONTEND QUALITY CHECKS"
echo "## Frontend" >> "$REPORT_FILE"

cd "$PROJECT_ROOT/frontend"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# 1. TypeScript
echo "### TypeScript (Type Checking)" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
if npx tsc --noEmit >> "$REPORT_FILE" 2>&1; then
    log_check "TypeScript" 0
    echo '```' >> "$REPORT_FILE"
    echo "**Status: PASSED**" >> "$REPORT_FILE"
else
    log_check "TypeScript" 1
    echo '```' >> "$REPORT_FILE"
    echo "**Status: TYPE ERRORS**" >> "$REPORT_FILE"
fi
echo "" >> "$REPORT_FILE"

# 2. ESLint
echo "### ESLint (Linting)" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
if npx eslint . --ext ts,tsx --max-warnings 0 >> "$REPORT_FILE" 2>&1; then
    log_check "ESLint" 0
    echo '```' >> "$REPORT_FILE"
    echo "**Status: PASSED**" >> "$REPORT_FILE"
else
    log_check "ESLint" 1
    echo '```' >> "$REPORT_FILE"
    echo "**Status: LINT ERRORS**" >> "$REPORT_FILE"
fi
echo "" >> "$REPORT_FILE"

# 3. Prettier
echo "### Prettier (Formatting)" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
if npx prettier --check "src/**/*.{ts,tsx,css,json}" >> "$REPORT_FILE" 2>&1; then
    log_check "Prettier Formatting" 0
    echo '```' >> "$REPORT_FILE"
    echo "**Status: PASSED**" >> "$REPORT_FILE"
else
    log_check "Prettier Formatting" 1
    echo '```' >> "$REPORT_FILE"
    echo "**Status: NEEDS FORMATTING**" >> "$REPORT_FILE"
fi
echo "" >> "$REPORT_FILE"

# 4. Vitest
echo "### Vitest (Tests)" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
if npx vitest run --coverage >> "$REPORT_FILE" 2>&1; then
    log_check "Vitest Tests" 0
    echo '```' >> "$REPORT_FILE"
    echo "**Status: PASSED**" >> "$REPORT_FILE"
else
    log_check "Vitest Tests" 1
    echo '```' >> "$REPORT_FILE"
    echo "**Status: TESTS FAILED**" >> "$REPORT_FILE"
fi
echo "" >> "$REPORT_FILE"

# 5. Knip
echo "### Knip (Dead Code/Exports)" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
if npx knip >> "$REPORT_FILE" 2>&1; then
    log_check "Knip Dead Code" 0
    echo '```' >> "$REPORT_FILE"
    echo "**Status: PASSED**" >> "$REPORT_FILE"
else
    log_warning "Knip found unused code/exports"
    echo '```' >> "$REPORT_FILE"
    echo "**Status: UNUSED CODE FOUND**" >> "$REPORT_FILE"
fi
echo "" >> "$REPORT_FILE"

# 6. Depcheck
echo "### Depcheck (Unused Dependencies)" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
npx depcheck >> "$REPORT_FILE" 2>&1 || log_warning "Depcheck found unused dependencies"
echo '```' >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 7. Build Check
echo "### Build Check" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
if npm run build >> "$REPORT_FILE" 2>&1; then
    log_check "Build" 0
    echo '```' >> "$REPORT_FILE"
    echo "**Status: PASSED**" >> "$REPORT_FILE"
else
    log_check "Build" 1
    echo '```' >> "$REPORT_FILE"
    echo "**Status: BUILD FAILED**" >> "$REPORT_FILE"
fi
echo "" >> "$REPORT_FILE"

##############################################
# SUMMARY
##############################################
log_header "QUALITY CHECK SUMMARY"

echo "## Summary" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "| Metric | Count |" >> "$REPORT_FILE"
echo "|--------|-------|" >> "$REPORT_FILE"
echo "| Passed | $PASSED |" >> "$REPORT_FILE"
echo "| Failed | $FAILED |" >> "$REPORT_FILE"
echo "| Warnings | $WARNINGS |" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

TOTAL=$((PASSED + FAILED))
if [ $TOTAL -gt 0 ]; then
    SCORE=$((PASSED * 100 / TOTAL))
    echo "**Quality Score: ${SCORE}%**" >> "$REPORT_FILE"
    echo -e "\n${BLUE}Quality Score: ${SCORE}%${NC}"
fi

echo ""
echo -e "${GREEN}Passed:${NC} $PASSED"
echo -e "${RED}Failed:${NC} $FAILED"
echo -e "${YELLOW}Warnings:${NC} $WARNINGS"
echo ""
echo -e "Report saved to: ${BLUE}$REPORT_FILE${NC}"

# Exit with error if any checks failed
if [ $FAILED -gt 0 ]; then
    exit 1
fi
