// ============================================================
// CodeWhisper PR - Card Component
// ============================================================

import React from 'react';

export interface CardProps {
  title?: string;
  subtitle?: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
  headerClassName?: string;
  bodyClassName?: string;
  footer?: React.ReactNode;
  footerClassName?: string;
  variant?: 'default' | 'bordered' | 'elevated';
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  description,
  children,
  className = '',
  headerClassName = '',
  bodyClassName = '',
  footer,
  footerClassName = '',
  variant = 'default',
  padding = 'md',
}) => {
  const variantStyles = {
    default: 'bg-gray-800/50 backdrop-blur-sm border border-gray-700',
    bordered: 'bg-gray-800/50 backdrop-blur-sm border-2 border-gray-600',
    elevated: 'bg-gray-800/50 backdrop-blur-sm shadow-xl',
  };

  const paddingStyles = {
    none: '',
    sm: 'p-3',
    md: 'p-6',
    lg: 'p-8',
  };

  return (
    <div
      className={`
        rounded-xl
        ${variantStyles[variant]}
        ${className}
      `}
    >
      {(title || subtitle || description) && (
        <div
          className={`
            border-b border-gray-700
            ${paddingStyles[padding]}
            ${headerClassName}
          `}
        >
          {title && (
            <h3 className="text-lg font-semibold text-white">{title}</h3>
          )}
          {subtitle && (
            <p className="text-sm text-gray-400">{subtitle}</p>
          )}
          {description && (
            <p className="text-sm text-gray-300 mt-1">{description}</p>
          )}
        </div>
      )}

      <div className={`${paddingStyles[padding]} ${bodyClassName}`}>
        {children}
      </div>

      {footer && (
        <div
          className={`
            border-t border-gray-700
            ${paddingStyles[padding]}
            ${footerClassName}
          `}
        >
          {footer}
        </div>
      )}
    </div>
  );
};

export default Card;
