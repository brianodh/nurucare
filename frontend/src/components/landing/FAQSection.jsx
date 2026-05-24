import React from 'react';
import { motion } from 'framer-motion';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';

const faqs = [
  { q: 'Is NuruCare a medical diagnosis tool?', a: 'No. NuruCare is an educational and decision-support platform. Our recommendations are based on WHO medical eligibility criteria but should not replace professional medical advice. Always consult a healthcare provider for medical decisions.' },
  { q: 'How is my data protected?', a: 'We use session-based access with expiring keys. Your health data is never permanently stored without your explicit consent. All consultations use anonymous identifiers.' },
  { q: 'Can my partner see my health information?', a: 'Only the information you explicitly choose to share through Partner Sync is visible. You control what gets shared through anonymous sync tokens.' },
  { q: 'Who creates the recommendations?', a: 'Our recommendation engine is built on WHO Medical Eligibility Criteria for Contraceptive Use (MEC), reviewed by reproductive health professionals.' },
  { q: 'Is this service free?', a: 'The core assessment, educational content, and recommendation features are free. Premium features like extended nurse consultations may have associated costs in the future.' },
  { q: 'Can healthcare providers use NuruCare?', a: 'Yes! Nurses and health experts have a dedicated dashboard to review patient profiles (with session-key access), view analytics, and provide data-driven consultations.' },
];

export default function FAQSection() {
  return (
    <section className="py-20 bg-card">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <p className="text-sm font-medium text-secondary uppercase tracking-wider mb-2">FAQ</p>
          <h2 className="font-heading text-3xl sm:text-4xl font-bold">Common questions</h2>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <Accordion type="single" collapsible className="space-y-3">
            {faqs.map((f, i) => (
              <AccordionItem key={i} value={`faq-${i}`} className="bg-background rounded-xl border px-4">
                <AccordionTrigger className="text-left font-medium text-sm py-4 hover:no-underline">
                  {f.q}
                </AccordionTrigger>
                <AccordionContent className="text-sm text-muted-foreground leading-relaxed pb-4">
                  {f.a}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </motion.div>
      </div>
    </section>
  );
}