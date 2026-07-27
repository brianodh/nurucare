import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Heart, User, Stethoscope, ArrowRight, RotateCcw, X } from 'lucide-react';
import { useLang } from '@/lib/i18n';
import { loadProgress, clearProgress, saveProgress } from '@/lib/useProgress';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/lib/AuthContext';

export default function RoleSelection() {
  const { t } = useLang();
  const { user } = useAuth();
  const navigate = useNavigate();
  const saved = loadProgress();
  const hasSaved = saved.lastPath && saved.intakeStep > 0;

  const formatTime = (ts) => {
    if (!ts) return '';
    const diff = Date.now() - ts;
    const mins = Math.floor(diff / 60000);
    const hrs = Math.floor(mins / 60);
    if (hrs > 0) return `${hrs}h ago`;
    if (mins > 0) return `${mins}m ago`;
    return 'just now';
  };

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
          <h1 className="font-heading text-3xl sm:text-4xl font-bold mb-4">
            {user?.name ? `Welcome, ${user.name.split(' ')[0]} 👋` : t('roles_title')}
          </h1>
          <p className="text-muted-foreground max-w-md mx-auto">{t('roles_sub')}</p>
        </motion.div>

        {hasSaved && (
          <motion.div
            initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
            className="mb-8 bg-primary/5 border border-primary/20 rounded-2xl p-4 flex items-center justify-between gap-4"
          >
            <div className="flex items-center gap-3">
              <RotateCcw className="w-5 h-5 text-primary flex-shrink-0" />
              <div>
                <p className="font-medium text-sm">Continue your assessment</p>
                <p className="text-xs text-muted-foreground">Step {(saved.intakeStep ?? 0) + 1} of 5 saved {formatTime(saved.savedAt)}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button size="sm" className="rounded-full" onClick={() => navigate(saved.lastPath)}>
                Resume
              </Button>
              <Button size="sm" variant="ghost" className="rounded-full px-2" onClick={() => { clearProgress(); window.location.reload(); }}>
                <X className="w-4 h-4" />
              </Button>
            </div>
          </motion.div>
        )}

        <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-5">
          {roles.map((r, i) => (
            <motion.div key={r.id} initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
              <Link to={r.path} onClick={() => saveProgress({ role: r.id, lastPath: r.path })}>
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