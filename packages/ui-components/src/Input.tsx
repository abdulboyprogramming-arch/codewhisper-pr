// ============================================================
// CodeWhisper PR - Input Component
// ============================================================

import React, { forwardRef } from 'react';

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helper?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  fullWidth?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      error,
      helper,
      leftIcon,
      rightIcon,
      fullWidth = true,
      className = '',
      id,
      type = 'text',
      ...props
    },
    ref
  ) => {
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;

    const baseStyles =
      'bg-gray-700 border rounded-lg px-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 transition-all duration-200';

    const stateStyles = error
      ? 'border-red-500 focus:ring-red-500'
      : 'border-gray-600 focus:ring-purple-500 focus:border-transparent';

    const widthStyles = fullWidth ? 'w-full' : '';

    return (
      <div className={`${fullWidth ? 'w-full' : ''}`}>
        {label && (
          <label
            htmlFor={inputId}
            className="block text-sm font-medium text-gray-300 mb-1.5"
          >
            {label}
          </label>
        )}

        <div className="relative">
          {leftIcon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <span className="text-gray-400">{leftIcon}</span>
            </div>
          )}

          <input
            ref={ref}
            id={inputId}
            type={type}
            className={`
              ${baseStyles}
              ${stateStyles}
              ${widthStyles}
              ${leftIcon ? 'pl-10' : ''}
              ${rightIcon ? 'pr-10' : ''}
              ${className}
            `}
            {...props}
          />

          {rightIcon && (
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
              <span className="text-gray-400">{rightIcon}</span>
            </div>
          )}
        </div>

        {error && <p className="mt-1 text-sm text-red-500">{error}</p>}
        {helper && !error && (
          <p className="mt-1 text-sm text-gray-400">{helper}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;
