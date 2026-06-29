#!/usr/bin/env bash
# Tiny runner: r.sh <rig> [savestate]  -> runs the rig, writes full output to
# /tmp/rigout.txt, prints just the rig results (LOC/PEEK/STATE/etc.).
cd "$(dirname "$(readlink -f "$0")")"
bash rig.sh tvtest/forest_test.gba "$1" "${2:-field.ss}" > /tmp/rigout.txt 2>&1
echo "exit=$?"
grep -vE '^===|^  png:|^=== [0-9]' /tmp/rigout.txt
