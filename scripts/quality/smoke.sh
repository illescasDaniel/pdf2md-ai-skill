#!/usr/bin/env bash

# Install smoke tests — editable CLI entry point and agent-install skill discovery.
# Does not pipx-install globally or write skills to agent config directories.

set -euo pipefail

quality_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/quality/internal/lib.sh
source "${quality_dir}/internal/lib.sh"

lib_require_venv

if ! command -v npx >/dev/null 2>&1; then
	echo "Missing npx (install Node.js)." >&2
	exit 1
fi

cd "${LIB_REPO_ROOT}" || exit 1

echo "Installing editable package for smoke test..."
"${LIB_REPO_ROOT}/.venv/bin/pip" install -e . -q

CLI="${LIB_REPO_ROOT}/.venv/bin/pdf2md-ai"
SKILL_DIR="${LIB_REPO_ROOT}/skill/pdf2md-ai"
PUBLISHED_SKILL="illescasDaniel/pdf2md-ai-skill/skill/pdf2md-ai"

echo "Checking CLI entry point..."
if ! "${CLI}" --help | grep -q 'pdf2md-ai'; then
	echo "pdf2md-ai --help failed or missing expected output" >&2
	exit 1
fi

assert_skill_listable() {
	local source="$1"
	local label="$2"
	local output

	if ! output="$(npx agent-install@latest skill add "${source}" -l -y 2>&1)"; then
		echo "${label}: agent-install skill list failed" >&2
		printf '%s\n' "${output}" >&2
		return 1
	fi

	if ! printf '%s\n' "${output}" | grep -q 'pdf2md-ai'; then
		echo "${label}: skill list did not include pdf2md-ai" >&2
		printf '%s\n' "${output}" >&2
		return 1
	fi

	printf '%s\n' "${output}"
}

echo "Checking local skill source..."
assert_skill_listable "${SKILL_DIR}" "local skill"

if [[ "${CI:-}" == "true" ]]; then
	echo "Skipping published GitHub skill source in CI (validates local checkout only)."
else
	echo "Checking published GitHub skill source..."
	assert_skill_listable "${PUBLISHED_SKILL}" "published skill"
fi

echo "Smoke tests passed."
