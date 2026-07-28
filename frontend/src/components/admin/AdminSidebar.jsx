import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Shield, LayoutDashboard, BookOpen, ScrollText, Users, KeyRound, Activity } from 'lucide-react';
import { Button } from '@/components/ui/button';

const navItems = [
  { icon: LayoutDashboard, label: 'Overview', path: '/admin/dashboard' },
  { icon: BookOpen, label: 'Content', path: '/admin/content' },
  { icon: ScrollText, label: 'WHO Rules', path: '/admin/who-rules' },
  { icon: Users, label: 'Accounts', path: '/admin/users' },
  { icon: KeyRound, label: 'Sessions', path: '/admin/sessions' },
  { icon: Activity, label: 'Health', path: '/admin/health' },
];

export default function AdminSidebar({ open, onClose }) {
  const location = useLocation();

  return (
    <>
      {open && <div className="fixed inset-0 bg-black/40 z-40 lg:hidden" onClick={onClose} />}
      <aside className={`fixed top-16 left-0 bottom-0 w-64 bg-slate-50/80 backdrop-blur border-r border-slate-200 z-50 transition-transform lg:translate-x-0 ${
        open ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <div className="p-4">
          <div className="flex items-center gap-2 mb-6 px-2">
            <div className="w-8 h-8 rounded-lg bg-indigo-100 flex items-center justify-center border border-indigo-200">
              <Shield className="w-4 h-4 text-indigo-600" />
            </div>
            <div>
              <p className="font-heading font-semibold text-sm text-slate-800">Admin Console</p>
              <p className="text-xs text-slate-500">NuruCare Admin</p>
            </div>
          </div>
          <nav className="space-y-1">
            {navItems.map(item => (
              <Link key={item.path} to={item.path} onClick={onClose}>
                <Button
                  variant={location.pathname === item.path ? 'default' : 'ghost'}
                  className={location.pathname === item.path
                    ? 'w-full justify-start gap-3 bg-indigo-600 hover:bg-indigo-700 text-white'
                    : 'w-full justify-start gap-3 text-slate-700 hover:bg-slate-200 hover:text-slate-900'}
                  size="sm"
                >
                  <item.icon className="w-4 h-4" />
                  {item.label}
                </Button>
              </Link>
            ))}
          </nav>
        </div>
      </aside>
    </>
  );
}
