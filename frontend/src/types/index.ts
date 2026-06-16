export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Dataset {
  id: number;
  name: string;
  original_filename: string;
  file_type: string;
  file_size: number;
  row_count: number;
  column_count: number;
  data_quality_score: number | null;
  status: string;
  created_at: string;
}

export interface Analysis {
  dataset_id: number;
  rows: number;
  columns: number;
  column_names: string[];
  dtypes: Record<string, string>;
  missing_values: Record<string, number>;
  duplicate_count: number;
  statistical_summary: Record<string, Record<string, number>>;
  correlation_matrix: Record<string, Record<string, number>> | null;
  insights: string[];
  data_quality_score: number;
}

export interface ChartRequest {
  chart_type: string;
  x_column?: string;
  y_column?: string;
  color_column?: string;
  filter_column?: string;
  filter_value?: string;
  sort_by?: string;
  sort_order?: string;
  limit?: number;
}

export interface PredictionResult {
  task_type: string;
  model_type: string;
  target_column: string;
  feature_columns: string[];
  metrics: Record<string, number>;
  train_size: number;
  test_size: number;
  feature_importance: Record<string, number> | null;
  message: string;
}

export interface DashboardData {
  kpis: { label: string; value: string | number; change: string; trend: string }[];
  recent_uploads: {
    id: number;
    name: string;
    rows: number;
    columns: number;
    quality_score: number | null;
    created_at: string;
  }[];
  recent_reports: { id: number; title: string; type: string; created_at: string }[];
  ai_recommendations: string[];
  stats: { total_datasets: number; total_rows: number; total_storage: number };
}
