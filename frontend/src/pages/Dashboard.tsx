import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Database, FileText, Sparkles, TrendingUp, Upload } from 'lucide-react';
import { datasetService } from '../services/datasetService';
import type { DashboardData } from '../types';
import { Card } from '../components/ui/Card';
import { CardSkeleton } from '../components/ui/Skeleton';
import { Button } from '../components/ui/Button';

export function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    datasetService
      .getDashboard()
      .then((res) => setData(res.data as DashboardData))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <CardSkeleton key={i} />
        ))}
      </div>
    );
  }

  const icons = [Database, TrendingUp, Sparkles, FileText];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
          <p className="text-gray-600 dark:text-gray-400">Your analytics overview</p>
        </div>
        <Link to="/upload">
          <Button>
            <Upload className="mr-2 h-4 w-4" /> Upload Dataset
          </Button>
        </Link>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {data?.kpis.map((kpi, i) => {
          const Icon = icons[i] || Database;
          return (
            <Card key={kpi.label} className="!p-0">
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500 dark:text-gray-400">{kpi.label}</span>
                  <Icon className="h-5 w-5 text-primary-600" />
                </div>
                <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">{kpi.value}</p>
              </div>
            </Card>
          );
        })}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Recent Uploads">
          {data?.recent_uploads.length ? (
            <ul className="space-y-3">
              {data.recent_uploads.map((d) => (
                <li key={d.id}>
                  <Link
                    to={`/datasets/${d.id}`}
                    className="flex items-center justify-between rounded-lg p-3 hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    <span className="font-medium text-gray-900 dark:text-white">{d.name}</span>
                    <span className="text-sm text-gray-500">
                      {d.rows} rows · Q:{d.quality_score?.toFixed(0) ?? '—'}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500">No datasets yet. Upload your first dataset!</p>
          )}
        </Card>

        <Card title="AI Recommendations">
          <ul className="space-y-2">
            {data?.ai_recommendations.map((rec, i) => (
              <li key={i} className="flex gap-2 text-sm text-gray-600 dark:text-gray-400">
                <Sparkles className="mt-0.5 h-4 w-4 shrink-0 text-primary-500" />
                {rec}
              </li>
            ))}
          </ul>
        </Card>
      </div>
    </div>
  );
}
