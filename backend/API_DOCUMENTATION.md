# DataInsight AI — API Documentation

Base URL: `http://localhost:8000/api/v1`

Interactive docs: `/api/docs` (Swagger) | `/api/redoc` (ReDoc)

## Authentication

All protected endpoints require header:
```
Authorization: Bearer <access_token>
```

### Register
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass1",
  "full_name": "John Doe"
}
```

### Login
```http
POST /auth/login

{ "email": "user@example.com", "password": "SecurePass1" }
```

Response:
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

## Datasets

### Upload
```http
POST /datasets/upload
Content-Type: multipart/form-data

file: <binary>
name: "Sales Q1 2024" (optional)
```

### Analysis
```http
GET /datasets/{id}/analysis?refresh=false
```

Returns rows, columns, dtypes, missing values, duplicates, statistical summary, correlation matrix, insights, and data quality score.

## Charts

```http
POST /charts/{dataset_id}

{
  "chart_type": "bar",
  "x_column": "category",
  "y_column": "sales",
  "limit": 100
}
```

Chart types: `bar`, `line`, `pie`, `scatter`, `histogram`, `heatmap`

## AI Chat

```http
POST /chat/{dataset_id}

{
  "message": "What are the top-selling products?",
  "history": [{"role": "user", "content": "..."}]
}
```

## Predictions

```http
POST /predictions/{dataset_id}

{
  "task_type": "regression",
  "target_column": "sales",
  "model_type": "auto"
}
```

Metrics:
- Regression: `rmse`, `mae`
- Classification: `accuracy`, `precision`, `recall`, `f1_score`

## Data Cleaning

```http
POST /cleaning/{dataset_id}/preview
{ "operations": [{"type": "remove_duplicates"}] }

POST /cleaning/{dataset_id}/apply
{ "operations": [...], "apply": true }
```

Operation types: `remove_duplicates`, `drop_null_rows`, `fill_missing`, `rename_column`, `convert_dtype`, `drop_columns`

## Reports

```http
POST /reports/{dataset_id}/export?format=pdf&title=My Report
GET /reports/download/{report_id}
```

Formats: `pdf`, `excel`, `word`, `csv`

## Dashboard

```http
GET /dashboard
```

## Admin (requires `is_admin`)

```http
GET /admin/stats
GET /admin/users
DELETE /admin/datasets/{id}
DELETE /admin/reports/{id}
```

## Error Responses

```json
{ "detail": "Error message" }
```

Status codes: 400, 401, 403, 404, 413, 422, 500
