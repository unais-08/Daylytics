"""Enforce the backend module boundaries without adding a dependency."""

import ast
from pathlib import Path

ROOT = Path(__file__).parents[1]
APP = ROOT / "app"


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def test_python_files_stay_within_hard_size_limit():
    oversized = [
        str(path.relative_to(ROOT))
        for path in APP.rglob("*.py")
        if len(path.read_text(encoding="utf-8").splitlines()) > 400
    ]
    assert not oversized, f"Python files exceed 400 lines: {oversized}"


def test_core_does_not_depend_on_application_layers():
    forbidden = ("app.modules", "app.analytics", "app.api")
    violations = []
    for path in (APP / "core").glob("*.py"):
        for imported in _imports(path):
            if imported.startswith(forbidden):
                violations.append(f"{path}: {imported}")
    assert not violations, "\n".join(violations)


def test_pure_analytics_does_not_import_framework_or_modules():
    forbidden = ("fastapi", "sqlalchemy", "app.modules")
    violations = []
    for path in (APP / "analytics").glob("*.py"):
        for imported in _imports(path):
            if imported == "app" or imported.startswith(forbidden):
                violations.append(f"{path}: {imported}")
    assert not violations, "\n".join(violations)


def test_routers_do_not_import_other_routers_or_queries():
    violations = []
    for path in (APP / "modules").glob("*/router.py"):
        package = path.parent.name
        for imported in _imports(path):
            if ".router" in imported or ".queries" in imported:
                violations.append(f"{path}: {imported}")
            if imported.startswith("app.modules.") and not imported.startswith(
                f"app.modules.{package}"
            ):
                violations.append(f"{path}: cross-module import {imported}")
    assert not violations, "\n".join(violations)


def test_services_never_import_routers():
    violations = []
    for path in (APP / "modules").glob("*/service.py"):
        for imported in _imports(path):
            if ".router" in imported:
                violations.append(f"{path}: {imported}")
    assert not violations, "\n".join(violations)
