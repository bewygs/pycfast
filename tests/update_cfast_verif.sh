#!/bin/bash
# Download all .in files from CFAST Verification directory (and subfolders)
# and place them in ./Verification/

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERIF_DIR="$SCRIPT_DIR/verification_tests/Verification"
TEMP_DIR=$(mktemp -d)

echo "Script directory: $SCRIPT_DIR"
echo "Target directory: $VERIF_DIR"
echo "Temp directory: $TEMP_DIR"

# Clean and create the verification directory
rm -rf "$VERIF_DIR"
mkdir -p "$VERIF_DIR"

echo "Downloading latest CFAST repository..."

# Download and extract the repository
cd "$TEMP_DIR"
curl -L https://github.com/firemodels/cfast/archive/refs/heads/master.tar.gz | tar -xz

# Check if the verification directory exists
if [ ! -d "$TEMP_DIR/cfast-master/Verification" ]; then
    echo "Error: Verification directory not found in downloaded archive"
    ls -la "$TEMP_DIR/cfast-master/"
    exit 1
fi

echo "Copying .in files using rsync..."
# Use rsync to copy all .in files while preserving directory structure
cd "$TEMP_DIR/cfast-master/Verification"
rsync -av --include="*/" --include="*.in" --exclude="*" . "$VERIF_DIR/"

# Count the files
file_count=$(find "$VERIF_DIR" -name "*.in" | wc -l)
echo "Successfully copied $file_count .in files to $VERIF_DIR"

# Show the directory structure
echo "Directory structure:"
find "$VERIF_DIR" -type d | sort

# Cleanup
rm -rf "$TEMP_DIR"
echo "Done!"
