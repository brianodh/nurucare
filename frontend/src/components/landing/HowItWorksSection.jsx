import React from 'react';
import { motion } from 'framer-motion';
import { UserCheck, ClipboardList, Sparkles, Heart } from 'lucide-react';
import { useLang } from '@/lib/i18n';

export default function HowItWorksSection() {
  const { t } = useLang();

  const steps = [
    { icon: UserCheck, titleKey: 'step_1_title', descKey: 'step_1_desc' },
    { icon: ClipboardList, titleKey: 'step_2_title', descKey: 'step_2_desc' },
    { icon: Sparkles, titleKey: 'step_3_title', descKey: 'step_3_desc' },
    { icon: Heart, titleKey: 'step_4_title', descKey: 'step_4_desc' },
  ];

  return (
    <section className="py-20 bg-card">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="text-center mb-16">
          <p className="text-sm font-medium text-secondary uppercase tracking-wider mb-2">{t('how_label')}</p>
          <h2 className="font-heading text-3xl sm:text-4xl font-bold">{t('how_h2')}</h2>
        </motion.div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((s, i) => (
            <motion.div
              key={s.titleKey}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="text-center"
            >
              <div className="relative inline-flex">
                <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto">
                  <s.icon className="w-7 h-7 text-primary" />
                </div>
                <span className="absolute -top-2 -right-2 w-7 h-7 rounded-full bg-primary text-primary-foreground text-xs font-bold flex items-center justify-center">
                  {i + 1}
                </span>
              </div>
              <h3 className="font-heading font-semibold mt-4 mb-2">{t(s.titleKey)}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{t(s.descKey)}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}