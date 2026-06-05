import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { AlertTriangle, CheckCircle, Shield, Info, XCircle, Loader2, ChevronDown, ChevronUp } from 'lucide-react';
import { useLang } from '@/lib/i18n';
import { submitIntake, getRecommendations } from '@/api/apiClient';

function toBackendPayload(data) {
  return {
    age: parseInt(data.age) || 0,
    gender: data.gender || 'female',
    systolic_bp: data.systolic ? parseInt(data.systolic) : null,
    diastolic_bp: data.diastolic ? parseInt(data.diastolic) : null,
    smoking: !!data.smoking,
    migraine_type: data.migraine || 'none',
    is_pregnant: !!data.isPregnant,
    breastfeeding: !!data.breastfeeding,
    fertility_intention: data.fertilityIntention || 'unsure',
    parity: parseInt(data.parity) || 0,
  };
}

// Renders the raw AI text cleanly — strip emoji/bullets and show as paragraphs
function AITextBlock({ text }) {
  if (!text) return null;

  // Split on bullet separators the backend uses
  const lines = text
    .split(/•|\n/)
    .map((l) => l.trim())
    .filter(Boolean);

  return (
    <div className="space-y-2 text-sm text-muted-foreground leading-relaxed">
      {lines.map((line, i) => (
        <p key={i}>{line}</p>
      ))}
    </div>
  );
}

// Collapsible section for AI explanation and Swahili
function CollapsibleSection({ icon: Icon, title, children, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="border rounded-2xl overflow-hidden">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between gap-3 p-4 text-left bg-muted/30 hover:bg-muted/50 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Icon className="w-4 h-4 text-primary flex-shrink-0" />
          <span className="font-medium text-sm">{title}</span>
        </div>
        {open ? <ChevronUp className="w-4 h-4 text-muted-foreground" /> : <ChevronDown className="w-4 h-4 text-muted-foreground" />}
      </button>
      {open && <div className="p-4 border-t bg-card">{children}</div>}
    </div>
  );
}

export default function IntakeStep5({ data }) {
  const { t } = useLang();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [recommendations, setRecommendations] = useState(null);

  useEffect(() => {
    let cancelled = false;
    async function fetchRecs() {
      setLoading(true);
      setError(null);
      try {
        const payload = toBackendPayload(data);
        const [, recResponse] = await Promise.all([
          submitIntake(payload),
          getRecommendations(payload),
        ]);
        if (!cancelled) setRecommendations(recResponse);
      } catch (err) {
        if (!cancelled) setError('Could not reach the server. Please check your connection and try again.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    fetchRecs();
    return () => { cancelled = true; };
  }, []);

  const isHighRisk =
    (parseInt(data.age) > 35 && data.smoking) || data.migraine === 'with_aura';

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-4">
        <Loader2 className="w-10 h-10 text-primary animate-spin" />
        <p className="text-muted-foreground text-sm">Analysing your health profile…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-destructive/10 border border-destructive/30 rounded-2xl p-6 text-center">
        <XCircle className="w-8 h-8 text-destructive mx-auto mb-3" />
        <p className="font-semibold text-destructive mb-1">Something went wrong</p>
        <p className="text-sm text-destructive/80">{error}</p>
      </div>
    );
  }

  const safe = recommendations?.recommended_methods ?? [];
  const restricted = recommendations?.restricted_methods ?? [];
  const aiText = recommendations?.full_ai_response ?? '';
  const swahiliText = recommendations?.swahili_version ?? '';

  return (
    <div className="space-y-5">
      {/* Header */}
      <div>
        <h3 className="font-heading font-semibold text-xl mb-1">{t('s5_title')}</h3>
        <p className="text-sm text-muted-foreground">{t('s5_sub')}</p>
      </div>

      {/* High risk warning */}
      {isHighRisk && (
        <motion.div
          initial={{ opacity: 0, scale: 0.97 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-destructive/10 border border-destructive/30 rounded-2xl p-4"
        >
          <div className="flex items-start gap-3">
            <XCircle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
            <div className="space-y-1">
              <p className="font-semibold text-destructive text-sm">{t('s5_risk_title')}</p>
              <p className="text-xs text-destructive/80">
                {data.migraine === 'with_aura' ? t('s5_risk_aura') : t('s5_risk_smoke')}
              </p>
              <p className="text-xs font-medium text-destructive">{t('s5_restricted_label')}</p>
              <p className="text-xs text-destructive/70">{t('s5_consult')}</p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Recommended methods */}
      {safe.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-secondary" />
            <h4 className="font-heading font-semibold text-sm">{t('s5_recommended')}</h4>
          </div>
          {safe.map((m, i) => (
            <motion.div
              key={m.name + i}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.07 }}
              className="bg-card border rounded-2xl p-4"
            >
              <div className="flex items-center justify-between mb-2">
                <h5 className="font-medium text-sm">{m.name}</h5>
                {m.effectiveness != null && (
                  <span className="text-sm font-bold text-secondary shrink-0 ml-2">{m.effectiveness}%</span>
                )}
              </div>
              {m.effectiveness != null && (
                <Progress value={m.effectiveness} className="h-1.5 mb-2" />
              )}
              {m.explanation && (
                <p className="text-xs text-muted-foreground">{m.explanation}</p>
              )}
            </motion.div>
          ))}
        </div>
      )}

      {/* Restricted methods */}
      {restricted.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-accent" />
            <h4 className="font-heading font-semibold text-sm">{t('s5_restricted')}</h4>
          </div>
          {restricted.map((m, i) => (
            <div key={m.name + i} className="bg-accent/5 border border-accent/20 rounded-2xl p-4">
              <div className="flex items-center gap-2 mb-1 flex-wrap">
                <Shield className="w-4 h-4 text-accent shrink-0" />
                <h5 className="font-medium text-sm">{m.name}</h5>
                {m.who_category && (
                  <Badge variant="outline" className="text-xs ml-auto">WHO Cat {m.who_category}</Badge>
                )}
              </div>
              <p className="text-xs text-muted-foreground">{m.reason}</p>
            </div>
          ))}
        </div>
      )}

      {/* AI Explanation — collapsible */}
      {aiText && (
        <CollapsibleSection icon={Info} title={t('s5_ai_label') || 'AI Explanation'}>
          <AITextBlock text={aiText} />
        </CollapsibleSection>
      )}

      {/* Swahili version — collapsible */}
      {swahiliText && (
        <CollapsibleSection icon={Info} title="Swahili / Kiswahili">
          <AITextBlock text={swahiliText} />
        </CollapsibleSection>
      )}

      {/* Disclaimer */}
      <div className="bg-muted rounded-xl p-4 text-xs text-muted-foreground flex items-start gap-2">
        <Info className="w-4 h-4 shrink-0 mt-0.5" />
        {t('s5_disclaimer')}
      </div>
    </div>
  );
}
