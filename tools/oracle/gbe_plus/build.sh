#!/usr/bin/env bash
# shellcheck disable=SC2312
set -euo pipefail

readonly REPOSITORY="https://github.com/shonumi/gbe-plus"
readonly COMMIT="05a05e931b3993ff3e6316b0d841a1fb4d3ac7a7"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly HERE
readonly TARGET="${1:-${HOME}/.cache/maeyomi-tools/gbe-plus}"

if [[ ! -d "${TARGET}/.git" ]]; then
    git clone --quiet "${REPOSITORY}" "${TARGET}"
fi
git -C "${TARGET}" checkout --quiet --force "${COMMIT}"
git -C "${TARGET}" apply "${HERE}/gbe_plus.patch"
cp -f "${HERE}/script_hook.h" "${TARGET}/src/nds/script_hook.h"
cmake -S "${TARGET}" -B "${TARGET}/build" -DUSE_NETPLAY=OFF -DUSE_OGL=OFF -DQT_GUI=OFF \
    -DCMAKE_BUILD_TYPE=Release >/dev/null
cmake --build "${TARGET}/build" --parallel 8 >"${TARGET}/build.log" 2>&1
printf '%s\n' "${TARGET}/build/src/gbe_plus"
