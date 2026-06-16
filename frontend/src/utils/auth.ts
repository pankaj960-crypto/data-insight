import type { User } from '../types';

export function isAdmin(user: User | null | undefined): boolean {
  return user?.is_admin === true;
}
