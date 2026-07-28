import React, { useState, useEffect } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import AdminSidebar from './AdminSidebar';
import Navbar from '../layout/Navbar';
import { Button } from '@/components/ui/button';
import { PanelLeft, ShieldAlert } from 'lucide-react';
import { useAuth } from '@/lib/AuthContext';

export default function AdminLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user, isAuthenticated, isLoadingAuth } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isLoadingAuth && (!isAuthenticated || !user || user.role !== 'admin')) {
      navigate('/login', { replace: true });
    }
  }, [isLoadingAuth, isAuthenticated, user, navigate]);

  if (isLoadingAuth) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-slate-200 border-t-indigo-600 rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!isAuthenticated || !user || user.role !== 'admin') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center space-y-4 p-8">
          <div className="w-16 h-16 rounded-full bg-indigo-100 flex items-center justify-center mx-auto">
            <ShieldAlert className="w-8 h-8 text-indigo-600" />
          </div>
          <h2 className="text-xl font-semibold text-slate-800">Admin access required</h2>
          <p className="text-sm text-slate-500">This area is restricted to administrators only.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="relative">
        <div className="absolute top-0 left-0 right-0 h-16 bg-gradient-to-r from-indigo-600/5 via-slate-600/5 to-indigo-600/5 pointer-events-none border-b border-indigo-100/60" />
        <Navbar />
      </div>
      <AdminSidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="pt-16 lg:pl-64">
        <div className="p-4 lg:hidden">
          <Button variant="ghost" size="icon" onClick={() => setSidebarOpen(true)} className="text-slate-700 hover:bg-slate-200">
            <PanelLeft className="w-5 h-5" />
          </Button>
        </div>
        <main className="p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
