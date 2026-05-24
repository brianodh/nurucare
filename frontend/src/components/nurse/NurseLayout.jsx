import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import NurseSidebar from './NurseSidebar';
import Navbar from '../layout/Navbar';
import { Button } from '@/components/ui/button';
import { PanelLeft } from 'lucide-react';

export default function NurseLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen">
      <Navbar />
      <NurseSidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="pt-16 lg:pl-64">
        <div className="p-4 lg:hidden">
          <Button variant="ghost" size="icon" onClick={() => setSidebarOpen(true)}>
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