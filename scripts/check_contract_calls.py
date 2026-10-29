#!/usr/bin/env python3
"""Check B: the hand-written files add no calls or wrappers to the generated client.

The SDK is the generated client: every operation is the generated method, sent as the
caller passes it. The hand-written files (the .py files listed in src/ibee/.fernignore:
configuration, transport and error fields) may not

* import a generated resource client (``from .<resource>.client`` or
  ``.raw_client``), so they cannot wrap, override or call an operation;
* name an API path (a string that starts with a top-level contract segment such as
  ``compute/``) that matches no path of contract/ibee-cloud.yaml.

The generated code is covered by check A (scripts/check_generated.sh).

Standard library only: python scripts/check_contract_calls.py
"""

import ast
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PACKAGE = ROOT / "src" / "ibee"
CONTRACT = ROOT / "contract" / "ibee-cloud.yaml"
#: Generated modules that hold the operations of one resource.
RESOURCE_CLIENT = re.compile(r"(^|\.)[a-z0-9_]+\.(raw_)?client$")


def read_contract():
    text = CONTRACT.read_text()
    paths = text.split("\npaths:\n", 1)[1].split("\ncomponents:\n", 1)[0]
    templates = [p.strip("/").split("/") for p in re.findall(r"^  (/\S*):\s*$", paths, re.M)]
    operations = {op for op in re.findall(r"^\s+operationId:\s*(\S+)\s*$", paths, re.M)}
    return templates, operations


TEMPLATES, OPERATIONS = read_contract()
TOP_SEGMENTS = {t[0] for t in TEMPLATES}


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
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and RESOURCE_CLIENT.search(node.module or ""):
            problems.append(f"{rel}:{node.lineno}: imports the generated client '{node.module}'")
        value = string_value(node)
        segments = api_path(value) if value is not None else None
        if segments and not any(path_matches(segments, t) for t in TEMPLATES):
            problems.append(f"{rel}:{node.lineno}: '{value}' is not a contract path")
    return problems


def main() -> int:
    files = list(hand_files())
    problems = [problem for path in files for problem in check(path)]
    for problem in sorted(set(problems)):
        print(problem, file=sys.stderr)
    if problems:
        print("Hand-written code adds calls outside the generated client.", file=sys.stderr)
        return 1
    print(
        f"{len(files)} hand-written files wrap no operation and name only contract paths "
        f"({len(OPERATIONS)} operations, {len(TEMPLATES)} paths)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
