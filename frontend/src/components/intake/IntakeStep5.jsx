import React from 'react';
import { motion } from 'framer-motion';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { AlertTriangle, CheckCircle, Shield, Info, XCircle } from 'lucide-react';
import { mockRecommendations } from '@/lib/mockData';
import { useLang } from '@/lib/i18n';

export default function IntakeStep5({ data }) {
  const { t } = useLang();
  const { safe, restricted, explanation, warnings } = mockRecommendations;
  const isHighRisk = (parseInt(data.age) > 35 && data.smoking) || data.migraine === 'with_aura';

  return (
    <div className="space-y-6">
      <div>
        <h3 className="font-heading font-semibold text-xl mb-1">{t('s5_title')}</h3>
        <p className="text-sm text-muted-foreground">{t('s5_sub')}</p>
      </div>

      {isHighRisk && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-destructive/10 border border-destructive/30 rounded-2xl p-5"
        >
          <div className="flex items-start gap-3">
            <XCircle className="w-6 h-6 text-destructive flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-heading font-semibold text-destructive">{t('s5_risk_title')}</p>
              <p className="text-sm text-destructive/80 mt-1">
                {data.migraine === 'with_aura' ? t('s5_risk_aura') : t('s5_risk_smoke')}
              </p>
              <p className="text-sm font-medium text-destructive mt-2">{t('s5_restricted_label')}</p>
              <p className="text-xs text-destructive/70 mt-2">{t('s5_consult')}</p>
            </div>
          </div>
        </motion.div>
      )}

      <div>
        <div className="flex items-center gap-2 mb-4">
          <CheckCircle className="w-5 h-5 text-secondary" />
          <h4 className="font-heading font-semibold">{t('s5_recommended')}</h4>
        </div>
        <div className="space-y-3">
          {safe.map((m, i) => (
            <motion.div
              key={m.name}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="bg-card border rounded-2xl p-4"
            >
              <div className="flex items-center justify-between mb-2 flex-wrap gap-2">
                <div className="flex items-center gap-2 flex-wrap">
                  <h5 className="font-medium">{m.name}</h5>
                  <Badge variant="secondary" className="text-xs">{m.category}</Badge>
                </div>
                <span className="text-sm font-bold text-secondary">{m.confidence}%</span>
              </div>
              <Progress value={m.confidence} className="h-1.5 mb-2" />
              <p className="text-sm text-muted-foreground">{m.description}</p>
            </motion.div>
          ))}
        </div>
      </div>

      {restricted.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="w-5 h-5 text-accent" />
            <h4 className="font-heading font-semibold">{t('s5_restricted')}</h4>
          </div>
          <div className="space-y-3">
            {restricted.map(m => (
              <div key={m.name} className="bg-accent/5 border border-accent/20 rounded-2xl p-4">
                <div className="flex items-center gap-2 mb-1">
                  <Shield className="w-4 h-4 text-accent" />
                  <h5 className="font-medium">{m.name}</h5>
                </div>
                <p className="text-sm text-muted-foreground">{m.reason}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bg-primary/5 border border-primary/20 rounded-2xl p-5">
        <div className="flex items-start gap-3">
          <Info className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-sm mb-1">{t('s5_ai_label')}</p>
            <p className="text-sm text-muted-foreground leading-relaxed">{explanation}</p>
          </div>
        </div>
      </div>

      <div className="bg-muted rounded-xl p-4 text-sm text-muted-foreground flex items-start gap-2">
        <Info className="w-4 h-4 flex-shrink-0 mt-0.5" />
        {t('s5_disclaimer')}
      </div>
    </div>
  );
}