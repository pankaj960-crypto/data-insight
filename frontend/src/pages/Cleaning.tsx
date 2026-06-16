import { useEffect, useState } from 'react';
import { datasetService } from '../services/datasetService';
import type { Dataset } from '../types';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';

type Operation = { type: string; [key: string]: unknown };

export function Cleaning() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [operations, setOperations] = useState<Operation[]>([]);
  const [preview, setPreview] = useState<{
    before_rows: number;
    after_rows: number;
    preview_before: Record<string, string>[];
    preview_after: Record<string, string>[];
  } | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    datasetService.list().then((res) => {
      setDatasets(res.data.datasets);
      if (res.data.datasets[0]) setSelectedId(res.data.datasets[0].id);
    });
  }, []);

  const addOp = (type: string, extra: Record<string, unknown> = {}) => {
    setOperations((ops) => [...ops, { type, ...extra }]);
  };

  const runPreview = async () => {
    if (!selectedId || !operations.length) return;
    setLoading(true);
    try {
      const { data } = await datasetService.cleanPreview(selectedId, operations);
      setPreview(data as typeof preview);
    } finally {
      setLoading(false);
    }
  };

  const applyCleaning = async () => {
    if (!selectedId) return;
    setLoading(true);
    try {
      await datasetService.cleanApply(selectedId, operations);
      alert('Cleaning applied successfully!');
      setPreview(null);
      setOperations([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Data Cleaning</h1>
      <Card>
        <select
          value={selectedId ?? ''}
          onChange={(e) => setSelectedId(Number(e.target.value))}
          className="w-full rounded-lg border px-3 py-2 dark:border-gray-600 dark:bg-gray-700"
        >
          {datasets.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
        </select>
        <div className="mt-4 flex flex-wrap gap-2">
          <Button variant="secondary" size="sm" onClick={() => addOp('remove_duplicates')}>Remove Duplicates</Button>
          <Button variant="secondary" size="sm" onClick={() => addOp('drop_null_rows')}>Drop Null Rows</Button>
          <Button variant="secondary" size="sm" onClick={() => addOp('fill_missing', { strategy: 'mean' })}>Fill Missing (Mean)</Button>
          <Button variant="secondary" size="sm" onClick={() => addOp('fill_missing', { strategy: 'mode' })}>Fill Missing (Mode)</Button>
        </div>
        {operations.length > 0 && (
          <ul className="mt-4 text-sm text-gray-600 dark:text-gray-400">
            {operations.map((op, i) => (
              <li key={i}>• {op.type}</li>
            ))}
          </ul>
        )}
        <div className="mt-4 flex gap-2">
          <Button onClick={runPreview} loading={loading} disabled={!operations.length}>Preview</Button>
          <Button variant="primary" onClick={applyCleaning} loading={loading} disabled={!preview}>Apply Changes</Button>
        </div>
      </Card>

      {preview && (
        <div className="grid gap-6 lg:grid-cols-2">
          <Card title={`Before (${preview.before_rows} rows)`}>
            <pre className="overflow-auto text-xs">{JSON.stringify(preview.preview_before?.slice(0, 5), null, 2)}</pre>
          </Card>
          <Card title={`After (${preview.after_rows} rows)`}>
            <pre className="overflow-auto text-xs">{JSON.stringify(preview.preview_after?.slice(0, 5), null, 2)}</pre>
          </Card>
        </div>
      )}
    </div>
  );
}
