# IFPA SDK - CI/CD Quick Start

## 🚀 Setup (5 Minutes)

### 1. Configure Repository
```bash
cd /Users/john/code/projects/ifpa-api-python
./.github/configure-repo.sh --apply
```

### 2. Add GitHub Secrets
Go to: https://github.com/jscom/ifpa-sdk/settings/secrets/actions

Required secrets:
- `IFPA_API_KEY` - From credentials file (optional for tests)
- `CODECOV_TOKEN` - From https://codecov.io/gh/jscom/ifpa-sdk
- `TEST_PYPI_TOKEN` - From https://test.pypi.org/manage/account/token/
- `PYPI_TOKEN` - From https://pypi.org/manage/account/token/

### 3. Enable Integrations
- Codecov: https://codecov.io/ → Connect repository
- pre-commit.ci: https://pre-commit.ci/ → Enable for repo

### 4. Test Pipeline
```bash
git add .github/ .codecov.yml .pre-commit-config.yaml
git commit -m "feat: add CI/CD infrastructure"
git push origin feat/client-starter
```

## 📦 Publishing a Release

```bash
# 1. Update version
poetry version 0.1.0

# 2. Commit and tag
git add pyproject.toml
git commit -m "chore: bump version to 0.1.0"
git tag v0.1.0

# 3. Push (triggers automated publishing)
git push origin main --tags
```

## 🔍 What Gets Automated

| Trigger | What Happens |
|---------|-------------|
| Push to any branch | Lint, type-check, test, build |
| Pull request | All CI checks + coverage report |
| Version tag (`v*.*.*`) | TestPyPI → PyPI + GitHub Release |
| Weekly (Monday) | Security scanning |
| Dependency updates | Dependabot PRs |

## 📊 Monitoring

- **CI Status**: Check GitHub Actions tab
- **Coverage**: Codecov comments on PRs
- **Security**: Weekly scan results in Issues
- **Dependencies**: Dependabot PRs

## 🛠️ Troubleshooting

**CI failing?**
- Check job logs in GitHub Actions
- Run locally: `poetry run pytest`, `poetry run ruff check`, etc.

**Publishing failing?**
- Verify secrets are set correctly
- Check version in pyproject.toml matches tag
- Review TestPyPI logs first

**Coverage dropping?**
- Add tests for new code
- Target: 80% coverage

## 📚 Full Documentation

- Detailed setup: `CICD_SETUP_SUMMARY.md`
- Team docs: `llm_memory/cicd_setup_complete.md`
- Configuration: `.github/configure-repo.sh`

---

**Ready?** Run the setup steps above, then push your code!
