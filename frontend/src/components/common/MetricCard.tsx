import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  trend?: {
    value: string;
    isPositive?: boolean;
    isGood?: boolean;
  };
  accentColor?: 'red' | 'emerald' | 'amber' | 'blue' | 'purple';
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  accentColor = 'blue',
}) => {
  const colorMap = {
    red: 'from-red-500/10 to-transparent border-red-500/20 text-red-400',
    emerald: 'from-emerald-500/10 to-transparent border-emerald-500/20 text-emerald-400',
    amber: 'from-amber-500/10 to-transparent border-amber-500/20 text-amber-400',
    blue: 'from-cyan-500/10 to-transparent border-cyan-500/20 text-cyan-400',
    purple: 'from-purple-500/10 to-transparent border-purple-500/20 text-purple-400',
  };

  return (
    <div
      className={`relative overflow-hidden rounded-xl border bg-slate-900/60 p-5 shadow-lg backdrop-blur transition-all duration-200 hover:border-slate-700 bg-gradient-to-br ${colorMap[accentColor]}`}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wider text-slate-400">
          {title}
        </span>
        <div className={`p-2 rounded-lg bg-slate-800/80 border border-slate-700/60 text-slate-300`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>

      <div className="mt-4 flex items-baseline justify-between">
        <span className="text-2xl font-bold tracking-tight text-white">{value}</span>
        {trend && (
          <span
            className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
              trend.isGood
                ? 'bg-emerald-950 text-emerald-400 border border-emerald-800/60'
                : 'bg-red-950 text-red-400 border border-red-800/60'
            }`}
          >
            {trend.value}
          </span>
        )}
      </div>

      {subtitle && <p className="mt-2 text-xs text-slate-400">{subtitle}</p>}
    </div>
  );
};

