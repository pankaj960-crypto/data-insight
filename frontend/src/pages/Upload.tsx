import { useCallback, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileSpreadsheet, Upload as UploadIcon } from 'lucide-react';
import { datasetService } from '../services/datasetService';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';

export function Upload() {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [name, setName] = useState('');
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) setFile(f);
  }, []);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError('');
    try {
      const { data } = await datasetService.upload(file, name || undefined);
      navigate(`/datasets/${data.id}`);
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(detail || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Upload Dataset</h1>
      <Card>
        <div
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          className={`rounded-xl border-2 border-dashed p-12 text-center transition ${
            dragging ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' : 'border-gray-300 dark:border-gray-600'
          }`}
        >
          <FileSpreadsheet className="mx-auto h-12 w-12 text-primary-600" />
          <p className="mt-4 font-medium text-gray-900 dark:text-white">
            Drag & drop or click to upload
          </p>
          <p className="mt-1 text-sm text-gray-500">CSV, Excel (.xlsx), JSON — max 50MB</p>
          <input
            type="file"
            accept=".csv,.xlsx,.json"
            className="mt-4"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
          {file && (
            <p className="mt-2 text-sm text-primary-600">
              Selected: {file.name} ({(file.size / 1024).toFixed(1)} KB)
            </p>
          )}
        </div>
        <div className="mt-4">
          <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Dataset Name (optional)
          </label>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-4 py-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
            placeholder="My Sales Data"
          />
        </div>
        {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
        <Button className="mt-4 w-full" onClick={handleUpload} loading={loading} disabled={!file}>
          <UploadIcon className="mr-2 h-4 w-4" /> Upload & Analyze
        </Button>
      </Card>
    </div>
  );
}
