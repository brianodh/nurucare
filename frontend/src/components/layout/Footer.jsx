import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Heart, AlertCircle, X } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';

export default function Footer() {
  const [maintenanceAlert, setMaintenanceAlert] = useState(null);

  const handleUnavailableClick = (e, name) => {
    e.preventDefault();
    setMaintenanceAlert(name);
  };

  const closeAlert = () => {
    setMaintenanceAlert(null);
  };

  return (
    <footer className="border-t bg-card">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {maintenanceAlert && (
          <Alert variant="destructive" className="mb-8">
            <AlertCircle className="w-4 h-4" />
            <AlertDescription className="flex items-center justify-between">
              This {maintenanceAlert} is currently under maintenance. Please check back soon.
              <Button variant="ghost" size="sm" onClick={closeAlert} className="h-auto p-1">
                <X className="w-4 h-4" />
              </Button>
            </AlertDescription>
          </Alert>
        )}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          <div className="col-span-2 md:col-span-1">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
                <Heart className="w-4 h-4 text-primary-foreground" />
              </div>
              <span className="font-heading font-bold text-lg">NuruCare</span>
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Empowering informed contraceptive decisions across Africa with compassion and science.
            </p>
          </div>
          <div>
            <h4 className="font-heading font-semibold mb-3 text-sm">Platform</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><Link to="/roles" className="hover:text-foreground">Assessment</Link></li>
              <li><Link to="/education" className="hover:text-foreground">Education</Link></li>
              <li><Link to="/female/sync" className="hover:text-foreground">Partner Sync</Link></li>
              <li><Link to="/nurse/dashboard" className="hover:text-foreground">Nurse Dashboard</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-heading font-semibold mb-3 text-sm">Resources</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><a href="#" onClick={(e) => handleUnavailableClick(e, 'FAQ')} className="hover:text-foreground">FAQ</a></li>
              <li><a href="#" onClick={(e) => handleUnavailableClick(e, 'Privacy Policy')} className="hover:text-foreground">Privacy Policy</a></li>
              <li><a href="#" onClick={(e) => handleUnavailableClick(e, 'Terms of Service')} className="hover:text-foreground">Terms of Service</a></li>
              <li><a href="#" onClick={(e) => handleUnavailableClick(e, 'Contact')} className="hover:text-foreground">Contact</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-heading font-semibold mb-3 text-sm">Community</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><a href="#" onClick={(e) => handleUnavailableClick(e, 'Blog')} className="hover:text-foreground">Blog</a></li>
              <li><a href="#" onClick={(e) => handleUnavailableClick(e, 'Research')} className="hover:text-foreground">Research</a></li>
              <li><a href="#" onClick={(e) => handleUnavailableClick(e, 'Partnerships')} className="hover:text-foreground">Partnerships</a></li>
              <li><a href="#" onClick={(e) => handleUnavailableClick(e, 'Support')} className="hover:text-foreground">Support</a></li>
            </ul>
          </div>
        </div>
        <div className="border-t mt-8 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-xs text-muted-foreground">© 2026 NuruCare. Educational decision-support platform. Not a medical diagnosis tool.</p>
        </div>
      </div>
    </footer>
  );
}
