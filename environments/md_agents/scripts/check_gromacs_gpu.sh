#!/usr/bin/env bash
set -euo pipefail

GMX_BIN="${GMX_BIN:-/home/boltzmann15/anaconda3/envs/gromacs-gpu/bin/gmx}"
test -x "$GMX_BIN"
version="$($GMX_BIN --version)"
grep -q 'GPU support:.*CUDA' <<<"$version"
grep -q 'GROMACS version:' <<<"$version"
printf '%s\n' "$version" | grep -E 'GROMACS version:|GPU support:|CUDA runtime:|CUDA driver:'
