import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Heart, User, Stethoscope, ArrowRight } from 'lucide-react';
import { useLang } from '@/lib/i18n';

export default function RoleSelection() {
  const { t } = useLang();

  const roles = [
    {
      id: 'female',
      icon: Heart,
      titleKey: 'role_female_title',
      descKey: 'role_female_desc',
      path: '/female/intake',
      color: 'from-accent/10 to-accent/5 border-accent/20',
      iconColor: 'text-accent bg-accent/10',
    },
    {
      id: 'male',
      icon: User,
      titleKey: 'role_male_title',
      descKey: 'role_male_desc',
      path: '/male/dashboard',
      color: 'from-primary/10 to-primary/5 border-primary/20',
      iconColor: 'text-primary bg-primary/10',
    },
    {
      id: 'nurse',
      icon: Stethoscope,
      titleKey: 'role_nurse_title',
      descKey: 'role_nurse_desc',
      path: '/nurse/dashboard',
      color: 'from-secondary/10 to-secondary/5 border-secondary/20',
      iconColor: 'text-secondary bg-secondary/10',
    },
  ];

  return (
    <div className="min-h-[85vh] flex items-center justify-center py-12 px-4">
      <div className="max-w-4xl mx-auto w-full">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-12">
          <h1 className="font-heading text-3xl sm:text-4xl font-bold mb-4">{t('roles_title')}</h1>
          <p className="text-muted-foreground max-w-md mx-auto">{t('roles_sub')}</p>
        </motion.div>

        <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-5">
          {roles.map((r, i) => (
            <motion.div key={r.id} initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
              <Link to={r.path}>
                <div className={`bg-gradient-to-br ${r.color} rounded-2xl border p-6 h-full hover:shadow-lg transition-all hover:-translate-y-1 cursor-pointer group`}>
                  <div className={`w-14 h-14 rounded-2xl ${r.iconColor} flex items-center justify-center mb-5`}>
                    <r.icon className="w-7 h-7" />
                  </div>
                  <h3 className="font-heading font-semibold text-xl mb-2">{t(r.titleKey)}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed mb-6">{t(r.descKey)}</p>
                  <div className="flex items-center gap-2 text-sm font-medium text-primary group-hover:gap-3 transition-all">
                    {t('role_continue')} <ArrowRight className="w-4 h-4" />
                  </div>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}