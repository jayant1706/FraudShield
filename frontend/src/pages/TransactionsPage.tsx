import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ChevronLeft,
  ChevronRight,
  Download,
  Eye,
  Filter,
  RefreshCw,
  Search,
  ShieldAlert,
  ShieldCheck,
  TrendingDown,
  X,
} from 'lucide-react';
import { Badge } from '../components/common/Badge';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import { transactionService } from '../services/transactionService';
import { Transaction } from '../types';

export const TransactionsPage: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(15);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [riskFilter, setRiskFilter] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchTransactions = async () => {
    setLoading(true);
    try {
      const data = await transactionService.listTransactions({
        page,
        page_size: pageSize,
        search: search || undefined,
        status: statusFilter || undefined,
        risk_level: riskFilter || undefined,
      });
      setTransactions(data.items);
      setTotal(data.total);
      setTotalPages(data.total_pages);
    } catch (err) {
      console.error('Failed to load transactions', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, [page, statusFilter, riskFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchTransactions();
  };

  const handleResetFilters = () => {
    setSearch('');
    setStatusFilter('');
    setRiskFilter('');
    setPage(1);
  };

  // CSV Export utility
  const exportToCSV = () => {
    if (!transactions.length) return;
    const headers = [
      'ID',
      'External_Transaction_ID',
      'Timestamp',
      'Amount',
      'Merchant_Category',
      'Location',
      'Risk_Level',
      'Fraud_Probability',
      'Status',
    ];

    const rows = transactions.map((t) => [
      t.id,
      t.external_transaction_id,
      t.transaction_time,
      t.amount.toFixed(2),
      t.merchant_category,
      t.location || 'Unknown',
      t.prediction?.risk_level || 'LOW',
      t.prediction ? (t.prediction.fraud_probability * 100).toFixed(2) + '%' : 'N/A',
      t.status,
    ]);

    const csvContent =
      'data:text/csv;charset=utf-8,' +
      [headers.join(','), ...rows.map((e) => e.map((x) => `"${x}"`).join(','))].join('\n');

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `fraudshield_ledger_export_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Quick stats computed from current view
  const currentTotalAmount = transactions.reduce((sum, t) => sum + t.amount, 0);
  const currentFlaggedCount = transactions.filter((t) => t.status === 'FLAGGED' || t.prediction?.risk_level === 'HIGH').length;

  return (
    <div className="space-y-6">
      {/* Title & Actions */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <span>Financial Transactions Ledger</span>
            <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-cyan-400 font-mono border border-slate-700">
              Audit-Ready
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time ledger of scored payment events, risk classifications, and investigator decisions
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={exportToCSV}
            disabled={transactions.length === 0}
            className="px-3.5 py-2 rounded-lg bg-slate-850 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs font-semibold transition flex items-center gap-1.5 disabled:opacity-40"
            title="Download CSV Audit Extract"
          >
            <Download className="w-3.5 h-3.5 text-cyan-400" /> Export CSV
          </button>
          <Link
            to="/detect"
            className="px-3.5 py-2 rounded-lg bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-xs font-semibold shadow-lg shadow-cyan-500/20 transition flex items-center gap-1.5"
          >
            <ShieldCheck className="w-4 h-4" /> Score New Transaction
          </Link>
        </div>
      </div>

      {/* Ledger Overview KPI Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs">
          <div className="text-slate-400">Total Filtered Count</div>
          <div className="text-lg font-bold text-white font-mono mt-1">{total.toLocaleString()}</div>
          <div className="text-[10px] text-slate-500 mt-0.5">Database indexed records</div>
        </div>
        <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs">
          <div className="text-slate-400">Page Volume ($)</div>
          <div className="text-lg font-bold text-cyan-400 font-mono mt-1">
            ${currentTotalAmount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">Current page batch gross</div>
        </div>
        <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs">
          <div className="text-slate-400">Flagged / High Risk</div>
          <div className="text-lg font-bold text-rose-400 font-mono mt-1">{currentFlaggedCount}</div>
          <div className="text-[10px] text-slate-500 mt-0.5">Requires investigator triage</div>
        </div>
        <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs">
          <div className="text-slate-400">Risk Policy Enforced</div>
          <div className="text-lg font-bold text-emerald-400 font-mono mt-1">Strict</div>
          <div className="text-[10px] text-slate-500 mt-0.5">Dual ML + Heuristic rules</div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 shadow-lg backdrop-blur space-y-3">
        <form onSubmit={handleSearchSubmit} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-12 gap-3">
          <div className="relative lg:col-span-4">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
            <input
              type="text"
              placeholder="Search by ID, Category, Location..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2 bg-slate-950/80 border border-slate-800 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition"
            />
          </div>

          <div className="lg:col-span-3">
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(1);
              }}
              className="w-full px-3 py-2 bg-slate-950/80 border border-slate-800 rounded-lg text-xs text-slate-300 focus:outline-none focus:border-cyan-500 transition"
            >
              <option value="">All Lifecycle Statuses</option>
              <option value="PENDING">Pending Review</option>
              <option value="FLAGGED">Flagged Suspicious</option>
              <option value="APPROVED">Approved Legitimate</option>
              <option value="REJECTED">Blocked / Rejected</option>
            </select>
          </div>

          <div className="lg:col-span-3">
            <select
              value={riskFilter}
              onChange={(e) => {
                setRiskFilter(e.target.value);
                setPage(1);
              }}
              className="w-full px-3 py-2 bg-slate-950/80 border border-slate-800 rounded-lg text-xs text-slate-300 focus:outline-none focus:border-cyan-500 transition"
            >
              <option value="">All Risk Tiers</option>
              <option value="LOW">Low Risk (&lt; 0.30)</option>
              <option value="MEDIUM">Medium Risk (0.30 - 0.70)</option>
              <option value="HIGH">High Risk (&ge; 0.70)</option>
            </select>
          </div>

          <div className="lg:col-span-2 flex items-center gap-2">
            <button
              type="submit"
              className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold rounded-lg transition"
            >
              <Filter className="w-3.5 h-3.5" /> Filter
            </button>
            {(search || statusFilter || riskFilter) && (
              <button
                type="button"
                onClick={handleResetFilters}
                className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white rounded-lg transition"
                title="Reset Filters"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        </form>

        {/* Quick Filter Presets */}
        <div className="flex flex-wrap items-center gap-2 pt-1 border-t border-slate-800/60 text-xs">
          <span className="text-[11px] text-slate-500 font-medium">Quick Presets:</span>
          <button
            onClick={() => {
              setStatusFilter('');
              setRiskFilter('');
              setPage(1);
            }}
            className={`px-2 py-0.5 rounded text-[11px] transition ${
              !statusFilter && !riskFilter
                ? 'bg-slate-800 text-cyan-400 font-semibold'
                : 'text-slate-400 hover:text-white hover:bg-slate-850'
            }`}
          >
            All Ledger
          </button>
          <button
            onClick={() => {
              setStatusFilter('FLAGGED');
              setRiskFilter('HIGH');
              setPage(1);
            }}
            className={`px-2 py-0.5 rounded text-[11px] transition ${
              statusFilter === 'FLAGGED' && riskFilter === 'HIGH'
                ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40 font-semibold'
                : 'text-rose-400/80 hover:text-rose-300 hover:bg-rose-500/10'
            }`}
          >
            Critical High Risk
          </button>
          <button
            onClick={() => {
              setStatusFilter('APPROVED');
              setRiskFilter('LOW');
              setPage(1);
            }}
            className={`px-2 py-0.5 rounded text-[11px] transition ${
              statusFilter === 'APPROVED' && riskFilter === 'LOW'
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-semibold'
                : 'text-emerald-400/80 hover:text-emerald-300 hover:bg-emerald-500/10'
            }`}
          >
            Approved Legitimate
          </button>
        </div>
      </div>

      {/* Transactions Table */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur">
        {loading ? (
          <LoadingSkeleton rows={10} />
        ) : transactions.length === 0 ? (
          <div className="text-center py-16 text-slate-500 text-xs space-y-2">
            <ShieldAlert className="w-8 h-8 text-slate-600 mx-auto" />
            <div>No transactions matching query criteria found in database ledger.</div>
            {(search || statusFilter || riskFilter) && (
              <button
                onClick={handleResetFilters}
                className="text-cyan-400 hover:text-cyan-300 underline font-medium"
              >
                Clear active filters
              </button>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider font-semibold">
                <tr>
                  <th className="pb-3 px-3">Transaction ID</th>
                  <th className="pb-3 px-3">Date & Time</th>
                  <th className="pb-3 px-3">Amount</th>
                  <th className="pb-3 px-3">Category</th>
                  <th className="pb-3 px-3">Location</th>
                  <th className="pb-3 px-3">Risk Tier</th>
                  <th className="pb-3 px-3">Probability</th>
                  <th className="pb-3 px-3">Status</th>
                  <th className="pb-3 px-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {transactions.map((txn) => (
                  <tr key={txn.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3 px-3 font-mono font-medium text-slate-200">
                      {txn.external_transaction_id}
                    </td>
                    <td className="py-3 px-3 text-slate-400 font-mono">
                      {new Date(txn.transaction_time).toLocaleString()}
                    </td>
                    <td className="py-3 px-3 font-mono font-semibold text-white">
                      ${txn.amount.toFixed(2)}
                    </td>
                    <td className="py-3 px-3 text-slate-300 capitalize">
                      {txn.merchant_category}
                    </td>
                    <td className="py-3 px-3 text-slate-400">
                      {txn.location || 'Unknown'}
                    </td>
                    <td className="py-3 px-3">
                      <Badge type="risk" value={txn.prediction?.risk_level || 'LOW'} />
                    </td>
                    <td className="py-3 px-3 font-mono font-medium">
                      {txn.prediction ? (
                        <span
                          className={
                            txn.prediction.fraud_probability >= 0.7
                              ? 'text-red-400 font-bold'
                              : txn.prediction.fraud_probability >= 0.3
                              ? 'text-amber-400'
                              : 'text-emerald-400'
                          }
                        >
                          {(txn.prediction.fraud_probability * 100).toFixed(1)}%
                        </span>
                      ) : (
                        <span className="text-slate-600">N/A</span>
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
                        <Eye className="w-3.5 h-3.5" /> Inspect
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Footer */}
        <div className="flex items-center justify-between border-t border-slate-800/80 pt-4 mt-4 text-xs text-slate-400">
          <div>
            Showing <span className="font-semibold text-slate-200">{transactions.length}</span> of{' '}
            <span className="font-semibold text-slate-200">{total}</span> total transactions
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="p-1.5 rounded-lg border border-slate-800 hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed text-slate-300"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="font-mono text-slate-300">
              Page {page} of {totalPages || 1}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="p-1.5 rounded-lg border border-slate-800 hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed text-slate-300"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
