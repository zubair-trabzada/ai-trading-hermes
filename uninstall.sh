#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# AI Trading Analyst — Hermes Uninstaller
# Removes all trading skills and the virtual environment.
# ============================================================

HERMES_DIR="${HOME}/.hermes"
SKILLS_DIR="${HERMES_DIR}/skills"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_error()   { echo -e "${RED}✗ $1${NC}"; }
print_info()    { echo -e "${BLUE}→ $1${NC}"; }

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  AI Trading Analyst — Hermes Uninstaller  ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo ""

# Confirmation
if [ -t 0 ]; then
    echo -e "${YELLOW}This will remove all AI Trading Analyst skills from Hermes.${NC}"
    read -p "Continue? (y/N) " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        print_info "Uninstall cancelled."
        exit 0
    fi
fi

# Remove main skill directory
if [ -d "${SKILLS_DIR}/trade" ]; then
    rm -rf "${SKILLS_DIR}/trade"
    print_success "Removed: ${SKILLS_DIR}/trade"
fi

# Remove sub-skill directories
for skill in trade-analyze trade-technical trade-fundamental trade-sentiment trade-risk trade-thesis trade-quick trade-screen trade-watchlist trade-portfolio trade-earnings trade-options trade-compare trade-sector trade-report-pdf; do
    if [ -d "${SKILLS_DIR}/${skill}" ]; then
        rm -rf "${SKILLS_DIR}/${skill}"
        print_success "Removed: ${SKILLS_DIR}/${skill}"
    fi
done

# Remove agent files (from previous Claude Code install if any)
if [ -d "${HOME}/.claude/skills/trade" ]; then
    print_warning "Claude Code version detected at ~/.claude/. Remove separately if needed."
fi

echo ""
print_success "AI Trading Analyst uninstalled successfully."
echo ""
print_info "To remove prospect/watchlist data (if any): rm -rf ~/.trade-prospects"
echo ""
echo -e "${YELLOW}Note: The Hermes config was not modified. Skills will no longer load.${NC}"
echo ""
