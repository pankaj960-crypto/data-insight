import { useEffect, useState } from 'react';
import { Download, FileText } from 'lucide-react';
import api from '../services/api';
import { datasetService } from '../services/datasetService';
import type { Dataset } from '../types';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';

const FORMATS = [
  { id: 'pdf', label: 'PDF Report' },
  { id: 'excel', label: 'Excel Workbook' },
  { id: 'word', label: 'Word Document' },
  { id: 'csv', label: 'CSV Export' },
];

export function Reports() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [reports, setReports] = useState<{ id: number; title: string; report_type: string; created_at: string; download_url: string }[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    datasetService.list().then((res) => {
      setDatasets(res.data.datasets);
      if (res.data.datasets[0]) setSelectedId(res.data.datasets[0].id);
    });
    loadReports();
  }, []);

  const loadReports = () => {
    api.get('/reports').then((res) => setReports(res.data));
  };

  const exportReport = async (format: string) => {
    if (!selectedId) return;
    setLoading(true);
    try {
      const { data } = await datasetService.exportReport(selectedId, format);
      const baseUrl = import.meta.env.VITE_API_URL?.replace('/api/v1', '') || 'http://localhost:8000';
      window.open(`${baseUrl}${data.download_url}`, '_blank');
      loadReports();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Export Reports</h1>
      <Card>
        <label className="text-sm font-medium">Select Dataset</label>
        <select
          value={selectedId ?? ''}
          onChange={(e) => setSelectedId(Number(e.target.value))}
          className="mt-1 w-full rounded-lg border px-3 py-2 dark:border-gray-600 dark:bg-gray-700"
        >
          {datasets.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
        </select>
        <div className="mt-6 grid gap-3 sm:grid-cols-2">
          {FORMATS.map((f) => (
            <Button key={f.id} variant="secondary" onClick={() => exportReport(f.id)} loading={loading}>
              <FileText className="mr-2 h-4 w-4" /> {f.label}
            </Button>
          ))}
        </div>
      </Card>

      <Card title="Generated Reports">
        {reports.length === 0 ? (
          <p className="text-gray-500">No reports generated yet.</p>
        ) : (
          <ul className="space-y-2">
            {reports.map((r) => (
              <li key={r.id} className="flex items-center justify-between rounded-lg p-3 hover:bg-gray-50 dark:hover:bg-gray-700">
                <span>{r.title} ({r.report_type})</span>
                <a
                  href={`${import.meta.env.VITE_API_URL?.replace('/api/v1', '') || 'http://localhost:8000'}${r.download_url}`}
                  className="text-primary-600 hover:underline flex items-center gap-1"
                >
                  <Download className="h-4 w-4" /> Download
                </a>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}
