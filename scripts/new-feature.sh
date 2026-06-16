#!/bin/bash

# New Feature Scaffolding Script
# Usage: ./scripts/new-feature.sh <ticket-id> <description>
# Example: ./scripts/new-feature.sh ERP-101 inventory-module

if [ $# -lt 2 ]; then
    echo "Usage: $0 <ticket-id> <description>"
    echo "Example: $0 ERP-101 inventory-module"
    exit 1
fi

TICKET_ID=$1
DESCRIPTION=$2
BRANCH_NAME="feature/${TICKET_ID}-${DESCRIPTION}"

echo "Creating new feature branch: $BRANCH_NAME"
git checkout -b "$BRANCH_NAME"

# Create module file template
MODULE_FILE="modules/${DESCRIPTION}.py"
if [ ! -f "$MODULE_FILE" ]; then
    cat > "$MODULE_FILE" << EOF
"""
${DESCRIPTION^} Module

Ticket: ${TICKET_ID}
"""

from modules import BaseModule


class ${DESCRIPTION^}Module(BaseModule):
    """${DESCRIPTION^} module implementation."""
    
    def __init__(self, config=None):
        super().__init__(config=config)
        self.name = "${DESCRIPTION}"
    
    def execute(self, **kwargs):
        """Execute the module's main functionality."""
        self.logger.info(f"Executing {self.name} module")
        # TODO: Implement module logic
        return {"status": "success", "module": self.name}
EOF
    echo "Created module template: $MODULE_FILE"
fi

# Create test file template
TEST_FILE="tests/test_${DESCRIPTION}.py"
if [ ! -f "$TEST_FILE" ]; then
    cat > "$TEST_FILE" << EOF
"""
Tests for ${DESCRIPTION^} Module

Ticket: ${TICKET_ID}
"""

import pytest
from modules.${DESCRIPTION} import ${DESCRIPTION^}Module


class Test${DESCRIPTION^}Module:
    """Test cases for ${DESCRIPTION^}Module."""
    
    def test_init(self):
        """Test module initialization."""
        module = ${DESCRIPTION^}Module()
        assert module.name == "${DESCRIPTION}"
    
    def test_execute(self):
        """Test module execution."""
        module = ${DESCRIPTION^}Module()
        result = module.execute()
        assert result["status"] == "success"
        assert result["module"] == "${DESCRIPTION}"
EOF
    echo "Created test template: $TEST_FILE"
fi

echo ""
echo "Feature branch '$BRANCH_NAME' is ready!"
echo "Next steps:"
echo "  1. Implement your feature in $MODULE_FILE"
echo "  2. Add tests in $TEST_FILE"
echo "  3. Run './scripts/dev-check.sh' before committing"
