import React from 'react';
import { motion } from 'framer-motion';
import { Brain, BookOpen, Users, Lock, Stethoscope, Sparkles } from 'lucide-react';

const features = [
  { icon: Brain, title: 'Smart Recommendation Engine', desc: 'AI-powered analysis of your health profile against WHO eligibility criteria for personalized guidance.', gradient: 'from-primary/10 to-primary/5' },
  { icon: BookOpen, title: 'Myth vs Fact Education', desc: 'Evidence-based content that separates fiction from science, presented in culturally sensitive ways.', gradient: 'from-secondary/10 to-secondary/5' },
  { icon: Users, title: 'Partner Sync', desc: 'Anonymous, secure way for couples to share health decisions and build shared understanding.', gradient: 'from-accent/10 to-accent/5' },
  { icon: Lock, title: 'Privacy-First Consultations', desc: 'Session-based access with expiring keys ensures your health data stays confidential and secure.', gradient: 'from-primary/10 to-secondary/5' },
  { icon: Stethoscope, title: 'Nurse Support Dashboard', desc: 'Healthcare professionals get streamlined tools to support clients with data-driven insights.', gradient: 'from-secondary/10 to-accent/5' },
  { icon: Sparkles, title: 'AI-Powered Guidance', desc: 'Natural language explanations of recommendations help you understand the "why" behind each option.', gradient: 'from-accent/10 to-primary/5' },
];

export default function FeaturesSection() {
  return (
    <section className="py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <p className="text-sm font-medium text-primary uppercase tracking-wider mb-2">Features</p>
          <h2 className="font-heading text-3xl sm:text-4xl font-bold">
            Everything you need for informed choices
          </h2>
        </motion.div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08 }}
              className={`bg-gradient-to-br ${f.gradient} rounded-2xl p-6 border hover:shadow-lg transition-all hover:-translate-y-1`}
            >
              <div className="w-12 h-12 rounded-xl bg-card flex items-center justify-center mb-4 shadow-sm">
                <f.icon className="w-6 h-6 text-primary" />
              </div>
              <h3 className="font-heading font-semibold text-lg mb-2">{f.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}