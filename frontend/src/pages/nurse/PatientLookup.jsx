import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Search, Shield, AlertTriangle, CheckCircle, Info, XCircle, Lock, Loader2 } from 'lucide-react';
import { getPatientBySessionKey } from '@/api/apiClient';
import { useToast } from '@/components/ui/use-toast';
import { useLang } from '@/lib/i18n';

const riskColors = {
  Low: 'bg-secondary/10 text-secondary',
  Medium: 'bg-accent/10 text-accent',
  High: 'bg-destructive/10 text-destructive',
};

export default function PatientLookup() {
  const { t } = useLang();
  const { toast } = useToast();
  const [code, setCode] = useState('');
  const [patient, setPatient] = useState(null);
  const [loading, setLoading] = useState(false);
  const [notFound, setNotFound] = useState(false);

  const lookup = async () => {
    if (code.trim().length < 6) return;
    setLoading(true);
    setNotFound(false);
    setPatient(null);

    try {
      const response = await getPatientBySessionKey(code.trim());

      if (response.success && response.patient_data) {
        setPatient(response.patient_data);
      } else {
        setNotFound(true);
        toast({
          title: t('error'),
          description: response.error || t('nurse_lookup_not_found'),
          variant: 'destructive',
        });
      }
    } catch (err) {
      console.error('Patient lookup failed:', err);
      setNotFound(true);
      toast({
        title: t('nurse_lookup_failed_title'),
        description: t('nurse_lookup_failed_desc'),
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') lookup();
  };

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="font-heading text-2xl font-bold">{t('nurse_lookup_title')}</h1>
        <p className="text-muted-foreground text-sm mt-1">{t('nurse_lookup_sub')}</p>
      </motion.div>

      <Card className="p-5 rounded-2xl">
        <div className="flex gap-3 max-w-md">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder={t('nurse_lookup_placeholder')}
              value={code}
              onChange={(e) => setCode(e.target.value)}
              onKeyDown={handleKeyDown}
              maxLength={6}
              className="pl-9 font-mono"
            />
          </div>
          <Button
            onClick={lookup}
            disabled={code.trim().length < 6 || loading}
            className="rounded-full gap-2"
          >
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
            {loading ? t('nurse_lookup_searching') : t('nurse_lookup_btn')}
          </Button>
        </div>
        <div className="flex items-center gap-2 mt-3 text-xs text-muted-foreground">
          <Lock className="w-3 h-3" /> {t('nurse_lookup_access_note')}
        </div>
      </Card>

      {/* Not found */}
      {notFound && !loading && (
        <Card className="p-5 rounded-2xl border-destructive/30 bg-destructive/5">
          <div className="flex items-center gap-3">
            <XCircle className="w-5 h-5 text-destructive flex-shrink-0" />
            <p className="text-sm text-destructive">{t('nurse_lookup_not_found')}</p>
          </div>
        </Card>
      )}

      {/* Patient data */}
      {patient && !loading && (
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
          <Card className="p-5 rounded-2xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-heading font-semibold">{t('nurse_lookup_patient_profile')}</h3>
              {patient.risk_level && (
                <Badge variant="secondary" className={riskColors[patient.risk_level] || 'bg-muted text-muted-foreground'}>
                  {patient.risk_level} {t('nurse_lookup_risk_suffix')}
                </Badge>
              )}
            </div>

            {/* Show whatever fields the backend returns */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {Object.entries(patient)
                .filter(([k]) => !['recommendations', 'restricted_methods', 'ai_response', 'id'].includes(k))
                .map(([key, value]) => (
                  <div key={key} className="bg-muted/50 rounded-xl p-3">
                    <p className="text-xs text-muted-foreground capitalize">{key.replace(/_/g, ' ')}</p>
                    <p className="font-medium text-sm mt-0.5 truncate">
                      {typeof value === 'boolean' ? (value ? 'Yes' : 'No') : String(value ?? '—')}
                    </p>
                  </div>
                ))}
            </div>
          </Card>

          {/* Recommendations if included in response */}
          {Array.isArray(patient.recommendations) && patient.recommendations.length > 0 && (
            <Card className="p-5 rounded-2xl">
              <h3 className="font-heading font-semibold mb-4 flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-secondary" /> {t('nurse_lookup_recommendations')}
              </h3>
              <div className="space-y-3">
                {patient.recommendations.map((m, i) => (
                  <div key={i} className="flex items-center gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="font-medium text-sm">{m.name}</p>
                      </div>
                      {m.effectiveness != null && (
                        <Progress value={m.effectiveness} className="h-1.5" />
                      )}
                    </div>
                    {m.effectiveness != null && (
                      <span className="text-sm font-bold text-secondary">{m.effectiveness}%</span>
                    )}
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* AI analysis if present */}
          {patient.ai_response && (
            <Card className="p-5 rounded-2xl bg-primary/5 border-primary/20">
              <div className="flex items-start gap-3">
                <Info className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-sm mb-1">{t('nurse_lookup_ai_analysis')}</p>
                  <p className="text-sm text-muted-foreground leading-relaxed">{patient.ai_response}</p>
                </div>
              </div>
            </Card>
          )}
        </motion.div>
      )}
    </div>
  );
}
