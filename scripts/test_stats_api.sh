#!/usr/bin/env bash
#
# test_stats_api.sh
#
# Comprehensive test script for all 10 IFPA Stats API endpoints.
# This script manually tests each endpoint to understand actual API behavior
# before implementing the Python client.
#
# Usage:
#   export IFPA_API_KEY='your-api-key'
#   ./scripts/test_stats_api.sh
#
# Requirements:
#   - curl (for API requests)
#   - jq (optional, for pretty JSON formatting)
#   - IFPA_API_KEY environment variable must be set
#
# Output:
#   - Console output with test results
#   - Sample responses saved to scripts/stats_responses/
#

set -euo pipefail

# Configuration
BASE_URL="https://api.ifpapinball.com"
RESPONSE_DIR="scripts/stats_responses"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if jq is available for pretty printing
HAS_JQ=false
if command -v jq &> /dev/null; then
    HAS_JQ=true
fi

# Validate API key is set
if [[ -z "${IFPA_API_KEY:-}" ]]; then
    echo -e "${RED}ERROR: IFPA_API_KEY environment variable is not set${NC}"
    echo "Please set it with: export IFPA_API_KEY='your-api-key'"
    exit 1
fi

# Create response directory
mkdir -p "${SCRIPT_DIR}/../${RESPONSE_DIR}"

# Test counter
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

#
# Helper Functions
#

print_header() {
    local title="$1"
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}${title}${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_subheader() {
    local title="$1"
    echo ""
    echo -e "${CYAN}--- ${title} ---${NC}"
}

print_curl_command() {
    local url="$1"
    echo -e "${YELLOW}curl -H 'X-API-Key: \$IFPA_API_KEY' '${url}'${NC}"
}

execute_test() {
    local endpoint="$1"
    local test_name="$2"
    local save_file="$3"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    local url="${BASE_URL}${endpoint}"
    local response_file="${SCRIPT_DIR}/../${RESPONSE_DIR}/${save_file}"

    print_subheader "${test_name}"
    print_curl_command "${url}"

    # Execute curl and capture response, status code, and HTTP code
    local http_code
    local response

    response=$(curl -s -w "\n%{http_code}" \
        -H "X-API-Key: ${IFPA_API_KEY}" \
        "${url}")

    http_code=$(echo "${response}" | tail -n1)
    response=$(echo "${response}" | sed '$d')

    echo -e "${CYAN}HTTP Status: ${http_code}${NC}"

    # Save response to file
    echo "${response}" > "${response_file}"

    # Pretty print if jq is available
    if [[ "${HAS_JQ}" == true ]]; then
        if echo "${response}" | jq . > /dev/null 2>&1; then
            echo "${response}" | jq . | head -n 50
            if [[ $(echo "${response}" | jq . | wc -l) -gt 50 ]]; then
                echo -e "${YELLOW}... (output truncated, full response saved to ${save_file})${NC}"
            fi
        else
            echo "${response}"
        fi
    else
        echo "${response}" | head -n 20
        if [[ $(echo "${response}" | wc -l) -gt 20 ]]; then
            echo -e "${YELLOW}... (output truncated, full response saved to ${save_file})${NC}"
        fi
    fi

    # Check if successful
    if [[ "${http_code}" == "200" ]]; then
        echo -e "${GREEN}✓ Test passed (200 OK)${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    elif [[ "${http_code}" == "404" ]]; then
        echo -e "${YELLOW}⚠ Test returned 404 (endpoint may not be available yet)${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    else
        echo -e "${RED}✗ Test failed (HTTP ${http_code})${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi

    echo -e "${CYAN}Response saved to: ${response_file}${NC}"
}

#
# Test Execution
#

echo -e "${GREEN}Starting IFPA Stats API Test Suite${NC}"
echo "Base URL: ${BASE_URL}"
echo "Response directory: ${RESPONSE_DIR}"
echo ""

# Test 1: Country Players
print_header "TEST 1: GET /stats/country_players"
execute_test "/stats/country_players" \
    "Test 1.1: Country players (default OPEN)" \
    "country_players_open.json"

execute_test "/stats/country_players?rank_type=OPEN" \
    "Test 1.2: Country players (explicit OPEN)" \
    "country_players_open_explicit.json"

execute_test "/stats/country_players?rank_type=WOMEN" \
    "Test 1.3: Country players (WOMEN)" \
    "country_players_women.json"

# Test 2: State Players
print_header "TEST 2: GET /stats/state_players"
execute_test "/stats/state_players" \
    "Test 2.1: State players (default OPEN)" \
    "state_players_open.json"

execute_test "/stats/state_players?rank_type=WOMEN" \
    "Test 2.2: State players (WOMEN)" \
    "state_players_women.json"

# Test 3: State Tournaments
print_header "TEST 3: GET /stats/state_tournaments"
execute_test "/stats/state_tournaments" \
    "Test 3.1: State tournaments (default OPEN)" \
    "state_tournaments_open.json"

execute_test "/stats/state_tournaments?rank_type=WOMEN" \
    "Test 3.2: State tournaments (WOMEN)" \
    "state_tournaments_women.json"

# Test 4: Events by Year
print_header "TEST 4: GET /stats/events_by_year"
execute_test "/stats/events_by_year" \
    "Test 4.1: Events by year (default OPEN)" \
    "events_by_year_open.json"

execute_test "/stats/events_by_year?rank_type=WOMEN" \
    "Test 4.2: Events by year (WOMEN)" \
    "events_by_year_women.json"

execute_test "/stats/events_by_year?country_code=US" \
    "Test 4.3: Events by year (US only)" \
    "events_by_year_us.json"

execute_test "/stats/events_by_year?rank_type=WOMEN&country_code=US" \
    "Test 4.4: Events by year (WOMEN, US)" \
    "events_by_year_women_us.json"

# Test 5: Players by Year
print_header "TEST 5: GET /stats/players_by_year"
execute_test "/stats/players_by_year" \
    "Test 5.1: Players by year (no parameters)" \
    "players_by_year.json"

# Test 6: Largest Tournaments
print_header "TEST 6: GET /stats/largest_tournaments"
execute_test "/stats/largest_tournaments" \
    "Test 6.1: Largest tournaments (default OPEN)" \
    "largest_tournaments_open.json"

execute_test "/stats/largest_tournaments?rank_type=WOMEN" \
    "Test 6.2: Largest tournaments (WOMEN)" \
    "largest_tournaments_women.json"

execute_test "/stats/largest_tournaments?country_code=US" \
    "Test 6.3: Largest tournaments (US only)" \
    "largest_tournaments_us.json"

# Test 7: Lucrative Tournaments
print_header "TEST 7: GET /stats/lucrative_tournaments"
execute_test "/stats/lucrative_tournaments" \
    "Test 7.1: Lucrative tournaments (default major=Y, OPEN)" \
    "lucrative_tournaments_major_open.json"

execute_test "/stats/lucrative_tournaments?major=N" \
    "Test 7.2: Lucrative tournaments (major=N)" \
    "lucrative_tournaments_non_major.json"

execute_test "/stats/lucrative_tournaments?rank_type=WOMEN" \
    "Test 7.3: Lucrative tournaments (WOMEN)" \
    "lucrative_tournaments_women.json"

execute_test "/stats/lucrative_tournaments?country_code=US" \
    "Test 7.4: Lucrative tournaments (US only)" \
    "lucrative_tournaments_us.json"

# Test 8: Points Given Period
print_header "TEST 8: GET /stats/points_given_period"
execute_test "/stats/points_given_period" \
    "Test 8.1: Points given period (no parameters)" \
    "points_given_period_default.json"

execute_test "/stats/points_given_period?start_date=2024-01-01&end_date=2024-12-31" \
    "Test 8.2: Points given period (2024 date range)" \
    "points_given_period_2024.json"

execute_test "/stats/points_given_period?start_date=2024-01-01&end_date=2024-12-31&limit=10" \
    "Test 8.3: Points given period (2024, limit 10)" \
    "points_given_period_2024_limit10.json"

execute_test "/stats/points_given_period?country_code=US&start_date=2024-01-01&end_date=2024-12-31" \
    "Test 8.4: Points given period (US, 2024)" \
    "points_given_period_us_2024.json"

# Test 9: Events Attended Period
print_header "TEST 9: GET /stats/events_attended_period"
execute_test "/stats/events_attended_period" \
    "Test 9.1: Events attended period (no parameters)" \
    "events_attended_period_default.json"

execute_test "/stats/events_attended_period?start_date=2024-01-01&end_date=2024-12-31" \
    "Test 9.2: Events attended period (2024 date range)" \
    "events_attended_period_2024.json"

execute_test "/stats/events_attended_period?start_date=2024-01-01&end_date=2024-12-31&limit=10" \
    "Test 9.3: Events attended period (2024, limit 10)" \
    "events_attended_period_2024_limit10.json"

execute_test "/stats/events_attended_period?country_code=US&start_date=2024-01-01&end_date=2024-12-31" \
    "Test 9.4: Events attended period (US, 2024)" \
    "events_attended_period_us_2024.json"

# Test 10: Overall Stats
print_header "TEST 10: GET /stats/overall"
execute_test "/stats/overall" \
    "Test 10.1: Overall stats (default OPEN)" \
    "overall_open.json"

execute_test "/stats/overall?system_code=OPEN" \
    "Test 10.2: Overall stats (explicit OPEN)" \
    "overall_open_explicit.json"

execute_test "/stats/overall?system_code=WOMEN" \
    "Test 10.3: Overall stats (WOMEN)" \
    "overall_women.json"

#
# Summary
#

print_header "TEST SUMMARY"
echo -e "Total tests executed: ${TOTAL_TESTS}"
echo -e "${GREEN}Passed: ${PASSED_TESTS}${NC}"
echo -e "${RED}Failed: ${FAILED_TESTS}${NC}"
echo ""

if [[ "${FAILED_TESTS}" -eq 0 ]]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${YELLOW}Some tests failed. Review output above for details.${NC}"
    echo -e "${YELLOW}Note: 404 responses may indicate endpoints are not yet available in the API.${NC}"
    exit 1
fi
