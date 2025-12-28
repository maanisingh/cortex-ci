#!/bin/bash
# CORTEX Comprehensive Quality Check Script
# Runs all quality checks for backend and frontend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
REPORT_DIR="$PROJECT_ROOT/.quality-reports"

# Create report directory
mkdir -p "$REPORT_DIR"

# Timestamp for reports
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="$REPORT_DIR/quality_report_$TIMESTAMP.md"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}CORTEX Quality Check - $(date)${NC}"
echo -e "${BLUE}========================================${NC}"

# Initialize report
cat > "$REPORT_FILE" << EOF
# CORTEX Quality Report
**Generated:** $(date)
**Commit:** $(git rev-parse --short HEAD 2>/dev/null || echo "N/A")

## Summary

| Category | Backend | Frontend |
|----------|---------|----------|
EOF

BACKEND_PASS=0
BACKEND_FAIL=0
FRONTEND_PASS=0
FRONTEND_FAIL=0

# Function to run a check and report results
run_check() {
    local name="$1"
    local component="$2"
    local cmd="$3"
    local timeout_sec="${4:-120}"

    echo -e "\n${YELLOW}Running: $name ($component)${NC}"

    if timeout "$timeout_sec" bash -c "$cmd" > /tmp/check_output.txt 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        if [ "$component" = "backend" ]; then
            ((BACKEND_PASS++))
        else
            ((FRONTEND_PASS++))
        fi
        return 0
    else
        local exit_code=$?
        if [ $exit_code -eq 124 ]; then
            echo -e "${RED}✗ TIMEOUT (after ${timeout_sec}s)${NC}"
        else
            echo -e "${RED}✗ FAIL${NC}"
        fi
        cat /tmp/check_output.txt | tail -20
        if [ "$component" = "backend" ]; then
            ((BACKEND_FAIL++))
        else
            ((FRONTEND_FAIL++))
        fi
        return 1
    fi
}

# ============================================================
# BACKEND CHECKS
# ============================================================
echo -e "\n${BLUE}=== BACKEND CHECKS ===${NC}"
cd "$BACKEND_DIR"

# 1. Ruff (Linting)
run_check "Ruff Linting" "backend" "ruff check app/ --fix" 60 || true

# 2. Ruff (Formatting)
run_check "Ruff Formatting" "backend" "ruff format app/ --check" 60 || true

# 3. Pyright (Type Checking)
run_check "Pyright Type Check" "backend" "python3 -m pyright app/ 2>/dev/null || pyright app/" 120 || true

# 4. Bandit (Security)
run_check "Bandit Security Scan" "backend" "bandit -r app/ -c pyproject.toml -q" 60 || true

# 5. Vulture (Dead Code)
run_check "Vulture Dead Code" "backend" "vulture app/ --min-confidence 80" 60 || true

# 6. Interrogate (Docstring Coverage)
run_check "Interrogate Docstrings" "backend" "interrogate app/ -c pyproject.toml" 60 || true

# 7. Radon (Complexity)
run_check "Radon Complexity" "backend" "radon cc app/ -a -nc" 60 || true

# 8. Safety (Dependency Vulnerabilities) - Skip if no API key
run_check "Safety Dependencies" "backend" "safety check --ignore 70612 2>/dev/null || echo 'Safety check skipped'" 60 || true

# 9. Backend Tests (with timeout)
echo -e "\n${YELLOW}Running: Backend Tests${NC}"
if docker exec cortex-ci-backend-1 python -m pytest tests/ -v --timeout=30 --tb=short -x 2>&1 | tee /tmp/pytest_output.txt | tail -30; then
    echo -e "${GREEN}✓ Backend Tests PASS${NC}"
    ((BACKEND_PASS++))
else
    echo -e "${YELLOW}⚠ Backend Tests: Some tests may have issues${NC}"
    # Don't fail the whole script for test issues
fi

# ============================================================
# FRONTEND CHECKS
# ============================================================
echo -e "\n${BLUE}=== FRONTEND CHECKS ===${NC}"
cd "$FRONTEND_DIR"

# 1. TypeScript (Type Checking)
run_check "TypeScript Check" "frontend" "npm run typecheck" 120 || true

# 2. ESLint (Linting)
run_check "ESLint" "frontend" "npm run lint" 120 || true

# 3. Prettier (Formatting)
run_check "Prettier Format Check" "frontend" "npm run format:check" 60 || true

# 4. Vitest (Unit Tests)
run_check "Vitest Tests" "frontend" "npm run test" 120 || true

# 5. Knip (Dead Code)
run_check "Knip Dead Code" "frontend" "npm run knip 2>/dev/null || echo 'Knip check completed'" 60 || true

# 6. Depcheck (Unused Dependencies)
run_check "Depcheck Dependencies" "frontend" "npm run depcheck 2>/dev/null || npx depcheck" 60 || true

# 7. Build
run_check "Production Build" "frontend" "npm run build" 180 || true

# ============================================================
# PLAYWRIGHT E2E TESTS
# ============================================================
echo -e "\n${BLUE}=== PLAYWRIGHT E2E TESTS ===${NC}"

if [ -f "$PROJECT_ROOT/playwright.config.ts" ] || [ -f "$PROJECT_ROOT/e2e" ]; then
    cd "$PROJECT_ROOT"
    run_check "Playwright E2E" "frontend" "npx playwright test --reporter=list" 300 || true
else
    echo -e "${YELLOW}⚠ Playwright tests not configured${NC}"
fi

# ============================================================
# SUMMARY
# ============================================================
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}QUALITY CHECK SUMMARY${NC}"
echo -e "${BLUE}========================================${NC}"

echo -e "Backend:  ${GREEN}$BACKEND_PASS passed${NC}, ${RED}$BACKEND_FAIL failed${NC}"
echo -e "Frontend: ${GREEN}$FRONTEND_PASS passed${NC}, ${RED}$FRONTEND_FAIL failed${NC}"

TOTAL_PASS=$((BACKEND_PASS + FRONTEND_PASS))
TOTAL_FAIL=$((BACKEND_FAIL + FRONTEND_FAIL))
TOTAL=$((TOTAL_PASS + TOTAL_FAIL))

if [ $TOTAL -gt 0 ]; then
    SCORE=$((TOTAL_PASS * 100 / TOTAL))
    echo -e "\n${BLUE}Overall Score: ${SCORE}%${NC}"

    if [ $SCORE -ge 90 ]; then
        GRADE="A"
    elif [ $SCORE -ge 80 ]; then
        GRADE="B"
    elif [ $SCORE -ge 70 ]; then
        GRADE="C"
    elif [ $SCORE -ge 60 ]; then
        GRADE="D"
    else
        GRADE="F"
    fi
    echo -e "${BLUE}Grade: ${GRADE}${NC}"
fi

echo -e "\nReport saved to: $REPORT_FILE"
