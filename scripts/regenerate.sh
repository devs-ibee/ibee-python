#!/usr/bin/env bash
# Regenerate src/ibee from contract/ibee-cloud.yaml (needs Fern CLI 5.45.3 and Docker).
# Hand-written files (src/ibee/.fernignore) are kept. The package version comes from
# pyproject.toml, so the generated User-Agent matches the release.
set -euo pipefail
cd "$(dirname "$0")/.."
version=$(sed -n 's/^version = "\(.*\)"$/\1/p' pyproject.toml)
cd fern
fern generate --local --group python-sdk --force --version "$version" --log-level warn
