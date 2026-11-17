# Managed by Devin / Sosoka Labs
"""Count unique vulnerabilities in a ``pip-audit --format json`` report.

Used by ``.github/workflows/security.yml``. pip-audit nests findings under
``dependencies[].vulns``; this parser counts unique package/advisory pairs, merging
advisories whose ID or aliases overlap, and fails closed on a missing, unreadable, or
malformed report so a broken audit can never read as a clean one.

Dependencies pip-audit skipped (``skip_reason``) are unaudited. A report in which every
dependency was skipped is rejected; a report with some skipped is valid but is labelled
partial coverage on stderr, and its count covers only the audited dependencies.

Usage: ``python pip_audit_report.py REPORT``

Exit codes:
    0  Report is valid; the vulnerability count (possibly 0) is printed to stdout.
    2  Report is missing, unreadable, or malformed; nothing is printed to stdout.

Standard library only: the workflow runs this on the runner's bare Python.
"""

from __future__ import annotations

import json
import re
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

EXIT_VALID_REPORT = 0
EXIT_INVALID_REPORT = 2


class AuditReportError(Exception):
    """The pip-audit report is missing or does not have the expected structure."""


@dataclass(frozen=True)
class Advisory:
    """One vulnerability affecting one package, identified by all its known IDs."""

    package: str
    ids: frozenset[str]


@dataclass(frozen=True)
class AuditSummary:
    """Unique advisories found in a report and the dependencies pip-audit skipped."""

    advisories: tuple[Advisory, ...]
    skipped_dependencies: tuple[str, ...]

    @property
    def vulnerability_count(self) -> int:
        return len(self.advisories)


def load_report(path: Path) -> object:
    """Read and decode a pip-audit JSON report."""
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise AuditReportError(f"pip-audit report not found: {path}") from exc
    except OSError as exc:
        raise AuditReportError(f"pip-audit report could not be read: {path}: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise AuditReportError(f"pip-audit report is not valid UTF-8: {path}: {exc}") from exc
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise AuditReportError(f"pip-audit report is not valid JSON: {path}: {exc}") from exc


def summarize_report(report: object) -> AuditSummary:
    """Validate a decoded pip-audit report and collect its unique advisories."""
    dependencies = _require_dependencies(report)
    advisory_ids_by_package: dict[str, list[frozenset[str]]] = {}
    skipped: list[str] = []
    for index, dependency in enumerate(dependencies):
        name, vuln_ids = _parse_dependency(dependency, index)
        if vuln_ids is None:
            skipped.append(name)
            continue
        package_advisories = advisory_ids_by_package.setdefault(_normalize_name(name), [])
        for ids in vuln_ids:
            _merge_advisory(package_advisories, ids)
    if len(skipped) == len(dependencies):
        raise AuditReportError("pip-audit report skipped every dependency; nothing was audited")
    advisories = tuple(
        Advisory(package, ids)
        for package, id_groups in sorted(advisory_ids_by_package.items())
        for ids in id_groups
    )
    return AuditSummary(advisories=advisories, skipped_dependencies=tuple(skipped))


def _require_dependencies(report: object) -> list[object]:
    if not isinstance(report, dict) or "dependencies" not in report:
        raise AuditReportError("pip-audit report has no top-level 'dependencies' key")
    dependencies = report["dependencies"]
    if not isinstance(dependencies, list):
        raise AuditReportError("pip-audit report 'dependencies' is not a list")
    if not dependencies:
        raise AuditReportError("pip-audit report audited no dependencies")
    return dependencies


def _parse_dependency(dependency: object, index: int) -> tuple[str, list[frozenset[str]] | None]:
    """Return the dependency name and the ID set of each vuln, or None vulns if skipped."""
    location = f"dependencies[{index}]"
    if not isinstance(dependency, dict):
        raise AuditReportError(f"{location} is not an object")
    name = dependency.get("name")
    if not isinstance(name, str) or not name:
        raise AuditReportError(f"{location} has no package name")
    if "vulns" not in dependency:
        if "skip_reason" in dependency:
            return name, None
        raise AuditReportError(f"{location} ({name}) has neither 'vulns' nor 'skip_reason'")
    vulns = dependency["vulns"]
    if not isinstance(vulns, list):
        raise AuditReportError(f"{location} ({name}) 'vulns' is not a list")
    return name, [_parse_vuln_ids(vuln, f"{location}.vulns[{i}]") for i, vuln in enumerate(vulns)]


def _parse_vuln_ids(vuln: object, location: str) -> frozenset[str]:
    if not isinstance(vuln, dict):
        raise AuditReportError(f"{location} is not an object")
    vuln_id = vuln.get("id")
    if not isinstance(vuln_id, str) or not vuln_id:
        raise AuditReportError(f"{location} has no advisory id")
    aliases = vuln.get("aliases", [])
    if not isinstance(aliases, list) or not all(isinstance(alias, str) for alias in aliases):
        raise AuditReportError(f"{location} ({vuln_id}) 'aliases' is not a list of strings")
    return frozenset([vuln_id, *aliases])


def _merge_advisory(package_advisories: list[frozenset[str]], ids: frozenset[str]) -> None:
    """Add an advisory, merging it with every known advisory that shares an ID."""
    overlapping = [known for known in package_advisories if known & ids]
    for known in overlapping:
        package_advisories.remove(known)
    package_advisories.append(ids.union(*overlapping))


def _normalize_name(name: str) -> str:
    """Normalize a package name per PEP 503 so case and separators don't split entries."""
    return re.sub(r"[-_.]+", "-", name).lower()


def _describe(summary: AuditSummary) -> str:
    lines = [f"{summary.vulnerability_count} unique vulnerabilities found in audited dependencies"]
    lines += [f"  {a.package}: {', '.join(sorted(a.ids))}" for a in summary.advisories]
    if summary.skipped_dependencies:
        lines.append(
            "WARNING: partial coverage; these dependencies were skipped by pip-audit and not "
            f"audited: {', '.join(summary.skipped_dependencies)}"
        )
    return "\n".join(lines)


def main(argv: Sequence[str]) -> int:
    if len(argv) != 1:
        print("usage: pip_audit_report.py REPORT", file=sys.stderr)
        return EXIT_INVALID_REPORT
    try:
        summary = summarize_report(load_report(Path(argv[0])))
    except AuditReportError as exc:
        print(f"Invalid pip-audit report: {exc}", file=sys.stderr)
        return EXIT_INVALID_REPORT
    print(_describe(summary), file=sys.stderr)
    print(summary.vulnerability_count)
    return EXIT_VALID_REPORT


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
