import React from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  change?: number;
  icon: React.ReactNode;
  iconBg?: string;
  className?: string;
}

export function StatCard({ title, value, change, icon, iconBg = 'bg-primary-50', className = '' }: StatCardProps) {
  const isPositive = change !== undefined && change >= 0;

  return (
    <div className={`bg-card rounded-xl border border-slate-200 shadow-card p-5 hover:shadow-card-hover transition-shadow duration-200 ${className}`}>
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <p className="text-sm font-medium text-slate-500">{title}</p>
          <p className="text-2xl font-bold text-slate-800">{value}</p>
          {change !== undefined && (
            <div className="flex items-center gap-1.5">
              <span className={`inline-flex items-center text-xs font-semibold px-1.5 py-0.5 rounded ${
                isPositive ? 'bg-emerald-50 text-emerald-600' : 'bg-red-50 text-red-600'
              }`}>
                {isPositive ? '↑' : '↓'} {Math.abs(change)}%
              </span>
              <span className="text-xs text-slate-400">vs last month</span>
            </div>
          )}
        </div>
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${iconBg}`}>
          <span className="text-primary text-xl">{icon}</span>
        </div>
      </div>
    </div>
  );
}
