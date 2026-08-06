// ============================================================
// CodeWhisper PR - useAuth Hook
// ============================================================

import { useAuth as useAuthContext } from '../contexts/AuthContext';

export function useAuth() {
  return useAuthContext();
}
