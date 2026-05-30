import React from 'react';
import { motion } from 'framer-motion';
import { Brain, BookOpen, Users, Lock, Stethoscope, Sparkles } from 'lucide-react';
import { useLang } from '@/lib/i18n';

export default function FeaturesSection() {
  const { t } = useLang();

  const features = [
    { icon: Brain, titleKey: 'feature_1_title', descKey: 'feature_1_desc', gradient: 'from-primary/10 to-primary/5' },
    { icon: BookOpen, titleKey: 'feature_2_title', descKey: 'feature_2_desc', gradient: 'from-secondary/10 to-secondary/5' },
    { icon: Users, titleKey: 'feature_3_title', descKey: 'feature_3_desc', gradient: 'from-accent/10 to-accent/5' },
    { icon: Lock, titleKey: 'feature_4_title', descKey: 'feature_4_desc', gradient: 'from-primary/10 to-secondary/5' },
    { icon: Stethoscope, titleKey: 'feature_5_title', descKey: 'feature_5_desc', gradient: 'from-secondary/10 to-accent/5' },
    { icon: Sparkles, titleKey: 'feature_6_title', descKey: 'feature_6_desc', gradient: 'from-accent/10 to-primary/5' },
  ];

  return (
    <section className="py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="text-center mb-16">
          <p className="text-sm font-medium text-primary uppercase tracking-wider mb-2">{t('features_label')}</p>
          <h2 className="font-heading text-3xl sm:text-4xl font-bold">{t('features_h2')}</h2>
        </motion.div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f, i) => (
            <motion.div
              key={f.titleKey}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08 }}
              className={`bg-gradient-to-br ${f.gradient} rounded-2xl p-6 border hover:shadow-lg transition-all hover:-translate-y-1`}
            >
              <div className="w-12 h-12 rounded-xl bg-card flex items-center justify-center mb-4 shadow-sm">
                <f.icon className="w-6 h-6 text-primary" />
              </div>
              <h3 className="font-heading font-semibold text-lg mb-2">{t(f.titleKey)}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{t(f.descKey)}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}