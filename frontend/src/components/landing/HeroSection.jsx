import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { motion } from 'framer-motion';
import { ArrowRight, Shield, Heart, Sparkles } from 'lucide-react';
import { useLang } from '@/lib/i18n';

export default function HeroSection() {
  const { t } = useLang();
  return (
    <section className="relative overflow-hidden min-h-[90vh] flex items-center">
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-secondary/5 to-accent/5" />
      <div className="absolute top-20 right-10 w-72 h-72 bg-primary/10 rounded-full blur-3xl" />
      <div className="absolute bottom-20 left-10 w-96 h-96 bg-secondary/10 rounded-full blur-3xl" />
      
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7 }}>
            <div className="inline-flex items-center gap-2 bg-primary/10 text-primary rounded-full px-4 py-1.5 text-sm font-medium mb-6">
              <Sparkles className="w-4 h-4" />
              {t('hero_badge')}
            </div>
            <h1 className="font-heading text-4xl sm:text-5xl lg:text-6xl font-bold leading-tight tracking-tight">
              {t('hero_h1_1')}{' '}
              <span className="text-primary">{t('hero_h1_2')}</span>{' '}
              <span className="text-secondary">{t('hero_h1_3')}</span>
            </h1>
            <p className="mt-6 text-lg text-muted-foreground leading-relaxed max-w-xl">{t('hero_sub')}</p>
            <div className="flex flex-wrap gap-4 mt-8">
              <Link to="/roles">
                <Button size="lg" className="rounded-full px-8 gap-2 text-base">
                  {t('hero_cta_start')} <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
              <Button variant="outline" size="lg" className="rounded-full px-8 text-base">
                {t('hero_cta_learn')}
              </Button>
            </div>
            <div className="flex items-center gap-6 mt-10 text-sm text-muted-foreground">
              <div className="flex items-center gap-2"><Shield className="w-4 h-4 text-secondary" /> {t('hero_privacy')}</div>
              <div className="flex items-center gap-2"><Heart className="w-4 h-4 text-accent" /> {t('hero_who')}</div>
            </div>
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.7, delay: 0.2 }}
            className="hidden lg:block"
          >
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-secondary/20 rounded-3xl blur-2xl" />
              <div className="relative bg-card rounded-3xl border shadow-xl p-8 space-y-6">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-2xl bg-primary/10 flex items-center justify-center">
                    <Heart className="w-6 h-6 text-primary" />
                  </div>
                  <div>
                    <p className="font-heading font-semibold">{t('hero_card_title')}</p>
                    <p className="text-sm text-muted-foreground">{t('hero_card_sub')}</p>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-3">
                  {['IUD', 'Implant', 'Oral Pill'].map((m, i) => (
                    <div key={m} className="bg-muted rounded-xl p-3 text-center">
                      <div className={`text-2xl font-bold ${i === 0 ? 'text-secondary' : i === 1 ? 'text-primary' : 'text-accent'}`}>
                        {[95, 88, 76][i]}%
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">{m}</p>
                    </div>
                  ))}
                </div>
                <div className="bg-secondary/10 rounded-xl p-4">
                  <p className="text-sm font-medium text-secondary">{t('hero_card_safe')}</p>
                  <p className="text-xs text-muted-foreground mt-1">{t('hero_card_who')}</p>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}