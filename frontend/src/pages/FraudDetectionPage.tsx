import React, { useState } from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Zap,
  Play,
  RotateCcw,
  Sliders,
  DollarSign,
  Tag,
  Laptop,
  MapPin,
  Clock,
  Sparkles,
  Layers,
  ArrowRight,
  Database,
  CheckCircle2,
  Cpu,
  Info,
} from 'lucide-react';
import { predictionService } from '../services/predictionService';
import { transactionService } from '../services/transactionService';
import { Prediction } from '../types';
import { Badge } from '../components/common/Badge';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from 'recharts';

export const FraudDetectionPage: React.FC = () => {
  const [amount, setAmount] = useState<number>(249.99);
  const [merchantCategory, setMerchantCategory] = useState<string>('electronics');
  const [location, setLocation] = useState<string>('New York, US');
  const [deviceId, setDeviceId] = useState<string>('dev_macbook_pro_991');
  const [vFeatures, setVFeatures] = useState<{ [key: string]: number }>({
    V1: -0.2,
    V2: 0.1,
    V3: 0.8,
    V4: -0.3,
    V10: 0.2,
    V12: 0.1,
    V14: 0.0,
    V17: -0.1,
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Prediction | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [savedSuccess, setSavedSuccess] = useState<string | null>(null);
  const [savingTxn, setSavingTxn] = useState(false);

  // Attack Vector Presets
  const loadPreset = (type: 'legitimate' | 'account_takeover' | 'carding_bot' | 'velocity_anomaly') => {
    if (type === 'legitimate') {
      setAmount(42.5);
      setMerchantCategory('grocery');
      setLocation('San Francisco, US');
      setDeviceId('dev_iphone_15');
      setVFeatures({
        V1: -0.25,
        V2: 0.12,
        V3: 1.2,
        V4: -0.4,
        V10: 0.15,
        V12: 0.22,
        V14: 0.05,
        V17: -0.1,
      });
    } else if (type === 'account_takeover') {
      setAmount(4850.0);
      setMerchantCategory('luxury');
      setLocation('Lagos, NG');
      setDeviceId('dev_emulator_x86');
      setVFeatures({
        V1: -4.8,
        V2: 3.9,
        V3: -6.2,
        V4: 5.1,
        V10: -5.4,
        V12: -7.1,
        V14: -8.3,
        V17: -9.0,
      });
    } else if (type === 'carding_bot') {
      setAmount(4.99);
      setMerchantCategory('online_services');
      setLocation('Bucharest, RO');
      setDeviceId('dev_selenium_headless');
      setVFeatures({
        V1: -2.8,
        V2: 2.1,
        V3: -3.8,
        V4: 3.2,
        V10: -3.4,
        V12: -4.2,
        V14: -5.1,
        V17: -4.6,
      });
    } else {
      setAmount(1250.0);
      setMerchantCategory('transfer');
      setLocation('Kyiv, UA');
      setDeviceId('dev_tor_exit_node');
      setVFeatures({
        V1: -3.1,
        V2: 2.8,
        V3: -4.5,
        V4: 3.8,
        V10: -4.1,
        V12: -5.0,
        V14: -6.2,
        V17: -5.8,
      });
    }
  };

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSavedSuccess(null);
    try {
      const payload = {
        transaction_id: 'TXN_' + Math.random().toString(36).substring(2, 9).toUpperCase(),
        amount,
        merchant_category: merchantCategory,
        location,
        device_id: deviceId,
        features: vFeatures,
      };
      const response = await predictionService.predict(payload);
      setResult(response);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Inference request failed. Please check backend services.');
    } finally {
      setLoading(false);
    }
  };

  const handleInjectToLedger = async () => {
    if (!result) return;
    setSavingTxn(true);
    try {
      await transactionService.createTransaction({
        external_transaction_id: result.transaction_id,
        amount,
        merchant_category: merchantCategory,
        location,
        device_id: deviceId,
        status: result.risk_level === 'HIGH' ? 'FLAGGED' : 'PENDING',
      });
      setSavedSuccess(`Transaction ${result.transaction_id} successfully injected to production ledger!`);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to inject transaction to database.');
    } finally {
      setSavingTxn(false);
    }
  };

  const shapData = (result?.explanations || []).map((exp) => ({
    feature: exp.feature.length > 15 ? exp.feature.substring(0, 15) + '...' : exp.feature,
    impact: exp.shap_value ?? (exp.impact === 'high' ? 0.6 : exp.impact === 'medium' ? 0.3 : 0.1),
  }));

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-3">
          <ShieldAlert className="w-7 h-7 text-cyan-400" />
          Interactive Fraud Detection & Scoring Sandbox
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Simulate transactions against the production XGBoost champion model, evaluate heuristic rules, and inspect real-time SHAP feature attributions.
        </p>
      </div>

      {/* Attack Vector Presets */}
      <div className="flex flex-wrap items-center gap-3 p-4 bg-slate-950/70 border border-slate-800 rounded-xl">
        <span className="text-xs uppercase font-semibold tracking-wider text-slate-400 flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5 text-cyan-400" /> Synthetic Attack Scenarios:
        </span>
        <button
          type="button"
          onClick={() => loadPreset('legitimate')}
          className="px-3 py-1.5 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded-lg text-xs font-medium transition"
        >
          Normal Grocery ($42.50)
        </button>
        <button
          type="button"
          onClick={() => loadPreset('account_takeover')}
          className="px-3 py-1.5 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 rounded-lg text-xs font-medium transition"
        >
          Account Takeover ($4,850.00 Luxury)
        </button>
        <button
          type="button"
          onClick={() => loadPreset('carding_bot')}
          className="px-3 py-1.5 bg-purple-500/10 hover:bg-purple-500/20 text-purple-400 border border-purple-500/30 rounded-lg text-xs font-medium transition"
        >
          Automated Carding Bot ($4.99 Micro)
        </button>
        <button
          type="button"
          onClick={() => loadPreset('velocity_anomaly')}
          className="px-3 py-1.5 bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/30 rounded-lg text-xs font-medium transition"
        >
          Suspicious Wire Transfer ($1,250.00)
        </button>
      </div>

      {/* Main Grid: Input Form vs Live Scoring Output */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Form (5 cols) */}
        <div className="lg:col-span-5">
          <form onSubmit={handlePredict} className="p-6 bg-slate-950/80 border border-slate-800 rounded-xl space-y-5">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-2">
              <Sliders className="w-4 h-4 text-cyan-400" /> Transaction Parameters
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1 flex items-center gap-1.5">
                  <DollarSign className="w-3.5 h-3.5 text-slate-500" /> Transaction Amount (USD)
                </label>
                <input
                  type="number"
                  step="0.01"
                  required
                  value={amount}
                  onChange={(e) => setAmount(parseFloat(e.target.value) || 0)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1 flex items-center gap-1.5">
                  <Tag className="w-3.5 h-3.5 text-slate-500" /> Merchant Category
                </label>
                <select
                  value={merchantCategory}
                  onChange={(e) => setMerchantCategory(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500"
                >
                  <option value="grocery">Grocery & Essentials</option>
                  <option value="electronics">Consumer Electronics</option>
                  <option value="travel">Airlines & Travel</option>
                  <option value="luxury">Luxury Retail & Jewelry</option>
                  <option value="transfer">Peer-to-Peer Transfer</option>
                  <option value="online_services">Digital Services</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1 flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-slate-500" /> Location Origin
                  </label>
                  <input
                    type="text"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1 flex items-center gap-1.5">
                    <Laptop className="w-3.5 h-3.5 text-slate-500" /> Device ID Hash
                  </label>
                  <input
                    type="text"
                    value={deviceId}
                    onChange={(e) => setDeviceId(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white font-mono focus:outline-none focus:border-cyan-500 text-xs"
                  />
                </div>
              </div>

              {/* Latent PCA Features Tuning */}
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="block text-xs font-medium text-slate-400">
                    Discriminative PCA Vectors (V1-V28)
                  </label>
                  <span className="text-[10px] text-cyan-400 font-mono">Key Fraud Indicators</span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  {['V14', 'V17', 'V12', 'V10', 'V4', 'V2', 'V3', 'V1'].map((vKey) => (
                    <div key={vKey} className="flex items-center gap-2 bg-slate-900 p-1.5 rounded border border-slate-800/80">
                      <span className={`font-mono w-8 ${['V14', 'V17', 'V12'].includes(vKey) ? 'text-amber-400 font-bold' : 'text-slate-500'}`}>
                        {vKey}:
                      </span>
                      <input
                        type="number"
                        step="0.1"
                        value={vFeatures[vKey] ?? 0}
                        onChange={(e) =>
                          setVFeatures({
                            ...vFeatures,
                            [vKey]: parseFloat(e.target.value) || 0,
                          })
                        }
                        className="w-full bg-transparent font-mono text-cyan-300 focus:outline-none"
                      />
                    </div>
                  ))}
                </div>
                <p className="text-[10px] text-slate-500 mt-1 italic">
                  Note: Large negative values in V14, V17, and V12 strongly trigger the XGBoost fraud decision boundary.
                </p>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-4 flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-semibold rounded-lg shadow-lg shadow-cyan-500/20 transition disabled:opacity-50 text-sm"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Computing Inference & SHAP...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-white" />
                  <span>Execute Real-Time Scoring</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Live Output & Explanations (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {error && (
            <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-400 text-sm flex items-center gap-3">
              <AlertTriangle className="w-5 h-5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {savedSuccess && (
            <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-400 text-sm flex items-center gap-3">
              <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
              <span>{savedSuccess}</span>
            </div>
          )}

          {result ? (
            <div className="p-6 bg-slate-950/80 border border-slate-800 rounded-xl space-y-6">
              <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                <div>
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <Zap className="w-5 h-5 text-amber-400" />
                    Transaction Scoring Verdict: {result.transaction_id}
                  </h3>
                  <span className="text-xs font-mono text-slate-500">
                    Engine Version: {result.model_version} • Inference Latency: {result.inference_latency_ms.toFixed(1)}ms
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Badge type="status" value={result.prediction} />
                  <Badge type="risk" value={result.risk_level} />
                </div>
              </div>

              {/* Gauge and Action */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-lg">
                  <span className="text-xs text-slate-400">ML Model Probability</span>
                  <div className="text-3xl font-extrabold font-mono text-white mt-1">
                    {(result.fraud_probability * 100).toFixed(2)}%
                  </div>
                  <div className="w-full h-2.5 bg-slate-800 rounded-full mt-3 overflow-hidden">
                    <div
                      className={`h-full ${
                        result.risk_level === 'HIGH'
                          ? 'bg-rose-500'
                          : result.risk_level === 'MEDIUM'
                          ? 'bg-amber-500'
                          : 'bg-emerald-500'
                      }`}
                      style={{ width: `${Math.max(result.fraud_probability * 100, 2)}%` }}
                    />
                  </div>
                </div>

                <div className="p-4 bg-slate-900 border border-slate-800 rounded-lg flex flex-col justify-between">
                  <span className="text-xs text-slate-400">Recommended Decision</span>
                  <div className="text-lg font-bold font-mono text-cyan-400">
                    {result.recommended_action}
                  </div>
                  <span className="text-[11px] text-slate-500">
                    {result.recommended_action === 'BLOCK'
                      ? 'Severe risk profile: step-up authentication or hold.'
                      : result.recommended_action === 'FLAG_FOR_REVIEW'
                      ? 'Elevated risk parameters: flagged for investigator review.'
                      : 'Low anomaly score: automated clearing.'}
                  </span>
                </div>
              </div>

              {/* Triggered Heuristics */}
              <div>
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                  Triggered Heuristic Rules ({result.rule_triggers?.length || 0})
                </h4>
                {result.rule_triggers && result.rule_triggers.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {result.rule_triggers.map((rule, idx) => (
                      <span
                        key={idx}
                        className="px-2.5 py-1 bg-amber-500/10 border border-amber-500/30 text-amber-300 font-mono text-xs rounded-md"
                      >
                        {rule}
                      </span>
                    ))}
                  </div>
                ) : (
                  <span className="text-xs text-slate-500 italic">No heuristic rules fired.</span>
                )}
              </div>

              {/* SHAP Chart */}
              <div>
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center justify-between">
                  <span>SHAP Feature Attribution (Prediction Drivers)</span>
                  <span className="text-[10px] text-slate-500 lowercase font-mono">XGBoost TreeExplainer</span>
                </h4>
                {shapData.length > 0 ? (
                  <div className="h-56 w-full bg-slate-900/50 p-2 rounded-lg border border-slate-800/80">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={shapData}
                        layout="vertical"
                        margin={{ top: 5, right: 30, left: 60, bottom: 5 }}
                      >
                        <XAxis type="number" stroke="#64748b" fontSize={11} />
                        <YAxis type="category" dataKey="feature" stroke="#94a3b8" fontSize={11} width={80} />
                        <Tooltip
                          contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                          formatter={(value: any) => [Number(value).toFixed(4), 'SHAP Impact']}
                        />
                        <ReferenceLine x={0} stroke="#475569" strokeDasharray="3 3" />
                        <Bar dataKey="impact" radius={[0, 4, 4, 0]}>
                          {shapData.map((entry, index) => (
                            <Cell
                              key={`cell-${index}`}
                              fill={entry.impact >= 0 ? '#f43f5e' : '#10b981'}
                            />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <p className="text-xs text-slate-500">Feature explanations not returned.</p>
                )}
              </div>

              {/* Ledger Action */}
              <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
                <span className="text-xs text-slate-400">Want to test ledger persistence?</span>
                <button
                  type="button"
                  onClick={handleInjectToLedger}
                  disabled={savingTxn}
                  className="flex items-center gap-1.5 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold border border-slate-700 transition"
                >
                  <Database className="w-3.5 h-3.5 text-cyan-400" />
                  <span>{savingTxn ? 'Injecting...' : 'Inject into Database Ledger'}</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="p-12 bg-slate-950/40 border border-slate-800/80 border-dashed rounded-xl text-center space-y-3">
              <ShieldCheck className="w-12 h-12 text-slate-700 mx-auto" />
              <h3 className="text-sm font-semibold text-slate-400">Ready for Live Inference</h3>
              <p className="text-xs text-slate-500 max-w-sm mx-auto">
                Configure transaction parameters on the left or click any synthetic attack scenario above, then click 'Execute Real-Time Scoring'.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FraudDetectionPage;
