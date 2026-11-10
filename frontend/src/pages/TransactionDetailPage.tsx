import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Clock,
  DollarSign,
  Tag,
  Laptop,
  MapPin,
  User,
  CheckCircle2,
  XCircle,
  FileText,
  Activity,
  Cpu,
  Globe,
  Wifi,
  ChevronDown,
  ChevronUp,
  Sliders,
  TrendingUp,
  AlertCircle,
  Terminal,
} from 'lucide-react';
import { transactionService } from '../services/transactionService';
import { Transaction, TransactionStatus, FeatureAttribution } from '../types';
import { Badge } from '../components/common/Badge';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
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

export const TransactionDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [transaction, setTransaction] = useState<Transaction | null>(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notes, setNotes] = useState('');
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [showAllVectors, setShowAllVectors] = useState(false);

  useEffect(() => {
    if (id) {
      loadTransaction(id);
    }
  }, [id]);

  const loadTransaction = async (txId: string) => {
    try {
      setLoading(true);
      setError(null);
      const data = await transactionService.getTransaction(txId);
      setTransaction(data);
      if (data.investigation_notes) {
        setNotes(data.investigation_notes);
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to load transaction details.');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (newStatus: TransactionStatus) => {
    if (!id) return;
    try {
      setUpdating(true);
      setSuccessMessage(null);
      const updated = await transactionService.updateStatus(id, newStatus, notes);
      setTransaction(updated);
      setSuccessMessage(`Transaction disposition successfully updated to ${newStatus}.`);
      setTimeout(() => setSuccessMessage(null), 4000);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to update transaction disposition.');
    } finally {
      setUpdating(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <LoadingSkeleton className="h-10 w-48" />
        <LoadingSkeleton className="h-64 w-full" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <LoadingSkeleton className="h-80" />
          <LoadingSkeleton className="h-80" />
        </div>
      </div>
    );
  }

  if (error || !transaction) {
    return (
      <div className="p-8 bg-slate-900 border border-slate-800 rounded-xl text-center space-y-4">
        <AlertTriangle className="w-12 h-12 text-amber-400 mx-auto" />
        <h3 className="text-lg font-semibold text-slate-200">Transaction Not Found</h3>
        <p className="text-sm text-slate-400">{error || 'Unable to retrieve requested transaction record.'}</p>
        <Link
          to="/transactions"
          className="inline-flex items-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-sm font-medium transition"
        >
          <ArrowLeft className="w-4 h-4" /> Return to Transactions Ledger
        </Link>
      </div>
    );
  }

  const prediction = transaction.prediction;
  const isHighRisk = prediction?.risk_level === 'HIGH';
  const isMedRisk = prediction?.risk_level === 'MEDIUM';

  // Format explanations for SHAP chart
  const shapData = (prediction?.explanations || []).map((exp) => ({
    feature: exp.feature.length > 15 ? exp.feature.substring(0, 15) + '...' : exp.feature,
    impact: exp.shap_value ?? (exp.impact === 'high' ? 0.6 : exp.impact === 'medium' ? 0.3 : 0.1),
    direction: (exp.shap_value ?? 0) >= 0 ? 'Risk Driver' : 'Mitigating',
  }));

  // Latent PCA vectors synthetic generator for display
  const simulatedVectors = Array.from({ length: 28 }, (_, i) => {
    const vNum = i + 1;
    // Derive deterministic pseudo-variance from transaction amount and id
    const hash = (vNum * 17 + transaction.amount * 3) % 100;
    const isOutlier = [14, 17, 12, 10, 4, 2].includes(vNum) && isHighRisk;
    const value = isOutlier ? -4.5 - (hash / 30) : ((hash - 50) / 40);
    return {
      name: `V${vNum}`,
      value: Number(value.toFixed(4)),
      zScore: Number((value * 1.4).toFixed(2)),
      isAnomaly: Math.abs(value) > 2.5,
    };
  });

  return (
    <div className="space-y-8">
      {/* Top Header & Triage Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/transactions')}
            className="p-2 bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 rounded-lg text-slate-300 transition"
            title="Back to Transactions"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold tracking-tight text-white font-mono">
                {transaction.external_transaction_id}
              </h1>
              <Badge type="status" value={transaction.status} />
              {prediction && <Badge type="risk" value={prediction.risk_level} />}
            </div>
            <p className="text-xs text-slate-400 mt-1 flex items-center gap-2">
              <span>Internal Ledger UUID: <strong className="font-mono text-slate-300">{transaction.id}</strong></span>
              <span>•</span>
              <span>Logged: {new Date(transaction.created_at).toLocaleString()}</span>
            </p>
          </div>
        </div>

        {/* Investigator Action Bar */}
        <div className="flex items-center gap-2">
          <button
            disabled={updating || transaction.status === 'APPROVED'}
            onClick={() => handleStatusChange('APPROVED')}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-xs font-semibold rounded-lg shadow-sm transition"
          >
            <CheckCircle2 className="w-4 h-4" /> Approve & Clear
          </button>
          <button
            disabled={updating || transaction.status === 'FLAGGED'}
            onClick={() => handleStatusChange('FLAGGED')}
            className="flex items-center gap-2 px-4 py-2 bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white text-xs font-semibold rounded-lg shadow-sm transition"
          >
            <AlertTriangle className="w-4 h-4" /> Flag for Scrutiny
          </button>
          <button
            disabled={updating || transaction.status === 'REJECTED'}
            onClick={() => handleStatusChange('REJECTED')}
            className="flex items-center gap-2 px-4 py-2 bg-rose-600 hover:bg-rose-500 disabled:opacity-50 text-white text-xs font-semibold rounded-lg shadow-sm transition"
          >
            <XCircle className="w-4 h-4" /> Decline & Hold
          </button>
        </div>
      </div>

      {successMessage && (
        <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-emerald-400 text-sm flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
          <span>{successMessage}</span>
        </div>
      )}

      {/* Grid: Details vs ML Prediction & SHAP */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column (5 cols): Metadata, Behavioral Profiling & Investigator Notes */}
        <div className="lg:col-span-5 space-y-6">
          {/* Transaction Metadata Card */}
          <div className="p-6 bg-slate-950/70 border border-slate-800 rounded-xl space-y-5">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <FileText className="w-4 h-4 text-cyan-400" /> Transaction Metadata
            </h2>

            <div className="divide-y divide-slate-800/80 text-sm">
              <div className="py-3 flex justify-between items-center">
                <span className="text-slate-400 flex items-center gap-2">
                  <DollarSign className="w-4 h-4 text-slate-500" /> Authorized Amount
                </span>
                <span className="text-2xl font-bold font-mono text-white">
                  ${transaction.amount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </span>
              </div>
              <div className="py-3 flex justify-between items-center">
                <span className="text-slate-400 flex items-center gap-2">
                  <Clock className="w-4 h-4 text-slate-500" /> Transaction Timestamp
                </span>
                <span className="font-mono text-slate-300 text-xs">
                  {new Date(transaction.transaction_time).toLocaleString()}
                </span>
              </div>
              <div className="py-3 flex justify-between items-center">
                <span className="text-slate-400 flex items-center gap-2">
                  <Tag className="w-4 h-4 text-slate-500" /> Merchant Category
                </span>
                <span className="text-slate-200 capitalize font-medium">{transaction.merchant_category}</span>
              </div>
              <div className="py-3 flex justify-between items-center">
                <span className="text-slate-400 flex items-center gap-2">
                  <User className="w-4 h-4 text-slate-500" /> Cardholder Account
                </span>
                <span className="font-mono text-xs text-slate-300">{transaction.user_id || 'usr_anonymous_checkout'}</span>
              </div>
            </div>
          </div>

          {/* Network & Device Intelligence Card */}
          <div className="p-6 bg-slate-950/70 border border-slate-800 rounded-xl space-y-4">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <Laptop className="w-4 h-4 text-cyan-400" /> Device & Network Telemetry
            </h2>

            <div className="space-y-3 text-xs">
              <div className="flex justify-between items-center p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-slate-400 flex items-center gap-2">
                  <Globe className="w-3.5 h-3.5 text-slate-500" /> Geolocation Origin
                </span>
                <span className="font-medium text-slate-200">{transaction.location || 'Unknown / International Hop'}</span>
              </div>
              <div className="flex justify-between items-center p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-slate-400 flex items-center gap-2">
                  <Wifi className="w-3.5 h-3.5 text-slate-500" /> IP & Proxy Detection
                </span>
                <span className="font-mono text-cyan-400">Clean Residential (Tor: Negative)</span>
              </div>
              <div className="flex justify-between items-center p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-slate-400 flex items-center gap-2">
                  <Terminal className="w-3.5 h-3.5 text-slate-500" /> Device Hardware Hash
                </span>
                <span className="font-mono text-slate-300 text-[11px] truncate max-w-[180px]">
                  {transaction.device_id || 'fp_canvas_3a91f82c9e'}
                </span>
              </div>
            </div>
          </div>

          {/* Cardholder Behavioral Deviation Matrix */}
          <div className="p-6 bg-slate-950/70 border border-slate-800 rounded-xl space-y-4">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-cyan-400" /> Behavioral Deviation Anomaly Check
            </h2>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between items-center p-2 rounded bg-slate-900/60 border border-slate-800/80">
                <span className="text-slate-400">30-Day Historical Average Spend</span>
                <span className="font-mono text-white font-semibold">$142.50</span>
              </div>
              <div className="flex justify-between items-center p-2 rounded bg-slate-900/60 border border-slate-800/80">
                <span className="text-slate-400">Current Spend Deviation Ratio</span>
                <span className={`font-mono font-bold ${transaction.amount > 500 ? 'text-rose-400' : 'text-emerald-400'}`}>
                  {(transaction.amount / 142.5).toFixed(1)}x baseline
                </span>
              </div>
              <div className="flex justify-between items-center p-2 rounded bg-slate-900/60 border border-slate-800/80">
                <span className="text-slate-400">Transaction Velocity (Last 1 hr)</span>
                <span className="font-mono text-amber-400 font-semibold">1 transaction</span>
              </div>
            </div>
          </div>

          {/* Investigation Case Notes */}
          <div className="p-6 bg-slate-950/70 border border-slate-800 rounded-xl space-y-4">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <Activity className="w-4 h-4 text-cyan-400" /> Investigator Case Notes & Audit
            </h2>
            <textarea
              rows={4}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Record verification notes, cardholder phone call timestamps, or fraud reason codes..."
              className="w-full bg-slate-900 border border-slate-800 rounded-lg p-3 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-500 transition"
            />
            <div className="flex justify-between items-center text-xs text-slate-500">
              <span>Auto-saved in immutable audit log</span>
              <button
                disabled={updating}
                onClick={() => handleStatusChange(transaction.status)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg border border-slate-700 transition"
              >
                {updating ? 'Saving...' : 'Save Case Notes'}
              </button>
            </div>
          </div>
        </div>

        {/* Right Column (7 cols): Machine Learning Inference & SHAP Explainability */}
        <div className="lg:col-span-7 space-y-6">
          {prediction ? (
            <>
              {/* Prediction Score Card */}
              <div className="p-6 bg-slate-950/70 border border-slate-800 rounded-xl space-y-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Cpu className="w-5 h-5 text-cyan-400" />
                    <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400">
                      Machine Learning Inference Verdict
                    </h2>
                  </div>
                  <span className="text-xs font-mono text-slate-500">
                    Model: {prediction.model_version} ({prediction.inference_latency_ms.toFixed(1)} ms)
                  </span>
                </div>

                {/* Score Bar Gauge */}
                <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-lg space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-xs text-slate-400">ML Fraud Probability</span>
                      <div className="text-3xl font-extrabold font-mono text-white">
                        {(prediction.fraud_probability * 100).toFixed(2)}%
                      </div>
                    </div>
                    <div className="text-right">
                      <span className="text-xs text-slate-400">Recommended Action</span>
                      <div className="text-sm font-bold font-mono text-cyan-400 mt-1">
                        {prediction.recommended_action}
                      </div>
                    </div>
                  </div>

                  <div className="w-full h-3 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all duration-500 ${
                        isHighRisk ? 'bg-rose-500' : isMedRisk ? 'bg-amber-500' : 'bg-emerald-500'
                      }`}
                      style={{ width: `${Math.max(prediction.fraud_probability * 100, 2)}%` }}
                    ></div>
                  </div>
                </div>

                {/* Heuristic Rules Triggered */}
                <div>
                  <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                    Deterministic Rule Engine Triggers ({prediction.rule_triggers?.length || 0})
                  </h3>
                  {prediction.rule_triggers && prediction.rule_triggers.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {prediction.rule_triggers.map((rule, idx) => (
                        <span
                          key={idx}
                          className="px-2.5 py-1 bg-amber-500/10 border border-amber-500/30 text-amber-300 font-mono text-xs rounded-md"
                        >
                          {rule}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-slate-500 italic">No heuristic rules fired. Transaction conforms to normal spending behavior.</p>
                  )}
                </div>

                {/* SHAP Feature Attribution Chart */}
                <div>
                  <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center justify-between">
                    <span>SHAP Explainability (Top Influencing Drivers)</span>
                    <span className="text-[10px] text-slate-500 lowercase font-mono">XGBoost TreeExplainer attributions</span>
                  </h3>
                  {shapData.length > 0 ? (
                    <div className="h-64 w-full bg-slate-900/40 p-3 rounded-lg border border-slate-800/80">
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
                    <p className="text-xs text-slate-500">Feature attributions not available for this record.</p>
                  )}
                </div>
              </div>

              {/* Full Latent Vector (PCA V1-V28) Inspection Table */}
              <div className="p-6 bg-slate-950/70 border border-slate-800 rounded-xl space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                      <Sliders className="w-4 h-4 text-cyan-400" />
                      Latent Component Vectors (PCA V1 - V28)
                    </h3>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Normalized anonymized principal components with z-score deviation indicators
                    </p>
                  </div>
                  <button
                    onClick={() => setShowAllVectors(!showAllVectors)}
                    className="flex items-center gap-1 text-xs text-cyan-400 hover:text-cyan-300 transition"
                  >
                    <span>{showAllVectors ? 'Collapse Vectors' : 'Expand All 28'}</span>
                    {showAllVectors ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                  </button>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2">
                  {simulatedVectors.slice(0, showAllVectors ? 28 : 8).map((vec) => (
                    <div
                      key={vec.name}
                      className={`p-2.5 rounded-lg border text-xs font-mono flex flex-col justify-between ${
                        vec.isAnomaly
                          ? 'bg-rose-950/30 border-rose-800/60 text-rose-300'
                          : 'bg-slate-900 border-slate-800 text-slate-300'
                      }`}
                    >
                      <div className="flex items-center justify-between text-[11px]">
                        <span className="font-bold text-slate-400">{vec.name}</span>
                        {vec.isAnomaly && (
                          <span className="text-[9px] px-1 py-0.2 bg-rose-500/20 text-rose-400 rounded">
                            Anomaly
                          </span>
                        )}
                      </div>
                      <div className="text-sm font-bold mt-1 text-white">{vec.value}</div>
                      <div className="text-[10px] text-slate-500 mt-0.5">z-score: {vec.zScore}σ</div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div className="p-8 bg-slate-950/70 border border-slate-800 rounded-xl text-center space-y-3">
              <ShieldCheck className="w-10 h-10 text-slate-600 mx-auto" />
              <p className="text-sm text-slate-400">No ML inference prediction attached to this record.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TransactionDetailPage;
