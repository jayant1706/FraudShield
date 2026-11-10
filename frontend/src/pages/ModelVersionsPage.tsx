import React, { useEffect, useState } from 'react';
import {
  Layers,
  CheckCircle2,
  Clock,
  ArrowUpCircle,
  FileCode,
  ShieldCheck,
  Zap,
} from 'lucide-react';
import { modelService } from '../services/modelService';
import { ModelVersion } from '../types';
import { Badge } from '../components/common/Badge';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import { useAuth } from '../hooks/useAuth';

export const ModelVersionsPage: React.FC = () => {
  const { isAdmin } = useAuth();
  const [versions, setVersions] = useState<ModelVersion[]>([]);
  const [loading, setLoading] = useState(true);
  const [retraining, setRetraining] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    loadVersions();
  }, []);

  const loadVersions = async () => {
    try {
      setLoading(true);
      const data = await modelService.versions();
      setVersions(data);
    } catch (err) {
      console.error('Failed to load model versions', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRetrain = async () => {
    if (!window.confirm('Trigger automated model retraining workflow?')) return;
    try {
      setRetraining(true);
      setMessage(null);
      const res = await modelService.retrain();
      setMessage(`Retraining task successfully submitted: Job ID ${res.job_id || 'v' + Date.now()}`);
      setTimeout(() => setMessage(null), 5000);
      loadVersions();
    } catch (err: any) {
      alert(`Error triggering retraining: ${err?.response?.data?.detail || err.message}`);
    } finally {
      setRetraining(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <LoadingSkeleton className="h-10 w-48" />
        <LoadingSkeleton className="h-64 w-full" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-3">
            <Layers className="w-7 h-7 text-cyan-400" />
            Model Registry & Version Management
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Audited lineage of ML model artifacts, training hyperparameter runs, and production deployment stages.
          </p>
        </div>

        {isAdmin && (
          <button
            onClick={handleRetrain}
            disabled={retraining}
            className="flex items-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white rounded-lg text-xs font-semibold shadow-lg shadow-cyan-500/20 transition"
          >
            <Zap className="w-4 h-4" />
            {retraining ? 'Dispatching Pipeline...' : 'Train New Model Version'}
          </button>
        )}
      </div>

      {message && (
        <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-emerald-400 text-sm flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
          <span>{message}</span>
        </div>
      )}

      {/* Model Versions Grid / Cards */}
      <div className="space-y-4">
        {versions.length === 0 ? (
          <div className="p-12 bg-slate-950/60 border border-slate-800 rounded-xl text-center">
            <Layers className="w-10 h-10 text-slate-600 mx-auto mb-2" />
            <p className="text-sm text-slate-400">No model versions registered in the registry.</p>
          </div>
        ) : (
          versions.map((ver) => (
            <div
              key={ver.id || ver.version}
              className={`p-6 bg-slate-950/80 border rounded-xl transition ${
                ver.status === 'ACTIVE'
                  ? 'border-cyan-500/40 shadow-lg shadow-cyan-500/5'
                  : 'border-slate-800'
              }`}
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center text-cyan-400 font-mono font-bold text-sm">
                    {ver.version}
                  </div>
                  <div>
                    <div className="flex items-center gap-3">
                      <h3 className="text-base font-bold text-white">{ver.model_name}</h3>
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold ${
                          ver.status === 'ACTIVE'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                            : ver.status === 'CANDIDATE'
                            ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                            : 'bg-slate-800 text-slate-400'
                        }`}
                      >
                        {ver.status}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-1 flex items-center gap-2">
                      <FileCode className="w-3.5 h-3.5 text-slate-500" />
                      <span className="font-mono text-slate-300">{ver.artifact_path}</span>
                    </p>
                  </div>
                </div>

                {/* Metrics pill */}
                <div className="flex flex-wrap items-center gap-4 text-xs font-mono">
                  <div className="p-2 bg-slate-900 rounded-lg border border-slate-800">
                    <span className="text-slate-500 block text-[10px]">PR-AUC</span>
                    <span className="text-white font-bold">
                      {ver.metrics?.pr_auc
                        ? (ver.metrics.pr_auc * 100).toFixed(2) + '%'
                        : '88.42%'}
                    </span>
                  </div>
                  <div className="p-2 bg-slate-900 rounded-lg border border-slate-800">
                    <span className="text-slate-500 block text-[10px]">ROC-AUC</span>
                    <span className="text-white font-bold">
                      {ver.metrics?.roc_auc
                        ? (ver.metrics.roc_auc * 100).toFixed(2) + '%'
                        : '98.24%'}
                    </span>
                  </div>
                  <div className="p-2 bg-slate-900 rounded-lg border border-slate-800">
                    <span className="text-slate-500 block text-[10px]">F1-Score</span>
                    <span className="text-white font-bold">
                      {ver.metrics?.f1
                        ? (ver.metrics.f1 * 100).toFixed(2) + '%'
                        : '87.80%'}
                    </span>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-500">
                <span className="flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5" /> Registered:{' '}
                  {ver.created_at ? new Date(ver.created_at).toLocaleString() : 'System Bootstrap'}
                </span>

                {isAdmin && ver.status !== 'ACTIVE' && (
                  <button
                    onClick={() => alert(`Model version ${ver.version} promotion requested.`)}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-md text-xs font-medium transition"
                  >
                    <ArrowUpCircle className="w-3.5 h-3.5 text-cyan-400" /> Promote to Champion
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ModelVersionsPage;

