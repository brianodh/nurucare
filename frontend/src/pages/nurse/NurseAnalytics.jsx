import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { mockDashboardStats } from '@/lib/mockData';
import { getDashboardStats } from '@/api/apiClient';
import { useLang } from '@/lib/i18n.jsx';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
} from 'recharts';

export default function NurseAnalytics() {
  const [stats, setStats] = useState(null);
  const { t } = useLang();

  useEffect(() => {
    getDashboardStats().then(setStats).catch(() => {});
  }, []);

  const ageDemographics = stats?.ageDemographics ?? mockDashboardStats.ageDemographics;
  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="font-heading text-2xl font-bold">{t('nurse_analytics_title')}</h1>
        <p className="text-muted-foreground text-sm mt-1">{t('nurse_analytics_sub')}</p>
      </motion.div>

      <div className="grid lg:grid-cols-2 gap-6">
        <Card className="p-5 rounded-2xl">
          <h3 className="font-heading font-semibold mb-4">{t('nurse_analytics_age_demo')}</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={ageDemographics}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(220,14%,88%)" />
              <XAxis dataKey="range" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="count" fill="hsl(243,60%,55%)" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card className="p-5 rounded-2xl">
          <h3 className="font-heading font-semibold mb-4">{t('nurse_analytics_risk_dist')}</h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={mockDashboardStats.riskDistribution}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                dataKey="value"
                stroke="none"
                label={({ name, value }) => `${name}: ${value}%`}
              >
                {mockDashboardStats.riskDistribution.map((entry, i) => (
                  <Cell key={i} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex justify-center gap-4 mt-2">
            {mockDashboardStats.riskDistribution.map(d => (
              <div key={d.name} className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: d.fill }} />
                {d.name} ({d.value}%)
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-5 rounded-2xl lg:col-span-2">
          <h3 className="font-heading font-semibold mb-4">{t('nurse_analytics_rec_cats')}</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={mockDashboardStats.recommendationDistribution} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(220,14%,88%)" />
              <XAxis type="number" tick={{ fontSize: 12 }} />
              <YAxis dataKey="name" type="category" tick={{ fontSize: 12 }} width={60} />
              <Tooltip />
              <Bar dataKey="value" radius={[0, 6, 6, 0]}>
                {mockDashboardStats.recommendationDistribution.map((_, i) => (
                  <Cell key={i} fill={['hsl(243,60%,55%)', 'hsl(174,52%,46%)', 'hsl(336,60%,65%)', 'hsl(43,74%,66%)', 'hsl(220,10%,70%)'][i]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>
    </div>
  );
}