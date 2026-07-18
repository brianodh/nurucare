import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, Info, CheckCircle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

export default function PartnerSummary({ profile }) {
  if (!profile) return null;

  const fields = [
    { label: 'Age', value: profile.age },
    { label: 'Smoking', value: profile.smoking ? 'Yes' : 'No' },
    { label: 'Migraine Type', value: profile.migraine_type?.replace(/_/g, ' ') || '—' },
    { label: 'Blood Pressure', value: profile.systolic_bp && profile.diastolic_bp ? `${profile.systolic_bp}/${profile.diastolic_bp}` : '—' },
  ];

  const isHighRisk = (profile.smoking && profile.age > 35) || profile.migraine_type === 'with_aura';

  return (
    <motion.div initial={{ opacity: 0, y:15 }} animate={{ opacity: 1, y: 0 }} className="space-y-4 mt-4">
      {isHighRisk && (
        <div className="flex items-start gap-3 bg-destructive/10 border border-destructive/30 rounded-xl p-4">
          <AlertTriangle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-destructive">High Risk Profile</p>
            <p className="text-xs text-destructive/80 mt-0.5">
              Your partner should consult a healthcare provider before starting any contraceptive method.
            </p>
          </div>
        </div>
      )}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {fields.map(({ label, value }) => (
          <div key={label} className="bg-muted/50 rounded-xl p-3">
            <p className="text-xs text-muted-foreground">{label}</p>
            <p className="font-medium text-sm mt-0.5 capitalize">{String(value ?? '—')}</p>
          </div>
        ))}
      </div>
      {Array.isArray(profile.allowed_methods) && profile.allowed_methods.length > 0 && (
        <div>
          <p className="text-sm font-medium mb-2 flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-secondary" /> Safe Methods for Your Partner
          </p>
          <div className="flex flex-wrap gap-2">
            {profile.allowed_methods.map((m) => (
              <Badge key={m} variant="secondary" className="text-xs capitalize">{m.replace(/_/g, ' ')}</Badge>
            ))}
          </div>
        </div>
      )}
      <div className="bg-muted rounded-xl p-3 flex items-start gap-2 text-xs text-muted-foreground">
        <Info className="w-4 h-4 flex-shrink-0 mt-0.5" />
        This is a summary to support informed conversations. Always consult a healthcare provider.
      </div>
    </motion.div>
  );
}
