import React from 'react';
import { motion } from 'framer-motion';
import { UserCheck, ClipboardList, Sparkles, Heart } from 'lucide-react';

const steps = [
  { icon: UserCheck, title: 'Choose Your Role', desc: 'Select your profile — female client, male client, or healthcare professional.' },
  { icon: ClipboardList, title: 'Complete Assessment', desc: 'Answer guided health questions in a safe, judgment-free environment.' },
  { icon: Sparkles, title: 'Get Recommendations', desc: 'Receive personalized, WHO-aligned contraceptive guidance with clear explanations.' },
  { icon: Heart, title: 'Take Action', desc: 'Access educational resources, connect with your partner, or consult a nurse.' },
];

export default function HowItWorksSection() {
  return (
    <section className="py-20 bg-card">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <p className="text-sm font-medium text-secondary uppercase tracking-wider mb-2">How It Works</p>
          <h2 className="font-heading text-3xl sm:text-4xl font-bold">Simple steps to clarity</h2>
        </motion.div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((s, i) => (
            <motion.div
              key={s.title}
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
              <h3 className="font-heading font-semibold mt-4 mb-2">{s.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{s.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}