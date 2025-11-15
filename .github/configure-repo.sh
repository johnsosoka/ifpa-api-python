#!/usr/bin/env bash
#
# GitHub Repository Configuration Script for IFPA API
#
# This script provides instructions and automation for configuring the
# johnsosoka/ifpa-api-python GitHub repository with proper settings, branch protection,
# secrets, and integrations.
#
# Usage:
#   ./configure-repo.sh [--apply]
#
# Without --apply flag, the script will only display instructions.
# With --apply flag, the script will attempt to apply settings using gh CLI.
#
# Requirements:
#   - gh (GitHub CLI) installed and authenticated
#   - Repository admin access
#   - jq (for JSON parsing)

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Repository details
REPO_OWNER="johnsosoka"
REPO_NAME="ifpa-api-python"
REPO_FULL="${REPO_OWNER}/${REPO_NAME}"

# Flag to determine if we should apply changes
APPLY_CHANGES=false
if [[ "${1:-}" == "--apply" ]]; then
    APPLY_CHANGES=true
fi

# Print section header
print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

# Print success message
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Print warning message
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Print error message
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Print info message
print_info() {
    echo -e "  $1"
}

# Check if gh CLI is installed
check_gh_cli() {
    if ! command -v gh &> /dev/null; then
        print_error "GitHub CLI (gh) is not installed"
        print_info "Install it from: https://cli.github.com/"
        exit 1
    fi

    # Check if authenticated
    if ! gh auth status &> /dev/null; then
        print_error "GitHub CLI is not authenticated"
        print_info "Run: gh auth login"
        exit 1
    fi
}

# Configure branch protection rules
configure_branch_protection() {
    print_header "BRANCH PROTECTION RULES"

    if [[ "$APPLY_CHANGES" == true ]]; then
        print_info "Applying branch protection rules for 'main'..."

        gh api repos/${REPO_FULL}/branches/main/protection \
            --method PUT \
            --field required_status_checks='{"strict":true,"contexts":["Lint (Ruff & Black)","Type Check (mypy)","Test (Python 3.11)","Test (Python 3.12)","Build Package"]}' \
            --field enforce_admins=false \
            --field required_pull_request_reviews='{"dismiss_stale_reviews":true,"require_code_owner_reviews":false,"required_approving_review_count":1}' \
            --field restrictions=null \
            --field required_linear_history=true \
            --field allow_force_pushes=false \
            --field allow_deletions=false \
            && print_success "Branch protection configured" \
            || print_error "Failed to configure branch protection"
    else
        print_info "Branch: main"
        print_info "  • Require pull request reviews: 1 approval"
        print_info "  • Dismiss stale reviews when new commits are pushed"
        print_info "  • Require status checks to pass before merging:"
        print_info "    - Lint (Ruff & Black)"
        print_info "    - Type Check (mypy)"
        print_info "    - Test (Python 3.11)"
        print_info "    - Test (Python 3.12)"
        print_info "    - Build Package"
        print_info "  • Require branches to be up to date before merging"
        print_info "  • Require linear history"
        print_info "  • Do not allow force pushes"
        print_info "  • Do not allow deletions"
        print_warning "Run with --apply to configure"
    fi
}

# Configure repository secrets
configure_secrets() {
    print_header "REQUIRED SECRETS"

    print_info "The following secrets must be configured in GitHub repository settings:"
    echo ""
    print_info "1. IFPA_API_KEY"
    print_info "   Description: API key for IFPA integration tests"
    print_info "   Value: (provided by IFPA - check credentials file)"
    print_info "   URL: https://github.com/${REPO_FULL}/settings/secrets/actions"
    echo ""
    print_info "2. CODECOV_TOKEN"
    print_info "   Description: Token for uploading coverage to Codecov"
    print_info "   Value: (obtain from https://codecov.io/${REPO_FULL})"
    print_info "   URL: https://github.com/${REPO_FULL}/settings/secrets/actions"
    echo ""
    print_info "3. TEST_PYPI_TOKEN"
    print_info "   Description: API token for TestPyPI publishing"
    print_info "   Value: (create at https://test.pypi.org/manage/account/token/)"
    print_info "   URL: https://github.com/${REPO_FULL}/settings/secrets/actions"
    echo ""
    print_info "4. PYPI_TOKEN"
    print_info "   Description: API token for PyPI publishing"
    print_info "   Value: (create at https://pypi.org/manage/account/token/)"
    print_info "   URL: https://github.com/${REPO_FULL}/settings/secrets/actions"
    echo ""

    if [[ "$APPLY_CHANGES" == true ]]; then
        print_warning "Secrets must be configured manually via GitHub UI"
        print_info "Visit: https://github.com/${REPO_FULL}/settings/secrets/actions"
    fi
}

# Configure repository environments
configure_environments() {
    print_header "DEPLOYMENT ENVIRONMENTS"

    print_info "Configure the following environments for deployment:"
    echo ""
    print_info "1. test-pypi"
    print_info "   Protection rules: None (or require reviewers if desired)"
    print_info "   Secrets: TEST_PYPI_TOKEN"
    print_info "   URL: https://github.com/${REPO_FULL}/settings/environments"
    echo ""
    print_info "2. pypi"
    print_info "   Protection rules: Require reviewers (recommended: 1)"
    print_info "   Secrets: PYPI_TOKEN"
    print_info "   URL: https://github.com/${REPO_FULL}/settings/environments"
    echo ""

    if [[ "$APPLY_CHANGES" == true ]]; then
        print_warning "Environments must be configured manually via GitHub UI"
        print_info "Visit: https://github.com/${REPO_FULL}/settings/environments"
    fi
}

# Configure repository labels
configure_labels() {
    print_header "REPOSITORY LABELS"

    LABELS=(
        "bug:d73a4a:Something isn't working"
        "documentation:0075ca:Improvements or additions to documentation"
        "enhancement:a2eeef:New feature or request"
        "dependencies:0366d6:Dependency updates"
        "security:d93f0b:Security-related issues"
        "github-actions:000000:GitHub Actions workflow changes"
        "automated:ededed:Automated updates"
        "needs-triage:fbca04:Needs initial review and categorization"
        "good first issue:7057ff:Good for newcomers"
        "help wanted:008672:Extra attention is needed"
        "wontfix:ffffff:This will not be worked on"
        "duplicate:cfd3d7:This issue or pull request already exists"
        "invalid:e4e669:This doesn't seem right"
    )

    if [[ "$APPLY_CHANGES" == true ]]; then
        print_info "Creating repository labels..."
        for label in "${LABELS[@]}"; do
            IFS=':' read -r name color description <<< "$label"
            gh label create "$name" --color "$color" --description "$description" --repo "$REPO_FULL" 2>/dev/null \
                && print_success "Created label: $name" \
                || print_warning "Label '$name' already exists or failed to create"
        done
    else
        print_info "The following labels will be created:"
        for label in "${LABELS[@]}"; do
            IFS=':' read -r name color description <<< "$label"
            print_info "  • $name - $description"
        done
        print_warning "Run with --apply to create labels"
    fi
}

# Configure integrations
configure_integrations() {
    print_header "THIRD-PARTY INTEGRATIONS"

    print_info "1. Codecov"
    print_info "   Purpose: Code coverage reporting and tracking"
    print_info "   Setup: Visit https://codecov.io/ and connect repository"
    print_info "   Note: .codecov.yml is already configured in the repository"
    echo ""
    print_info "2. pre-commit.ci"
    print_info "   Purpose: Automated pre-commit hook running on PRs"
    print_info "   Setup: Visit https://pre-commit.ci/ and enable for repository"
    print_info "   Note: .pre-commit-config.yaml is already configured"
    echo ""
    print_info "3. Dependabot"
    print_info "   Purpose: Automated dependency updates"
    print_info "   Setup: Automatically enabled with .github/dependabot.yml"
    print_info "   Note: Configure Dependabot settings in repository settings if needed"
    echo ""

    if [[ "$APPLY_CHANGES" == true ]]; then
        print_warning "Integrations must be configured manually via their respective websites"
    fi
}

# Configure GitHub Pages (future documentation)
configure_github_pages() {
    print_header "GITHUB PAGES (OPTIONAL)"

    print_info "For hosting documentation with MkDocs:"
    print_info "  1. Navigate to: https://github.com/${REPO_FULL}/settings/pages"
    print_info "  2. Source: Deploy from a branch"
    print_info "  3. Branch: gh-pages (will be created by MkDocs deploy)"
    print_info "  4. Folder: / (root)"
    echo ""
    print_info "Deploy documentation with: poetry run mkdocs gh-deploy"
    echo ""

    if [[ "$APPLY_CHANGES" == true ]]; then
        print_warning "GitHub Pages must be configured manually via GitHub UI"
    fi
}

# Configure repository settings
configure_repository_settings() {
    print_header "REPOSITORY SETTINGS"

    if [[ "$APPLY_CHANGES" == true ]]; then
        print_info "Updating repository settings..."

        # Enable features
        gh repo edit "$REPO_FULL" \
            --enable-issues \
            --enable-projects=false \
            --enable-wiki=false \
            --enable-discussions \
            && print_success "Repository settings updated" \
            || print_error "Failed to update repository settings"

        # Set description and topics
        gh repo edit "$REPO_FULL" \
            --description "Typed Python client for the IFPA (International Flipper Pinball Association) API" \
            --add-topic python \
            --add-topic sdk \
            --add-topic ifpa \
            --add-topic pinball \
            --add-topic api-client \
            --add-topic pydantic \
            && print_success "Repository description and topics updated" \
            || print_error "Failed to update description/topics"
    else
        print_info "Repository Configuration:"
        print_info "  • Enable Issues: Yes"
        print_info "  • Enable Projects: No"
        print_info "  • Enable Wiki: No"
        print_info "  • Enable Discussions: Yes"
        print_info "  • Description: Typed Python client for the IFPA API"
        print_info "  • Topics: python, sdk, ifpa, pinball, api-client, pydantic"
        print_warning "Run with --apply to configure"
    fi
}

# Main execution
main() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  IFPA API - GitHub Repository Configuration                 ║${NC}"
    echo -e "${GREEN}║  Repository: ${REPO_FULL}                               ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"

    if [[ "$APPLY_CHANGES" == true ]]; then
        check_gh_cli
        print_success "GitHub CLI is authenticated"
        echo ""
        print_warning "APPLYING CHANGES TO REPOSITORY"
        echo ""
    else
        echo ""
        print_info "Running in DRY-RUN mode (no changes will be applied)"
        print_info "Run with --apply flag to apply changes"
        echo ""
    fi

    configure_repository_settings
    configure_branch_protection
    configure_labels
    configure_secrets
    configure_environments
    configure_integrations
    configure_github_pages

    print_header "SUMMARY"

    if [[ "$APPLY_CHANGES" == true ]]; then
        print_success "Automated configuration steps completed"
        print_warning "Manual steps still required:"
        print_info "  • Configure repository secrets"
        print_info "  • Set up deployment environments"
        print_info "  • Enable Codecov integration"
        print_info "  • Enable pre-commit.ci integration"
    else
        print_info "To apply these configurations, run:"
        print_info "  ./configure-repo.sh --apply"
        echo ""
        print_info "Some steps require manual configuration via GitHub UI"
    fi

    print_header "NEXT STEPS"

    print_info "1. Review and apply this configuration"
    print_info "2. Set up required secrets in GitHub"
    print_info "3. Enable Codecov and pre-commit.ci integrations"
    print_info "4. Push code to trigger CI workflows"
    print_info "5. Test the CI/CD pipeline with a pull request"
    print_info "6. When ready, create a version tag to test publishing"
    echo ""
    print_success "Repository configuration guide completed!"
    echo ""
}

# Run main function
main
