import { useEffect, useState } from 'react';
import { datasetService } from '../services/datasetService';
import type { Dataset, PredictionResult } from '../types';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';

const PRESETS = [
  { label: 'Sales Prediction', task: 'regression', target: 'sales', model: 'auto' },
  { label: 'Revenue Forecasting', task: 'regression', target: 'revenue', model: 'auto' },
  { label: 'Customer Churn', task: 'classification', target: 'churn', model: 'auto' },
  { label: 'Category Prediction', task: 'classification', target: 'category', model: 'auto' },
];

export function Predictions() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [columns, setColumns] = useState<string[]>([]);
  const [taskType, setTaskType] = useState('regression');
  const [targetCol, setTargetCol] = useState('');
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    datasetService.list().then((res) => {
      setDatasets(res.data.datasets);
      if (res.data.datasets[0]) setSelectedId(res.data.datasets[0].id);
    });
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    datasetService.getAnalysis(selectedId).then((res) => {
      setColumns(res.data.column_names);
      const numeric = res.data.column_names.filter((c) =>
        res.data.dtypes[c]?.includes('int') || res.data.dtypes[c]?.includes('float')
      );
      setTargetCol(numeric[0] || res.data.column_names[0] || '');
    });
  }, [selectedId]);

  const runPrediction = async (target?: string, task?: string) => {
    if (!selectedId) return;
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const { data } = await datasetService.predict(selectedId, {
        task_type: task || taskType,
        target_column: target || targetCol,
        model_type: 'auto',
      });
      setResult(data);
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(detail || 'Prediction failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">ML Predictions</h1>

      <Card title="Quick Presets">
        <div className="flex flex-wrap gap-2">
          {PRESETS.map((p) => (
            <Button
              key={p.label}
              variant="secondary"
              size="sm"
              onClick={() => {
                setTaskType(p.task);
                if (columns.includes(p.target)) {
                  setTargetCol(p.target);
                  runPrediction(p.target, p.task);
                }
              }}
            >
              {p.label}
            </Button>
          ))}
        </div>
      </Card>

      <Card>
        <div className="grid gap-4 sm:grid-cols-3">
          <div>
            <label className="text-sm font-medium">Dataset</label>
            <select
              value={selectedId ?? ''}
              onChange={(e) => setSelectedId(Number(e.target.value))}
              className="mt-1 w-full rounded-lg border px-3 py-2 dark:border-gray-600 dark:bg-gray-700"
            >
              {datasets.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
            </select>
          </div>
          <div>
            <label className="text-sm font-medium">Task Type</label>
            <select value={taskType} onChange={(e) => setTaskType(e.target.value)} className="mt-1 w-full rounded-lg border px-3 py-2 dark:border-gray-600 dark:bg-gray-700">
              <option value="regression">Regression</option>
              <option value="classification">Classification</option>
            </select>
          </div>
          <div>
            <label className="text-sm font-medium">Target Column</label>
            <select value={targetCol} onChange={(e) => setTargetCol(e.target.value)} className="mt-1 w-full rounded-lg border px-3 py-2 dark:border-gray-600 dark:bg-gray-700">
              {columns.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
        </div>
        {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
        <Button className="mt-4" onClick={() => runPrediction()} loading={loading}>
          Train Model
        </Button>
      </Card>

      {result && (
        <Card title="Results">
          <p className="mb-4 text-gray-600 dark:text-gray-400">{result.message}</p>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {Object.entries(result.metrics).map(([k, v]) => (
              <div key={k} className="rounded-lg bg-gray-50 p-4 dark:bg-gray-700">
                <p className="text-xs uppercase text-gray-500">{k}</p>
                <p className="text-xl font-bold">{typeof v === 'number' ? v.toFixed(4) : v}</p>
              </div>
            ))}
          </div>
          <p className="mt-4 text-sm text-gray-500">
            Train: {result.train_size} | Test: {result.test_size} | Model: {result.model_type}
          </p>
          {result.feature_importance && (
            <div className="mt-4">
              <h4 className="font-medium mb-2">Feature Importance</h4>
              {Object.entries(result.feature_importance)
                .sort(([, a], [, b]) => b - a)
                .map(([f, v]) => (
                  <div key={f} className="flex items-center gap-2 mb-1">
                    <span className="w-32 text-sm truncate">{f}</span>
                    <div className="flex-1 h-2 bg-gray-200 rounded dark:bg-gray-600">
                      <div className="h-2 bg-primary-600 rounded" style={{ width: `${v * 100}%` }} />
                    </div>
                  </div>
                ))}
            </div>
          )}
        </Card>
      )}
    </div>
  );
}
