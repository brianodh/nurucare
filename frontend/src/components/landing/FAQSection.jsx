import React from 'react';
import { motion } from 'framer-motion';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { useLang } from '@/lib/i18n';

export default function FAQSection() {
  const { t } = useLang();

  const faqs = [
    { qKey: 'faq_1_q', aKey: 'faq_1_a' },
    { qKey: 'faq_2_q', aKey: 'faq_2_a' },
    { qKey: 'faq_3_q', aKey: 'faq_3_a' },
    { qKey: 'faq_4_q', aKey: 'faq_4_a' },
    { qKey: 'faq_5_q', aKey: 'faq_5_a' },
    { qKey: 'faq_6_q', aKey: 'faq_6_a' },
  ];

  return (
    <section className="py-20 bg-card">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="text-center mb-12">
          <p className="text-sm font-medium text-secondary uppercase tracking-wider mb-2">{t('faq_label')}</p>
          <h2 className="font-heading text-3xl sm:text-4xl font-bold">{t('faq_h2')}</h2>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
          <Accordion type="single" collapsible className="space-y-3">
            {faqs.map((f, i) => (
              <AccordionItem key={i} value={`faq-${i}`} className="bg-background rounded-xl border px-4">
                <AccordionTrigger className="text-left font-medium text-sm py-4 hover:no-underline">
                  {t(f.qKey)}
                </AccordionTrigger>
                <AccordionContent className="text-sm text-muted-foreground leading-relaxed pb-4">
                  {t(f.aKey)}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </motion.div>
      </div>
    </section>
  );
}