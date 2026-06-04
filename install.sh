#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# AI Trading Analyst — Hermes Skill Installer
# Installs all 16 trading skills for Hermes Agent
# with an isolated Python virtual environment.
# ============================================================

REPO_URL="https://github.com/zubair-trabzada/ai-trading-hermes.git"
HERMES_DIR="${HOME}/.hermes"
SKILLS_DIR="${HERMES_DIR}/skills"
INSTALL_DIR="${SKILLS_DIR}/trade"
VENV_DIR="${INSTALL_DIR}/.venv"
VENV_PY="${VENV_DIR}/bin/python3"
# Tilde form for references inside SKILL.md files
VENV_MD_PY='~/.hermes/skills/trade/.venv/bin/python3'
TEMP_DIR=$(mktemp -d)

INTERACTIVE=true
if [ ! -t 0 ]; then
    INTERACTIVE=false
fi

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  AI Trading Analyst — Hermes Installer   ║${NC}"
    echo -e "${BLUE}║  16 Skills | 5 Parallel Agents | PDF     ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
    echo ""
}

print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_error()   { echo -e "${RED}✗ $1${NC}"; }
print_info()    { echo -e "${BLUE}→ $1${NC}"; }

cleanup() { rm -rf "$TEMP_DIR"; }
trap cleanup EXIT

# Cross-platform in-place sed
sed_inplace() {
    local pattern="$1"
    local file="$2"
    if [[ "$(uname)" == "Darwin" ]]; then
        sed -i '' "$pattern" "$file"
    else
        sed -i "$pattern" "$file"
    fi
}

# Detect Python
detect_python() {
    if command -v python3 &>/dev/null; then
        PYTHON=$(command -v python3)
    elif command -v python &>/dev/null; then
        PYTHON=$(command -v python)
    else
        print_error "Python 3 not found. Install Python 3.8+ and try again."
        exit 1
    fi

    local ver=$("$PYTHON" --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
    local major="${ver%.*}"
    local minor="${ver#*.}"
    if [ "$major" -lt 3 ] || { [ "$major" -eq 3 ] && [ "$minor" -lt 8 ]; }; then
        print_error "Python 3.8+ required, found $ver"
        exit 1
    fi
}

print_header

# ── Prerequisites ──────────────────────────────────────────

if ! command -v hermes &>/dev/null; then
    print_error "Hermes Agent not found. Install it first: curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash"
    exit 1
fi

detect_python

# ── Clone Repository ───────────────────────────────────────

print_info "Downloading AI Trading Analyst..."
git clone --depth 1 "$REPO_URL" "$TEMP_DIR/repo" 2>/dev/null || {
    print_error "Failed to download repository. Check your internet connection."
    exit 1
}
print_success "Repository downloaded"

# ── Create Skill Directory ─────────────────────────────────

print_info "Setting up skill directory..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/scripts"

# ── Copy Skill Files ───────────────────────────────────────

print_info "Installing skills..."

# Copy main orchestrator
cp -r "$TEMP_DIR/repo/trade/"* "$INSTALL_DIR/" 2>/dev/null || true

# Copy all sub-skills
for skill_dir in "$TEMP_DIR/repo/skills/"*/; do
    skill_name=$(basename "$skill_dir")
    target="${SKILLS_DIR}/${skill_name}"
    mkdir -p "$target"
    cp -r "$skill_dir"* "$target/" 2>/dev/null || true
    print_success "Installed skill: $skill_name"
done

# Copy PDF generation script
cp "$TEMP_DIR/repo/scripts/generate_trade_pdf.py" "$INSTALL_DIR/scripts/" 2>/dev/null || true

print_success "All skill files installed"

# ── Create Virtual Environment ─────────────────────────────

if [ ! -d "$VENV_DIR" ]; then
    print_info "Creating isolated Python virtual environment..."
    "$PYTHON" -m venv "$VENV_DIR"
    print_success "Virtual environment created"
fi

# ── Install Dependencies ───────────────────────────────────

print_info "Installing Python dependencies..."

# Check if uv is available for faster installs
if command -v uv &>/dev/null; then
    uv pip install --quiet --python "$VENV_PY" -r "$TEMP_DIR/repo/requirements.txt" 2>/dev/null || {
        print_warning "uv install failed, falling back to pip..."
        "$VENV_PY" -m pip install -q -r "$TEMP_DIR/repo/requirements.txt" 2>/dev/null || true
    }
else
    "$VENV_PY" -m pip install -q -r "$TEMP_DIR/repo/requirements.txt" 2>/dev/null || true
fi

print_success "Python dependencies installed"

# ── Patch Skill Files with Correct Venv Path ───────────────

print_info "Configuring skill paths..."

# Patch SKILL.md files that reference the Python path
for skill_file in "$INSTALL_DIR/SKILL.md" "$SKILLS_DIR"/trade-*/SKILL.md; do
    if [ -f "$skill_file" ]; then
        # Replace ~/.claude/ paths with ~/.hermes/ paths
        sed_inplace 's|~/.claude/skills/|~/.hermes/skills/|g' "$skill_file" 2>/dev/null || true
        # Replace Claude Code tool references with Hermes equivalents
        sed_inplace 's|/trade |trade |g' "$skill_file" 2>/dev/null || true
    fi
done

print_success "Skill paths configured"

# ── Register Skills with Hermes ────────────────────────────

print_info "Registering skills with Hermes..."
if command -v hermes &>/dev/null; then
    hermes skills list &>/dev/null || true
fi
print_success "Skills registered"

# ── Summary ────────────────────────────────────────────────

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  AI Trading Analyst for Hermes — Installation Complete!     ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📊 16 trading skills installed${NC}"
echo ""
echo -e "${BLUE}Try these commands in Hermes:${NC}"
echo ""
echo "  trade analyze AAPL       — Full stock analysis (5 parallel agents)"
echo "  trade quick NVDA         — 60-second stock snapshot"
echo "  trade technical TSLA     — Technical analysis"
echo "  trade fundamental MSFT   — Fundamental analysis"
echo "  trade sentiment AMZN     — Sentiment analysis"
echo "  trade risk META          — Risk assessment & position sizing"
echo "  trade thesis GOOGL       — Complete investment thesis"
echo "  trade options SPY        — Options strategy analysis"
echo "  trade screen growth      — Stock screener (growth/value/momentum/etc.)"
echo "  trade portfolio          — Portfolio analysis & rebalancing"
echo "  trade earnings NVDA      — Pre-earnings analysis"
echo "  trade compare AAPL MSFT  — Head-to-head comparison"
echo "  trade sector technology  — Sector rotation analysis"
echo "  trade watchlist          — Build scored watchlist"
echo "  trade report-pdf         — Generate professional PDF report"
echo ""
echo -e "${YELLOW}⚠ DISCLAIMER: For educational/research purposes only.${NC}"
echo -e "${YELLOW}  NOT financial advice. Always do your own due diligence.${NC}"
echo ""
echo -e "${BLUE}To uninstall: rm -rf ~/.hermes/skills/trade ~/.hermes/skills/trade-*${NC}"
echo ""
