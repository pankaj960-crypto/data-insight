import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { isAdmin } from '../utils/auth';
import { authService } from '../services/authService';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';

export function Profile() {
  const { user, refreshUser } = useAuth();
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [username, setUsername] = useState(user?.username || '');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSave = async () => {
    setLoading(true);
    try {
      await authService.updateProfile({ full_name: fullName, username });
      await refreshUser();
      setMessage('Profile updated successfully');
    } catch {
      setMessage('Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  if (!user) return null;

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Profile</h1>
      <Card>
        <div className="space-y-4">
          <div>
            <label className="text-sm text-gray-500">Email</label>
            <p className="font-medium">{user.email}</p>
          </div>
          <div>
            <label className="text-sm font-medium">Full Name</label>
            <input
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="mt-1 w-full rounded-lg border px-4 py-2 dark:border-gray-600 dark:bg-gray-700"
            />
          </div>
          <div>
            <label className="text-sm font-medium">Username</label>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="mt-1 w-full rounded-lg border px-4 py-2 dark:border-gray-600 dark:bg-gray-700"
            />
          </div>
          {isAdmin(user) && (
            <span className="inline-block rounded-full bg-primary-100 px-3 py-1 text-xs text-primary-700 dark:bg-primary-900/30 dark:text-primary-300">
              Administrator
            </span>
          )}
          {message && <p className="text-sm text-green-600">{message}</p>}
          <Button onClick={handleSave} loading={loading}>Save Changes</Button>
        </div>
      </Card>
    </div>
  );
}
