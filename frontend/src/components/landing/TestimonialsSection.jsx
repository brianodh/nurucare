import React from 'react';
import { motion } from 'framer-motion';
import { Star } from 'lucide-react';

const testimonials = [
  { name: 'Amara K.', location: 'Nairobi, Kenya', text: 'NuruCare helped me understand my options without judgment. I finally feel confident in my choice.', role: 'Female Client' },
  { name: 'Nurse Fatima', location: 'Lagos, Nigeria', text: 'The dashboard saves me hours. I can review patient profiles quickly and provide better-informed consultations.', role: 'Healthcare Provider' },
  { name: 'David & Grace', location: 'Kampala, Uganda', text: 'The Partner Sync feature opened up conversations we never knew how to start. We made the decision together.', role: 'Couple' },
];

export default function TestimonialsSection() {
  return (
    <section className="py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <p className="text-sm font-medium text-accent uppercase tracking-wider mb-2">Testimonials</p>
          <h2 className="font-heading text-3xl sm:text-4xl font-bold">Voices of empowerment</h2>
        </motion.div>
        <div className="grid md:grid-cols-3 gap-6">
          {testimonials.map((t, i) => (
            <motion.div
              key={t.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="bg-card rounded-2xl p-6 border shadow-sm"
            >
              <div className="flex gap-1 mb-4">
                {[1,2,3,4,5].map(s => <Star key={s} className="w-4 h-4 fill-primary text-primary" />)}
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed mb-6 italic">"{t.text}"</p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center font-heading font-bold text-primary text-sm">
                  {t.name[0]}
                </div>
                <div>
                  <p className="font-medium text-sm">{t.name}</p>
                  <p className="text-xs text-muted-foreground">{t.role} · {t.location}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}