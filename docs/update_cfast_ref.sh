#!/bin/bash
# Update CFAST User's Guide documentation
#
# This script downloads the latest CFAST User's Guide LaTeX files from the
# latest official release of firemodels/cfast.

set -e

DOCS_DIR="$(dirname "$0")/cfast-reference"
VERSION_FILE="$DOCS_DIR/.cfast_version"
TEMP_DIR=$(mktemp -d)

# Fetch the latest release tag from the official repo
echo "Fetching latest CFAST release info..."
LATEST_TAG=$(curl -s https://api.github.com/repos/firemodels/cfast/releases/latest | grep '"tag_name"' | cut -d'"' -f4)

if [ -z "$LATEST_TAG" ]; then
    echo "ERROR: Could not determine latest CFAST release tag" >&2
    exit 1
fi

echo "Latest release: $LATEST_TAG"

# Skip download if already up to date
if [ -f "$VERSION_FILE" ] && [ "$(cat "$VERSION_FILE")" = "$LATEST_TAG" ]; then
    echo "Already up to date ($LATEST_TAG), skipping download."
    echo "Release: $LATEST_TAG"
    rm -rf "$TEMP_DIR"
    exit 0
fi

echo "Downloading CFAST User's Guide..."

# Download and extract only the User's Guide folder from the release tarball
curl -L "https://github.com/firemodels/cfast/archive/refs/tags/${LATEST_TAG}.tar.gz" | \
    tar -xz -C "$TEMP_DIR" --strip-components=3 "cfast-${LATEST_TAG}/Manuals/CFAST_Users_Guide"

# Clear existing docs and replace in-place (git history serves as backup)
rm -rf "$DOCS_DIR"
mkdir -p "$DOCS_DIR"

# Copy only .tex files and build scripts
echo "Installing new documentation (only .tex files and scripts)..."
find "$TEMP_DIR" -name "*.tex" -exec cp {} "$DOCS_DIR/" \;
find "$TEMP_DIR" -name "*.sh" -exec cp {} "$DOCS_DIR/" \;
find "$TEMP_DIR" -name "*.bat" -exec cp {} "$DOCS_DIR/" \;

# Record current version to avoid unnecessary re-downloads
echo "$LATEST_TAG" > "$VERSION_FILE"

echo "CFAST User's Guide documentation updated successfully!"
echo "Location: $DOCS_DIR"
echo "Release: $LATEST_TAG"

# Cleanup
rm -rf "$TEMP_DIR"
