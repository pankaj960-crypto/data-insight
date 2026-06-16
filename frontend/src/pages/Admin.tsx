import { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { Card } from '../components/ui/Card';
import { CardSkeleton } from '../components/ui/Skeleton';
import { isAdmin } from '../utils/auth';

interface AdminStats {
  total_users: number;
  active_users: number;
  total_datasets: number;
  total_reports: number;
  total_storage_bytes: number;
  recent_uploads: { id: number; name: string; row_count: number }[];
}

interface AdminUser {
  id: number;
  email: string;
  username: string;
  dataset_count: number;
  is_active: boolean;
  is_admin: boolean;
}

export function Admin() {
  const { user, loading: authLoading } = useAuth();
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [forbidden, setForbidden] = useState(false);

  useEffect(() => {
    if (!isAdmin(user)) return;

    Promise.all([api.get('/admin/stats'), api.get('/admin/users')])
      .then(([s, u]) => {
        setStats(s.data);
        setUsers(u.data);
      })
      .catch((err) => {
        if (err?.response?.status === 403) setForbidden(true);
      })
      .finally(() => setLoading(false));
  }, [user]);

  if (authLoading) return <CardSkeleton />;
  if (!isAdmin(user) || forbidden) return <Navigate to="/dashboard" replace />;
  if (loading) return <CardSkeleton />;

  const storageMB = ((stats?.total_storage_bytes || 0) / 1024 / 1024).toFixed(2);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Admin Panel</h1>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: 'Total Users', value: stats?.total_users },
          { label: 'Active Users', value: stats?.active_users },
          { label: 'Total Datasets', value: stats?.total_datasets },
          { label: 'Storage Used', value: `${storageMB} MB` },
        ].map((s) => (
          <Card key={s.label}>
            <p className="text-sm text-gray-500">{s.label}</p>
            <p className="text-2xl font-bold">{s.value}</p>
          </Card>
        ))}
      </div>

      <Card title="Users">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500">
                <th className="pb-2">Email</th>
                <th>Username</th>
                <th>Datasets</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} className="border-t border-gray-100 dark:border-gray-700">
                  <td className="py-2">{u.email}</td>
                  <td>{u.username}</td>
                  <td>{u.dataset_count}</td>
                  <td>{u.is_active ? 'Active' : 'Inactive'}{u.is_admin ? ' (Admin)' : ''}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
