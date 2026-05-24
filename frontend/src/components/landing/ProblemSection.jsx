import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, MessageCircle, Frown, HelpCircle } from 'lucide-react';

const problems = [
  { icon: MessageCircle, title: 'Misinformation', desc: 'Myths and rumors about contraception spread faster than facts, especially on social media.', color: 'text-destructive' },
  { icon: AlertTriangle, title: 'Stigma & Shame', desc: 'Cultural taboos prevent open conversations about reproductive health and family planning.', color: 'text-accent' },
  { icon: Frown, title: 'Side Effect Fears', desc: 'Unaddressed concerns about side effects lead to contraceptive discontinuation and unplanned pregnancies.', color: 'text-primary' },
  { icon: HelpCircle, title: 'Lack of Guidance', desc: 'Limited access to trained healthcare providers leaves many without personalized contraceptive advice.', color: 'text-secondary' },
];

export default function ProblemSection() {
  return (
    <section className="py-20 bg-card">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <p className="text-sm font-medium text-accent uppercase tracking-wider mb-2">The Challenge</p>
          <h2 className="font-heading text-3xl sm:text-4xl font-bold">
            Why contraceptive decisions are hard
          </h2>
          <p className="mt-4 text-muted-foreground max-w-2xl mx-auto">
            Millions of African women face barriers to informed contraceptive choices every day.
          </p>
        </motion.div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {problems.map((p, i) => (
            <motion.div
              key={p.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="bg-background rounded-2xl p-6 border hover:shadow-lg transition-shadow"
            >
              <p.icon className={`w-8 h-8 ${p.color} mb-4`} />
              <h3 className="font-heading font-semibold text-lg mb-2">{p.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{p.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}