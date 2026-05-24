import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Search, Shield, AlertTriangle, CheckCircle, Info, XCircle, Lock } from 'lucide-react';
import { mockRecommendations } from '@/lib/mockData';

const mockPatientData = {
  sessionId: 'SC-482901',
  age: 24,
  relationshipStatus: 'In a Relationship',
  systolic: 118,
  diastolic: 76,
  smoking: false,
  migraine: 'none',
  cycleLength: 28,
  irregularPeriods: false,
  breastfeeding: false,
  fertilityIntention: 'Long-term',
  sideEffectConcerns: ['mood_shifts', 'weight_gain'],
  riskLevel: 'Low',
};

export default function PatientLookup() {
  const [code, setCode] = useState('');
  const [patient, setPatient] = useState(null);
  const [loading, setLoading] = useState(false);

  const lookup = () => {
    if (code.length < 6) return;
    setLoading(true);
    setTimeout(() => {
      setPatient(mockPatientData);
      setLoading(false);
    }, 1200);
  };

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="font-heading text-2xl font-bold">Patient Lookup</h1>
        <p className="text-muted-foreground text-sm mt-1">Enter a 6-digit session key to access patient summary.</p>
      </motion.div>

      <Card className="p-5 rounded-2xl">
        <div className="flex gap-3 max-w-md">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Enter session key..."
              value={code}
              onChange={e => setCode(e.target.value)}
              maxLength={6}
              className="pl-9 font-mono"
            />
          </div>
          <Button onClick={lookup} disabled={code.length < 6 || loading} className="rounded-full">
            {loading ? 'Searching...' : 'Lookup'}
          </Button>
        </div>
        <div className="flex items-center gap-2 mt-3 text-xs text-muted-foreground">
          <Lock className="w-3 h-3" /> Access is temporary and session-based
        </div>
      </Card>

      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-4 border-muted border-t-primary rounded-full animate-spin" />
        </div>
      )}

      {patient && !loading && (
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
          <Card className="p-5 rounded-2xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-heading font-semibold">Patient Profile</h3>
              <Badge variant="secondary" className="bg-secondary/10 text-secondary">
                {patient.riskLevel} Risk
              </Badge>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: 'Age', value: patient.age },
                { label: 'BP', value: `${patient.systolic}/${patient.diastolic}` },
                { label: 'Cycle Length', value: `${patient.cycleLength} days` },
                { label: 'Fertility Plan', value: patient.fertilityIntention },
                { label: 'Smoking', value: patient.smoking ? 'Yes' : 'No' },
                { label: 'Migraine', value: patient.migraine === 'none' ? 'None' : patient.migraine },
                { label: 'Breastfeeding', value: patient.breastfeeding ? 'Yes' : 'No' },
                { label: 'Relationship', value: patient.relationshipStatus },
              ].map(item => (
                <div key={item.label} className="bg-muted/50 rounded-xl p-3">
                  <p className="text-xs text-muted-foreground">{item.label}</p>
                  <p className="font-medium text-sm mt-0.5">{item.value}</p>
                </div>
              ))}
            </div>
          </Card>

          <Card className="p-5 rounded-2xl">
            <h3 className="font-heading font-semibold mb-4 flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-secondary" /> Recommendations
            </h3>
            <div className="space-y-3">
              {mockRecommendations.safe.map(m => (
                <div key={m.name} className="flex items-center gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="font-medium text-sm">{m.name}</p>
                      <Badge variant="outline" className="text-xs">{m.category}</Badge>
                    </div>
                    <Progress value={m.confidence} className="h-1.5" />
                  </div>
                  <span className="text-sm font-bold text-secondary">{m.confidence}%</span>
                </div>
              ))}
            </div>
          </Card>

          <Card className="p-5 rounded-2xl">
            <h3 className="font-heading font-semibold mb-4 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-accent" /> Restricted Methods
            </h3>
            {mockRecommendations.restricted.map(m => (
              <div key={m.name} className="bg-accent/5 border border-accent/20 rounded-xl p-4 mb-3 last:mb-0">
                <p className="font-medium text-sm">{m.name}</p>
                <p className="text-xs text-muted-foreground mt-1">{m.reason}</p>
              </div>
            ))}
          </Card>

          <Card className="p-5 rounded-2xl bg-primary/5 border-primary/20">
            <div className="flex items-start gap-3">
              <Info className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-sm mb-1">AI Analysis</p>
                <p className="text-sm text-muted-foreground leading-relaxed">{mockRecommendations.explanation}</p>
              </div>
            </div>
          </Card>
        </motion.div>
      )}
    </div>
  );
}