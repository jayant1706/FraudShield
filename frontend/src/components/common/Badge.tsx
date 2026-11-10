import React from 'react';
import { RiskLevel, TransactionStatus } from '../../types';

export interface BadgeProps {
  type?: 'risk' | 'status' | 'role';
  value?: RiskLevel | TransactionStatus | string;
  variant?: string;
  children?: React.ReactNode;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ type, value, variant, children, className = '' }) => {
  const actualValue = String(value || variant || children || '').toUpperCase();

  if (actualValue === 'HIGH' || actualValue === 'HIGH RISK' || actualValue === 'FRAUD') {
    return (
      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-950/80 text-rose-400 border border-rose-800/60 ${className}`}>
        <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-pulse"></span>
        {children || 'HIGH RISK'}
      </span>
    );
  }

  if (actualValue === 'MEDIUM' || actualValue === 'MEDIUM RISK' || actualValue === 'FLAGGED' || actualValue === 'FLAG_FOR_REVIEW') {
    return (
      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-950/80 text-amber-400 border border-amber-800/60 ${className}`}>
        <span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
        {children || actualValue}
      </span>
    );
  }

  if (actualValue === 'LOW' || actualValue === 'LOW RISK' || actualValue === 'LEGITIMATE' || actualValue === 'APPROVED' || actualValue === 'ALLOW') {
    return (
      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-950/80 text-emerald-400 border border-emerald-800/60 ${className}`}>
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
        {children || actualValue}
      </span>
    );
  }

  if (actualValue === 'REJECTED' || actualValue === 'BLOCK') {
    return (
      <span className={`px-2.5 py-1 rounded-full text-xs font-medium bg-rose-950/60 text-rose-400 border border-rose-800/60 ${className}`}>
        {children || actualValue}
      </span>
    );
  }

  return (
    <span className={`px-2.5 py-1 rounded-full text-xs font-medium bg-slate-800/80 text-slate-300 border border-slate-700/60 ${className}`}>
      {children || actualValue}
    </span>
  );
};

export default Badge;
