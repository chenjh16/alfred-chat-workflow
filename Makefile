.PHONY: help all bump-version build install clean

# Shell setup
SHELL := /bin/bash

# Get current version from info.plist
CURRENT_VERSION = $(shell sed -n 's/.*<string>\(20[0-9][0-9]\.[0-9]*\)<\/string>.*/\1/p' info.plist | head -n 1)
YEAR = $(shell date +%Y)

# Calculate new version
# If current version starts with current year, increment last part. Otherwise start with YEAR.1
NEW_VERSION = $(shell \
	if [[ "$(CURRENT_VERSION)" =~ ^$(YEAR)\.([0-9]+)$$ ]]; then \
		echo "$(YEAR).$$(( $${BASH_REMATCH[1]} + 1 ))"; \
	else \
		echo "$(YEAR).1"; \
	fi \
)

all: build install

help:
	@echo "Available targets:"
	@echo "  make          - Build and install the workflow (Default)"
	@echo "  bump-version  - Increment version in info.plist (Current: $(CURRENT_VERSION) -> Next: $(NEW_VERSION))"
	@echo "  build         - Package the workflow into an .alfredworkflow file"
	@echo "  install       - Open the built .alfredworkflow file to install in Alfred"
	@echo "  clean         - Remove generated .alfredworkflow files"

bump-version:
	@echo "Bumping version from $(CURRENT_VERSION) to $(NEW_VERSION)..."
	@sed -i '' "s/<string>$(CURRENT_VERSION)<\/string>/<string>$(NEW_VERSION)<\/string>/" info.plist
	@echo "Version updated in info.plist"

build:
	@echo "Building Alfred Workflow v$(CURRENT_VERSION)..."
	@zip -r alfred-chathub-v$(CURRENT_VERSION).alfredworkflow . -x "*.git*" "*.github*" "*.DS_Store" "Makefile" "AGENTS.md" "LICENSE"
	@echo "Created alfred-chathub-v$(CURRENT_VERSION).alfredworkflow"

install:
	@echo "Installing Alfred Workflow v$(CURRENT_VERSION)..."
	@open alfred-chathub-v$(CURRENT_VERSION).alfredworkflow
	@echo "Opened alfred-chathub-v$(CURRENT_VERSION).alfredworkflow in Alfred"

clean:
	@echo "Cleaning up..."
	@rm -f *.alfredworkflow
	@echo "Done"
