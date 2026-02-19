#!/bin/bash
# Update CFAST User's Guide documentation
# 
# This script downloads the latest CFAST User's Guide LaTeX files

set -e

DOCS_DIR="$(dirname "$0")/cfast-reference"
TEMP_DIR=$(mktemp -d)

echo "Downloading latest CFAST User's Guide..."

# Download and extract only the User's Guide folder
curl -L https://github.com/bewygs/cfast/archive/refs/heads/master.tar.gz | \
    tar -xz -C "$TEMP_DIR" --strip-components=3 "cfast-master/Manuals/CFAST_Users_Guide"

# Backup current docs if they exist
if [ -d "$DOCS_DIR" ]; then
    echo "Backing up current documentation..."
    mv "$DOCS_DIR" "${DOCS_DIR}.backup.$(date +%Y%m%d-%H%M%S)"
fi

# Create docs directory
mkdir -p "$DOCS_DIR"

# Move only .tex files and shell scripts
echo "Installing new documentation (only .tex files and scripts)..."
find "$TEMP_DIR" -name "*.tex" -exec cp {} "$DOCS_DIR/" \;
find "$TEMP_DIR" -name "*.sh" -exec cp {} "$DOCS_DIR/" \;
find "$TEMP_DIR" -name "*.bat" -exec cp {} "$DOCS_DIR/" \;

echo "CFAST User's Guide documentation updated successfully!"
echo "Location: $DOCS_DIR"

# Cleanup
rm -rf "$TEMP_DIR"
