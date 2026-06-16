"""Automatic data analysis and insight generation."""

from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


def _safe_json(obj: Any) -> Any:
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        val = float(obj)
        return None if np.isnan(val) else val
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: _safe_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_safe_json(v) for v in obj]
    if isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
        return None
    return obj


def compute_data_quality_score(df: pd.DataFrame) -> float:
    if df.empty:
        return 0.0
    total_cells = df.shape[0] * df.shape[1]
    missing_ratio = df.isnull().sum().sum() / max(total_cells, 1)
    dup_ratio = df.duplicated().sum() / max(len(df), 1)
    score = max(0.0, 100.0 * (1.0 - 0.6 * missing_ratio - 0.4 * dup_ratio))
    return round(float(score), 2)


def generate_insights(df: pd.DataFrame) -> List[str]:
    insights: List[str] = []
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if numeric_cols:
        means = df[numeric_cols].mean()
        max_col = means.idxmax()
        min_col = means.idxmin()
        insights.append(
            f"Highest average value column: '{max_col}' (mean: {means[max_col]:.2f})"
        )
        insights.append(
            f"Lowest average value column: '{min_col}' (mean: {means[min_col]:.2f})"
        )

        for col in numeric_cols[:5]:
            q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
            iqr = q3 - q1
            if iqr > 0:
                outliers = ((df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)).sum()
                if outliers > 0:
                    insights.append(f"Column '{col}' has {int(outliers)} potential outliers (IQR method)")

        if len(numeric_cols) >= 2:
            trend_col = numeric_cols[0]
            if len(df) >= 3:
                values = df[trend_col].dropna().values
                if len(values) >= 3:
                    slope = np.polyfit(range(len(values)), values, 1)[0]
                    direction = "upward" if slope > 0 else "downward" if slope < 0 else "flat"
                    insights.append(f"Trend in '{trend_col}' appears {direction} over row order")

    missing_total = int(df.isnull().sum().sum())
    if missing_total > 0:
        pct = 100 * missing_total / max(df.size, 1)
        insights.append(f"Data quality: {missing_total} missing values ({pct:.1f}% of cells)")
    else:
        insights.append("Data quality: no missing values detected")

    dup = int(df.duplicated().sum())
    if dup > 0:
        insights.append(f"Found {dup} duplicate rows — consider removing them")
    else:
        insights.append("No duplicate rows detected")

    cat_cols = df.select_dtypes(include=["object", "category"]).columns
    if len(cat_cols) > 0:
        col = cat_cols[0]
        top = df[col].value_counts().head(1)
        if len(top) > 0:
            insights.append(f"Top category in '{col}': '{top.index[0]}' ({int(top.iloc[0])} records)")

    return insights[:12]


def analyze_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    numeric_df = df.select_dtypes(include=[np.number])
    summary: Dict[str, Any] = {}
    if not numeric_df.empty:
        desc = numeric_df.describe().round(4)
        summary = _safe_json(desc.to_dict())

    correlation: Optional[Dict[str, Dict[str, float]]] = None
    if numeric_df.shape[1] >= 2:
        corr = numeric_df.corr().round(4)
        correlation = _safe_json(corr.to_dict())

    quality = compute_data_quality_score(df)
    insights = generate_insights(df)

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_values": {col: int(df[col].isnull().sum()) for col in df.columns},
        "duplicate_count": int(df.duplicated().sum()),
        "statistical_summary": summary,
        "correlation_matrix": correlation,
        "insights": insights,
        "data_quality_score": quality,
    }


def get_analysis_response(dataset_id: int, df: pd.DataFrame) -> Tuple[Dict[str, Any], float, List[str]]:
    result = analyze_dataframe(df)
    result["dataset_id"] = dataset_id
    return result, result["data_quality_score"], result["insights"]
