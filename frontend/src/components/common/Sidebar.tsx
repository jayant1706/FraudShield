import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Receipt,
  ShieldAlert,
  BarChart3,
  Cpu,
  Layers,
  Users,
  Settings as SettingsIcon,
  Activity,
  LogOut,
} from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';

export const Sidebar: React.FC = () => {
  const { user, logout, isAdmin } = useAuth();

  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Transactions', path: '/transactions', icon: Receipt },
    { name: 'Fraud Detection', path: '/detect', icon: ShieldAlert },
    { name: 'Analytics', path: '/analytics', icon: BarChart3 },
    { name: 'Model Performance', path: '/model-performance', icon: Cpu },
    { name: 'Model Versions', path: '/model-versions', icon: Layers, adminOnly: true },
    { name: 'User Management', path: '/users', icon: Users, adminOnly: true },
    { name: 'Settings', path: '/settings', icon: SettingsIcon },
  ];

  return (
    <aside className="w-64 flex-shrink-0 bg-slate-950/95 border-r border-slate-800/80 flex flex-col justify-between h-screen sticky top-0">
      <div>
        {/* Brand */}
        <div className="h-16 flex items-center gap-3 px-6 border-b border-slate-800/80">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <ShieldAlert className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-cyan-400 bg-clip-text text-transparent">
              FraudShield
            </span>
            <span className="block text-[10px] uppercase font-mono tracking-widest text-cyan-400 font-semibold">
              AI Intelligence
            </span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-1.5">
          <div className="px-3 py-1 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
            Operations
          </div>
          {navItems.map((item) => {
            if (item.adminOnly && !isAdmin) return null;
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/10 text-cyan-400 border border-cyan-500/30 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                  }`
                }
              >
                <Icon className="w-4 h-4" />
                <span>{item.name}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Footer Profile & Logout */}
      <div className="p-4 border-t border-slate-800/80">
        <div className="flex items-center gap-2 px-3 py-2 bg-slate-900/70 border border-slate-800 rounded-lg mb-3">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></div>
          <span className="text-xs font-mono text-slate-300">Engine: Active (v1.0.0)</span>
        </div>

        <div className="flex items-center justify-between px-2">
          <div className="truncate">
            <div className="text-xs font-semibold text-slate-200 truncate">{user?.full_name}</div>
            <div className="text-[10px] font-mono text-cyan-400 uppercase">{user?.role}</div>
          </div>
          <button
            onClick={logout}
            title="Log Out"
            className="p-1.5 text-slate-400 hover:text-red-400 rounded-md hover:bg-slate-900 transition"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
};

