#!/bin/bash
# Sync .in files from the CFAST repository (Verification and/or Validation)
# Usage: ./sync_cfast_inputs.sh [--suite verification|validation|all]

set -e

SUITE="all"
while [[ $# -gt 0 ]]; do
    case "$1" in
        --suite) SUITE="$2"; shift 2 ;;
        *) echo "Unknown argument: $1"; exit 1 ;;
    esac
done

if [[ "$SUITE" != "verification" && "$SUITE" != "validation" && "$SUITE" != "all" ]]; then
    echo "Error: --suite must be one of: verification, validation, all"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMP_DIR=$(mktemp -d)

echo "Suite: $SUITE"
echo "Script directory: $SCRIPT_DIR"
echo "Temp directory: $TEMP_DIR"

echo "Downloading latest CFAST repository..."
cd "$TEMP_DIR"
curl -L https://github.com/firemodels/cfast/archive/refs/heads/master.tar.gz | tar -xz

sync_suite() {
    local name="$1"      # "Verification" or "Validation"
    local target="$2"    # destination path

    local src="$TEMP_DIR/cfast-master/$name"
    if [ ! -d "$src" ]; then
        echo "Error: $name directory not found in downloaded archive"
        ls -la "$TEMP_DIR/cfast-master/"
        exit 1
    fi

    echo "Syncing $name → $target"
    rm -rf "$target"
    mkdir -p "$target"

    cd "$src"
    rsync -a --include="*/" --include="*.in" --exclude="*" . "$target/"

    local count
    count=$(find "$target" -name "*.in" | wc -l)
    echo "  $count .in files copied"
}

if [[ "$SUITE" == "verification" || "$SUITE" == "all" ]]; then
    sync_suite "Verification" "$SCRIPT_DIR/verification_tests/Verification"
fi

if [[ "$SUITE" == "validation" || "$SUITE" == "all" ]]; then
    sync_suite "Validation" "$SCRIPT_DIR/validation_tests/Validation"
fi

rm -rf "$TEMP_DIR"
echo "Done!"
