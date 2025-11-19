# IFPA API Testing Scripts

This directory contains testing and development scripts for the IFPA API Python client.

## Scripts

### test_stats_api.sh

Comprehensive bash script to manually test all 10 IFPA Stats API endpoints using curl.

**Purpose**: Manually verify API endpoint behavior before implementing Python client code.

**Usage**:
```bash
# Set your API key
export IFPA_API_KEY='your-api-key-here'

# Run the test suite
./scripts/test_stats_api.sh
```

**Features**:
- Tests all 10 stats endpoints with multiple parameter variations (30 total tests)
- Color-coded output for easy reading
- Automatic response saving to `stats_responses/` directory
- Pretty-printed JSON output (using jq if available)
- HTTP status code validation
- Comprehensive error handling

**Requirements**:
- `curl` (for API requests)
- `jq` (optional, for pretty JSON formatting)
- `IFPA_API_KEY` environment variable

**Output**:
- Console output with test results
- Sample responses saved to `scripts/stats_responses/*.json`
- Test summary with pass/fail counts

## Response Files

### stats_responses/

Contains JSON response files from real API calls. These files serve multiple purposes:

1. **Test Fixtures**: Use as mock data for unit tests
2. **Reference Data**: Understand actual API response structures
3. **Model Validation**: Verify Pydantic models against real data

**Response Files** (30 total):
- `country_players_*.json` - Country statistics (OPEN/WOMEN)
- `state_players_*.json` - State statistics (North America)
- `state_tournaments_*.json` - Tournament statistics by state
- `events_by_year_*.json` - Yearly event statistics
- `players_by_year.json` - Player retention metrics
- `largest_tournaments_*.json` - Largest tournaments by attendance
- `lucrative_tournaments_*.json` - Tournaments by WPPR value
- `points_given_period_*.json` - Top point earners in date range
- `events_attended_period_*.json` - Most active players in date range
- `overall_*.json` - Overall IFPA statistics

## Test Results

See `/Users/john/code/projects/ifpa-api-python/V0.3.0_HANDS_ON_TESTING_REPORT.md` for detailed test results and findings.

See `/Users/john/code/projects/ifpa-api-python/llm_memory/stats_api_curl_findings.md` for comprehensive API behavior analysis and implementation recommendations.

## Adding New Test Scripts

When adding new testing scripts to this directory:

1. Make them executable: `chmod +x scripts/your_script.sh`
2. Add proper shebang: `#!/usr/bin/env bash`
3. Include help text and usage instructions
4. Use `set -euo pipefail` for safety
5. Document in this README
6. Save any output/responses to appropriate subdirectory
