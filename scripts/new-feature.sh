#!/bin/bash

# New Feature Scaffolding Script
# Usage: ./scripts/new-feature.sh <ticket-id> <module_name>
# Example: ./scripts/new-feature.sh ERP-101 inventory
#
# <module_name> must be a valid Python identifier (letters, digits,
# underscores; cannot start with a digit) because it is used to generate
# file names and class names.

set -e

if [ $# -lt 2 ]; then
    echo "Usage: $0 <ticket-id> <module_name>"
    echo "Example: $0 ERP-101 inventory"
    echo "Note: <module_name> must be a valid Python identifier"
    echo "      (use 'inventory' or 'stock_control', not 'inventory-module')"
    exit 1
fi

TICKET_ID=$1
MODULE_NAME=$2

# Validate module name: must be a snake_case Python identifier.
if ! printf '%s' "$MODULE_NAME" | grep -Eq '^[a-z][a-z0-9_]*$'; then
    echo "Error: '$MODULE_NAME' is not a valid module name." >&2
    echo "Use lowercase letters, digits and underscores, starting with a" >&2
    echo "letter (e.g. 'inventory', 'stock_control')." >&2
    exit 1
fi

BRANCH_NAME="feature/${TICKET_ID}-${MODULE_NAME}"

# Convert snake_case to PascalCase for the class name (no bash 4
# parameter-expansion capitalization hacks, which break on hyphens).
CLASS_NAME=$(printf '%s' "$MODULE_NAME" | awk -F'_' '{
    for (i = 1; i <= NF; i++) {
        printf "%s%s", toupper(substr($i, 1, 1)), substr($i, 2)
    }
}')

echo "Creating new feature branch: $BRANCH_NAME"
git checkout -b "$BRANCH_NAME"

# Create module file template
MODULE_FILE="modules/${MODULE_NAME}.py"
if [ ! -f "$MODULE_FILE" ]; then
    cat > "$MODULE_FILE" << EOF
"""
${CLASS_NAME} Module

Ticket: ${TICKET_ID}
"""

from modules.base import BaseModule


class ${CLASS_NAME}Module(BaseModule):
    """${CLASS_NAME} module implementation."""

    def __init__(self, config=None):
        super().__init__(name="${MODULE_NAME}", config=config)

    def initialize(self) -> bool:
        """Initialize the module."""
        self.logger.info("Initializing %s module", self.name)
        # TODO: Set up resources (DB connections, caches, ...)
        self._initialized = True
        return True

    def execute(self, *args, **kwargs):
        """Execute the module's main functionality."""
        if not self._initialized:
            self.initialize()
        self.logger.info("Executing %s module", self.name)
        # TODO: Implement module logic
        return {"status": "success", "module": self.name}
EOF
    echo "Created module template: $MODULE_FILE"
fi

# Create test file template
TEST_FILE="tests/test_${MODULE_NAME}.py"
if [ ! -f "$TEST_FILE" ]; then
    cat > "$TEST_FILE" << EOF
"""
Tests for ${CLASS_NAME} Module

Ticket: ${TICKET_ID}
"""

import pytest

from modules.${MODULE_NAME} import ${CLASS_NAME}Module


class Test${CLASS_NAME}Module:
    """Test cases for ${CLASS_NAME}Module."""

    @pytest.fixture
    def module(self):
        """Provide a fresh module instance."""
        return ${CLASS_NAME}Module()

    def test_init(self, module):
        """Test module initialization."""
        assert module.name == "${MODULE_NAME}"

    def test_initialize(self, module):
        """Test explicit initialization."""
        assert module.initialize() is True
        assert module._initialized is True

    def test_execute(self, module):
        """Test module execution."""
        result = module.execute()
        assert result["status"] == "success"
        assert result["module"] == "${MODULE_NAME}"
EOF
    echo "Created test template: $TEST_FILE"
fi

echo ""
echo "Feature branch '$BRANCH_NAME' is ready!"
echo "Next steps:"
echo "  1. Implement your feature in $MODULE_FILE"
echo "  2. Add tests in $TEST_FILE"
echo "  3. Run './scripts/dev-check.sh' before committing"
