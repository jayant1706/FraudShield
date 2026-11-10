import React from 'react';

export interface LoadingSkeletonProps {
  rows?: number;
  className?: string;
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({ rows = 5, className }) => {
  if (className) {
    return <div className={`bg-slate-800/60 rounded-lg animate-pulse ${className}`} />;
  }

  return (
    <div className="space-y-3 animate-pulse">
      <div className="h-10 bg-slate-800/60 rounded-lg w-full"></div>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="h-14 bg-slate-900/60 border border-slate-800/40 rounded-lg w-full"></div>
      ))}
    </div>
  );
};

export default LoadingSkeleton;
