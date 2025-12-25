#!/bin/bash
# ============================================
# PHASE 2.1 Implementation Checklist
# ============================================
# Run this to verify Phase 2.1 is complete
# ============================================

set +e  # Don't exit on errors

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}   PHASE 2.1 IMPLEMENTATION CHECKLIST${NC}"
echo -e "${CYAN}   Multi-Layer Dependency Modeling${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""

COMPLETE=0
INCOMPLETE=0

check() {
    local desc="$1"
    local condition="$2"

    if eval "$condition" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} $desc"
        COMPLETE=$((COMPLETE + 1))
    else
        echo -e "  ${RED}✗${NC} $desc"
        INCOMPLETE=$((INCOMPLETE + 1))
    fi
}

# ============================================
# BACKEND CHECKS
# ============================================
echo -e "\n${YELLOW}Backend Implementation${NC}"
echo -e "─────────────────────────────────────────"

check "DependencyLayer enum exists" \
    "grep -q 'class DependencyLayer' $PROJECT_DIR/backend/app/models/dependency.py 2>/dev/null"

check "Layer summary endpoint exists" \
    "grep -q '/layers/summary' $PROJECT_DIR/backend/app/api/v1/endpoints/dependencies.py 2>/dev/null"

check "Cross-layer impact endpoint exists" \
    "grep -q '/cross-layer-impact/' $PROJECT_DIR/backend/app/api/v1/endpoints/dependencies.py 2>/dev/null"

check "Layer risk weights defined" \
    "grep -q '_get_layer_risk_weight' $PROJECT_DIR/backend/app/api/v1/endpoints/dependencies.py 2>/dev/null"

check "Risk recommendation function exists" \
    "grep -q '_get_risk_recommendation' $PROJECT_DIR/backend/app/api/v1/endpoints/dependencies.py 2>/dev/null"

# ============================================
# FRONTEND CHECKS
# ============================================
echo -e "\n${YELLOW}Frontend Implementation${NC}"
echo -e "─────────────────────────────────────────"

check "dependencyLayersApi defined" \
    "grep -q 'dependencyLayersApi' $PROJECT_DIR/frontend/src/services/api.ts 2>/dev/null"

check "Layer summary API method" \
    "grep -q 'layers/summary' $PROJECT_DIR/frontend/src/services/api.ts 2>/dev/null"

check "Cross-layer impact API method" \
    "grep -q 'cross-layer-impact' $PROJECT_DIR/frontend/src/services/api.ts 2>/dev/null"

# These are TODO - will fail until implemented
check "DependencyLayers page exists" \
    "[[ -f '$PROJECT_DIR/frontend/src/pages/DependencyLayers.tsx' ]]"

check "CrossLayerAnalysis page exists" \
    "[[ -f '$PROJECT_DIR/frontend/src/pages/CrossLayerAnalysis.tsx' ]]"

check "Layer colors defined" \
    "grep -rq 'LAYER_COLORS\|layerColors' $PROJECT_DIR/frontend/src 2>/dev/null"

# ============================================
# INTEGRATION CHECKS
# ============================================
echo -e "\n${YELLOW}Integration${NC}"
echo -e "─────────────────────────────────────────"

check "API route registered" \
    "grep -q 'dependencies' $PROJECT_DIR/backend/app/api/v1/router.py 2>/dev/null"

check "Frontend route for layers" \
    "grep -q 'layer\|Layer' $PROJECT_DIR/frontend/src/App.tsx 2>/dev/null"

# ============================================
# TESTING CHECKS
# ============================================
echo -e "\n${YELLOW}Testing${NC}"
echo -e "─────────────────────────────────────────"

check "Backend dependency tests exist" \
    "[[ -f '$PROJECT_DIR/backend/tests/test_dependencies.py' ]]"

check "Frontend layer component tests" \
    "find $PROJECT_DIR/frontend -name '*.test.ts*' -exec grep -l 'layer\|Layer' {} \; 2>/dev/null | grep -q ."

# ============================================
# SUMMARY
# ============================================
echo -e "\n${CYAN}============================================${NC}"
echo -e "${CYAN}   SUMMARY${NC}"
echo -e "${CYAN}============================================${NC}"

TOTAL=$((COMPLETE + INCOMPLETE))
PERCENT=$((COMPLETE * 100 / TOTAL))

echo ""
echo -e "  Complete:   ${GREEN}$COMPLETE${NC} / $TOTAL"
echo -e "  Incomplete: ${RED}$INCOMPLETE${NC} / $TOTAL"
echo -e "  Progress:   ${YELLOW}$PERCENT%${NC}"
echo ""

if [[ $INCOMPLETE -eq 0 ]]; then
    echo -e "${GREEN}✅ Phase 2.1 is COMPLETE!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Phase 2.1 has $INCOMPLETE remaining tasks${NC}"
    echo ""
    echo -e "Next steps:"
    echo -e "  1. Create frontend pages for layer visualization"
    echo -e "  2. Add layer-colored dependency graph"
    echo -e "  3. Write tests for new components"
    echo -e "  4. Run: ./scripts/pre-deploy-check.sh"
    exit 1
fi
