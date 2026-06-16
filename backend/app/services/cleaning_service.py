"""Data cleaning operations with preview support."""

from typing import Any, Dict, List, Tuple

import pandas as pd


def apply_operations(df: pd.DataFrame, operations: List[Dict[str, Any]]) -> pd.DataFrame:
    result = df.copy()
    for op in operations:
        op_type = op.get("type")
        if op_type == "remove_duplicates":
            result = result.drop_duplicates()
        elif op_type == "drop_null_rows":
            result = result.dropna(how="any")
        elif op_type == "fill_missing":
            strategy = op.get("strategy", "mean")
            columns = op.get("columns") or result.columns.tolist()
            for col in columns:
                if col not in result.columns:
                    continue
                if strategy == "mean" and pd.api.types.is_numeric_dtype(result[col]):
                    result[col] = result[col].fillna(result[col].mean())
                elif strategy == "median" and pd.api.types.is_numeric_dtype(result[col]):
                    result[col] = result[col].fillna(result[col].median())
                elif strategy == "mode":
                    mode = result[col].mode()
                    if len(mode) > 0:
                        result[col] = result[col].fillna(mode.iloc[0])
                elif strategy in ("ffill", "forward"):
                    result[col] = result[col].ffill()
                elif strategy == "value":
                    result[col] = result[col].fillna(op.get("value", ""))
        elif op_type == "rename_column":
            old_name = op.get("old_name")
            new_name = op.get("new_name")
            if old_name and new_name and old_name in result.columns:
                result = result.rename(columns={old_name: new_name})
        elif op_type == "convert_dtype":
            col = op.get("column")
            dtype = op.get("dtype")
            if col in result.columns and dtype:
                if dtype == "numeric":
                    result[col] = pd.to_numeric(result[col], errors="coerce")
                elif dtype == "string":
                    result[col] = result[col].astype(str)
                elif dtype == "datetime":
                    result[col] = pd.to_datetime(result[col], errors="coerce")
                elif dtype == "category":
                    result[col] = result[col].astype("category")
        elif op_type == "drop_columns":
            cols = op.get("columns", [])
            result = result.drop(columns=[c for c in cols if c in result.columns], errors="ignore")
    return result


def preview_cleaning(df: pd.DataFrame, operations: List[Dict[str, Any]], rows: int = 10) -> Dict[str, Any]:
    cleaned = apply_operations(df, operations)
    return {
        "before_rows": len(df),
        "after_rows": len(cleaned),
        "before_columns": len(df.columns),
        "after_columns": len(cleaned.columns),
        "preview_before": df.head(rows).fillna("").astype(str).to_dict(orient="records"),
        "preview_after": cleaned.head(rows).fillna("").astype(str).to_dict(orient="records"),
        "changes_summary": {
            "rows_removed": len(df) - len(cleaned),
            "duplicates_removed": int(df.duplicated().sum()) if any(o.get("type") == "remove_duplicates" for o in operations) else 0,
        },
    }
