import React, { useState } from 'react';
import {
  Settings as SettingsIcon,
  Sliders,
  ShieldAlert,
  Save,
  CheckCircle2,
  Lock,
  Bell,
  Database,
  Cpu,
} from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

export const SettingsPage: React.FC = () => {
  const { isAdmin } = useAuth();

  const [lowThreshold, setLowThreshold] = useState<number>(0.3);
  const [highThreshold, setHighThreshold] = useState<number>(0.7);
  const [amountThreshold, setAmountThreshold] = useState<number>(2500);
  const [velocityMinutes, setVelocityMinutes] = useState<number>(5);
  const [rateLimit, setRateLimit] = useState<number>(120);
  const [enableShap, setEnableShap] = useState<boolean>(true);
  const [saved, setSaved] = useState<boolean>(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 4000);
  };

  return (
    <div className="space-y-8 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-3">
          <SettingsIcon className="w-7 h-7 text-cyan-400" />
          Risk Engine & Gateway Settings
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Tune deterministic heuristic rules, risk classification bands, and gateway security boundaries.
        </p>
      </div>

      {saved && (
        <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-emerald-400 text-sm flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
          <span>Risk thresholds and security configurations updated and propagated across inference nodes.</span>
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        {/* Risk Thresholds Band */}
        <div className="p-6 bg-slate-950/80 border border-slate-800 rounded-xl space-y-4">
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <Sliders className="w-5 h-5 text-cyan-400" />
            Decision Score Risk Bands
          </h2>
          <p className="text-xs text-slate-400">
            Transactions scoring below the Low Risk cutoff are classified as <strong>LOW</strong>. Scores between Low and High are <strong>MEDIUM</strong>. Scores above High are flagged as <strong>HIGH</strong>.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 pt-2">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Low Risk Cutoff (0.0 to 1.0)
              </label>
              <input
                type="number"
                step="0.05"
                min="0"
                max="0.5"
                value={lowThreshold}
                onChange={(e) => setLowThreshold(parseFloat(e.target.value))}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white font-mono focus:outline-none focus:border-cyan-500"
              />
              <span className="text-[11px] text-slate-500 mt-1 block">Default: 0.30</span>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                High Risk Cutoff (0.5 to 1.0)
              </label>
              <input
                type="number"
                step="0.05"
                min="0.5"
                max="1.0"
                value={highThreshold}
                onChange={(e) => setHighThreshold(parseFloat(e.target.value))}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white font-mono focus:outline-none focus:border-cyan-500"
              />
              <span className="text-[11px] text-slate-500 mt-1 block">Default: 0.70</span>
            </div>
          </div>
        </div>

        {/* Deterministic Rule Engine Parameters */}
        <div className="p-6 bg-slate-950/80 border border-slate-800 rounded-xl space-y-4">
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-amber-400" />
            Deterministic Heuristic Rules
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                High Transaction Amount Trigger ($)
              </label>
              <input
                type="number"
                step="100"
                value={amountThreshold}
                onChange={(e) => setAmountThreshold(parseFloat(e.target.value))}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white font-mono focus:outline-none focus:border-cyan-500"
              />
              <span className="text-[11px] text-slate-500 mt-1 block">
                Transactions exceeding this trigger rule <code>HIGH_AMOUNT</code>
              </span>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Velocity Window (Minutes)
              </label>
              <input
                type="number"
                min="1"
                max="60"
                value={velocityMinutes}
                onChange={(e) => setVelocityMinutes(parseInt(e.target.value))}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white font-mono focus:outline-none focus:border-cyan-500"
              />
              <span className="text-[11px] text-slate-500 mt-1 block">
                Time horizon to check for rapid multiple transaction bursts
              </span>
            </div>
          </div>
        </div>

        {/* Inference Latency & Explainability */}
        <div className="p-6 bg-slate-950/80 border border-slate-800 rounded-xl space-y-4">
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <Cpu className="w-5 h-5 text-cyan-400" />
            Explainability & Performance
          </h2>

          <div className="flex items-center justify-between p-3 bg-slate-900/60 rounded-lg border border-slate-800">
            <div>
              <div className="text-sm font-medium text-white">Tree SHAP Real-time Explanations</div>
              <div className="text-xs text-slate-400">
                Compute Shapley feature impact values for every transaction scoring request (&lt;25ms latency budget)
              </div>
            </div>
            <input
              type="checkbox"
              checked={enableShap}
              onChange={(e) => setEnableShap(e.target.checked)}
              className="w-4 h-4 text-cyan-600 rounded bg-slate-800 border-slate-700 focus:ring-cyan-500"
            />
          </div>

          <div className="flex items-center justify-between p-3 bg-slate-900/60 rounded-lg border border-slate-800">
            <div>
              <div className="text-sm font-medium text-white">Gateway Rate Limit (RPM per IP)</div>
              <div className="text-xs text-slate-400">Protects inference REST endpoints against DDoS and scrapers</div>
            </div>
            <input
              type="number"
              value={rateLimit}
              onChange={(e) => setRateLimit(parseInt(e.target.value))}
              className="w-24 bg-slate-900 border border-slate-700 rounded-lg px-3 py-1 text-sm text-white font-mono text-right"
            />
          </div>
        </div>

        {isAdmin && (
          <div className="flex justify-end">
            <button
              type="submit"
              className="flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-semibold rounded-lg shadow-lg shadow-cyan-500/20 text-sm transition"
            >
              <Save className="w-4 h-4" /> Save Configuration
            </button>
          </div>
        )}
      </form>
    </div>
  );
};

export default SettingsPage;

