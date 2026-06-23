#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -n "${PDF2MD_AI_REPO:-}" ]]; then
	REPO="$PDF2MD_AI_REPO"
else
	REPO="$(cd "$SCRIPT_DIR/../../.." && pwd)"
	if [[ ! -f "$REPO/pyproject.toml" ]]; then
		echo "Could not find pdf2md-ai repo root. Run from a clone, or set PDF2MD_AI_REPO." >&2
		exit 1
	fi
fi

if ! command -v pipx >/dev/null 2>&1; then
	echo "pipx is required. Install from https://pipx.pypa.io/" >&2
	exit 1
fi

install_or_upgrade_cli() {
	# pipx 1.14+ uses uv; --force alone fails when the pipx venv already exists
	# from a previous session (uv refuses to overwrite without --clear).
	export UV_VENV_CLEAR=1

	if pipx list 2>/dev/null | grep -q 'package pdf2md-ai '; then
		echo "Upgrading pdf2md-ai CLI via pipx from: $REPO"
	else
		echo "Installing pdf2md-ai CLI via pipx from: $REPO"
	fi

	pipx install "$REPO" --force
}

install_or_upgrade_cli

SKILL_SRC="$REPO/skill/pdf2md-ai"
SKILL_DST="$HOME/.cursor/skills/pdf2md-ai"

echo "Installing Cursor skill to: $SKILL_DST"
mkdir -p "$HOME/.cursor/skills"
rm -rf "$SKILL_DST"
cp -r "$SKILL_SRC" "$SKILL_DST"

echo
echo "Done."
echo "  CLI:   $(command -v pdf2md-ai)"
echo "  Skill: $SKILL_DST"
echo
echo "Set your API key:"
echo "  export OPENAI_API_KEY='your-key-here'"
