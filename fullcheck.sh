#!/bin/bash
# Advanced Full Stack Quality Check with Context Analysis
# Usage: fullcheck [project_path]
# If no path provided, uses current directory

set -o pipefail

# Project directory - use argument or current directory
PROJECT_DIR="${1:-.}"
cd "$PROJECT_DIR" || { echo "Cannot access $PROJECT_DIR"; exit 1; }
PROJECT_DIR=$(pwd)

# Output directory for reports
REPORT_DIR="$PROJECT_DIR/.quality-reports"
mkdir -p "$REPORT_DIR"

# Report file
REPORT_FILE="$REPORT_DIR/analysis-$(date +%Y%m%d-%H%M%S).md"
JSON_REPORT="$REPORT_DIR/analysis-$(date +%Y%m%d-%H%M%S).json"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Initialize JSON report
echo '{"project": "'"$PROJECT_DIR"'", "timestamp": "'"$(date -Iseconds)"'", "issues": []}' > "$JSON_REPORT"

# Helper to add issue to JSON
add_issue() {
    local tool="$1"
    local type="$2"
    local file="$3"
    local line="$4"
    local message="$5"
    local context="$6"
    local suggestion="$7"

    # Escape quotes for JSON
    message=$(echo "$message" | sed 's/"/\\"/g' | tr '\n' ' ')
    context=$(echo "$context" | sed 's/"/\\"/g' | tr '\n' ' ')
    suggestion=$(echo "$suggestion" | sed 's/"/\\"/g' | tr '\n' ' ')

    local tmp=$(mktemp)
    jq --arg tool "$tool" \
       --arg type "$type" \
       --arg file "$file" \
       --arg line "$line" \
       --arg msg "$message" \
       --arg ctx "$context" \
       --arg sug "$suggestion" \
       '.issues += [{"tool": $tool, "type": $type, "file": $file, "line": $line, "message": $msg, "context": $ctx, "suggestion": $sug}]' \
       "$JSON_REPORT" > "$tmp" && mv "$tmp" "$JSON_REPORT"
}

echo "============================================" | tee "$REPORT_FILE"
echo "    ADVANCED FULL STACK QUALITY CHECK" | tee -a "$REPORT_FILE"
echo "============================================" | tee -a "$REPORT_FILE"
echo "Project: $PROJECT_DIR" | tee -a "$REPORT_FILE"
echo "Time: $(date)" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# ============ DETECT PROJECT TYPE ============
echo -e "\n${CYAN}[*] Detecting project structure...${NC}"

HAS_PYTHON=false
HAS_NODE=false
HAS_TYPESCRIPT=false
HAS_REACT=false
FRONTEND_DIR=""

# Check for Python
[[ -f "requirements.txt" || -f "setup.py" || -f "pyproject.toml" || $(find . -maxdepth 3 -name "*.py" 2>/dev/null | head -1) ]] && HAS_PYTHON=true

# Check for Node.js (root or subdirectory)
if [[ -f "package.json" ]]; then
    HAS_NODE=true
elif [[ -f "frontend/package.json" ]]; then
    HAS_NODE=true
    FRONTEND_DIR="frontend"
elif [[ -f "client/package.json" ]]; then
    HAS_NODE=true
    FRONTEND_DIR="client"
fi

# Check for TypeScript
if [[ -f "tsconfig.json" || -f "frontend/tsconfig.json" || -f "client/tsconfig.json" ]]; then
    HAS_TYPESCRIPT=true
fi

# Check for React
if [[ -n "$FRONTEND_DIR" ]]; then
    grep -q "react" "$FRONTEND_DIR/package.json" 2>/dev/null && HAS_REACT=true
elif [[ -f "package.json" ]]; then
    grep -q "react" package.json 2>/dev/null && HAS_REACT=true
fi

echo "  Python: $HAS_PYTHON" | tee -a "$REPORT_FILE"
echo "  Node.js: $HAS_NODE" | tee -a "$REPORT_FILE"
echo "  TypeScript: $HAS_TYPESCRIPT" | tee -a "$REPORT_FILE"
echo "  React: $HAS_REACT" | tee -a "$REPORT_FILE"
[[ -n "$FRONTEND_DIR" ]] && echo "  Frontend dir: $FRONTEND_DIR" | tee -a "$REPORT_FILE"

# ============ PYTHON ANALYSIS ============
if $HAS_PYTHON; then
    echo -e "\n${YELLOW}═══════════════════════════════════════════${NC}"
    echo -e "${YELLOW}              PYTHON ANALYSIS${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════${NC}"
    echo -e "\n## Python Analysis\n" >> "$REPORT_FILE"

    # --- Ruff Lint ---
    echo -e "\n${GREEN}[ruff] Linting...${NC}"
    if command -v ruff &>/dev/null; then
        RUFF_OUTPUT=$(ruff check . --output-format=json 2>/dev/null || echo "[]")
        if [[ "$RUFF_OUTPUT" != "[]" ]]; then
            echo "$RUFF_OUTPUT" | jq -r '.[] | "\(.filename):\(.location.row) - \(.code): \(.message)"' 2>/dev/null | while read -r line; do
                echo "  $line"
                file=$(echo "$line" | cut -d: -f1)
                lineno=$(echo "$line" | cut -d: -f2 | cut -d' ' -f1)
                msg=$(echo "$line" | cut -d: -f3-)
                add_issue "ruff" "lint" "$file" "$lineno" "$msg" "" "Run: ruff check --fix"
            done
            echo -e "\n### Ruff Issues\n\`\`\`" >> "$REPORT_FILE"
            echo "$RUFF_OUTPUT" | jq -r '.[] | "\(.filename):\(.location.row) - \(.code): \(.message)"' >> "$REPORT_FILE" 2>/dev/null
            echo -e "\`\`\`\n" >> "$REPORT_FILE"
        else
            echo -e "  ${GREEN}✓ No lint issues${NC}"
        fi
    fi

    # --- Ruff Format Check ---
    echo -e "\n${GREEN}[ruff] Format check...${NC}"
    if command -v ruff &>/dev/null; then
        FORMAT_OUTPUT=$(ruff format . --check 2>&1 || true)
        if echo "$FORMAT_OUTPUT" | grep -q "would reformat"; then
            echo -e "  ${YELLOW}Formatting issues found:${NC}"
            echo "$FORMAT_OUTPUT" | grep "would reformat" | head -10
            echo -e "\n### Formatting Issues\n\`\`\`" >> "$REPORT_FILE"
            echo "$FORMAT_OUTPUT" >> "$REPORT_FILE"
            echo -e "\`\`\`\n" >> "$REPORT_FILE"
        else
            echo -e "  ${GREEN}✓ Code is properly formatted${NC}"
        fi
    fi

    # --- Python Syntax Check ---
    echo -e "\n${GREEN}[compile] Syntax check...${NC}"
    COMPILE_OUTPUT=$(python3 -m compileall . -q 2>&1 || true)
    if [[ -n "$COMPILE_OUTPUT" ]]; then
        echo -e "  ${RED}Syntax errors found:${NC}"
        echo "$COMPILE_OUTPUT" | head -20
        echo -e "\n### Syntax Errors\n\`\`\`" >> "$REPORT_FILE"
        echo "$COMPILE_OUTPUT" >> "$REPORT_FILE"
        echo -e "\`\`\`\n" >> "$REPORT_FILE"
    else
        echo -e "  ${GREEN}✓ All Python files have valid syntax${NC}"
    fi

    # --- MyPy Type Check ---
    echo -e "\n${GREEN}[mypy] Type checking...${NC}"
    if command -v mypy &>/dev/null; then
        MYPY_OUTPUT=$(mypy . --ignore-missing-imports --show-error-codes 2>/dev/null || true)
        if [[ -n "$MYPY_OUTPUT" && ! "$MYPY_OUTPUT" =~ "Success" ]]; then
            echo "$MYPY_OUTPUT" | head -20
            echo -e "\n### MyPy Type Errors\n\`\`\`" >> "$REPORT_FILE"
            echo "$MYPY_OUTPUT" >> "$REPORT_FILE"
            echo -e "\`\`\`\n" >> "$REPORT_FILE"

            # Parse and add to JSON
            echo "$MYPY_OUTPUT" | grep -E "^[^:]+:[0-9]+:" | while read -r line; do
                file=$(echo "$line" | cut -d: -f1)
                lineno=$(echo "$line" | cut -d: -f2)
                msg=$(echo "$line" | cut -d: -f3-)
                add_issue "mypy" "type_error" "$file" "$lineno" "$msg" "" ""
            done
        else
            echo -e "  ${GREEN}✓ No type errors${NC}"
        fi
    fi

    # --- Dead Code Analysis with Context ---
    echo -e "\n${GREEN}[vulture] Dead code analysis with context...${NC}"
    if command -v vulture &>/dev/null; then
        VULTURE_OUTPUT=$(vulture . --min-confidence 70 2>/dev/null || true)
        if [[ -n "$VULTURE_OUTPUT" ]]; then
            echo -e "\n### Dead Code Analysis\n" >> "$REPORT_FILE"
            echo "$VULTURE_OUTPUT" | while read -r line; do
                if [[ -n "$line" ]]; then
                    file=$(echo "$line" | cut -d: -f1)
                    lineno=$(echo "$line" | cut -d: -f2)
                    msg=$(echo "$line" | cut -d: -f3-)

                    # Extract the symbol name
                    symbol=$(echo "$msg" | grep -oP "unused \w+ '\K[^']+")

                    echo -e "  ${RED}$line${NC}"

                    # Find where this symbol is defined
                    echo -e "    ${BLUE}Definition context:${NC}"
                    if [[ -f "$file" ]]; then
                        sed -n "$((lineno-2)),$((lineno+2))p" "$file" 2>/dev/null | sed 's/^/      /'
                    fi

                    # Search for imports/references to this symbol across the project
                    echo -e "    ${BLUE}References found:${NC}"
                    refs=$(grep -rn --include="*.py" "$symbol" . 2>/dev/null | grep -v "^$file:$lineno:" | head -5)
                    if [[ -n "$refs" ]]; then
                        echo "$refs" | sed 's/^/      /'
                        ref_context="Found references: $refs"
                    else
                        echo -e "      ${YELLOW}No other references found - possibly orphaned${NC}"
                        ref_context="No references found - likely orphaned code"
                    fi

                    # Check if it might be exported via __all__
                    if grep -q "__all__.*$symbol" "$file" 2>/dev/null; then
                        echo -e "    ${CYAN}Note: Listed in __all__ - may be public API${NC}"
                        ref_context="$ref_context. Listed in __all__"
                    fi

                    # Check for dynamic usage patterns
                    if grep -rq "getattr.*['\"]$symbol['\"]" . 2>/dev/null; then
                        echo -e "    ${CYAN}Note: May be accessed dynamically via getattr${NC}"
                        ref_context="$ref_context. Dynamic getattr usage found"
                    fi

                    echo "" >> "$REPORT_FILE"
                    echo "**$file:$lineno** - $msg" >> "$REPORT_FILE"
                    echo "- Context: $ref_context" >> "$REPORT_FILE"

                    add_issue "vulture" "dead_code" "$file" "$lineno" "$msg" "$ref_context" "Verify if intentionally unused or remove"
                fi
            done
        else
            echo -e "  ${GREEN}✓ No dead code detected${NC}"
        fi
    fi

    # --- Import Analysis ---
    echo -e "\n${GREEN}[imports] Analyzing imports and dependencies...${NC}"
    echo -e "\n### Import Analysis\n" >> "$REPORT_FILE"

    # Find broken imports
    BROKEN_IMPORTS=$(python3 -c "
import ast
import os
import sys

broken = []
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ['venv', 'env', '.venv', 'node_modules', '__pycache__', '.git']]
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            try:
                with open(path) as file:
                    tree = ast.parse(file.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            try:
                                __import__(alias.name.split('.')[0])
                            except ImportError as e:
                                broken.append(f'{path}:{node.lineno} - Cannot import {alias.name}: {e}')
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            try:
                                __import__(node.module.split('.')[0])
                            except ImportError as e:
                                broken.append(f'{path}:{node.lineno} - Cannot import from {node.module}: {e}')
            except SyntaxError as e:
                broken.append(f'{path}:{e.lineno} - Syntax error: {e.msg}')
            except Exception:
                pass

for b in broken:
    print(b)
" 2>/dev/null || true)

    if [[ -n "$BROKEN_IMPORTS" ]]; then
        echo -e "  ${RED}Broken imports found:${NC}"
        echo "$BROKEN_IMPORTS" | while read -r line; do
            echo -e "    $line"
            file=$(echo "$line" | cut -d: -f1)
            lineno=$(echo "$line" | cut -d: -f2)
            msg=$(echo "$line" | cut -d: -f3-)

            # Try to find similar modules
            module=$(echo "$msg" | grep -oP "import \K\S+" | head -1)
            if [[ -n "$module" ]]; then
                similar=$(find . -name "*.py" -exec basename {} .py \; 2>/dev/null | grep -i "${module:0:4}" | head -3 | tr '\n' ', ')
                if [[ -n "$similar" ]]; then
                    echo -e "      ${CYAN}Similar modules: $similar${NC}"
                fi
            fi

            add_issue "import_check" "broken_import" "$file" "$lineno" "$msg" "" "Check if module is installed or fix import path"
        done
        echo -e "\n#### Broken Imports\n\`\`\`" >> "$REPORT_FILE"
        echo "$BROKEN_IMPORTS" >> "$REPORT_FILE"
        echo -e "\`\`\`\n" >> "$REPORT_FILE"
    else
        echo -e "  ${GREEN}✓ All imports valid${NC}"
    fi

    # --- Security Scan ---
    echo -e "\n${GREEN}[bandit] Security scan...${NC}"
    if command -v bandit &>/dev/null; then
        BANDIT_OUTPUT=$(bandit -r . -ll -f json 2>/dev/null || echo '{"results":[]}')
        BANDIT_COUNT=$(echo "$BANDIT_OUTPUT" | jq '.results | length' 2>/dev/null || echo "0")
        if [[ "$BANDIT_COUNT" -gt 0 ]]; then
            echo -e "  ${RED}Found $BANDIT_COUNT security issues${NC}"
            echo "$BANDIT_OUTPUT" | jq -r '.results[] | "  \(.filename):\(.line_number) [\(.severity)] \(.issue_text)"' 2>/dev/null

            echo -e "\n### Security Issues\n" >> "$REPORT_FILE"
            echo "$BANDIT_OUTPUT" | jq -r '.results[] | "- **\(.filename):\(.line_number)** [\(.severity)] \(.issue_text)"' >> "$REPORT_FILE" 2>/dev/null
        else
            echo -e "  ${GREEN}✓ No security issues${NC}"
        fi
    fi

    # --- Dependency Vulnerabilities ---
    echo -e "\n${GREEN}[safety] Checking dependency vulnerabilities...${NC}"
    if command -v safety &>/dev/null; then
        if [[ -f "requirements.txt" ]]; then
            SAFETY_OUTPUT=$(safety check -r requirements.txt --json 2>/dev/null || echo '[]')
            SAFETY_COUNT=$(echo "$SAFETY_OUTPUT" | jq 'if type == "array" then length else 0 end' 2>/dev/null || echo "0")
            if [[ "$SAFETY_COUNT" -gt 0 ]]; then
                echo -e "  ${RED}Found $SAFETY_COUNT vulnerable dependencies${NC}"
                echo "$SAFETY_OUTPUT" | jq -r '.[] | "  \(.[0]): \(.[3])"' 2>/dev/null | head -10
                echo -e "\n### Vulnerable Dependencies\n" >> "$REPORT_FILE"
                echo "$SAFETY_OUTPUT" | jq -r '.[] | "- **\(.[0])**: \(.[3])"' >> "$REPORT_FILE" 2>/dev/null
            else
                echo -e "  ${GREEN}✓ No known vulnerabilities${NC}"
            fi
        else
            echo -e "  ${YELLOW}No requirements.txt found${NC}"
        fi
    else
        echo -e "  ${YELLOW}safety not installed${NC}"
    fi

    # --- Pytest ---
    echo -e "\n${GREEN}[pytest] Running tests...${NC}"
    if command -v pytest &>/dev/null && find . -name "test_*.py" -o -name "*_test.py" 2>/dev/null | grep -q .; then
        PYTEST_OUTPUT=$(pytest -v --tb=short 2>&1 || true)
        if echo "$PYTEST_OUTPUT" | grep -q "FAILED\|ERROR"; then
            echo -e "  ${RED}Test failures found${NC}"
            echo "$PYTEST_OUTPUT" | grep -E "FAILED|ERROR|AssertionError" | head -20
            echo -e "\n### Test Failures\n\`\`\`" >> "$REPORT_FILE"
            echo "$PYTEST_OUTPUT" >> "$REPORT_FILE"
            echo -e "\`\`\`\n" >> "$REPORT_FILE"
        else
            echo -e "  ${GREEN}✓ All tests passed${NC}"
        fi
    else
        echo -e "  ${YELLOW}No tests found${NC}"
    fi
fi

# ============ JAVASCRIPT/TYPESCRIPT ANALYSIS ============
if $HAS_NODE; then
    echo -e "\n${YELLOW}═══════════════════════════════════════════${NC}"
    echo -e "${YELLOW}         JAVASCRIPT/TYPESCRIPT ANALYSIS${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════${NC}"
    echo -e "\n## JavaScript/TypeScript Analysis\n" >> "$REPORT_FILE"

    # Change to frontend directory if needed
    JS_DIR="."
    if [[ -n "$FRONTEND_DIR" ]]; then
        JS_DIR="$FRONTEND_DIR"
        echo -e "  ${CYAN}Analyzing: $FRONTEND_DIR${NC}"
    fi

    # --- ESLint ---
    echo -e "\n${GREEN}[eslint] Linting...${NC}"
    if [[ -f "$JS_DIR/package.json" ]]; then
        pushd "$JS_DIR" > /dev/null 2>&1 || true
        ESLINT_OUTPUT=$(npx eslint . --ext .js,.jsx,.ts,.tsx -f json 2>/dev/null || echo "[]")
        ESLINT_ERRORS=$(echo "$ESLINT_OUTPUT" | jq '[.[] | .errorCount] | add // 0' 2>/dev/null || echo "0")
        if [[ "$ESLINT_ERRORS" -gt 0 ]]; then
            echo -e "  ${RED}Found $ESLINT_ERRORS errors${NC}"
            echo "$ESLINT_OUTPUT" | jq -r '.[] | select(.errorCount > 0) | .filePath as $f | .messages[] | select(.severity == 2) | "  \($f):\(.line) - \(.ruleId): \(.message)"' 2>/dev/null | head -20

            echo -e "\n### ESLint Errors\n\`\`\`" >> "$REPORT_FILE"
            echo "$ESLINT_OUTPUT" | jq -r '.[] | select(.errorCount > 0) | .filePath as $f | .messages[] | select(.severity == 2) | "\($f):\(.line) - \(.ruleId): \(.message)"' >> "$REPORT_FILE" 2>/dev/null
            echo -e "\`\`\`\n" >> "$REPORT_FILE"
        else
            echo -e "  ${GREEN}✓ No ESLint errors${NC}"
        fi
    fi

    # --- Prettier Format Check ---
    echo -e "\n${GREEN}[prettier] Format check...${NC}"
    if [[ -f "package.json" ]]; then
        PRETTIER_OUTPUT=$(npx prettier --check "**/*.{js,jsx,ts,tsx,json,css,scss,md}" 2>&1 || true)
        if echo "$PRETTIER_OUTPUT" | grep -q "Checking\|would"; then
            UNFORMATTED=$(echo "$PRETTIER_OUTPUT" | grep -c "\..*$" || echo "0")
            if [[ "$UNFORMATTED" -gt 0 ]]; then
                echo -e "  ${YELLOW}$UNFORMATTED files need formatting${NC}"
                echo "$PRETTIER_OUTPUT" | grep "\." | head -10
            else
                echo -e "  ${GREEN}✓ All files formatted${NC}"
            fi
        else
            echo -e "  ${GREEN}✓ All files formatted${NC}"
        fi
    fi

    # --- TypeScript ---
    if $HAS_TYPESCRIPT; then
        echo -e "\n${GREEN}[tsc] Type checking...${NC}"
        TSC_OUTPUT=$(npx tsc --noEmit 2>&1 || true)
        if [[ -n "$TSC_OUTPUT" ]] && echo "$TSC_OUTPUT" | grep -q "error TS"; then
            echo -e "  ${RED}TypeScript errors found${NC}"
            echo "$TSC_OUTPUT" | grep "error TS" | head -20

            echo -e "\n### TypeScript Errors\n\`\`\`" >> "$REPORT_FILE"
            echo "$TSC_OUTPUT" >> "$REPORT_FILE"
            echo -e "\`\`\`\n" >> "$REPORT_FILE"

            # Parse TS errors
            echo "$TSC_OUTPUT" | grep "error TS" | while read -r line; do
                file=$(echo "$line" | cut -d'(' -f1)
                lineno=$(echo "$line" | grep -oP '\((\d+)' | tr -d '(')
                msg=$(echo "$line" | cut -d':' -f2-)
                add_issue "typescript" "type_error" "$file" "$lineno" "$msg" "" ""
            done
        else
            echo -e "  ${GREEN}✓ No TypeScript errors${NC}"
        fi
    fi

    # --- Dead Code / Unused Exports Analysis ---
    echo -e "\n${GREEN}[exports] Analyzing unused exports...${NC}"

    # Find exported functions/classes that aren't imported anywhere
    echo -e "\n### Unused Exports Analysis\n" >> "$REPORT_FILE"

    UNUSED_EXPORTS=$(node -e "
const fs = require('fs');
const path = require('path');

const getAllFiles = (dir, exts) => {
    let results = [];
    try {
        const list = fs.readdirSync(dir);
        list.forEach(file => {
            const filePath = path.join(dir, file);
            const stat = fs.statSync(filePath);
            if (stat.isDirectory() && !['node_modules', '.git', 'dist', 'build', '.next'].includes(file)) {
                results = results.concat(getAllFiles(filePath, exts));
            } else if (exts.some(ext => file.endsWith(ext))) {
                results.push(filePath);
            }
        });
    } catch (e) {}
    return results;
};

const files = getAllFiles('.', ['.js', '.jsx', '.ts', '.tsx']);
const exports = {};
const imports = new Set();

// Find all exports
files.forEach(file => {
    try {
        const content = fs.readFileSync(file, 'utf8');
        const exportMatches = content.matchAll(/export\s+(?:const|let|var|function|class|interface|type|enum)\s+(\w+)/g);
        for (const match of exportMatches) {
            exports[match[1]] = exports[match[1]] || [];
            exports[match[1]].push(file);
        }
        const namedExports = content.matchAll(/export\s*\{\s*([^}]+)\s*\}/g);
        for (const match of namedExports) {
            match[1].split(',').forEach(e => {
                const name = e.trim().split(/\s+as\s+/)[0].trim();
                if (name) {
                    exports[name] = exports[name] || [];
                    exports[name].push(file);
                }
            });
        }
    } catch (e) {}
});

// Find all imports
files.forEach(file => {
    try {
        const content = fs.readFileSync(file, 'utf8');
        const importMatches = content.matchAll(/import\s*\{([^}]+)\}/g);
        for (const match of importMatches) {
            match[1].split(',').forEach(i => {
                const name = i.trim().split(/\s+as\s+/)[0].trim();
                if (name) imports.add(name);
            });
        }
        // Default imports
        const defaultImports = content.matchAll(/import\s+(\w+)\s+from/g);
        for (const match of defaultImports) {
            imports.add(match[1]);
        }
    } catch (e) {}
});

// Find unused
Object.entries(exports).forEach(([name, files]) => {
    if (!imports.has(name) && !['default', 'App', 'main', 'handler', 'getServerSideProps', 'getStaticProps'].includes(name)) {
        files.forEach(f => console.log(f + ': exported \"' + name + '\" is never imported'));
    }
});
" 2>/dev/null || true)

    if [[ -n "$UNUSED_EXPORTS" ]]; then
        echo -e "  ${YELLOW}Potentially unused exports:${NC}"
        echo "$UNUSED_EXPORTS" | while read -r line; do
            echo -e "    $line"
            file=$(echo "$line" | cut -d: -f1)
            msg=$(echo "$line" | cut -d: -f2-)
            symbol=$(echo "$msg" | grep -oP 'exported "\K[^"]+')

            # Check if used dynamically
            if grep -rq "\[.*['\"]$symbol['\"].*\]" . --include="*.js" --include="*.ts" --include="*.jsx" --include="*.tsx" 2>/dev/null; then
                echo -e "      ${CYAN}Note: May be accessed dynamically${NC}"
            fi

            add_issue "export_check" "unused_export" "$file" "0" "$msg" "" "Verify if export is needed or remove"
        done
        echo "$UNUSED_EXPORTS" >> "$REPORT_FILE"
    else
        echo -e "  ${GREEN}✓ No obviously unused exports${NC}"
    fi

    # --- Missing File Analysis ---
    echo -e "\n${GREEN}[imports] Checking for missing files/modules...${NC}"

    MISSING_FILES=$(node -e "
const fs = require('fs');
const path = require('path');

const getAllFiles = (dir, exts) => {
    let results = [];
    try {
        const list = fs.readdirSync(dir);
        list.forEach(file => {
            const filePath = path.join(dir, file);
            const stat = fs.statSync(filePath);
            if (stat.isDirectory() && !['node_modules', '.git', 'dist', 'build'].includes(file)) {
                results = results.concat(getAllFiles(filePath, exts));
            } else if (exts.some(ext => file.endsWith(ext))) {
                results.push(filePath);
            }
        });
    } catch (e) {}
    return results;
};

const files = getAllFiles('.', ['.js', '.jsx', '.ts', '.tsx']);

files.forEach(file => {
    try {
        const content = fs.readFileSync(file, 'utf8');
        const dir = path.dirname(file);

        // Check relative imports
        const relativeImports = content.matchAll(/(?:import|require)\s*\(?['\"](\.[^'\"]+)['\"]\)?/g);
        for (const match of relativeImports) {
            let importPath = path.resolve(dir, match[1]);
            const extensions = ['', '.js', '.jsx', '.ts', '.tsx', '/index.js', '/index.jsx', '/index.ts', '/index.tsx'];
            const exists = extensions.some(ext => fs.existsSync(importPath + ext));
            if (!exists) {
                console.log(file + ': imports missing \"' + match[1] + '\"');
            }
        }
    } catch (e) {}
});
" 2>/dev/null || true)

    if [[ -n "$MISSING_FILES" ]]; then
        echo -e "  ${RED}Missing imports found:${NC}"
        echo "$MISSING_FILES" | while read -r line; do
            echo -e "    $line"
            file=$(echo "$line" | cut -d: -f1)
            msg=$(echo "$line" | cut -d: -f2-)
            add_issue "import_check" "missing_file" "$file" "0" "$msg" "" "Create missing file or fix import path"
        done
        echo -e "\n#### Missing Files\n\`\`\`" >> "$REPORT_FILE"
        echo "$MISSING_FILES" >> "$REPORT_FILE"
        echo -e "\`\`\`\n" >> "$REPORT_FILE"
    else
        echo -e "  ${GREEN}✓ All imports resolve${NC}"
    fi

    # --- Build Check ---
    echo -e "\n${GREEN}[build] Build check...${NC}"
    if grep -q '"build"' package.json 2>/dev/null; then
        BUILD_OUTPUT=$(npm run build 2>&1 || true)
        if echo "$BUILD_OUTPUT" | grep -qi "error\|failed"; then
            echo -e "  ${RED}Build failed${NC}"
            echo "$BUILD_OUTPUT" | grep -i "error" | head -10
            echo -e "\n### Build Errors\n\`\`\`" >> "$REPORT_FILE"
            echo "$BUILD_OUTPUT" >> "$REPORT_FILE"
            echo -e "\`\`\`\n" >> "$REPORT_FILE"
        else
            echo -e "  ${GREEN}✓ Build succeeded${NC}"
        fi
    else
        echo -e "  ${YELLOW}No build script found${NC}"
    fi

    # --- Tests ---
    echo -e "\n${GREEN}[test] Running tests...${NC}"
    if grep -q '"test"' package.json 2>/dev/null; then
        TEST_OUTPUT=$(npm test -- --passWithNoTests 2>&1 || npx vitest run 2>&1 || true)
        if echo "$TEST_OUTPUT" | grep -qi "fail\|error"; then
            echo -e "  ${RED}Test failures${NC}"
            echo "$TEST_OUTPUT" | grep -iE "fail|error|✗" | head -10
            echo -e "\n### Test Failures\n\`\`\`" >> "$REPORT_FILE"
            echo "$TEST_OUTPUT" >> "$REPORT_FILE"
            echo -e "\`\`\`\n" >> "$REPORT_FILE"
        else
            echo -e "  ${GREEN}✓ Tests passed${NC}"
        fi
    else
        echo -e "  ${YELLOW}No test script found${NC}"
    fi

    # Return to original directory
    popd > /dev/null 2>&1 || true
fi

# ============ HTML/CSS ANALYSIS ============
# Only check HTML/CSS if we have files outside node_modules
HTML_FILES=$(find . -maxdepth 5 -name "*.html" -not -path "*/node_modules/*" 2>/dev/null | head -1)
CSS_FILES=$(find . -maxdepth 5 \( -name "*.css" -o -name "*.scss" \) -not -path "*/node_modules/*" 2>/dev/null | head -1)

if [[ -n "$HTML_FILES" || -n "$CSS_FILES" ]]; then
    echo -e "\n${YELLOW}═══════════════════════════════════════════${NC}"
    echo -e "${YELLOW}            HTML/CSS ANALYSIS${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════${NC}"
    echo -e "\n## HTML/CSS Analysis\n" >> "$REPORT_FILE"

    # HTML Validation (exclude node_modules, only check project files)
    echo -e "\n${GREEN}[html] Validating HTML...${NC}"
    if command -v npx &>/dev/null && [[ -n "$HTML_FILES" ]]; then
        # Find HTML files excluding node_modules
        HTML_TO_CHECK=$(find . -name "*.html" -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | tr '\n' ' ')
        if [[ -n "$HTML_TO_CHECK" ]]; then
            HTML_OUTPUT=$(npx html-validate $HTML_TO_CHECK 2>/dev/null || true)
            # Filter out void-style warnings (self-closing tags are valid in HTML5/JSX)
            REAL_ERRORS=$(echo "$HTML_OUTPUT" | grep -v "void-style" | grep "error" || true)
            if [[ -n "$REAL_ERRORS" ]]; then
                echo -e "  ${RED}HTML errors found${NC}"
                echo "$REAL_ERRORS" | head -20
            else
                echo -e "  ${GREEN}✓ HTML valid${NC}"
            fi
        else
            echo -e "  ${YELLOW}No HTML files to check${NC}"
        fi
    else
        echo -e "  ${YELLOW}No HTML files found${NC}"
    fi

    # CSS/Stylelint (exclude node_modules)
    echo -e "\n${GREEN}[stylelint] Checking CSS...${NC}"
    if command -v npx &>/dev/null && [[ -n "$CSS_FILES" ]]; then
        CSS_OUTPUT=$(npx stylelint "**/*.{css,scss}" --ignore-pattern "node_modules/**" 2>/dev/null || true)
        if [[ -n "$CSS_OUTPUT" ]]; then
            echo -e "  ${YELLOW}Stylelint issues:${NC}"
            echo "$CSS_OUTPUT" | head -10
        else
            echo -e "  ${GREEN}✓ CSS valid${NC}"
        fi
    else
        echo -e "  ${YELLOW}No CSS files found${NC}"
    fi
fi

# ============ SUMMARY ============
echo -e "\n${YELLOW}═══════════════════════════════════════════${NC}"
echo -e "${YELLOW}                 SUMMARY${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════${NC}"

ISSUE_COUNT=$(jq '.issues | length' "$JSON_REPORT" 2>/dev/null || echo "0")
echo -e "\nTotal issues found: ${RED}$ISSUE_COUNT${NC}"
echo -e "\n## Summary\n" >> "$REPORT_FILE"
echo "Total issues: $ISSUE_COUNT" >> "$REPORT_FILE"

# Group by type
echo -e "\nBy category:"
jq -r '.issues | group_by(.type) | .[] | "  \(.[0].type): \(length)"' "$JSON_REPORT" 2>/dev/null

echo -e "\n${GREEN}Reports saved to:${NC}"
echo "  Markdown: $REPORT_FILE"
echo "  JSON: $JSON_REPORT"

echo -e "\n${CYAN}═══════════════════════════════════════════${NC}"
echo -e "${CYAN}    FOR CLAUDE CODE ANALYSIS, RUN:${NC}"
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo -e "\nReview the JSON report and fix issues:"
echo -e "  cat $JSON_REPORT"
echo -e "\nOr ask Claude Code to analyze:"
echo -e "  \"Analyze $JSON_REPORT and fix all issues with proper context\""
echo ""
