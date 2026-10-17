#!/bin/bash
# Update the CFAST User's Guide LaTeX sources used as reference for docstrings
#
# Usage: ./update_cfast_ref.sh [REF]
#
# REF is a branch, tag or commit SHA of firemodels/cfast (default: master).
# The resolved commit SHA is recorded in cfast-reference/.cfast_version. It is
# only updated when the User's Guide itself changed, so a commit touching other
# parts of CFAST does not produce a new reference.

set -euo pipefail

REPO_URL="https://github.com/firemodels/cfast.git"
GUIDE_PATH="Manuals/CFAST_Users_Guide"
REF="${1:-master}"

DOCS_DIR="$(cd "$(dirname "$0")" && pwd)/cfast-reference"
VERSION_FILE="$DOCS_DIR/.cfast_version"
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

echo "Resolving $REF on firemodels/cfast..."
REFS=$(git ls-remote "$REPO_URL" "refs/heads/$REF" "refs/tags/$REF" "refs/tags/$REF^{}")
# An annotated tag is listed twice, prefer the commit it points to ("^{}")
SHA=$(echo "$REFS" | awk '$2 ~ /\^\{\}$/ { print $1; exit }')
if [ -z "$SHA" ]; then
    SHA=$(echo "$REFS" | head -n 1 | cut -f 1)
fi
if [ -z "$SHA" ]; then
    if [[ "$REF" =~ ^[0-9a-f]{40}$ ]]; then
        SHA="$REF"
    else
        echo "ERROR: could not resolve '$REF' (use a branch, a tag or a full commit SHA)" >&2
        exit 1
    fi
fi
echo "Commit: $SHA"

# Fetch only the User's Guide folder at that commit
git -C "$TEMP_DIR" init -q
git -C "$TEMP_DIR" remote add origin "$REPO_URL"
git -C "$TEMP_DIR" sparse-checkout set --no-cone "/$GUIDE_PATH/"
git -C "$TEMP_DIR" fetch -q --depth 1 --filter=blob:none origin "$SHA"
git -C "$TEMP_DIR" checkout -q FETCH_HEAD

# Keep only the .tex sources and build scripts
NEW_DIR="$TEMP_DIR/new"
mkdir -p "$NEW_DIR"
find "$TEMP_DIR/$GUIDE_PATH" \( -name "*.tex" -o -name "*.sh" -o -name "*.bat" \) -exec cp {} "$NEW_DIR/" \;

if [ -f "$VERSION_FILE" ] && diff -rq --exclude=.cfast_version "$NEW_DIR" "$DOCS_DIR" > /dev/null; then
    echo "User's Guide unchanged since $(cat "$VERSION_FILE"), nothing to do."
    echo "Reference: $(cat "$VERSION_FILE" | cut -c 1-7)"
    exit 0
fi

# Replace in place (git history serves as backup)
rm -rf "$DOCS_DIR"
mkdir -p "$DOCS_DIR"
cp "$NEW_DIR"/* "$DOCS_DIR/"
echo "$SHA" > "$VERSION_FILE"

echo "CFAST User's Guide updated in $DOCS_DIR"
echo "Reference: ${SHA:0:7}"
