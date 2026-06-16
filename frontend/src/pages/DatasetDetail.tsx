import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { datasetService } from '../services/datasetService';
import type { Analysis, Dataset } from '../types';
import { Card } from '../components/ui/Card';
import { CardSkeleton } from '../components/ui/Skeleton';

export function DatasetDetail() {
  const { id } = useParams<{ id: string }>();
  const [dataset, setDataset] = useState<Dataset | null>(null);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    const dsId = parseInt(id);
    Promise.all([
      datasetService.get(dsId),
      datasetService.getAnalysis(dsId),
    ])
      .then(([ds, an]) => {
        setDataset(ds.data);
        setAnalysis(an.data);
      })
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <CardSkeleton />;
  if (!dataset || !analysis) return <p>Dataset not found</p>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{dataset.name}</h1>
        <p className="text-gray-500">{dataset.original_filename}</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: 'Rows', value: analysis.rows },
          { label: 'Columns', value: analysis.columns },
          { label: 'Duplicates', value: analysis.duplicate_count },
          { label: 'Quality Score', value: `${analysis.data_quality_score}%` },
        ].map((s) => (
          <Card key={s.label}>
            <p className="text-sm text-gray-500">{s.label}</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">{s.value}</p>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Column Info">
          <div className="max-h-64 overflow-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500">
                  <th className="pb-2">Column</th>
                  <th>Type</th>
                  <th>Missing</th>
                </tr>
              </thead>
              <tbody>
                {analysis.column_names.map((col) => (
                  <tr key={col} className="border-t border-gray-100 dark:border-gray-700">
                    <td className="py-2 font-medium">{col}</td>
                    <td>{analysis.dtypes[col]}</td>
                    <td>{analysis.missing_values[col] || 0}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        <Card title="AI Insights">
          <ul className="space-y-2">
            {analysis.insights.map((ins, i) => (
              <li key={i} className="text-sm text-gray-600 dark:text-gray-400">
                • {ins}
              </li>
            ))}
          </ul>
        </Card>
      </div>

      {analysis.correlation_matrix && (
        <Card title="Correlation Matrix">
          <div className="overflow-x-auto text-xs">
            <table className="w-full">
              <thead>
                <tr>
                  <th></th>
                  {Object.keys(analysis.correlation_matrix).map((c) => (
                    <th key={c} className="p-1">{c}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {Object.entries(analysis.correlation_matrix).map(([row, vals]) => (
                  <tr key={row}>
                    <td className="p-1 font-medium">{row}</td>
                    {Object.values(vals).map((v, i) => (
                      <td key={i} className="p-1 text-center">{typeof v === 'number' ? v.toFixed(2) : v}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}
