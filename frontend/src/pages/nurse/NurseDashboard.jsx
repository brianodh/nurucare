import React from 'react';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Users, AlertTriangle, Activity, Calendar } from 'lucide-react';
import { mockDashboardStats, mockNursePatients } from '@/lib/mockData';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

const statCards = [
  { title: 'Active Consultations', value: mockDashboardStats.activeConsultations, icon: Users, color: 'text-primary bg-primary/10' },
  { title: 'Risk Flags', value: mockDashboardStats.riskFlags, icon: AlertTriangle, color: 'text-destructive bg-destructive/10' },
  { title: 'Daily Sessions', value: mockDashboardStats.dailySessions, icon: Activity, color: 'text-secondary bg-secondary/10' },
  { title: 'This Week', value: '87', icon: Calendar, color: 'text-accent bg-accent/10' },
];

const riskColors = { Low: 'bg-secondary/10 text-secondary', Medium: 'bg-accent/10 text-accent', High: 'bg-destructive/10 text-destructive' };
const statusColors = { Active: 'bg-secondary/10 text-secondary', Pending: 'bg-muted text-muted-foreground', Flagged: 'bg-destructive/10 text-destructive' };

export default function NurseDashboard() {
  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="font-heading text-2xl font-bold">Dashboard Overview</h1>
        <p className="text-muted-foreground text-sm mt-1">Welcome back. Here's today's summary.</p>
      </motion.div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((s, i) => (
          <motion.div key={s.title} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}>
            <Card className="p-4 rounded-2xl">
              <div className="flex items-center justify-between mb-3">
                <div className={`w-10 h-10 rounded-xl ${s.color} flex items-center justify-center`}>
                  <s.icon className="w-5 h-5" />
                </div>
              </div>
              <p className="text-2xl font-heading font-bold">{s.value}</p>
              <p className="text-xs text-muted-foreground mt-1">{s.title}</p>
            </Card>
          </motion.div>
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <Card className="p-5 rounded-2xl lg:col-span-2">
          <h3 className="font-heading font-semibold mb-4">Recent Patients</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-muted-foreground border-b">
                  <th className="pb-3 font-medium">Session ID</th>
                  <th className="pb-3 font-medium">Age</th>
                  <th className="pb-3 font-medium">Status</th>
                  <th className="pb-3 font-medium">Risk</th>
                  <th className="pb-3 font-medium">Recommendation</th>
                </tr>
              </thead>
              <tbody>
                {mockNursePatients.map(p => (
                  <tr key={p.id} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                    <td className="py-3 font-mono font-medium">{p.id}</td>
                    <td className="py-3">{p.age}</td>
                    <td className="py-3"><Badge variant="secondary" className={`${statusColors[p.status]} text-xs`}>{p.status}</Badge></td>
                    <td className="py-3"><Badge variant="secondary" className={`${riskColors[p.riskLevel]} text-xs`}>{p.riskLevel}</Badge></td>
                    <td className="py-3 text-muted-foreground">{p.recommendation}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        <Card className="p-5 rounded-2xl">
          <h3 className="font-heading font-semibold mb-4">Recommendation Distribution</h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={mockDashboardStats.recommendationDistribution}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={80}
                dataKey="value"
                stroke="none"
              >
                {mockDashboardStats.recommendationDistribution.map((_, i) => (
                  <Cell key={i} fill={['hsl(243,60%,55%)', 'hsl(174,52%,46%)', 'hsl(336,60%,65%)', 'hsl(43,74%,66%)', 'hsl(220,10%,70%)'][i]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex flex-wrap gap-2 mt-2">
            {mockDashboardStats.recommendationDistribution.map((d, i) => (
              <div key={d.name} className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: ['hsl(243,60%,55%)', 'hsl(174,52%,46%)', 'hsl(336,60%,65%)', 'hsl(43,74%,66%)', 'hsl(220,10%,70%)'][i] }} />
                {d.name}
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}