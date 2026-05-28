import React from 'react';
import { motion } from 'framer-motion';
import { Star } from 'lucide-react';
import { useLang } from '@/lib/i18n';

export default function TestimonialsSection() {
  const { t } = useLang();

  const testimonials = [
    { name: 'Amara K.', location: 'Nairobi, Kenya', textKey: 't1_text', roleKey: 't1_role' },
    { name: 'Nurse Fatima', location: 'Lagos, Nigeria', textKey: 't2_text', roleKey: 't2_role' },
    { name: 'David & Grace', location: 'Kampala, Uganda', textKey: 't3_text', roleKey: 't3_role' },
  ];

  return (
    <section className="py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="text-center mb-16">
          <p className="text-sm font-medium text-accent uppercase tracking-wider mb-2">{t('testimonials_label')}</p>
          <h2 className="font-heading text-3xl sm:text-4xl font-bold">{t('testimonials_h2')}</h2>
        </motion.div>
        <div className="grid md:grid-cols-3 gap-6">
          {testimonials.map((testimonial, i) => (
            <motion.div
              key={testimonial.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="bg-card rounded-2xl p-6 border shadow-sm"
            >
              <div className="flex gap-1 mb-4">
                {[1,2,3,4,5].map(s => <Star key={s} className="w-4 h-4 fill-primary text-primary" />)}
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed mb-6 italic">"{t(testimonial.textKey)}"</p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center font-heading font-bold text-primary text-sm">
                  {testimonial.name[0]}
                </div>
                <div>
                  <p className="font-medium text-sm">{testimonial.name}</p>
                  <p className="text-xs text-muted-foreground">{t(testimonial.roleKey)} · {testimonial.location}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}