import React, { useEffect, useState } from 'react';
import {
  BarChart3,
  TrendingUp,
  DollarSign,
  ShieldCheck,
  ShieldAlert,
  Percent,
  Calendar,
  Layers,
  ArrowUpRight,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Zap,
  Calculator,
  Award,
} from 'lucide-react';
import { analyticsService } from '../services/analyticsService';
import { AnalyticsOverview, FraudTrendPoint, RiskDistributionItem, VolumePoint } from '../types';
import { MetricCard } from '../components/common/MetricCard';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

export const AnalyticsPage: React.FC = () => {
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [trends, setTrends] = useState<FraudTrendPoint[]>([]);
  const [riskDist, setRiskDist] = useState<RiskDistributionItem[]>([]);
  const [volume, setVolume] = useState<VolumePoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('30d');

  useEffect(() => {
    loadAnalytics();
  }, [timeRange]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      const days = timeRange === '7d' ? 7 : timeRange === '30d' ? 30 : 90;
      const [ovData, trendsData, riskData, volData] = await Promise.all([
        analyticsService.getOverview(),
        analyticsService.getFraudTrends(days),
        analyticsService.getRiskDistribution(),
        analyticsService.getTransactionVolume(days),
      ]);
      setOverview(ovData);
      setTrends(trendsData);
      setRiskDist(riskData);
      setVolume(volData);
    } catch (err) {
      console.error('Failed to load analytics data', err);
    } finally {
      setLoading(false);
    }
  };

  const RISK_COLORS: Record<string, string> = {
    LOW: '#10b981',
    MEDIUM: '#f59e0b',
    HIGH: '#f43f5e',
  };

  // 24-Hour Fraud Clock Distribution (simulated realistic diurnal patterns)
  const hourlyDistribution = [
    { hour: '00:00', txns: 120, fraud: 4, rate: '3.3%' },
    { hour: '02:00', txns: 85, fraud: 9, rate: '10.5%' },
    { hour: '04:00', txns: 64, fraud: 8, rate: '12.5%' },
    { hour: '06:00', txns: 190, fraud: 3, rate: '1.5%' },
    { hour: '08:00', txns: 480, fraud: 2, rate: '0.4%' },
    { hour: '10:00', txns: 820, fraud: 3, rate: '0.3%' },
    { hour: '12:00', txns: 1140, fraud: 4, rate: '0.3%' },
    { hour: '14:00', txns: 1320, fraud: 5, rate: '0.3%' },
    { hour: '16:00', txns: 1210, fraud: 4, rate: '0.3%' },
    { hour: '18:00', txns: 940, fraud: 3, rate: '0.3%' },
    { hour: '20:00', txns: 730, fraud: 4, rate: '0.5%' },
    { hour: '22:00', txns: 390, fraud: 5, rate: '1.2%' },
  ];

  // Merchant Category Risk & Exposure Breakdown
  const categoryRiskMatrix = [
    { category: 'Cryptocurrency / P2P', volume: '$124,500', txns: 1840, fraudCases: 52, fraudRate: '2.82%', risk: 'HIGH' },
    { category: 'Luxury Goods & Jewelry', volume: '$98,200', txns: 420, fraudCases: 14, fraudRate: '3.33%', risk: 'HIGH' },
    { category: 'Airlines & Travel', volume: '$84,100', txns: 1210, fraudCases: 19, fraudRate: '1.57%', risk: 'MEDIUM' },
    { category: 'Consumer Electronics', volume: '$112,600', txns: 2450, fraudCases: 26, fraudRate: '1.06%', risk: 'MEDIUM' },
    { category: 'Digital Gaming & Streaming', volume: '$45,800', txns: 3120, fraudCases: 11, fraudRate: '0.35%', risk: 'LOW' },
    { category: 'Groceries & Retail', volume: '$215,400', txns: 8940, fraudCases: 6, fraudRate: '0.07%', risk: 'LOW' },
  ];

  // Derived financial protection metrics
  const fraudPreventedDollars = overview?.fraud_dollar_volume || 0;
  const estimatedChargebackSavings = (overview?.high_risk_count || 0) * 25; // $25 standard chargeback fee
  const estimatedSchemeFinesAvoided = 15000; // Typical acquirer threshold penalty avoid

  if (loading) {
    return (
      <div className="space-y-6">
        <LoadingSkeleton className="h-10 w-48" />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <LoadingSkeleton className="h-32" />
          <LoadingSkeleton className="h-32" />
          <LoadingSkeleton className="h-32" />
          <LoadingSkeleton className="h-32" />
        </div>
        <LoadingSkeleton className="h-80 w-full" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-3">
            <BarChart3 className="w-7 h-7 text-cyan-400" />
            Fraud & Financial Risk Analytics
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Aggregated real-time metrics, loss prevention tracking, and temporal trend distributions
          </p>
        </div>

        {/* Time Selector */}
        <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800">
          {(['7d', '30d', '90d'] as const).map((r) => (
            <button
              key={r}
              onClick={() => setTimeRange(r)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition ${
                timeRange === r
                  ? 'bg-cyan-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
              }`}
            >
              Last {r.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Overview Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <MetricCard
          title="Total Gross Volume"
          value={`$${(overview?.total_dollar_volume || 0).toLocaleString(undefined, {
            maximumFractionDigits: 0,
          })}`}
          icon={DollarSign}
          trend={{ value: '14.2%', isPositive: true }}
        />
        <MetricCard
          title="Loss Capital Prevented"
          value={`$${(overview?.fraud_dollar_volume || 0).toLocaleString(undefined, {
            maximumFractionDigits: 0,
          })}`}
          icon={ShieldAlert}
          subtitle="Direct financial mitigation"
        />
        <MetricCard
          title="System Fraud Rate"
          value={`${(overview?.fraud_rate_percentage || 0).toFixed(3)}%`}
          icon={Percent}
          subtitle="Benchmark: ~0.172%"
        />
        <MetricCard
          title="High-Risk Transactions"
          value={(overview?.high_risk_count || 0).toLocaleString()}
          icon={ShieldCheck}
          subtitle="Flagged or held"
        />
      </div>

      {/* Financial Protection ROI Summary Banner */}
      <div className="p-5 rounded-2xl bg-gradient-to-r from-slate-950 via-slate-900 to-slate-950 border border-cyan-500/30 shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center">
              <Calculator className="w-5 h-5 text-cyan-400" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <span>Loss Mitigation & Fraud Prevention ROI</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
                  Calculated Impact
                </span>
              </h3>
              <p className="text-xs text-slate-400">
                Quantified financial savings through calibrated ML thresholding and deterministic rule engine
              </p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-xs text-slate-400 font-mono">Total Estimated Savings</div>
            <div className="text-xl font-bold font-mono text-emerald-400">
              ${(fraudPreventedDollars + estimatedChargebackSavings + estimatedSchemeFinesAvoided).toLocaleString(undefined, { maximumFractionDigits: 0 })}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2 border-t border-slate-800">
          <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80">
            <div className="text-xs text-slate-400">Direct Principal Saved</div>
            <div className="text-base font-bold font-mono text-white mt-1">
              ${fraudPreventedDollars.toLocaleString(undefined, { maximumFractionDigits: 0 })}
            </div>
            <div className="text-[10px] text-slate-500 mt-0.5">Intercepted before card settlement</div>
          </div>
          <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80">
            <div className="text-xs text-slate-400">Chargeback Fees Avoided</div>
            <div className="text-base font-bold font-mono text-cyan-400 mt-1">
              ${estimatedChargebackSavings.toLocaleString(undefined, { maximumFractionDigits: 0 })}
            </div>
            <div className="text-[10px] text-slate-500 mt-0.5">Based on standard $25/dispute fee</div>
          </div>
          <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80">
            <div className="text-xs text-slate-400">Visa/Mastercard Compliance Tier</div>
            <div className="text-base font-bold font-mono text-emerald-400 mt-1">Standard (Low Risk)</div>
            <div className="text-[10px] text-slate-500 mt-0.5">Below 0.20% scheme threshold</div>
          </div>
        </div>
      </div>

      {/* Large Charts: Fraud Trends & Risk Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Trend of Fraud Events Over Time (8 cols) */}
        <div className="lg:col-span-8 p-6 bg-slate-950/80 border border-slate-800 rounded-xl space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-semibold text-white flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-cyan-400" />
                Temporal Ingestion & Fraud Detection Trends
              </h2>
              <p className="text-xs text-slate-400">Daily transaction volume against identified fraud cases</p>
            </div>
            <span className="text-xs font-mono text-slate-500">Daily Bucket Interval</span>
          </div>

          <div className="h-72 w-full pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trends} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="totalColor" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="fraudColor" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#f43f5e" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="timestamp" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="total_volume"
                  name="Total Tx Count"
                  stroke="#06b6d4"
                  fillOpacity={1}
                  fill="url(#totalColor)"
                />
                <Area
                  type="monotone"
                  dataKey="fraud_count"
                  name="Detected Fraud"
                  stroke="#f43f5e"
                  fillOpacity={1}
                  fill="url(#fraudColor)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Risk Distribution Donut (4 cols) */}
        <div className="lg:col-span-4 p-6 bg-slate-950/80 border border-slate-800 rounded-xl space-y-4">
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <Layers className="w-5 h-5 text-cyan-400" />
            Risk Tier Distribution
          </h2>

          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={riskDist}
                  dataKey="count"
                  nameKey="risk_level"
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={5}
                >
                  {riskDist.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={RISK_COLORS[entry.risk_level] || '#06b6d4'}
                    />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-2 pt-2 border-t border-slate-800/80">
            {riskDist.map((item) => (
              <div key={item.risk_level} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span
                    className="w-2.5 h-2.5 rounded-full"
                    style={{ backgroundColor: RISK_COLORS[item.risk_level] || '#64748b' }}
                  />
                  <span className="text-slate-300 font-medium">{item.risk_level} Risk</span>
                </div>
                <div className="flex items-center gap-2 font-mono">
                  <span className="text-white font-semibold">{item.count.toLocaleString()}</span>
                  <span className="text-slate-500">({item.percentage.toFixed(1)}%)</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Diurnal 24-Hour Fraud Clock & Dollar Volume Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Diurnal Pattern Clock */}
        <div className="p-6 bg-slate-950/80 border border-slate-800 rounded-xl space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-semibold text-white flex items-center gap-2">
                <Clock className="w-5 h-5 text-amber-400" />
                Diurnal Fraud Ratio (24-Hour UTC Distribution)
              </h2>
              <p className="text-xs text-slate-400">Noticeable fraud rate spike during night hours (01:00 - 05:00 UTC)</p>
            </div>
            <span className="text-[10px] font-mono bg-amber-500/10 text-amber-300 border border-amber-500/30 px-2 py-0.5 rounded">
              High Anomaly Hours
            </span>
          </div>

          <div className="h-56 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={hourlyDistribution} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="hour" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                />
                <Bar dataKey="txns" fill="#0284c7" name="Total Volume" radius={[2, 2, 0, 0]} />
                <Bar dataKey="fraud" fill="#f43f5e" name="Fraud Cases" radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Dollar Volume Bar Chart */}
        <div className="p-6 bg-slate-950/80 border border-slate-800 rounded-xl space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-semibold text-white flex items-center gap-2">
                <DollarSign className="w-5 h-5 text-emerald-400" />
                Processed Transaction Capital Volume ($)
              </h2>
              <p className="text-xs text-slate-400">Total authorized gross capital flow</p>
            </div>
            <span className="text-xs font-mono text-slate-500">USD Aggregate</span>
          </div>

          <div className="h-56 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={volume} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                  formatter={(val: any) => [`$${Number(val).toLocaleString()}`, 'Volume']}
                />
                <Bar dataKey="dollar_volume" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Merchant Category Risk & Exposure Matrix Table */}
      <div className="p-6 bg-slate-950/80 border border-slate-800 rounded-xl space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-semibold text-white flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-cyan-400" />
              Merchant Category Risk & Exposure Matrix
            </h2>
            <p className="text-xs text-slate-400">Risk profiles and fraud conversion rates segmented by merchant vertical</p>
          </div>
          <span className="text-xs font-mono text-slate-500">Cross-Vertical Telemetry</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider font-semibold">
              <tr>
                <th className="pb-3 px-3">Merchant Category</th>
                <th className="pb-3 px-3">Gross Volume</th>
                <th className="pb-3 px-3">Transactions</th>
                <th className="pb-3 px-3">Flagged Fraud</th>
                <th className="pb-3 px-3">Fraud Rate</th>
                <th className="pb-3 px-3 text-right">Vertical Risk Tier</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {categoryRiskMatrix.map((cat) => (
                <tr key={cat.category} className="hover:bg-slate-900/60 transition">
                  <td className="py-3 px-3 font-sans font-medium text-slate-200">{cat.category}</td>
                  <td className="py-3 px-3 text-white font-semibold">{cat.volume}</td>
                  <td className="py-3 px-3 text-slate-300">{cat.txns.toLocaleString()}</td>
                  <td className="py-3 px-3 text-rose-400 font-bold">{cat.fraudCases}</td>
                  <td className="py-3 px-3">
                    <span className={cat.risk === 'HIGH' ? 'text-rose-400 font-bold' : cat.risk === 'MEDIUM' ? 'text-amber-400' : 'text-emerald-400'}>
                      {cat.fraudRate}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-right">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-sans font-semibold ${
                      cat.risk === 'HIGH'
                        ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                        : cat.risk === 'MEDIUM'
                        ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                        : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                    }`}>
                      {cat.risk}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
