#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$root"

repo=${MAEYOMI_REPO:-gufranco/maeyomi}
account=${MAEYOMI_GH_ACCOUNT:-gufranco}

strapline=$(sed -n 's/^<strong>\(.*\)<\/strong>$/\1/p' README.md | head -1)
if [[ -z "$strapline" ]]; then
	printf 'the README has no strapline for anything else to be made from\n' >&2
	exit 1
fi
readme_says=${strapline%.}

if [[ -z "${GH_TOKEN:-}" ]]; then
	GH_TOKEN=$(gh auth token --user "$account")
	export GH_TOKEN
fi

github_says=$(gh repo view "$repo" --json description --jq '.description')
github_links_to=$(gh repo view "$repo" --json homepageUrl --jq '.homepageUrl')

drifted=0

if [[ "$github_says" != "$readme_says" ]]; then
	printf 'the repository description no longer matches the README\n' >&2
	printf '  README: %s\n' "$readme_says" >&2
	printf '  GitHub: %s\n' "$github_says" >&2
	printf 'fix with: gh repo edit %s --description "%s"\n' "$repo" "$readme_says" >&2
	drifted=1
fi

if [[ -n "$github_links_to" && "$github_links_to" != "https://github.com/${repo}" ]]; then
	printf 'the repository homepage points away from the project: %s\n' "$github_links_to" >&2
	drifted=1
fi

if [[ "$drifted" -eq 0 ]]; then
	printf 'GitHub says what the README says\n'
fi

exit "$drifted"
