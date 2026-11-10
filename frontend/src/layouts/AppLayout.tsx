import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from '../components/common/Sidebar';
import { Header } from '../components/common/Header';

export const AppLayout: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-row">
      {/* Fixed Left Sidebar */}
      <Sidebar />

      {/* Main content wrapper */}
      <div className="flex-1 flex flex-col min-w-0 min-h-screen bg-slate-900">
        <Header />

        {/* Regulatory/Compliance Disclaimer Banner */}
        <div className="bg-amber-500/10 border-b border-amber-500/20 px-8 py-2 text-xs text-amber-300/80 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center space-x-2">
            <span className="inline-block w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
            <span>
              <strong>Compliance Notice:</strong> FraudShield predictions are machine learning decision-support signals. Final financial transaction disposition requires investigator review.
            </span>
          </div>
          <span className="text-[10px] text-amber-400/60 font-mono hidden md:inline">PCI-DSS Tier-1 Ready (Zero PAN Storage)</span>
        </div>

        {/* Main Routed Page Content */}
        <main className="flex-1 p-8 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AppLayout;
