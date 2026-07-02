# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pandas>=2.0.0",
#     "numpy>=1.24.0",
#     "scipy>=1.10.0",
# ]
# ///

"""
Data Quality Validation Script.

Validates CSV, JSON, or Excel datasets and produces a structured quality report.
Checks for missing values, outliers, type consistency, duplicates, and basic
statistical properties. Run without arguments for full help.

Usage:
    python validate_dataset.py <filepath> [options]

Arguments:
    filepath              Path to CSV, JSON, or Excel file.
    --sheet SHEET         Excel sheet name or index (default: 0).
    --outlier-method METHOD  Outlier detection: 'iqr' (default) or 'zscore'.
    --outlier-threshold N  Threshold for outlier detection (default: 1.5 for IQR, 3 for Z-score).
    --missing-threshold N  Flag columns with >N% missing (default: 20).
    --sample N             Use a random sample of N rows for large files.
    --json                Output report as JSON instead of text.

Examples:
    python validate_dataset.py sales.csv
    python validate_dataset.py users.json
    python validate_dataset.py report.xlsx --sheet "Q4 Data"
    python validate_dataset.py big_file.csv --sample 10000 --outlier-method zscore
    python validate_dataset.py data.csv --json > report.json
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd


def load_dataset(filepath: str, sheet=None, sample: int = None) -> pd.DataFrame:
    """Load a dataset from CSV, JSON, or Excel, with optional sampling."""
    path = Path(filepath)
    suffix = path.suffix.lower()

    if suffix == ".csv":
        # Try common encodings and delimiters
        for enc in ["utf-8", "latin-1", "utf-16", "cp1252"]:
            try:
                # Sniff delimiter from first few KB
                with open(path, "r", encoding=enc) as f:
                    first_bytes = f.read(4096)
                try:
                    import csv as csv_mod
                    dialect = csv_mod.Sniffer().sniff(first_bytes)
                    delimiter = dialect.delimiter
                except Exception:
                    delimiter = ","
                df = pd.read_csv(path, encoding=enc, delimiter=delimiter, low_memory=False)
                break
            except (UnicodeDecodeError, Exception):
                continue
        else:
            raise ValueError(f"Could not read CSV with any common encoding: {filepath}")

    elif suffix == ".json":
        df = pd.read_json(path)
        # Flatten nested structures if needed
        for col in df.columns:
            if df[col].dtype == "object" and isinstance(df[col].dropna().iloc[0] if not df[col].dropna().empty else None, (dict, list)):
                try:
                    nested = pd.json_normalize(df[col].dropna().iloc)
                    if not nested.empty:
                        flattened = pd.json_normalize(df[col].tolist())
                        # Add as new columns with prefix, drop original
                        for fcol in flattened.columns:
                            df[f"{col}_{fcol}"] = flattened[fcol].values
                        df = df.drop(columns=[col])
                except Exception:
                    pass  # Keep as-is if normalization fails

    elif suffix in (".xlsx", ".xls"):
        xls = pd.ExcelFile(path, engine="openpyxl")
        available = xls.sheet_names
        if sheet is None:
            sheet = 0
        if isinstance(sheet, str) and sheet not in available:
            print(f"Error: Sheet '{sheet}' not found. Available: {available}")
            sys.exit(1)
        df = pd.read_excel(path, sheet_name=sheet, engine="openpyxl")
    else:
        raise ValueError(f"Unsupported file format: {suffix}. Supported: .csv, .json, .xlsx, .xls")

    if sample and len(df) > sample:
        df = df.sample(n=sample, random_state=42)

    return df


def check_missing(df: pd.DataFrame, missing_threshold: float) -> dict:
    """Analyze missing values per column."""
    total_rows = len(df)
    missing = df.isnull().sum()
    missing_pct = (missing / total_rows * 100).round(2)

    columns_above_threshold = missing_pct[missing_pct > missing_threshold].to_dict()
    columns_any_missing = missing_pct[missing_pct > 0].to_dict()

    total_missing_cells = int(missing.sum())
    total_missing_pct = round(total_missing_cells / (total_rows * len(df.columns)) * 100, 2)
    rows_with_missing = int((df.isnull().any(axis=1)).sum())
    rows_missing_pct = round(rows_with_missing / total_rows * 100, 2)

    return {
        "total_cells": total_rows * len(df.columns),
        "total_missing_cells": total_missing_cells,
        "total_missing_pct": total_missing_pct,
        "rows_with_missing": rows_with_missing,
        "rows_with_missing_pct": rows_missing_pct,
        "columns_with_any_missing": columns_any_missing,
        "columns_above_threshold": columns_above_threshold,
        "threshold_used": missing_threshold,
    }


def check_outliers(df: pd.DataFrame, method: str, threshold: float) -> dict:
    """Detect outliers in numeric columns using IQR or Z-score method."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    outlier_report = {}

    for col in numeric_cols:
        col_data = df[col].dropna()
        if len(col_data) < 4:
            continue

        if method == "iqr":
            Q1 = col_data.quantile(0.25)
            Q3 = col_data.quantile(0.75)
            IQR = Q3 - Q1
            if IQR == 0:
                continue
            lower = Q1 - threshold * IQR
            upper = Q3 + threshold * IQR
            outliers = ((df[col] < lower) | (df[col] > upper)).sum()
        elif method == "zscore":
            from scipy import stats
            z_scores = np.abs(stats.zscore(col_data, nan_policy="omit"))
            outliers = int((z_scores > threshold).sum())
            lower, upper = None, None
        else:
            raise ValueError(f"Unknown outlier method: {method}")

        if outliers > 0:
            outlier_report[col] = {
                "outlier_count": int(outliers),
                "outlier_pct": round(outliers / len(df) * 100, 2),
                "lower_bound": round(float(lower), 4) if lower is not None else None,
                "upper_bound": round(float(upper), 4) if upper is not None else None,
            }

    total_outlier_rows = 0
    if outlier_report:
        outlier_mask = pd.Series(False, index=df.index)
        for col in outlier_report:
            col_data = df[col].dropna()
            if method == "iqr" and len(col_data) >= 4:
                Q1, Q3 = col_data.quantile(0.25), col_data.quantile(0.75)
                IQR = Q3 - Q1
                if IQR > 0:
                    lower = Q1 - threshold * IQR
                    upper = Q3 + threshold * IQR
                    outlier_mask |= (df[col] < lower) | (df[col] > upper)
        total_outlier_rows = int(outlier_mask.sum())

    return {
        "method": method,
        "threshold": threshold,
        "columns_with_outliers": len(outlier_report),
        "outlier_details": outlier_report,
        "rows_affected": total_outlier_rows,
        "rows_affected_pct": round(total_outlier_rows / len(df) * 100, 2) if len(df) > 0 else 0,
        "total_rows": len(df),
    }


def check_types(df: pd.DataFrame) -> dict:
    """Check for type consistency issues."""
    type_issues = []
    type_summary = {}

    for col in df.columns:
        dtype = str(df[col].dtype)
        type_summary[col] = dtype

        # Check for mixed types in object columns
        if df[col].dtype == "object":
            non_null = df[col].dropna()
            if non_null.empty:
                continue
            # Check if column looks numeric
            numeric_convertible = 0
            for val in non_null.head(min(1000, len(non_null))):
                try:
                    float(str(val).replace(",", "").replace("$", "").replace("€", "").strip())
                    numeric_convertible += 1
                except (ValueError, TypeError):
                    pass
            if numeric_convertible > 0:
                ratio = numeric_convertible / min(1000, len(non_null))
                if ratio > 0.8:
                    type_issues.append({
                        "column": col,
                        "issue": "appears_numeric",
                        "detail": f"Column is object dtype but {ratio:.0%} of sampled values look numeric. Consider pd.to_numeric().",
                    })
                elif ratio > 0.1:
                    type_issues.append({
                        "column": col,
                        "issue": "mixed_types",
                        "detail": f"Column has mixed content: {ratio:.0%} numeric-like values detected.",
                    })

            # Check if column looks like dates
            date_like = 0
            for val in non_null.head(min(100, len(non_null))):
                try:
                    pd.to_datetime(str(val))
                    date_like += 1
                except Exception:
                    pass
            if date_like > 0 and date_like / min(100, len(non_null)) > 0.5:
                type_issues.append({
                    "column": col,
                    "issue": "appears_datetime",
                    "detail": f"Column contains date-like strings. Consider pd.to_datetime().",
                })

    return {
        "column_types": type_summary,
        "type_issues": type_issues,
        "issues_count": len(type_issues),
    }


def check_duplicates(df: pd.DataFrame) -> dict:
    """Check for duplicate rows and duplicate values in key columns."""
    exact_dupes = int(df.duplicated().sum())
    exact_dupes_pct = round(exact_dupes / len(df) * 100, 2)

    # Check for near-duplicates (potential ID columns)
    potential_id_cols = []
    for col in df.columns:
        if df[col].dtype in ("int64", "float64") and df[col].nunique() > len(df) * 0.5:
            continue
        uniqueness = df[col].nunique() / len(df)
        if uniqueness > 0.98:
            potential_id_cols.append({
                "column": col,
                "uniqueness_ratio": round(uniqueness, 4),
                "note": "Near-unique — may be an identifier column.",
            })

    return {
        "exact_duplicates": exact_dupes,
        "exact_duplicates_pct": exact_dupes_pct,
        "potential_id_columns": potential_id_cols,
    }


def basic_statistics(df: pd.DataFrame) -> dict:
    """Compute basic statistical summary for numeric columns."""
    numeric_df = df.select_dtypes(include=[np.number])

    stats_report = {}
    for col in numeric_df.columns:
        col_data = numeric_df[col].dropna()
        if len(col_data) == 0:
            continue
        stats_report[col] = {
            "count": int(len(col_data)),
            "mean": round(float(col_data.mean()), 4),
            "std": round(float(col_data.std()), 4),
            "min": round(float(col_data.min()), 4),
            "p25": round(float(col_data.quantile(0.25)), 4),
            "p50": round(float(col_data.quantile(0.50)), 4),
            "p75": round(float(col_data.quantile(0.75)), 4),
            "max": round(float(col_data.max()), 4),
            "skewness": round(float(col_data.skew()), 4),
            "kurtosis": round(float(col_data.kurtosis()), 4),
            "zeros_count": int((col_data == 0).sum()),
            "zeros_pct": round((col_data == 0).sum() / len(col_data) * 100, 2),
            "negative_count": int((col_data < 0).sum()),
        }

    # Column-level flags
    flags = []
    for col, s in stats_report.items():
        if s.get("zeros_pct", 0) > 50:
            flags.append(f"Column '{col}': {s['zeros_pct']}% of values are zero — verify data integrity.")
        if s.get("negative_count", 0) > 0:
            # Only flag if column name suggests it shouldn't be negative
            col_lower = col.lower()
            if any(kw in col_lower for kw in ["count", "age", "quantity", "price", "revenue", "volume"]):
                flags.append(f"Column '{col}': contains {s['negative_count']} negative values — may be unexpected.")
        if abs(s.get("skewness", 0)) > 2:
            flags.append(f"Column '{col}': highly skewed (skewness={s['skewness']}) — consider transformation for modeling.")

    return {
        "numeric_columns": len(stats_report),
        "column_statistics": stats_report,
        "flags": flags,
    }


def generate_quality_score(
    missing: dict,
    outliers: dict,
    duplicates: dict,
    type_info: dict,
    stats_info: dict,
) -> tuple:
    """Generate an overall quality score from 0–100 and a grade."""
    score = 100.0

    # Deduct for missing values
    missing_pct = missing["total_missing_pct"]
    score -= min(missing_pct * 1.5, 30)

    # Deduct for duplicates
    dup_pct = duplicates["exact_duplicates_pct"]
    score -= min(dup_pct * 2, 20)

    # Deduct for type issues
    score -= min(type_info["issues_count"] * 5, 15)

    # Deduct for outlier-affected rows
    outlier_pct = outliers.get("rows_affected_pct", 0)
    score -= min(outlier_pct * 0.5, 15)

    score = max(0, min(100, round(score, 1)))

    if score >= 90:
        grade = "A — Excellent"
    elif score >= 75:
        grade = "B — Good"
    elif score >= 60:
        grade = "C — Fair"
    elif score >= 40:
        grade = "D — Poor"
    else:
        grade = "F — Critical Issues"

    return score, grade


def format_report(report: dict) -> str:
    """Format the report as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("  DATA QUALITY REPORT")
    lines.append("=" * 60)
    lines.append(f"  File:         {report['file']}")
    lines.append(f"  Format:       {report['format']}")
    lines.append(f"  Generated:    {report['generated_at']}")
    lines.append(f"  Rows:         {report['shape']['rows']:,}")
    lines.append(f"  Columns:      {report['shape']['columns']}")
    lines.append(f"  Quality:      {report['quality_score']}/100 ({report['quality_grade']})")
    lines.append("")

    # Missing values
    m = report["missing_values"]
    lines.append("-" * 60)
    lines.append("  MISSING VALUES")
    lines.append("-" * 60)
    lines.append(f"  Missing cells:      {m['total_missing_cells']:,} ({m['total_missing_pct']}%)")
    lines.append(f"  Rows with missing:  {m['rows_with_missing']:,} ({m['rows_with_missing_pct']}%)")
    if m["columns_with_any_missing"]:
        lines.append(f"  Columns with missing values:")
        for col, pct in sorted(m["columns_with_any_missing"].items(), key=lambda x: -x[1]):
            flag = " ⚠️ " if pct > m["threshold_used"] else ""
            lines.append(f"    {col}: {pct}%{flag}")
    else:
        lines.append("  ✅ No missing values detected.")
    lines.append("")

    # Outliers
    o = report["outliers"]
    lines.append("-" * 60)
    lines.append("  OUTLIERS  (method: {method}, threshold: {threshold})".format(**o))
    lines.append("-" * 60)
    if o["columns_with_outliers"] > 0:
        lines.append(f"  Columns with outliers: {o['columns_with_outliers']}")
        lines.append(f"  Rows affected: {o['rows_affected']:,} ({o['rows_affected_pct']}%)")
        for col, detail in sorted(o["outlier_details"].items(), key=lambda x: -x[1]["outlier_pct"]):
            bounds = ""
            if detail.get("lower_bound") is not None:
                bounds = f" [range: {detail['lower_bound']} – {detail['upper_bound']}]"
            lines.append(f"    {col}: {detail['outlier_count']} outliers ({detail['outlier_pct']}%){bounds}")
    else:
        lines.append("  ✅ No significant outliers detected.")
    lines.append("")

    # Type issues
    t = report["type_issues"]
    lines.append("-" * 60)
    lines.append("  TYPE ISSUES")
    lines.append("-" * 60)
    if t["issues_count"] > 0:
        lines.append(f"  Issues found: {t['issues_count']}")
        for issue in t["type_issues"]:
            lines.append(f"    [{issue['issue']}] {issue['column']}: {issue['detail']}")
    else:
        lines.append("  ✅ No type issues detected.")
    lines.append("")

    # Duplicates
    d = report["duplicates"]
    lines.append("-" * 60)
    lines.append("  DUPLICATES")
    lines.append("-" * 60)
    lines.append(f"  Exact duplicate rows: {d['exact_duplicates']:,} ({d['exact_duplicates_pct']}%)")
    if d["potential_id_columns"]:
        lines.append("  Potential identifier columns:")
        for id_col in d["potential_id_columns"]:
            lines.append(f"    {id_col['column']}: {id_col['uniqueness_ratio']:.2%} unique — {id_col['note']}")
    if d["exact_duplicates"] == 0 and not d["potential_id_columns"]:
        lines.append("  ✅ No duplicates or identifier columns detected.")
    lines.append("")

    # Statistics
    s = report["statistics"]
    lines.append("-" * 60)
    lines.append("  NUMERIC COLUMN STATISTICS  ({n} columns)".format(n=s["numeric_columns"]))
    lines.append("-" * 60)
    if s["numeric_columns"] > 0:
        for col, stats_data in sorted(s["column_statistics"].items()):
            lines.append(f"  {col}:")
            lines.append(f"    count={stats_data['count']:,}  mean={stats_data['mean']}  std={stats_data['std']}")
            lines.append(f"    min={stats_data['min']}  p25={stats_data['p25']}  p50={stats_data['p50']}  p75={stats_data['p75']}  max={stats_data['max']}")
            lines.append(f"    skewness={stats_data['skewness']}  kurtosis={stats_data['kurtosis']}")
            if stats_data['zeros_pct'] > 0:
                lines.append(f"    zero values: {stats_data['zeros_count']:,} ({stats_data['zeros_pct']}%)")
    else:
        lines.append("  No numeric columns found.")
    if s["flags"]:
        lines.append("")
        lines.append("  ⚠️  Flags:")
        for flag in s["flags"]:
            lines.append(f"    - {flag}")
    lines.append("")

    # Column types
    lines.append("-" * 60)
    lines.append("  COLUMN TYPES")
    lines.append("-" * 60)
    for col, dtype in sorted(report["type_issues"]["column_types"].items()):
        lines.append(f"  {col}: {dtype}")

    lines.append("")
    lines.append("=" * 60)
    lines.append("  END OF REPORT")
    lines.append("=" * 60)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Data Quality Validation Script — analyzes CSV, JSON, and Excel datasets.",
        epilog="Example: python validate_dataset.py sales.csv --outlier-method iqr",
    )
    parser.add_argument("filepath", help="Path to CSV, JSON, or Excel file")
    parser.add_argument("--sheet", default=None, help="Excel sheet name or index (default: first sheet)")
    parser.add_argument("--outlier-method", default="iqr", choices=["iqr", "zscore"], help="Outlier detection method")
    parser.add_argument("--outlier-threshold", type=float, default=None, help="Outlier threshold (default: 1.5 IQR, 3 zscore)")
    parser.add_argument("--missing-threshold", type=float, default=20.0, help="Flag columns with >N%% missing (default: 20)")
    parser.add_argument("--sample", type=int, default=None, help="Random sample size for large files")
    parser.add_argument("--json", action="store_true", help="Output report as JSON")
    args = parser.parse_args()

    if not Path(args.filepath).exists():
        print(f"Error: File not found: {args.filepath}", file=sys.stderr)
        sys.exit(1)

    # Set default thresholds
    if args.outlier_threshold is None:
        args.outlier_threshold = 3.0 if args.outlier_method == "zscore" else 1.5

    # Load data
    print(f"Loading {args.filepath}...", file=sys.stderr)
    df = load_dataset(args.filepath, sheet=args.sheet, sample=args.sample)
    print(f"Loaded {len(df):,} rows × {len(df.columns)} columns", file=sys.stderr)

    # Run checks
    missing_info = check_missing(df, args.missing_threshold)
    outlier_info = check_outliers(df, args.outlier_method, args.outlier_threshold)
    type_info = check_types(df)
    duplicate_info = check_duplicates(df)
    stats_info = basic_statistics(df)

    quality_score, quality_grade = generate_quality_score(
        missing_info, outlier_info, duplicate_info, type_info, stats_info
    )

    report = {
        "file": str(Path(args.filepath).resolve()),
        "format": Path(args.filepath).suffix.lower(),
        "generated_at": datetime.now().isoformat(),
        "sample_used": args.sample if args.sample else None,
        "shape": {"rows": len(df), "columns": len(df.columns)},
        "quality_score": quality_score,
        "quality_grade": quality_grade,
        "missing_values": missing_info,
        "outliers": outlier_info,
        "type_issues": type_info,
        "duplicates": duplicate_info,
        "statistics": stats_info,
    }

    if args.json:
        print(json.dumps(report, indent=2, default=str))
    else:
        print(format_report(report))


if __name__ == "__main__":
    main()