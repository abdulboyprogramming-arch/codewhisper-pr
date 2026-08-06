// ============================================================
// CodeWhisper PR - LoadingSpinner Component
// ============================================================

import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
}

export default function LoadingSpinner({ size = 'md' }: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  return (
    <div className="animate-spin rounded-full border-2 border-gray-600 border-t-primary-500" style={{ width: size === 'sm' ? '1rem' : size === 'md' ? '2rem' : '3rem' }}>
      <span className="sr-only">Loading...</span>
    </div>
  );
}
