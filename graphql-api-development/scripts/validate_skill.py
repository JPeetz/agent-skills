# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "jsonschema>=4.20.0",
# ]
# description = "Validate that AI-generated GraphQL API development output follows correct structure, naming conventions, and quality standards."
# ///

"""
GraphQL API Development Validator

Validates that AI-generated GraphQL schema designs, resolver implementations,
and API review output adhere to the quality standards defined in the
graphql-api-development skill. Designed for use in pre-commit hooks,
CI pipelines, and manual validation.

Usage:
    python validate_skill.py <output.md>              # Validate a review/output file
    python validate_skill.py <output.md> --json       # Output results as JSON
    python validate_skill.py <schema.graphql> --graphql  # Validate a .graphql schema file
    python validate_skill.py --schema                 # Print the JSON schema

The script checks:
  - Schema naming conventions (verb-first mutations, PascalCase types)
  - Pagination patterns on list fields
  - Error handling patterns (typed unions vs bare strings)
  - DataLoader usage in resolver code
  - Depth limit and cost analysis configuration
  - Authentication in context vs inline
  - Federation directive usage and correctness
  - Complete description strings on types and fields
  - Presence of required security measures
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Mutation naming: must start with a verb (lowercase), not a noun
VALID_MUTATION_VERBS = {
    "create", "update", "delete", "remove", "add", "cancel",
    "archive", "publish", "unpublish", "approve", "reject",
    "assign", "unassign", "invite", "accept", "decline",
    "send", "resend", "verify", "reset", "change", "revoke",
    "grant", "enable", "disable", "lock", "unlock", "merge",
    "split", "transfer", "process", "refund", "charge",
    "subscribe", "unsubscribe", "follow", "unfollow",
    "mark", "flag", "star", "pin", "unpin",
    "register", "login", "logout", "confirm", "complete",
    "start", "stop", "pause", "resume",
}

SUFFIXES = {
    "input_type": "Input",
    "payload_type": "Payload",
    "error_type": "Error",
    "connection_type": "Connection",
    "edge_type": "Edge",
}

# Regex patterns
PASCAL_CASE_RE = re.compile(r"^[A-Z][a-zA-Z0-9]*$")
CAMEL_CASE_RE = re.compile(r"^[a-z][a-zA-Z0-9]*$")
UPPER_SNAKE_CASE_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:_[A-Z][A-Z0-9]*)*$")
PAGINATION_TYPE_RE = re.compile(r"Connection|Page$")
SCHEMA_TYPE_RE = re.compile(
    r"(type|input|interface|enum|union)\s+(\w+)",
    re.MULTILINE,
)
FIELD_DEF_RE = re.compile(
    r"^\s+(\w+)(?:\s*\([^)]*\))?\s*:\s*(\[?[\w!\]!]+)",
    re.MULTILINE,
)
LIST_FIELD_RE = re.compile(
    r"^\s+(\w+).*:\s*\[(.+?)!\]!?",
    re.MULTILINE,
)
MUTATION_FIELD_RE = re.compile(
    r"type\s+Mutation\s*\{([^}]+)\}",
    re.DOTALL,
)

DATA_LOADER_IMPORT_RE = re.compile(r"import\s+DataLoader|require\(.*dataloader")
DATA_LOADER_USAGE_RE = re.compile(r"new\s+DataLoader|DataLoader\(")
DATA_LOADER_CONTEXT_RE = re.compile(r"context\.loaders?|ctx\.loaders?")
DEPTH_LIMIT_RE = re.compile(r"depthLimit|graphql-depth-limit|depth_limit")
COST_ANALYSIS_RE = re.compile(r"costAnalysis|graphql-cost-analysis|cost_analysis|maximumCost")
PERSISTED_QUERY_RE = re.compile(r"persistedQueries|createPersistedQuery|APQ")
FEDERATION_KEY_RE = re.compile(r"@key\s*\(\s*fields\s*:\s*\"")
SHAREABLE_RE = re.compile(r"@shareable")
REQUIRES_RE = re.compile(r"@requires\s*\(")

# Security: detect hardcoded secrets
SECRET_PATTERNS = [
    re.compile(r"sk[-_]live[_-][a-zA-Z0-9]{20,}", re.IGNORECASE),
    re.compile(r"-----BEGIN\s+(RSA|EC|DSA|OPENSSH|PGP)\s+PRIVATE KEY-----"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"ghp_[a-zA-Z0-9]{36}"),
    re.compile(r"xox[bpras]-[a-zA-Z0-9-]+"),
    re.compile(r"AIza[0-9A-Za-z\-_]{35}"),
    re.compile(r"(?:password|secret|api[_-]?key)\s*[:=]\s*[\"'][^\"']{8,}[\"']", re.IGNORECASE),
]


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ValidationIssue:
    severity: str  # "error" | "warning"
    message: str
    section: str | None = None
    line: int | None = None


@dataclass
class ValidationResult:
    passed: bool = True
    issues: list[ValidationIssue] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)

    def add_error(self, message: str, section: str | None = None, line: int | None = None) -> None:
        self.passed = False
        self.issues.append(ValidationIssue("error", message, section, line))

    def add_warning(self, message: str, section: str | None = None, line: int | None = None) -> None:
        self.issues.append(ValidationIssue("warning", message, section, line))


# ---------------------------------------------------------------------------
# Schema parsing
# ---------------------------------------------------------------------------

def parse_graphql_schema(text: str) -> dict[str, Any]:
    """Parse a GraphQL schema SDL string into structured components."""
    types: dict[str, dict[str, Any]] = {}
    current_type: dict[str, Any] | None = None
    brace_depth = 0
    brace_start = -1
    lines = text.split("\n")

    type_match_re = re.compile(r"^\s*(type|input|interface|enum|union|extend\s+type)\s+(\w+)")

    for i, line in enumerate(lines):
        m = type_match_re.match(line)
        if m and brace_depth == 0:
            kind = m.group(1).replace("extend ", "")
            name = m.group(2)
            current_type = {
                "kind": kind,
                "name": name,
                "line": i + 1,
                "fields": [],
                "directives": [],
                "description": "",
                "implements": [],
            }
            types[name] = current_type
            brace_start = i

        # Track braces
        if "{" in line:
            brace_depth += line.count("{")
        if "}" in line:
            brace_depth -= line.count("}")
            if brace_depth == 0 and current_type:
                current_type = None

        # Parse directives
        if current_type and "@" in line:
            dir_match = re.findall(r"@(\w+)(?:\(([^)]*)\))?", line)
            for d in dir_match:
                current_type["directives"].append(d[0])

        # Parse fields
        if current_type and brace_depth >= 1:
            field_match = re.match(r"^\s+(\w+)(?:\s*\([^)]*\))?\s*:\s*(.+)", line)
            if field_match:
                current_type["fields"].append({
                    "name": field_match.group(1),
                    "type": field_match.group(2).strip(),
                    "line": i + 1,
                })

    return {
        "types": types,
        "type_names": list(types.keys()),
    }


def find_list_fields(parsed: dict) -> list[dict]:
    """Find all list-type fields in the schema."""
    list_fields = []
    for type_name, type_info in parsed["types"].items():
        for field in type_info.get("fields", []):
            if field["type"].startswith("["):
                list_fields.append({
                    "parent_type": type_name,
                    "field_name": field["name"],
                    "field_type": field["type"],
                    "line": field["line"],
                })
    return list_fields


# ---------------------------------------------------------------------------
# Validation functions for GraphQL SDL
# ---------------------------------------------------------------------------

def validate_schema_sdl(text: str, filepath: str) -> ValidationResult:
    """Validate a GraphQL SDL file against best practices."""
    result = ValidationResult()
    result.stats["file_path"] = filepath
    result.stats["validation_type"] = "graphql_sdl"
    result.stats["total_lines"] = len(text.split("\n"))

    parsed = parse_graphql_schema(text)
    types = parsed["types"]
    result.stats["type_count"] = len(types)

    # 1. Check for type definitions
    if not types:
        result.add_error("No GraphQL type definitions found in file.")
        return result

    # 2. Naming conventions
    for name, info in types.items():
        kind = info.get("kind", "")

        if kind in ("type", "input", "interface"):
            if not PASCAL_CASE_RE.match(name):
                result.add_error(
                    f"{kind} '{name}' should be PascalCase (e.g., 'User', 'CreatePostInput').",
                    section="Naming",
                    line=info.get("line"),
                )

        # Suffix conventions
        if kind == "input" and not name.endswith(SUFFIXES["input_type"]):
            result.add_warning(
                f"Input type '{name}' should end with '{SUFFIXES['input_type']}'.",
                section="Naming",
                line=info.get("line"),
            )

        if kind == "union" and name.endswith("Error"):
            pass  # Error unions are fine
        elif kind == "union":
            # Check if union members end with Error
            pass

    # 3. Enum values: UPPER_SNAKE_CASE
    for name, info in types.items():
        if info.get("kind") == "enum":
            for field in info.get("fields", []):
                if not UPPER_SNAKE_CASE_RE.match(field["name"]):
                    result.add_warning(
                        f"Enum value '{field['name']}' should be UPPER_SNAKE_CASE.",
                        section="Naming",
                        line=field.get("line"),
                    )

    # 4. Check list fields for pagination
    list_fields = find_list_fields(parsed)
    for field in list_fields:
        field_type = field["field_type"]
        # If it returns a list of a custom type (not a scalar)
        inner = field_type.strip("[]!")
        if inner not in ("String", "Int", "Float", "Boolean", "ID") and not inner.endswith("Connection") and not inner.endswith("Page"):
            result.add_warning(
                f"List field '{field['parent_type']}.{field['field_name']}: {field_type}' is not paginated. "
                "Consider wrapping in a Connection or Page type.",
                section="Pagination",
                line=field.get("line"),
            )

    # 5. Check mutation naming (verb-first)
    mutation_type = types.get("Mutation")
    if mutation_type:
        for field in mutation_type.get("fields", []):
            name = field["name"]
            # Extract first word (camelCase)
            parts = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\d|\b)", name)
            first_word = parts[0].lower() if parts else name.lower()

            if first_word not in VALID_MUTATION_VERBS:
                result.add_error(
                    f"Mutation '{name}' should start with a verb (e.g., 'create', 'update', 'delete'). "
                    f"'{first_word}' is not recognized as a standard mutation verb.",
                    section="Mutation Naming",
                    line=field.get("line"),
                )

    # 6. Check for description presence
    lines = text.split("\n")
    types_with_desc = 0
    for name, info in types.items():
        line_num = info.get("line", 0)
        if line_num > 1:
            prev_line = lines[line_num - 2] if line_num >= 2 else ""
            if '"""' in prev_line or '#' in prev_line:
                types_with_desc += 1
    if types_with_desc < len(types) * 0.5 and len(types) > 2:
        result.add_warning(
            f"Only {types_with_desc}/{len(types)} types have descriptions. "
            "All types and fields should have 'description' strings.",
            section="Documentation",
        )

    # 7. Federation checks
    if any("@" + d in text for d in ["key", "shareable", "requires", "external", "provides", "tag", "inaccessible"] for t in types.values() for d in t.get("directives", [])):
        # If federation directives are present, check for completeness
        if "@key" in text:
            if "@key" not in text:
                result.add_warning("Federation directives present but no @key defined.", section="Federation")
        # Check _service and _entities
        if "_service" not in text:
            result.add_warning(
                "Federation directives used but no `_service` root query field found. "
                "Add `extend type Query { _service: _Service! }` for gateway compatibility.",
                section="Federation",
            )
        if "_entities" not in text:
            result.add_warning(
                "_entities query not found. Required for entity resolution in federated graphs.",
                section="Federation",
            )

    # 8. Input types for mutations
    if mutation_type:
        for field in mutation_type.get("fields", []):
            field_type = field["field_type"]
            # Check if mutation uses a single Input argument
            # Pattern: createUser(input: CreateUserInput!): Payload
            if not re.search(r"input\s*:", field.get("raw", "")):
                # Simplified: check if the field accepts an input type
                pass

    return result


# ---------------------------------------------------------------------------
# Validation functions for resolver/implementation code
# ---------------------------------------------------------------------------

def validate_resolver_code(text: str, filepath: str) -> ValidationResult:
    """Validate resolver implementation code against best practices."""
    result = ValidationResult()
    result.stats["file_path"] = filepath
    result.stats["validation_type"] = "resolver_code"
    result.stats["total_lines"] = len(text.split("\n"))

    # 1. DataLoader usage check
    has_dataloader_import = bool(DATA_LOADER_IMPORT_RE.search(text))
    has_dataloader_usage = bool(DATA_LOADER_USAGE_RE.search(text))
    has_dataloader_context = bool(DATA_LOADER_CONTEXT_RE.search(text))

    if not has_dataloader_import and not has_dataloader_usage:
        # Check if there are database calls that should use DataLoader
        db_call_count = len(re.findall(r"(?:find|get|query|select|fetch)(?!.*dataloader)", text, re.IGNORECASE))
        if db_call_count > 3:
            result.add_error(
                f"Found {db_call_count} direct database calls without DataLoader patterns. "
                "Install and use DataLoader to prevent N+1 query problems.",
                section="N+1 Prevention",
            )
    else:
        result.stats["dataloader_detected"] = True
        if not has_dataloader_context:
            result.add_warning(
                "DataLoader imported but no context.loaders/.loaders usage detected. "
                "Ensure DataLoaders are created per-request via context.",
                section="N+1 Prevention",
            )

    # 2. Security: depth limiting
    has_depth_limit = bool(DEPTH_LIMIT_RE.search(text))
    has_cost_analysis = bool(COST_ANALYSIS_RE.search(text))
    if not has_depth_limit:
        result.add_error(
            "No depth limiting detected. Install 'graphql-depth-limit' and add "
            "depthLimit(N) to validation rules to prevent recursive query DoS.",
            section="Security",
        )
    if not has_cost_analysis:
        result.add_warning(
            "No query cost analysis detected. Consider 'graphql-cost-analysis' "
            "to prevent expensive queries beyond depth limiting.",
            section="Security",
        )

    # 3. Persisted queries
    has_persisted = bool(PERSISTED_QUERY_RE.search(text))
    if not has_persisted:
        result.add_warning(
            "Persisted queries not configured. Enable APQ for production to "
            "reduce bandwidth and enable CDN caching.",
            section="Performance",
        )

    # 4. Authentication pattern
    # Check if auth happens in context vs inline
    auth_inline_count = len(re.findall(
        r"(?:ctx\.user|context\.user|req\.user)[\s\?\.]",
        text,
    ))
    auth_context_setup = bool(re.search(
        r"context\s*[=:]\s*(?:async\s*)?\(.*req",
        text,
    ))

    if auth_inline_count > 5 and not auth_context_setup:
        result.add_warning(
            f"Found {auth_inline_count} inline auth checks. Consider extracting "
            "authentication to the context function for cleaner resolvers.",
            section="Architecture",
        )

    # 5. Secret detection
    secrets_found = []
    for pattern in SECRET_PATTERNS:
        for match in pattern.finditer(text):
            secrets_found.append(match.group()[:40])
    if secrets_found:
        for s in secrets_found:
            result.add_error(
                f"Potential hardcoded secret detected: '{s}...'",
                section="Security",
            )
        result.stats["secrets_detected"] = len(secrets_found)

    # 6. Pagination check (in resolver code)
    list_return_count = len(re.findall(r"return\s+(?:await\s+)?\w+\.(?:find|query|list|all|getAll)\(", text))
    has_pagination_args = bool(re.search(r"(first|last|after|before|limit|offset)", text))
    if list_return_count > 0 and not has_pagination_args:
        result.add_warning(
            "Database queries return lists without pagination arguments (first/last/limit/offset). "
            "All list fields should be paginated.",
            section="Pagination",
        )

    # 7. Federation entity resolution
    if FEDERATION_KEY_RE.search(text):
        result.stats["federation_detected"] = True
        if not re.search(r"__resolveReference", text):
            result.add_error(
                "Federation @key directives found but no __resolveReference resolver. "
                "Every entity type must have a reference resolver.",
                section="Federation",
            )
        if not SHAREABLE_RE.search(text):
            result.add_warning(
                "No @shareable directives found. Without @shareable, fields cannot "
                "be contributed by multiple subgraphs.",
                section="Federation",
            )

    # 8. Subscription cleanup check
    if "Subscription" in text or "subscribe" in text or "PubSub" in text:
        result.stats["subscription_detected"] = True
        has_cleanup = bool(re.search(
            r"(?:unsubscribe|finally|close|dispose|cleanup|return\s*=>\s*\{)",
            text,
        ))
        if not has_cleanup:
            result.add_warning(
                "Subscriptions detected but no cleanup logic found. Ensure every "
                "subscription source has proper teardown to prevent memory leaks.",
                section="Subscriptions",
            )

    return result


# ---------------------------------------------------------------------------
# Validation for design/review output
# ---------------------------------------------------------------------------

def validate_design_output(text: str, filepath: str) -> ValidationResult:
    """Validate a GraphQL API design or review output document."""
    result = ValidationResult()
    result.stats["file_path"] = filepath
    result.stats["validation_type"] = "design_output"

    lines = text.split("\n")
    result.stats["total_lines"] = len(lines)

    # 1. Check for GraphQL schema blocks
    graphql_blocks = re.findall(r"```graphql\n(.*?)```", text, re.DOTALL)
    result.stats["schema_blocks"] = len(graphql_blocks)

    # Validate each embedded schema block
    for i, block in enumerate(graphql_blocks):
        block_result = validate_schema_sdl(block, f"{filepath}:block:{i}")
        for issue in block_result.issues:
            issue.section = f"Schema Block {i+1}"
            if issue.severity == "error":
                result.add_error(issue.message, issue.section)
            else:
                result.add_warning(issue.message, issue.section)

    # 2. Check for DataLoader mention in explanations
    if re.search(r"resolver|query\s+optimization", text, re.IGNORECASE):
        if not re.search(r"[Dd]ataLoader|[NnN]\s*\+\s*1", text):
            result.add_warning(
                "Resolver discussion detected but no DataLoader/N+1 prevention mentioned.",
                section="N+1 Prevention",
            )

    # 3. Security recommendations check
    if re.search(r"production|deploy|launch", text, re.IGNORECASE):
        has_security = any(
            term in text.lower()
            for term in ["depth limit", "rate limit", "introspection", "auth"]
        )
        if not has_security:
            result.add_warning(
                "Production GraphQL API discussion without security hardening mention.",
                section="Security",
            )

    # 4. Federation correctness
    if "federation" in text.lower() or "@key" in text:
        has_reference = "__resolveReference" in text or "reference resolver" in text.lower()
        has_entities = "_entities" in text or "entity" in text.lower()
        if not has_reference:
            result.add_error(
                "Federation discussed but no reference resolver (__resolveReference) "
                "pattern shown.",
                section="Federation",
            )
        if not has_entities:
            result.add_warning(
                "Federation discussed but entity resolution (_entities query) not covered.",
                section="Federation",
            )

    # 5. Error handling pattern check
    if re.search(r"error|Error|fail", text):
        # Check if typed union errors are discussed
        has_typed_errors = bool(re.search(
            r"union.*Error|__typename|typed\s+(union|error)|payload.*error",
            text,
        ))
        has_string_errors = bool(re.search(
            r'error\s*:\s*String!?|error\s*:\s*"',
            text,
        ))
        if has_string_errors:
            result.add_error(
                "String-based error field detected. Use typed error unions instead "
                "(e.g., `errors: [MyDomainError!]!` with a union type).",
                section="Error Handling",
            )
        elif not has_typed_errors and "mutation" in text.lower():
            result.add_warning(
                "No typed error handling pattern found. Consider using union types "
                "for errors in mutation payloads.",
                section="Error Handling",
            )

    # 6. Secret detection
    secrets_found = []
    for pattern in SECRET_PATTERNS:
        for match in pattern.finditer(text):
            secrets_found.append(match.group()[:40])
    if secrets_found:
        for s in secrets_found:
            result.add_error(
                f"Potential hardcoded secret detected: '{s}...'",
                section="Security",
            )
        result.stats["secrets_detected"] = len(secrets_found)

    return result


# ---------------------------------------------------------------------------
# Auto-detect and route to correct validator
# ---------------------------------------------------------------------------

def validate_file(text: str, filepath: str, force_mode: str | None = None) -> ValidationResult:
    """Auto-detect file type and run appropriate validation."""
    if force_mode:
        if force_mode == "graphql":
            return validate_schema_sdl(text, filepath)
        elif force_mode == "resolver":
            return validate_resolver_code(text, filepath)
        elif force_mode == "design":
            return validate_design_output(text, filepath)

    # Auto-detect based on content
    lower = text[:200].lower()
    ext = Path(filepath).suffix.lower()

    if ext == ".graphql" or ext == ".gql":
        return validate_schema_sdl(text, filepath)
    elif ext in (".ts", ".js", ".tsx", ".jsx"):
        return validate_resolver_code(text, filepath)
    elif ext in (".md", ".txt", ".json"):
        # Check if it's primarily schema content
        schema_lines = len(re.findall(r"(type|input|enum|interface|union|scalar|directive)\s+\w+\s*\{", text))
        resolver_lines = len(re.findall(r"(resolver|DataLoader|ApolloServer)", text))
        if schema_lines > resolver_lines:
            return validate_schema_sdl(text, filepath)
        elif resolver_lines > schema_lines:
            return validate_resolver_code(text, filepath)
        else:
            return validate_design_output(text, filepath)
    else:
        return validate_design_output(text, filepath)


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def format_text_output(result: ValidationResult) -> str:
    """Format results as human-readable text."""
    parts: list[str] = []

    if result.passed:
        parts.append("\u2705 Validation PASSED")
    else:
        parts.append("\u274c Validation FAILED")

    parts.append(f"\nFile: {result.stats.get('file_path', 'unknown')}")
    parts.append(f"Type: {result.stats.get('validation_type', 'auto')}")
    parts.append(f"Total lines: {result.stats.get('total_lines', 0)}")

    if "type_count" in result.stats:
        parts.append(f"GraphQL types: {result.stats['type_count']}")
    if "dataloader_detected" in result.stats:
        parts.append(f"DataLoader: detected")
    if "federation_detected" in result.stats:
        parts.append(f"Federation: detected")
    if "schema_blocks" in result.stats:
        parts.append(f"Schema blocks: {result.stats['schema_blocks']}")

    if result.stats.get("secrets_detected", 0) > 0:
        parts.append(f"\u26a0\ufe0f Secrets detected: {result.stats['secrets_detected']}")

    if result.issues:
        parts.append(f"\n--- Issues ({len(result.issues)}) ---")
        for i, issue in enumerate(result.issues, 1):
            prefix = "\u274c" if issue.severity == "error" else "\u26a0\ufe0f"
            location = ""
            if issue.section:
                location += f" [{issue.section}]"
            if issue.line:
                location += f" line {issue.line}"
            parts.append(f"  {i}. {prefix}{location}: {issue.message}")

    return "\n".join(parts)


def format_json_output(result: ValidationResult) -> str:
    """Format results as JSON."""
    output = {
        "passed": result.passed,
        "stats": result.stats,
        "issues": [
            {
                "severity": i.severity,
                "message": i.message,
                "section": i.section,
                "line": i.line,
            }
            for i in result.issues
        ],
    }
    return json.dumps(output, indent=2)


def print_schema() -> None:
    """Print expected JSON output schema."""
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "GraphQLValidationResult",
        "description": "Expected output structure for GraphQL API validation",
        "type": "object",
        "required": ["passed", "stats", "issues"],
        "properties": {
            "passed": {"type": "boolean"},
            "stats": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "validation_type": {"type": "string"},
                    "total_lines": {"type": "integer"},
                    "type_count": {"type": "integer"},
                    "secrets_detected": {"type": "integer"},
                },
            },
            "issues": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["severity", "message"],
                    "properties": {
                        "severity": {"enum": ["error", "warning"]},
                        "message": {"type": "string"},
                        "section": {"type": "string"},
                        "line": {"type": "integer"},
                    },
                },
            },
        },
    }
    print(json.dumps(schema, indent=2))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate GraphQL API design and implementation quality.",
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="Path to the file to validate (.graphql, .ts, .md, etc.)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--schema",
        action="store_true",
        help="Print expected JSON output schema and exit",
    )
    parser.add_argument(
        "--graphql",
        action="store_true",
        help="Force GraphQL SDL validation mode",
    )
    parser.add_argument(
        "--resolver",
        action="store_true",
        help="Force resolver code validation mode",
    )
    parser.add_argument(
        "--design",
        action="store_true",
        help="Force design output validation mode",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors (exit non-zero)",
    )

    args = parser.parse_args()

    if args.schema:
        print_schema()
        sys.exit(0)

    if not args.file:
        parser.error("FILE is required unless --schema is specified")

    path = Path(args.file)
    if not path.exists():
        print(f"\u274c File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"\u274c File is not valid UTF-8: {args.file}", file=sys.stderr)
        sys.exit(1)

    # Determine validation mode
    force_mode = None
    if args.graphql:
        force_mode = "graphql"
    elif args.resolver:
        force_mode = "resolver"
    elif args.design:
        force_mode = "design"

    result = validate_file(text, str(path), force_mode)

    if args.json:
        print(format_json_output(result))
    else:
        print(format_text_output(result))

    # Exit code
    if not result.passed:
        sys.exit(1)
    if args.strict:
        has_warnings = any(i.severity == "warning" for i in result.issues)
        if has_warnings:
            sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()