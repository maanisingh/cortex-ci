#!/bin/bash
# ============================================
# CORTEX-CI Pre-Deployment Quality Check
# ============================================
# Run this script before any deployment to ensure
# the platform is production-ready.
#
# Usage:
#   ./scripts/pre-deploy-check.sh [--fix] [--strict]
#
# Options:
#   --fix     Auto-fix issues where possible
#   --strict  Fail on any warning (not just errors)
# ============================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Parse arguments
FIX_MODE=false
STRICT_MODE=false
for arg in "$@"; do
    case $arg in
        --fix) FIX_MODE=true ;;
        --strict) STRICT_MODE=true ;;
    esac
done

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}   CORTEX-CI PRE-DEPLOYMENT CHECK${NC}"
echo -e "${CYAN}============================================${NC}"
echo -e "Project: $PROJECT_DIR"
echo -e "Time: $(date)"
echo -e "Fix mode: $FIX_MODE"
echo -e "Strict mode: $STRICT_MODE"
echo ""

# Track failures
FAILURES=0
WARNINGS=0

# Helper functions
pass() {
    echo -e "  ${GREEN}✓${NC} $1"
}

fail() {
    echo -e "  ${RED}✗${NC} $1"
    ((FAILURES++))
}

warn() {
    echo -e "  ${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
    if $STRICT_MODE; then
        ((FAILURES++))
    fi
}

section() {
    echo -e "\n${YELLOW}═══════════════════════════════════════════${NC}"
    echo -e "${YELLOW}  $1${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════${NC}"
}

# ============================================
# PYTHON BACKEND CHECKS
# ============================================
section "PYTHON BACKEND"

cd "$PROJECT_DIR/backend"

# 1. Ruff Lint
echo -e "\n${GREEN}[1/8] Ruff Lint${NC}"
if $FIX_MODE; then
    ruff check . --fix --quiet 2>/dev/null || true
fi
if ruff check . --quiet 2>/dev/null; then
    pass "No lint errors"
else
    fail "Lint errors found - run: ruff check . --fix"
fi

# 2. Ruff Format
echo -e "\n${GREEN}[2/8] Ruff Format${NC}"
if $FIX_MODE; then
    ruff format . --quiet 2>/dev/null || true
fi
if ruff format . --check --quiet 2>/dev/null; then
    pass "Code properly formatted"
else
    warn "Formatting issues - run: ruff format ."
fi

# 3. Python Syntax
echo -e "\n${GREEN}[3/8] Python Syntax${NC}"
if python3 -m compileall . -q 2>/dev/null; then
    pass "All Python files have valid syntax"
else
    fail "Syntax errors found"
fi

# 4. MyPy Type Check
echo -e "\n${GREEN}[4/8] MyPy Type Check${NC}"
if command -v mypy &>/dev/null; then
    MYPY_OUT=$(mypy app --ignore-missing-imports --no-error-summary 2>/dev/null | grep -c "error:" || echo "0")
    if [[ "$MYPY_OUT" == "0" ]]; then
        pass "No type errors"
    else
        warn "$MYPY_OUT type errors found"
    fi
else
    warn "mypy not installed"
fi

# 5. Security Scan
echo -e "\n${GREEN}[5/8] Bandit Security Scan${NC}"
if command -v bandit &>/dev/null; then
    BANDIT_OUT=$(bandit -r app -ll -q 2>/dev/null | grep -c "Issue:" || echo "0")
    if [[ "$BANDIT_OUT" == "0" ]]; then
        pass "No security issues"
    else
        fail "$BANDIT_OUT security issues found - run: bandit -r app -ll"
    fi
else
    warn "bandit not installed"
fi

# 6. Dead Code
echo -e "\n${GREEN}[6/8] Vulture Dead Code${NC}"
if command -v vulture &>/dev/null; then
    DEAD=$(vulture app --min-confidence 80 2>/dev/null | wc -l)
    if [[ "$DEAD" -lt 5 ]]; then
        pass "Minimal dead code detected"
    else
        warn "$DEAD potential dead code items"
    fi
else
    warn "vulture not installed"
fi

# 7. Requirements Check
echo -e "\n${GREEN}[7/8] Dependencies${NC}"
if [[ -f "requirements.txt" ]]; then
    if command -v safety &>/dev/null; then
        VULNS=$(safety check -r requirements.txt --json 2>/dev/null | jq 'length' 2>/dev/null || echo "0")
        if [[ "$VULNS" == "0" ]]; then
            pass "No known vulnerabilities"
        else
            warn "$VULNS vulnerable dependencies"
        fi
    else
        warn "safety not installed"
    fi
else
    warn "No requirements.txt found"
fi

# 8. Tests
echo -e "\n${GREEN}[8/8] Python Tests${NC}"
if [[ -d "tests" ]] || find . -name "test_*.py" 2>/dev/null | grep -q .; then
    if command -v pytest &>/dev/null; then
        if pytest -q --tb=no 2>/dev/null; then
            pass "All tests pass"
        else
            fail "Test failures - run: pytest -v"
        fi
    else
        warn "pytest not installed"
    fi
else
    warn "No tests found"
fi

# ============================================
# FRONTEND CHECKS
# ============================================
section "FRONTEND"

cd "$PROJECT_DIR/frontend"

# 1. NPM Install Check
echo -e "\n${GREEN}[1/6] Dependencies${NC}"
if [[ -f "package-lock.json" ]]; then
    if npm ci --dry-run &>/dev/null; then
        pass "Dependencies are locked"
    else
        warn "package-lock.json out of sync"
    fi
else
    warn "No package-lock.json"
fi

# 2. TypeScript
echo -e "\n${GREEN}[2/6] TypeScript${NC}"
if npx tsc --noEmit 2>/dev/null; then
    pass "No type errors"
else
    fail "TypeScript errors - run: npx tsc --noEmit"
fi

# 3. ESLint
echo -e "\n${GREEN}[3/6] ESLint${NC}"
ESLINT_ERRORS=$(npx eslint src --ext .ts,.tsx -f json 2>/dev/null | jq '[.[] | .errorCount] | add // 0' || echo "0")
if [[ "$ESLINT_ERRORS" == "0" ]]; then
    pass "No ESLint errors"
else
    fail "$ESLINT_ERRORS ESLint errors - run: npx eslint src --ext .ts,.tsx"
fi

# 4. Prettier
echo -e "\n${GREEN}[4/6] Prettier${NC}"
if $FIX_MODE; then
    npx prettier --write "src/**/*.{ts,tsx}" --quiet 2>/dev/null || true
fi
if npx prettier --check "src/**/*.{ts,tsx}" --quiet 2>/dev/null; then
    pass "Code properly formatted"
else
    warn "Formatting issues - run: npx prettier --write src/"
fi

# 5. Build
echo -e "\n${GREEN}[5/6] Build${NC}"
if npm run build --silent 2>/dev/null; then
    pass "Build succeeds"
else
    fail "Build failed - run: npm run build"
fi

# 6. Tests
echo -e "\n${GREEN}[6/6] Frontend Tests${NC}"
if grep -q '"test"' package.json 2>/dev/null; then
    if npm test -- --passWithNoTests --watchAll=false 2>/dev/null; then
        pass "All tests pass"
    else
        fail "Test failures - run: npm test"
    fi
else
    warn "No test script configured"
fi

# ============================================
# INTEGRATION CHECKS
# ============================================
section "INTEGRATION"

cd "$PROJECT_DIR"

# 1. Docker Build (if Dockerfile exists)
echo -e "\n${GREEN}[1/3] Docker${NC}"
if [[ -f "Dockerfile" ]] || [[ -f "docker-compose.yml" ]]; then
    if command -v docker &>/dev/null; then
        pass "Docker available"
    else
        warn "Docker not available"
    fi
else
    pass "No Docker config (skipped)"
fi

# 2. Environment Files
echo -e "\n${GREEN}[2/3] Environment${NC}"
if [[ -f ".env.example" ]] || [[ -f "backend/.env.example" ]]; then
    pass "Environment template exists"
else
    warn "No .env.example found"
fi

# 3. Database Migrations
echo -e "\n${GREEN}[3/3] Migrations${NC}"
if [[ -d "backend/alembic/versions" ]]; then
    MIGRATION_COUNT=$(ls -1 backend/alembic/versions/*.py 2>/dev/null | wc -l)
    if [[ "$MIGRATION_COUNT" -gt 0 ]]; then
        pass "$MIGRATION_COUNT migrations found"
    else
        warn "No migrations found"
    fi
else
    warn "No alembic directory"
fi

# ============================================
# SUMMARY
# ============================================
section "SUMMARY"

echo ""
if [[ $FAILURES -eq 0 ]] && [[ $WARNINGS -eq 0 ]]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED - Ready for deployment!${NC}"
    exit 0
elif [[ $FAILURES -eq 0 ]]; then
    echo -e "${YELLOW}⚠️  $WARNINGS warnings (no failures)${NC}"
    echo -e "${YELLOW}   Consider fixing warnings before deployment${NC}"
    exit 0
else
    echo -e "${RED}❌ $FAILURES failures, $WARNINGS warnings${NC}"
    echo -e "${RED}   Fix failures before deployment!${NC}"
    exit 1
fi
