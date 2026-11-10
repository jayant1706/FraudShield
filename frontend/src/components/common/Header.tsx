import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Bell,
  CheckCircle2,
  ChevronDown,
  Cpu,
  Database,
  ExternalLink,
  Flame,
  Info,
  Radio,
  Server,
  ShieldAlert,
  ShieldCheck,
  X,
  Zap,
} from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';

export const Header: React.FC = () => {
  const { user } = useAuth();
  const [showSystemModal, setShowSystemModal] = useState(false);
  const [showAlertsDropdown, setShowAlertsDropdown] = useState(false);

  // Simulated live security incident alerts for investigator situational awareness
  const liveAlerts = [
    {
      id: 'TXN_98421',
      amount: '$4,850.00',
      reason: 'Cross-Border Velocity Spike (V14 < -7.2)',
      probability: '96.4%',
      risk: 'HIGH',
      time: '3 min ago',
    },
    {
      id: 'TXN_98418',
      amount: '$1,920.00',
      reason: 'Rapid Multi-card Probe (Tor Exit Node)',
      probability: '91.8%',
      risk: 'HIGH',
      time: '12 min ago',
    },
    {
      id: 'TXN_98399',
      amount: '$840.00',
      reason: 'Off-hours High-value Purchase',
      probability: '74.2%',
      risk: 'MEDIUM',
      time: '28 min ago',
    },
  ];

  return (
    <>
      <header className="h-16 bg-slate-950/80 backdrop-blur border-b border-slate-800/80 px-6 sm:px-8 flex items-center justify-between sticky top-0 z-30">
        <div className="flex items-center gap-3 sm:gap-4">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <ShieldCheck className="w-4 h-4 text-cyan-400" />
            <span className="font-semibold text-slate-200 hidden sm:inline">FraudShield Enterprise Gateway</span>
            <span className="text-slate-600 hidden sm:inline">|</span>
            <button
              onClick={() => setShowSystemModal(true)}
              className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono text-[11px] hover:bg-emerald-500/20 transition cursor-pointer"
              title="Click to view live microservices health"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              All Systems Operational
              <ChevronDown className="w-3 h-3 text-emerald-400/80" />
            </button>
          </div>
        </div>

        <div className="flex items-center gap-4 sm:gap-6">
          {/* Active Model Pill */}
          <div className="hidden lg:flex items-center gap-2 px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300">
            <Cpu className="w-3.5 h-3.5 text-cyan-400" />
            <span>XGBoost v1.0.0</span>
            <span className="text-slate-600">·</span>
            <span className="text-cyan-400 font-medium">PR-AUC 88.4%</span>
          </div>

          {/* Quick Simulation Link */}
          <Link
            to="/detect"
            className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-gradient-to-r from-cyan-600/20 to-blue-600/20 hover:from-cyan-600/30 hover:to-blue-600/30 border border-cyan-500/30 text-cyan-300 text-xs font-medium transition"
          >
            <Zap className="w-3.5 h-3.5 text-cyan-400" />
            <span>Score Vector</span>
          </Link>

          {/* Notifications / Live Security Alerts Bell */}
          <div className="relative">
            <button
              onClick={() => setShowAlertsDropdown(!showAlertsDropdown)}
              className="relative p-2 rounded-lg bg-slate-900/80 hover:bg-slate-850 border border-slate-800 text-slate-300 hover:text-white transition"
              title="View Security Incident Alerts"
            >
              <Bell className="w-4 h-4" />
              <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-rose-600 text-[9px] font-bold text-white shadow-sm ring-2 ring-slate-950">
                {liveAlerts.length}
              </span>
            </button>

            {/* Alerts Dropdown Panel */}
            {showAlertsDropdown && (
              <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-slate-950 border border-slate-800 rounded-xl shadow-2xl p-4 z-50 space-y-3">
                <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                  <div className="flex items-center gap-2">
                    <ShieldAlert className="w-4 h-4 text-rose-500" />
                    <span className="text-xs font-bold text-white uppercase tracking-wider">High-Risk Alerts</span>
                  </div>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30">
                    Live Telemetry
                  </span>
                </div>

                <div className="space-y-2">
                  {liveAlerts.map((alert) => (
                    <div
                      key={alert.id}
                      className="p-2.5 rounded-lg bg-slate-900/80 hover:bg-slate-900 border border-slate-800/80 text-xs space-y-1 transition"
                    >
                      <div className="flex items-center justify-between font-mono">
                        <span className="font-bold text-slate-200">{alert.id}</span>
                        <span className="text-rose-400 font-bold">{alert.probability} Risk</span>
                      </div>
                      <div className="text-[11px] text-slate-400">{alert.reason}</div>
                      <div className="flex items-center justify-between text-[10px] text-slate-500 pt-1">
                        <span>Amount: {alert.amount}</span>
                        <span>{alert.time}</span>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="pt-2 border-t border-slate-800 flex items-center justify-between">
                  <Link
                    to="/transactions"
                    onClick={() => setShowAlertsDropdown(false)}
                    className="text-xs text-cyan-400 hover:text-cyan-300 font-medium flex items-center gap-1"
                  >
                    View All in Ledger &rarr;
                  </Link>
                  <button
                    onClick={() => setShowAlertsDropdown(false)}
                    className="text-[11px] text-slate-500 hover:text-slate-300"
                  >
                    Close
                  </button>
                </div>
              </div>
            )}
          </div>

          <div className="h-4 w-px bg-slate-800"></div>

          {/* User Profile */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-cyan-600 to-blue-600 flex items-center justify-center text-xs font-bold text-white uppercase shadow-sm ring-1 ring-cyan-500/30">
              {user?.full_name?.charAt(0) || 'U'}
            </div>
            <div className="hidden md:block text-left">
              <span className="block text-xs font-semibold text-slate-200 leading-tight">{user?.full_name}</span>
              <span className="block text-[10px] text-slate-500 font-mono leading-tight">{user?.role}</span>
            </div>
          </div>
        </div>
      </header>

      {/* System Health & Architecture Modal */}
      {showSystemModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full p-6 shadow-2xl space-y-6">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center">
                  <Server className="w-5 h-5 text-cyan-400" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">FraudShield Infrastructure & Microservices</h3>
                  <p className="text-xs text-slate-400">Live operational status across docker container stack</p>
                </div>
              </div>
              <button
                onClick={() => setShowSystemModal(false)}
                className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
              <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-white flex items-center gap-2">
                    <Zap className="w-3.5 h-3.5 text-cyan-400" /> FastAPI REST Gateway
                  </span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                    Port 8000
                  </span>
                </div>
                <div className="text-[11px] text-slate-400">ASGI Uvicorn 4-worker pool with sub-25ms response SLA</div>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-white flex items-center gap-2">
                    <Cpu className="w-3.5 h-3.5 text-purple-400" /> XGBoost Champion Model
                  </span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                    PR-AUC 88.4%
                  </span>
                </div>
                <div className="text-[11px] text-slate-400">Calibrated tree probability scoring with SHAP attribution</div>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-white flex items-center gap-2">
                    <Database className="w-3.5 h-3.5 text-blue-400" /> PostgreSQL 16
                  </span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                    Port 5432
                  </span>
                </div>
                <div className="text-[11px] text-slate-400">SQLAlchemy 2.0 ORM, indexed transactional audit logs</div>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-white flex items-center gap-2">
                    <Radio className="w-3.5 h-3.5 text-rose-400" /> Redis Broker & Cache
                  </span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                    Port 6379
                  </span>
                </div>
                <div className="text-[11px] text-slate-400">Task queue routing and token revocation store</div>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-white flex items-center gap-2">
                    <Server className="w-3.5 h-3.5 text-amber-400" /> Celery Async Worker
                  </span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                    4 Workers
                  </span>
                </div>
                <div className="text-[11px] text-slate-400">Batch transaction scoring & Kolmogorov-Smirnov drift test</div>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-white flex items-center gap-2">
                    <Flame className="w-3.5 h-3.5 text-orange-400" /> Prometheus & Grafana
                  </span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                    9090 / 3001
                  </span>
                </div>
                <div className="text-[11px] text-slate-400">Scrapes endpoint latency, request throughput & drift metrics</div>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-cyan-950/30 border border-cyan-800/40 text-xs text-cyan-200/90 flex items-center justify-between">
              <span>Security standard: Zero storage of Primary Account Numbers (PAN) or CVV codes.</span>
              <button
                onClick={() => setShowSystemModal(false)}
                className="px-3 py-1 bg-cyan-600 hover:bg-cyan-500 text-white rounded font-medium text-xs transition"
              >
                Acknowledge
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
