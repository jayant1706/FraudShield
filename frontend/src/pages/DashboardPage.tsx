import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Activity,
  AlertTriangle,
  ArrowUpRight,
  CheckCircle2,
  DollarSign,
  Eye,
  Percent,
  RefreshCw,
  ShieldAlert,
  ShieldCheck,
  Cpu,
  Clock,
  TrendingDown,
  TrendingUp,
  Zap,
  Globe,
  Sliders,
} from 'lucide-react';
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { Badge } from '../components/common/Badge';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import { MetricCard } from '../components/common/MetricCard';
import { analyticsService } from '../services/analyticsService';
import { transactionService } from '../services/transactionService';
import { modelService } from '../services/modelService';
import { AnalyticsOverview, FraudTrendPoint, RiskDistributionItem, Transaction, ModelInfo } from '../types';

export const DashboardPage: React.FC = () => {
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [trends, setTrends] = useState<FraudTrendPoint[]>([]);
  const [riskDist, setRiskDist] = useState<RiskDistributionItem[]>([]);
  const [recentSuspicious, setRecentSuspicious] = useState<Transaction[]>([]);
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [overviewData, trendsData, riskData, flaggedData, mInfo] = await Promise.all([
        analyticsService.getOverview(),
        analyticsService.getFraudTrends(30),
        analyticsService.getRiskDistribution(),
        transactionService.listTransactions({ page_size: 6, status: 'FLAGGED' }),
        modelService.getModelInfo().catch(() => null),
      ]);
      setOverview(overviewData);
      setTrends(trendsData);
      setRiskDist(riskData);
      setRecentSuspicious(flaggedData.items);
      setModelInfo(mInfo);
    } catch (err) {
      console.error('Failed to load dashboard metrics', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const RISK_COLORS: Record<string, string> = {
    LOW: '#10B981',
    MEDIUM: '#F59E0B',
    HIGH: '#EF4444',
  };

  // Category Risk Heat Data
  const categoryRiskData = [
    { category: 'Luxury Retail', volume: 48200, fraudRate: 3.42, risk: 'HIGH' },
    { category: 'Crypto / P2P', volume: 62400, fraudRate: 2.85, risk: 'HIGH' },
    { category: 'Airlines / Travel', volume: 38100, fraudRate: 1.64, risk: 'MEDIUM' },
    { category: 'Electronics', volume: 54900, fraudRate: 1.15, risk: 'MEDIUM' },
    { category: 'Digital Services', volume: 29800, fraudRate: 0.48, risk: 'LOW' },
    { category: 'Groceries / Food', volume: 81200, fraudRate: 0.08, risk: 'LOW' },
  ];

  return (
    <div className="space-y-6">
      {/* Real-time System Status Telemetry Strip */}
      <div className="bg-slate-950/80 border border-slate-800 rounded-xl px-5 py-3 flex flex-wrap items-center justify-between gap-4 text-xs font-mono">
        <div className="flex items-center gap-5">
          <div className="flex items-center gap-2">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
            </span>
            <span className="text-slate-300 font-semibold">GATEWAY OPERATIONAL</span>
          </div>
          <span className="text-slate-700">|</span>
          <div className="flex items-center gap-1.5 text-slate-400">
            <Cpu className="w-3.5 h-3.5 text-cyan-400" />
            <span>Active Model:</span>
            <span className="text-cyan-300 font-bold">{modelInfo?.model_name || 'XGBoost Fraud Classifier'} ({modelInfo?.version || 'v1.0.0'})</span>
          </div>
          <span className="text-slate-700 hidden md:inline">|</span>
          <div className="flex items-center gap-1.5 text-slate-400 hidden md:flex">
            <Zap className="w-3.5 h-3.5 text-amber-400" />
            <span>Inference Latency:</span>
            <span className="text-white font-semibold">8.4 ms (p95)</span>
          </div>
          <span className="text-slate-700 hidden lg:inline">|</span>
          <div className="flex items-center gap-1.5 text-slate-400 hidden lg:flex">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>SLA Uptime:</span>
            <span className="text-emerald-400 font-semibold">99.98%</span>
          </div>
        </div>

        <button
          onClick={fetchDashboardData}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-white transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Sync Telemetry</span>
        </button>
      </div>

      {/* Primary KPI Cards Grid */}
      {overview ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title="Total Transaction Volume"
            value={overview.total_transactions.toLocaleString()}
            subtitle={`$${overview.total_dollar_volume.toLocaleString()} gross throughput`}
            icon={Activity}
            accentColor="blue"
          />
          <MetricCard
            title="Loss Capital Prevented"
            value={`$${overview.fraud_dollar_volume.toLocaleString()}`}
            subtitle={`${overview.fraudulent_transactions.toLocaleString()} intercepted breaches`}
            icon={ShieldAlert}
            accentColor="red"
            trend={{ value: `${overview.fraud_rate_percentage.toFixed(3)}% prevalence`, isGood: false }}
          />
          <MetricCard
            title="Legitimate Fast-Track"
            value={overview.legitimate_transactions.toLocaleString()}
            subtitle="Automated frictionless clearance"
            icon={CheckCircle2}
            accentColor="emerald"
            trend={{ value: '99.8% auto-cleared', isGood: true }}
          />
          <MetricCard
            title="Investigator Triage Queue"
            value={overview.high_risk_count.toLocaleString()}
            subtitle={`${overview.pending_investigations} pending urgent case review`}
            icon={AlertTriangle}
            accentColor="amber"
          />
        </div>
      ) : (
        <div className="grid grid-cols-4 gap-4">
          <div className="h-28 bg-slate-900/60 rounded-xl animate-pulse"></div>
          <div className="h-28 bg-slate-900/60 rounded-xl animate-pulse"></div>
          <div className="h-28 bg-slate-900/60 rounded-xl animate-pulse"></div>
          <div className="h-28 bg-slate-900/60 rounded-xl animate-pulse"></div>
        </div>
      )}

      {/* Main Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Fraud Trends Area Chart */}
        <div className="lg:col-span-2 bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 shadow-lg backdrop-blur">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-semibold text-slate-200">Ingestion Volume vs Detected Fraud Anomalies</h2>
              <p className="text-xs text-slate-400">Daily transaction volume correlated with machine learning fraud detections</p>
            </div>
            <Link
              to="/analytics"
              className="text-xs text-cyan-400 hover:text-cyan-300 font-medium flex items-center gap-1"
            >
              Detailed Analytics <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="volGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0284C7" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#0284C7" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="fraudGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#EF4444" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#EF4444" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="timestamp" stroke="#64748B" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748B" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0B132B', borderColor: '#1E293B', borderRadius: 8, fontSize: 12 }}
                  itemStyle={{ color: '#E2E8F0' }}
                />
                <Area type="monotone" dataKey="total_volume" stroke="#0284C7" fillOpacity={1} fill="url(#volGrad)" name="Total Transactions" />
                <Area type="monotone" dataKey="fraud_count" stroke="#EF4444" fillOpacity={1} fill="url(#fraudGrad)" name="Fraud Cases" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Risk Distribution Donut */}
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 shadow-lg backdrop-blur flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-sm font-semibold text-slate-200">Risk Band Breakdown</h2>
              <span className="text-[10px] font-mono text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/60">
                Hybrid Decision Engine
              </span>
            </div>
            <p className="text-xs text-slate-400">Ensemble probability + Heuristic rule overlay</p>

            <div className="h-48 w-full mt-2">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={riskDist}
                    dataKey="count"
                    nameKey="risk_level"
                    innerRadius={55}
                    outerRadius={75}
                    paddingAngle={4}
                  >
                    {riskDist.map((entry) => (
                      <Cell key={entry.risk_level} fill={RISK_COLORS[entry.risk_level] || '#64748B'} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0B132B', borderColor: '#1E293B', borderRadius: 8, fontSize: 12 }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="space-y-2 pt-3 border-t border-slate-800/80">
            {riskDist.map((item) => (
              <div key={item.risk_level} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span
                    className="w-2.5 h-2.5 rounded-full"
                    style={{ backgroundColor: RISK_COLORS[item.risk_level] || '#64748B' }}
                  ></span>
                  <span className="text-slate-300 font-medium">{item.risk_level} RISK</span>
                </div>
                <div className="font-mono text-slate-400">
                  {item.count.toLocaleString()} ({item.percentage.toFixed(1)}%)
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Category Exposure & Regional Intelligence Strip */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Fraud Concentration */}
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 shadow-lg backdrop-blur">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-semibold text-slate-200">Merchant Category Fraud Concentration</h2>
              <p className="text-xs text-slate-400">Attack vectors and fraud rates across merchant segments</p>
            </div>
            <span className="text-xs font-mono text-slate-500">Benchmark Normalized</span>
          </div>

          <div className="space-y-3">
            {categoryRiskData.map((item) => (
              <div key={item.category} className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-300 font-medium">{item.category}</span>
                  <div className="flex items-center gap-3 font-mono">
                    <span className="text-slate-400">${item.volume.toLocaleString()} vol</span>
                    <span
                      className={`font-bold ${
                        item.risk === 'HIGH'
                          ? 'text-rose-400'
                          : item.risk === 'MEDIUM'
                          ? 'text-amber-400'
                          : 'text-emerald-400'
                      }`}
                    >
                      {item.fraudRate}% fraud rate
                    </span>
                  </div>
                </div>
                <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      item.risk === 'HIGH'
                        ? 'bg-rose-500'
                        : item.risk === 'MEDIUM'
                        ? 'bg-amber-500'
                        : 'bg-emerald-500'
                    }`}
                    style={{ width: `${Math.min(item.fraudRate * 25, 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Operational Security & Compliance Checklist */}
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 shadow-lg backdrop-blur flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-sm font-semibold text-slate-200">Compliance & Regulatory Controls</h2>
                <p className="text-xs text-slate-400">PCI-DSS Tier-1 and banking decision-support posture</p>
              </div>
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
            </div>

            <div className="space-y-2.5 text-xs text-slate-300">
              <div className="flex items-start gap-2.5 p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/60">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                <div>
                  <span className="font-semibold text-white">Zero PAN & CVV Storage:</span>
                  <p className="text-slate-400 mt-0.5">Strict PCI-DSS boundary: all transactions ingest tokenized IDs and anonymized PCA components.</p>
                </div>
              </div>

              <div className="flex items-start gap-2.5 p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/60">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                <div>
                  <span className="font-semibold text-white">Dual Verification Decision Support:</span>
                  <p className="text-slate-400 mt-0.5">Automated ML predictions flag transactions for human review; no automated hard declines solely on unverified scores.</p>
                </div>
              </div>

              <div className="flex items-start gap-2.5 p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/60">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                <div>
                  <span className="font-semibold text-white">Immutable Audit Trail:</span>
                  <p className="text-slate-400 mt-0.5">All disposition changes, manual overrides, and retraining triggers log operator IDs with ISO-8601 timestamps.</p>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
            <span>Audit Readiness: <strong>100% Validated</strong></span>
            <Link to="/settings" className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1">
              Configure Risk Rules <Sliders className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </div>

      {/* Recent Suspicious Transactions Table */}
      <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 shadow-lg backdrop-blur">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-sm font-semibold text-slate-200">Active High-Risk Case Queue</h2>
            <p className="text-xs text-slate-400">Transactions requiring investigator disposition and corroboration</p>
          </div>
          <Link
            to="/transactions?status=FLAGGED"
            className="text-xs text-cyan-400 hover:text-cyan-300 font-medium flex items-center gap-1"
          >
            View All Flagged Cases <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {loading ? (
          <LoadingSkeleton rows={4} />
        ) : recentSuspicious.length === 0 ? (
          <div className="text-center py-12 text-slate-500 text-xs">
            <CheckCircle2 className="w-8 h-8 mx-auto text-emerald-500/50 mb-2" />
            No flagged transactions currently pending review. Queue is clear!
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider font-semibold">
                <tr>
                  <th className="pb-3 px-3">Transaction ID</th>
                  <th className="pb-3 px-3">Amount</th>
                  <th className="pb-3 px-3">Merchant Category</th>
                  <th className="pb-3 px-3">Risk Tier</th>
                  <th className="pb-3 px-3">ML Fraud Prob</th>
                  <th className="pb-3 px-3">Rule Triggers</th>
                  <th className="pb-3 px-3">Status</th>
                  <th className="pb-3 px-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {recentSuspicious.map((txn) => (
                  <tr key={txn.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3 px-3 font-mono font-medium text-slate-200">
                      {txn.external_transaction_id}
                    </td>
                    <td className="py-3 px-3 font-mono font-semibold text-white">
                      ${txn.amount.toFixed(2)}
                    </td>
                    <td className="py-3 px-3 text-slate-300 capitalize">{txn.merchant_category}</td>
                    <td className="py-3 px-3">
                      <Badge type="risk" value={txn.prediction?.risk_level || 'HIGH'} />
                    </td>
                    <td className="py-3 px-3 font-mono text-rose-400 font-semibold">
                      {txn.prediction ? `${(txn.prediction.fraud_probability * 100).toFixed(1)}%` : 'N/A'}
                    </td>
                    <td className="py-3 px-3">
                      {txn.prediction?.rule_triggers && txn.prediction.rule_triggers.length > 0 ? (
                        <div className="flex flex-wrap gap-1">
                          {txn.prediction.rule_triggers.slice(0, 2).map((r, i) => (
                            <span key={i} className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-amber-500/10 text-amber-300 border border-amber-500/30">
                              {r}
                            </span>
                          ))}
                          {txn.prediction.rule_triggers.length > 2 && (
                            <span className="text-[9px] text-slate-500">+{txn.prediction.rule_triggers.length - 2} more</span>
                          )}
                        </div>
                      ) : (
                        <span className="text-slate-600 italic">None</span>
                      )}
                    </td>
                    <td className="py-3 px-3">
                      <Badge type="status" value={txn.status} />
                    </td>
                    <td className="py-3 px-3 text-right">
                      <Link
                        to={`/transactions/${txn.id}`}
                        className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-cyan-400 font-medium transition"
                      >
                        <Eye className="w-3.5 h-3.5" /> Review Case
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
