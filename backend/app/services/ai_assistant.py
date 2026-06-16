"""Rule-based AI data assistant (analyzes dataset context in plain English)."""

import re
from typing import List, Optional

import numpy as np
import pandas as pd


SUGGESTIONS = [
    "Summarize this dataset",
    "What are the top values?",
    "Show revenue trends",
    "Which category performs best?",
    "Find anomalies",
    "What is the data quality score?",
]


def _top_products(df: pd.DataFrame) -> Optional[str]:
    cat_cols = df.select_dtypes(include=["object", "category"]).columns
    num_cols = df.select_dtypes(include=[np.number]).columns
    if len(cat_cols) == 0:
        return None
    product_col = None
    for c in cat_cols:
        if any(k in c.lower() for k in ("product", "item", "name", "category")):
            product_col = c
            break
    product_col = product_col or cat_cols[0]
    if len(num_cols) > 0:
        sales_col = num_cols[0]
        for c in num_cols:
            if any(k in c.lower() for k in ("sales", "revenue", "amount", "quantity", "price")):
                sales_col = c
                break
        grouped = df.groupby(product_col)[sales_col].sum().sort_values(ascending=False).head(5)
        lines = [f"  • {idx}: {val:,.2f}" for idx, val in grouped.items()]
        return f"Top performers by '{sales_col}':\n" + "\n".join(lines)
    top = df[product_col].value_counts().head(5)
    lines = [f"  • {idx}: {cnt} records" for idx, cnt in top.items()]
    return f"Most frequent in '{product_col}':\n" + "\n".join(lines)


def _revenue_trends(df: pd.DataFrame) -> Optional[str]:
    num_cols = df.select_dtypes(include=[np.number]).columns
    rev_col = None
    for c in num_cols:
        if any(k in c.lower() for k in ("revenue", "sales", "amount", "profit")):
            rev_col = c
            break
    if rev_col is None and len(num_cols) > 0:
        rev_col = num_cols[0]
    if rev_col is None:
        return None
    values = df[rev_col].dropna()
    if len(values) < 3:
        return f"Not enough data to analyze trends in '{rev_col}'."
    slope = np.polyfit(range(len(values)), values.values, 1)[0]
    total = values.sum()
    avg = values.mean()
    direction = "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
    return (
        f"Revenue trend analysis for '{rev_col}':\n"
        f"  • Total: {total:,.2f}\n"
        f"  • Average: {avg:,.2f}\n"
        f"  • Trend direction: {direction} (slope: {slope:.4f})"
    )


def _best_category(df: pd.DataFrame) -> Optional[str]:
    cat_cols = df.select_dtypes(include=["object", "category"]).columns
    num_cols = df.select_dtypes(include=[np.number]).columns
    if len(cat_cols) == 0:
        return None
    cat_col = cat_cols[0]
    for c in cat_cols:
        if "category" in c.lower():
            cat_col = c
            break
    if len(num_cols) == 0:
        top = df[cat_col].value_counts().head(1)
        return f"Most common category in '{cat_col}': {top.index[0]} ({int(top.iloc[0])} records)"
    metric = num_cols[0]
    for c in num_cols:
        if any(k in c.lower() for k in ("sales", "revenue", "score", "amount")):
            metric = c
            break
    best = df.groupby(cat_col)[metric].sum().sort_values(ascending=False).head(3)
    lines = [f"  • {idx}: {val:,.2f}" for idx, val in best.items()]
    return f"Best performing categories by '{metric}':\n" + "\n".join(lines)


def _find_anomalies(df: pd.DataFrame) -> str:
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()[:5]
    if not num_cols:
        return "No numeric columns found for anomaly detection."
    findings = []
    for col in num_cols:
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        if iqr <= 0:
            continue
        count = int(((df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)).sum())
        if count > 0:
            findings.append(f"  • '{col}': {count} outliers detected")
    return "Anomaly scan (IQR method):\n" + ("\n".join(findings) if findings else "  • No significant outliers detected")


def _summarize(df: pd.DataFrame, quality_score: Optional[float]) -> str:
    missing = int(df.isnull().sum().sum())
    dup = int(df.duplicated().sum())
    num_cols = len(df.select_dtypes(include=[np.number]).columns)
    cat_cols = len(df.select_dtypes(include=["object", "category"]).columns)
    q = f"{quality_score:.1f}/100" if quality_score else "N/A"
    return (
        f"Dataset Summary:\n"
        f"  • Rows: {len(df):,} | Columns: {len(df.columns)}\n"
        f"  • Numeric columns: {num_cols} | Categorical: {cat_cols}\n"
        f"  • Missing values: {missing} | Duplicates: {dup}\n"
        f"  • Data quality score: {q}"
    )


def process_chat_message(
    message: str,
    df: pd.DataFrame,
    insights: Optional[List[str]] = None,
    quality_score: Optional[float] = None,
) -> tuple[str, List[str]]:
    msg = message.lower().strip()

    if re.search(r"summarize|summary|overview|describe", msg):
        reply = _summarize(df, quality_score)
    elif re.search(r"top.?sell|top product|best.?sell|highest.?sell", msg):
        reply = _top_products(df) or "Could not identify product/sales columns. Try specifying column names."
    elif re.search(r"revenue|trend|forecast|sales trend", msg):
        reply = _revenue_trends(df) or "Could not identify revenue/sales columns for trend analysis."
    elif re.search(r"category|segment|perform|best", msg):
        reply = _best_category(df) or "Could not analyze categories in this dataset."
    elif re.search(r"anomal|outlier|unusual|abnormal|fraud", msg):
        reply = _find_anomalies(df)
    elif re.search(r"quality|missing|duplicate|clean", msg):
        reply = _summarize(df, quality_score)
        if insights:
            reply += "\n\nKey insights:\n" + "\n".join(f"  • {i}" for i in insights[:5])
    elif re.search(r"insight|recommend", msg):
        if insights:
            reply = "AI Recommendations:\n" + "\n".join(f"  • {i}" for i in insights)
        else:
            reply = _summarize(df, quality_score)
    elif re.search(r"column|field|feature", msg):
        cols = ", ".join(df.columns.tolist()[:20])
        reply = f"Dataset has {len(df.columns)} columns: {cols}"
        if len(df.columns) > 20:
            reply += f" ... and {len(df.columns) - 20} more"
    else:
        reply = (
            "I analyzed your dataset. Here's a quick overview:\n\n"
            + _summarize(df, quality_score)
            + "\n\nTry asking about: top products, revenue trends, categories, anomalies, or insights."
        )

    return reply, SUGGESTIONS
