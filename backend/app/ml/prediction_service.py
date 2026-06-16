"""ML prediction service for regression and classification."""

from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

from app.schemas.dataset import PredictionRequest


def _prepare_features(
    df: pd.DataFrame, target: str, feature_cols: Optional[List[str]]
) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
    work = df.dropna(subset=[target]).copy()
    if target not in work.columns:
        raise ValueError(f"Target column '{target}' not found")

    if feature_cols:
        features = [c for c in feature_cols if c in work.columns and c != target]
    else:
        features = [c for c in work.columns if c != target]

    if not features:
        raise ValueError("No feature columns available")

    X = work[features].copy()
    y = work[target]

    for col in X.columns:
        if X[col].dtype == "object" or str(X[col].dtype) == "category":
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
        X[col] = pd.to_numeric(X[col], errors="coerce")

    X = X.fillna(X.mean(numeric_only=True))
    X = X.fillna(0)

    return X, y, features


def run_prediction(df: pd.DataFrame, req: PredictionRequest) -> Dict[str, Any]:
    X, y, features = _prepare_features(df, req.target_column, req.feature_columns)

    is_classification = req.task_type == "classification"
    if not is_classification:
        y = pd.to_numeric(y, errors="coerce")
        mask = ~y.isna()
        X, y = X[mask], y[mask]
    else:
        le = LabelEncoder()
        y = le.fit_transform(y.astype(str))

    if len(X) < 20:
        raise ValueError("Need at least 20 valid rows for training")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y if is_classification and len(np.unique(y)) > 1 else None
    )

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    model_type = req.model_type
    feature_importance: Optional[Dict[str, float]] = None

    if is_classification:
        if model_type in ("logistic", "auto"):
            model = LogisticRegression(max_iter=1000, random_state=42)
            model_type = "logistic_regression"
        else:
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model_type = "random_forest_classifier"
        model.fit(X_train_s, y_train)
        y_pred = model.predict(X_test_s)
        metrics = {
            "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
            "precision": round(float(precision_score(y_test, y_pred, average="weighted", zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, y_pred, average="weighted", zero_division=0)), 4),
            "f1_score": round(float(f1_score(y_test, y_pred, average="weighted", zero_division=0)), 4),
        }
        if hasattr(model, "feature_importances_"):
            imp = model.feature_importances_
            feature_importance = {f: round(float(v), 4) for f, v in zip(features, imp)}
        elif hasattr(model, "coef_"):
            imp = np.abs(model.coef_).mean(axis=0)
            feature_importance = {f: round(float(v), 4) for f, v in zip(features, imp)}
        message = f"Classification model trained on '{req.target_column}' with {metrics['accuracy']*100:.1f}% accuracy"
    else:
        if model_type in ("linear", "auto"):
            model = LinearRegression()
            model_type = "linear_regression"
        else:
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model_type = "random_forest_regressor"
        model.fit(X_train_s, y_train)
        y_pred = model.predict(X_test_s)
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        mae = float(mean_absolute_error(y_test, y_pred))
        metrics = {"rmse": round(rmse, 4), "mae": round(mae, 4)}
        if hasattr(model, "feature_importances_"):
            feature_importance = {
                f: round(float(v), 4) for f, v in zip(features, model.feature_importances_)
            }
        elif hasattr(model, "coef_"):
            feature_importance = {f: round(float(abs(c)), 4) for f, c in zip(features, model.coef_)}
        message = f"Regression model trained on '{req.target_column}' — RMSE: {metrics['rmse']}"

    return {
        "task_type": req.task_type,
        "model_type": model_type,
        "target_column": req.target_column,
        "feature_columns": features,
        "metrics": metrics,
        "train_size": len(X_train),
        "test_size": len(X_test),
        "feature_importance": feature_importance,
        "message": message,
    }
