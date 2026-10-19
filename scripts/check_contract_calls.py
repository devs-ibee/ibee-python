#!/usr/bin/env python3
"""Check B: the hand-written code calls nothing outside contract/ibee-cloud.yaml.

The hand-written files are the .py files listed in src/ibee/.fernignore; the generated
code is covered by check A (scripts/check_generated.sh). This fails on

* a generated-client method that is not a contract operation (operationId), when the
  hand layer calls or overrides it: ``super().x``, ``self.x`` and ``def x`` in a class
  built on a generated client, and ``SomeClient(...).x`` (also through a name bound to
  ``SomeClient(...)``);
* a string that names an API path (it starts with a top-level contract segment such as
  ``compute/``) and matches no contract path.

Standard library only: python scripts/check_contract_calls.py
"""

import ast
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PACKAGE = ROOT / "src" / "ibee"
CONTRACT = ROOT / "contract" / "ibee-cloud.yaml"
#: Attributes of a generated client that are not operations.
CLIENT_ATTRIBUTES = {"with_raw_response"}


def read_contract():
    text = CONTRACT.read_text()
    paths = text.split("\npaths:\n", 1)[1].split("\ncomponents:\n", 1)[0]
    templates = [p.strip("/").split("/") for p in re.findall(r"^  (/\S*):\s*$", paths, re.M)]
    operations = {op.lower() for op in re.findall(r"^\s+operationId:\s*(\S+)\s*$", paths, re.M)}
    return templates, operations


TEMPLATES, OPERATIONS = read_contract()
TOP_SEGMENTS = {t[0] for t in TEMPLATES}


def is_operation(name: str) -> bool:
    return name.replace("_", "").lower() in OPERATIONS


def path_matches(segments, template) -> bool:
    return len(segments) == len(template) and all(
        s == "{}" or t.startswith("{") or s == t for s, t in zip(segments, template)
    )


def api_path(value: str):
    """The path segments when ``value`` names an API path, else None."""
    if re.search(r"\s", value) or "/" not in value:
        return None
    value = re.sub(r"^(https?://[^/]+)?/?(v1/)?", "", value).strip("/")
    segments = value.split("/")
    return segments if segments[0] in TOP_SEGMENTS else None


def string_value(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):  # f"compute/cloud-vms/{vm_id}" -> "compute/cloud-vms/{}"
        return "".join(v.value if isinstance(v, ast.Constant) else "{}" for v in node.values)
    return None


def hand_files():
    for line in (PACKAGE / ".fernignore").read_text().splitlines():
        line = line.strip()
        if line.endswith(".py") and not line.startswith("#"):
            yield PACKAGE / line


def check(path: pathlib.Path):
    tree = ast.parse(path.read_text(), str(path))
    rel = path.relative_to(ROOT)
    problems = []

    def flag(node, name, why="is not a contract operation"):
        if not name.startswith("_") and name not in CLIENT_ATTRIBUTES and not is_operation(name):
            problems.append(f"{rel}:{node.lineno}: {name} {why}")

    # Generated client classes imported here (from .<resource>.client).
    generated = {
        alias.asname or alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[-1] == "client"
        for alias in node.names
        if alias.name.endswith("Client")
    }
    classes = {node.name: node for node in tree.body if isinstance(node, ast.ClassDef)}

    def on_generated(cls, seen=()):
        bases = [b.id for b in cls.bases if isinstance(b, ast.Name)]
        return any(b in generated or (b in classes and b not in seen and on_generated(classes[b], seen + (b,))) for b in bases)

    def own_names(cls, seen=()):
        names = {n.name for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
        for b in cls.bases:
            if isinstance(b, ast.Name) and b.id in classes and b.id not in seen:
                names |= own_names(classes[b.id], seen + (b.id,))
        return names

    for cls in classes.values():
        if not on_generated(cls):
            continue
        local = own_names(cls)  # methods the hand layer defines itself
        for node in cls.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                flag(node, node.name, "overrides no contract operation")
        for node in ast.walk(cls):
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Call):
                func = node.value.func
                if isinstance(func, ast.Name) and func.id == "super":
                    flag(node, node.attr)
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "self":
                if node.attr not in local:
                    flag(node, node.attr)

    def is_client(node):
        return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in generated

    for function in ast.walk(tree):
        if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        bound = {  # names bound to SomeClient(...) in this function
            t.id
            for node in ast.walk(function)
            if isinstance(node, ast.Assign) and is_client(node.value)
            for t in node.targets
            if isinstance(t, ast.Name)
        }
        for node in ast.walk(function):
            if isinstance(node, ast.Attribute) and (
                is_client(node.value) or (isinstance(node.value, ast.Name) and node.value.id in bound)
            ):
                flag(node, node.attr)

    for node in ast.walk(tree):
        value = string_value(node)
        segments = api_path(value) if value is not None else None
        if segments and not any(path_matches(segments, t) for t in TEMPLATES):
            problems.append(f"{rel}:{node.lineno}: '{value}' is not a contract path")
    return problems


def main() -> int:
    problems = [problem for path in hand_files() for problem in check(path)]
    for problem in sorted(set(problems)):
        print(problem, file=sys.stderr)
    if problems:
        print("Hand-written code calls outside contract/ibee-cloud.yaml.", file=sys.stderr)
        return 1
    print(f"Hand-written code calls only contract operations and paths ({len(OPERATIONS)} operations, {len(TEMPLATES)} paths).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
