import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Database, Trash2 } from 'lucide-react';
import { datasetService } from '../services/datasetService';
import type { Dataset } from '../types';
import { Card } from '../components/ui/Card';
import { CardSkeleton } from '../components/ui/Skeleton';

export function Datasets() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    datasetService
      .list()
      .then((res) => setDatasets(res.data.datasets))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this dataset?')) return;
    await datasetService.delete(id);
    load();
  };

  if (loading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => <CardSkeleton key={i} />)}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">My Datasets</h1>
      {datasets.length === 0 ? (
        <Card>
          <p className="text-center text-gray-500">No datasets yet.</p>
          <Link to="/upload" className="mt-4 block text-center text-primary-600 hover:underline">
            Upload your first dataset
          </Link>
        </Card>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {datasets.map((d) => (
            <Card key={d.id} className="!p-0">
              <div className="p-6">
                <div className="flex items-start justify-between">
                  <Database className="h-8 w-8 text-primary-600" />
                  <button onClick={() => handleDelete(d.id)} className="text-red-500 hover:text-red-700">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
                <Link to={`/datasets/${d.id}`}>
                  <h3 className="mt-3 font-semibold text-gray-900 hover:text-primary-600 dark:text-white">
                    {d.name}
                  </h3>
                </Link>
                <p className="mt-1 text-sm text-gray-500">
                  {d.row_count} rows · {d.column_count} cols · {d.file_type.toUpperCase()}
                </p>
                {d.data_quality_score != null && (
                  <div className="mt-3">
                    <div className="flex justify-between text-xs">
                      <span>Quality</span>
                      <span>{d.data_quality_score.toFixed(0)}%</span>
                    </div>
                    <div className="mt-1 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
                      <div
                        className="h-2 rounded-full bg-primary-600"
                        style={{ width: `${d.data_quality_score}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
