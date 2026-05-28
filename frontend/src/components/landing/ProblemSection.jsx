import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, MessageCircle, Frown, HelpCircle } from 'lucide-react';
import { useLang } from '@/lib/i18n';

export default function ProblemSection() {
  const { t } = useLang();

  const problems = [
    { icon: MessageCircle, titleKey: 'problem_1_title', descKey: 'problem_1_desc', color: 'text-destructive' },
    { icon: AlertTriangle, titleKey: 'problem_2_title', descKey: 'problem_2_desc', color: 'text-accent' },
    { icon: Frown, titleKey: 'problem_3_title', descKey: 'problem_3_desc', color: 'text-primary' },
    { icon: HelpCircle, titleKey: 'problem_4_title', descKey: 'problem_4_desc', color: 'text-secondary' },
  ];

  return (
    <section className="py-20 bg-card">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="text-center mb-16">
          <p className="text-sm font-medium text-accent uppercase tracking-wider mb-2">{t('problem_label')}</p>
          <h2 className="font-heading text-3xl sm:text-4xl font-bold">{t('problem_h2')}</h2>
          <p className="mt-4 text-muted-foreground max-w-2xl mx-auto">{t('problem_sub')}</p>
        </motion.div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {problems.map((p, i) => (
            <motion.div
              key={p.titleKey}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="bg-background rounded-2xl p-6 border hover:shadow-lg transition-shadow"
            >
              <p.icon className={`w-8 h-8 ${p.color} mb-4`} />
              <h3 className="font-heading font-semibold text-lg mb-2">{t(p.titleKey)}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{t(p.descKey)}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}