#!/bin/bash
# PersonaSay Backend Test Runner

set -e

echo "================================================"
echo "PersonaSay Backend Test Suite"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if pytest is installed
if ! python -c "import pytest" 2>/dev/null; then
    echo -e "${RED}Error: pytest not installed${NC}"
    echo "Run: pip install pytest pytest-cov pytest-asyncio"
    exit 1
fi

# Parse arguments
TEST_TYPE="${1:-all}"

case "$TEST_TYPE" in
    unit)
        echo -e "${YELLOW}Running Unit Tests Only...${NC}"
        pytest tests/unit/ -v --tb=short
        ;;
    integration)
        echo -e "${YELLOW}Running Integration Tests Only...${NC}"
        pytest tests/integration/ -v --tb=short
        ;;
    coverage)
        echo -e "${YELLOW}Running All Tests with Coverage...${NC}"
        pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html
        echo ""
        echo -e "${GREEN}Coverage report generated in htmlcov/index.html${NC}"
        ;;
    fast)
        echo -e "${YELLOW}Running Fast Tests (no slow tests)...${NC}"
        pytest tests/ -v --tb=short -m "not slow"
        ;;
    all)
        echo -e "${YELLOW}Running All Tests...${NC}"
        pytest tests/ -v --tb=short
        ;;
    *)
        echo "Usage: $0 {unit|integration|coverage|fast|all}"
        echo ""
        echo "Options:"
        echo "  unit         - Run unit tests only"
        echo "  integration  - Run integration tests only"
        echo "  coverage     - Run all tests with coverage report"
        echo "  fast         - Run all tests except slow ones"
        echo "  all          - Run all tests (default)"
        exit 1
        ;;
esac

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}================================================${NC}"
    echo -e "${GREEN}All tests passed! ✓${NC}"
    echo -e "${GREEN}================================================${NC}"
else
    echo ""
    echo -e "${RED}================================================${NC}"
    echo -e "${RED}Some tests failed! ✗${NC}"
    echo -e "${RED}================================================${NC}"
    exit 1
fi



