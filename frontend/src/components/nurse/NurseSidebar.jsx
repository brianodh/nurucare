import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Heart, LayoutDashboard, Search, BarChart3, Settings } from 'lucide-react';
import { Button } from '@/components/ui/button';

const navItems = [
  { icon: LayoutDashboard, label: 'Overview', path: '/nurse/dashboard' },
  { icon: Search, label: 'Patient Lookup', path: '/nurse/lookup' },
  { icon: BarChart3, label: 'Analytics', path: '/nurse/analytics' },
];

export default function NurseSidebar({ open, onClose }) {
  const location = useLocation();

  return (
    <>
      {open && <div className="fixed inset-0 bg-black/40 z-40 lg:hidden" onClick={onClose} />}
      <aside className={`fixed top-16 left-0 bottom-0 w-64 bg-card border-r z-50 transition-transform lg:translate-x-0 ${
        open ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <div className="p-4">
          <div className="flex items-center gap-2 mb-6 px-2">
            <div className="w-8 h-8 rounded-lg bg-secondary/10 flex items-center justify-center">
              <Heart className="w-4 h-4 text-secondary" />
            </div>
            <div>
              <p className="font-heading font-semibold text-sm">Nurse Portal</p>
              <p className="text-xs text-muted-foreground">NuruCare Pro</p>
            </div>
          </div>
          <nav className="space-y-1">
            {navItems.map(item => (
              <Link key={item.path} to={item.path} onClick={onClose}>
                <Button
                  variant={location.pathname === item.path ? 'secondary' : 'ghost'}
                  className="w-full justify-start gap-3"
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