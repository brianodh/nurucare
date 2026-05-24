import React from 'react';
import { Heart } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="border-t bg-card">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
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
              <li>Assessment</li>
              <li>Education</li>
              <li>Partner Sync</li>
              <li>Nurse Dashboard</li>
            </ul>
          </div>
          <div>
            <h4 className="font-heading font-semibold mb-3 text-sm">Resources</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>FAQ</li>
              <li>Privacy Policy</li>
              <li>Terms of Service</li>
              <li>Contact</li>
            </ul>
          </div>
          <div>
            <h4 className="font-heading font-semibold mb-3 text-sm">Community</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>Blog</li>
              <li>Research</li>
              <li>Partnerships</li>
              <li>Support</li>
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