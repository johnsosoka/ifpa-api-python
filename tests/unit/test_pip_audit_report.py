# Managed by Devin / Sosoka Labs
"""Tests for the pip-audit report parser used by the security workflow.

All reports below are synthetic fixtures shaped like ``pip-audit --format json``
output. Package names and advisory IDs are invented; none is live audit evidence.
"""

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PARSER_PATH = REPO_ROOT / ".github" / "scripts" / "pip_audit_report.py"
SECURITY_WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "security.yml"


def _load_parser() -> ModuleType:
    spec = importlib.util.spec_from_file_location("pip_audit_report", PARSER_PATH)
    assert spec is not None and spec.loader is not None, f"parser not found at {PARSER_PATH}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


parser = _load_parser()


def make_vuln(vuln_id: str, *aliases: str) -> dict[str, Any]:
    return {
        "id": vuln_id,
        "fix_versions": ["9.9.9"],
        "aliases": list(aliases),
        "description": "synthetic advisory",
    }


def make_dependency(name: str, *vulns: dict[str, Any]) -> dict[str, Any]:
    return {"name": name, "version": "1.0.0", "vulns": list(vulns)}


def make_report(*dependencies: dict[str, Any]) -> dict[str, Any]:
    return {"dependencies": list(dependencies), "fixes": []}


def write_report(tmp_path: Path, content: str) -> Path:
    report_path = tmp_path / "audit-report.json"
    report_path.write_text(content)
    return report_path


class TestSummarizeReport:
    def test_clean_report_has_zero_vulnerabilities(self) -> None:
        report = make_report(make_dependency("example-a"), make_dependency("example-b"))

        assert parser.summarize_report(report).vulnerability_count == 0

    def test_counts_vulnerabilities_nested_under_dependencies(self) -> None:
        report = make_report(
            make_dependency("example-a", make_vuln("PYSEC-0000-0001")),
            make_dependency("example-b", make_vuln("GHSA-test-0002"), make_vuln("GHSA-test-0003")),
            make_dependency("example-c"),
        )

        assert parser.summarize_report(report).vulnerability_count == 3

    def test_counts_five_unique_pairs_despite_duplicates_and_aliases(self) -> None:
        report = make_report(
            make_dependency(
                "example-a",
                make_vuln("PYSEC-0000-0001", "GHSA-test-0001"),
                make_vuln("GHSA-test-0001", "PYSEC-0000-0001"),
            ),
            make_dependency("example-b", make_vuln("GHSA-test-0002"), make_vuln("GHSA-test-0003")),
            make_dependency("Example_B", make_vuln("GHSA-test-0002")),
            make_dependency(
                "example-c", make_vuln("PYSEC-0000-0004"), make_vuln("PYSEC-0000-0005")
            ),
        )

        assert parser.summarize_report(report).vulnerability_count == 5

    def test_same_advisory_in_different_packages_counts_once_per_package(self) -> None:
        report = make_report(
            make_dependency("example-a", make_vuln("GHSA-test-0001")),
            make_dependency("example-b", make_vuln("GHSA-test-0001")),
        )

        assert parser.summarize_report(report).vulnerability_count == 2

    def test_aliases_that_bridge_earlier_entries_merge_into_one_advisory(self) -> None:
        report = make_report(
            make_dependency(
                "example-a",
                make_vuln("PYSEC-0000-0001"),
                make_vuln("GHSA-test-0001"),
                make_vuln("CVE-0000-0001", "PYSEC-0000-0001", "GHSA-test-0001"),
            )
        )

        assert parser.summarize_report(report).vulnerability_count == 1

    def test_skipped_dependencies_are_reported_not_counted(self) -> None:
        report = make_report(
            make_dependency("example-a"),
            {"name": "example-local", "skip_reason": "not found on PyPI"},
        )

        summary = parser.summarize_report(report)

        assert summary.vulnerability_count == 0
        assert summary.skipped_dependencies == ("example-local",)

    @pytest.mark.parametrize(
        "report",
        [
            pytest.param({"vulnerabilities": []}, id="legacy-key-without-dependencies"),
            pytest.param({}, id="empty-object"),
            pytest.param([], id="top-level-list"),
            pytest.param(None, id="null"),
            pytest.param({"dependencies": {}}, id="dependencies-not-a-list"),
            pytest.param({"dependencies": []}, id="no-dependencies-audited"),
            pytest.param(
                {"dependencies": [{"name": "example-a", "skip_reason": "not found on PyPI"}]},
                id="all-dependencies-skipped",
            ),
            pytest.param({"dependencies": ["example-a"]}, id="dependency-not-an-object"),
            pytest.param({"dependencies": [{"vulns": []}]}, id="dependency-missing-name"),
            pytest.param({"dependencies": [{"name": "example-a"}]}, id="missing-vulns-and-skip"),
            pytest.param(
                {"dependencies": [{"name": "example-a", "vulns": {}}]}, id="vulns-not-a-list"
            ),
            pytest.param(
                {"dependencies": [{"name": "example-a", "vulns": ["PYSEC-0000-0001"]}]},
                id="vuln-not-an-object",
            ),
            pytest.param(
                {"dependencies": [{"name": "example-a", "vulns": [{"aliases": []}]}]},
                id="vuln-missing-id",
            ),
            pytest.param(
                {"dependencies": [{"name": "example-a", "vulns": [{"id": "X", "aliases": "Y"}]}]},
                id="aliases-not-a-list",
            ),
        ],
    )
    def test_malformed_report_raises(self, report: object) -> None:
        with pytest.raises(parser.AuditReportError):
            parser.summarize_report(report)


class TestLoadReport:
    def test_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(parser.AuditReportError, match="not found"):
            parser.load_report(tmp_path / "missing.json")

    @pytest.mark.parametrize("content", ["", "{not json", "Traceback (most recent call last):"])
    def test_invalid_json_raises(self, tmp_path: Path, content: str) -> None:
        with pytest.raises(parser.AuditReportError, match="not valid JSON"):
            parser.load_report(write_report(tmp_path, content))

    def test_unreadable_path_raises(self, tmp_path: Path) -> None:
        with pytest.raises(parser.AuditReportError, match="could not be read"):
            parser.load_report(tmp_path)

    def test_undecodable_bytes_raise(self, tmp_path: Path) -> None:
        report_path = tmp_path / "audit-report.json"
        report_path.write_bytes(b"\xff\xfe\x00{")

        with pytest.raises(parser.AuditReportError, match="not valid UTF-8"):
            parser.load_report(report_path)


class TestMain:
    def test_prints_count_and_exits_zero_for_valid_report(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        report = make_report(make_dependency("example-a", make_vuln("PYSEC-0000-0001")))
        report_path = write_report(tmp_path, json.dumps(report))

        exit_code = parser.main([str(report_path)])

        assert exit_code == 0
        assert capsys.readouterr().out.strip() == "1"

    def test_exits_with_invalid_report_code_and_no_count_for_malformed_report(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        report_path = write_report(tmp_path, json.dumps({"vulnerabilities": []}))

        exit_code = parser.main([str(report_path)])

        captured = capsys.readouterr()
        assert exit_code == parser.EXIT_INVALID_REPORT
        assert captured.out == ""
        assert "dependencies" in captured.err

    def test_reports_partial_coverage_when_some_dependencies_skipped(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        report = make_report(
            make_dependency("example-a"),
            {"name": "example-local", "skip_reason": "not found on PyPI"},
        )
        report_path = write_report(tmp_path, json.dumps(report))

        exit_code = parser.main([str(report_path)])

        captured = capsys.readouterr()
        assert exit_code == 0
        assert captured.out.strip() == "0"
        assert "partial coverage" in captured.err.lower()
        assert "example-local" in captured.err

    def test_exits_invalid_with_no_count_for_unreadable_path(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        exit_code = parser.main([str(tmp_path)])

        captured = capsys.readouterr()
        assert exit_code == parser.EXIT_INVALID_REPORT
        assert captured.out == ""
        assert "could not be read" in captured.err

    def test_exits_invalid_with_no_count_for_undecodable_report(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        report_path = tmp_path / "audit-report.json"
        report_path.write_bytes(b"\xff\xfe\x00{")

        exit_code = parser.main([str(report_path)])

        captured = capsys.readouterr()
        assert exit_code == parser.EXIT_INVALID_REPORT
        assert captured.out == ""
        assert "not valid UTF-8" in captured.err


def test_security_workflow_counts_vulnerabilities_with_parser() -> None:
    workflow = SECURITY_WORKFLOW_PATH.read_text()

    assert ".github/scripts/pip_audit_report.py audit-report.json" in workflow
    assert "data.get('vulnerabilities'" not in workflow
