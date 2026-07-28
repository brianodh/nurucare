/*
 ENDPOINT → METRIC MAPPING (all live DB queries, no seed numbers):
 ─────────────────────────────────────────────────────────────────
 GET /api/v1/admin/overview →
   total_patients         : Card "Total Patients"
   total_nurses           : Card "Total Nurses"
   total_admins           : Card "Total Admins"
   new_signups_this_week  : Card "New This Week"
   channel_split.web      : Channel split (web intake count)
   channel_split.ussd     : Channel split (USSD intake count)
   ussd_sessions.total    : USSD sessions total
   ussd_sessions.active   : USSD sessions active
   ussd_sessions.tracked  : if false → show "not yet tracked" instead of 0
 ─────────────────────────────────────────────────────────────────
 GET /api/v1/admin/signup-trend → last-7-days bar chart x=date, y=total
 GET /api/v1/admin/health  → recommendation_engine.active_path banner:
   - hardcoded_fallback            → amber banner "Engine not connected (hardcoded fallback live)"
   - engine_available_but_not_connected → blue banner "WHO MEC engine available; /recommend endpoint not wired yet"
   - connected                     → green banner "WHO MEC + RAG engine active"
*/

import React, { useEffect, useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Users, UserPlus, Shield, TrendingUp, Loader2, RefreshCw, Globe, Smartphone, BarChart3, Activity } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { getAdminOverview, getAdminSignupTrend, getAdminSystemHealth } from '@/api/apiClient';

const engineBannerStyles = {
  hardcoded_fallback: 'bg-amber-500/10 border-amber-500/30 text-amber-700 dark:text-amber-300',
  engine_available_but_not_connected: 'bg-blue-500/10 border-blue-500/30 text-blue-700 dark:text-blue-300',
  connected: 'bg-green-500/10 border-green-500/30 text-green-700 dark:text-green-300',
};

const engineBannerMessages = {
  hardcoded_fallback: 'Engine not connected (hardcoded fallback live)',
  engine_available_but_not_connected: 'WHO MEC engine available; /recommend endpoint not wired yet',
  connected: 'WHO MEC + RAG engine active',
};

export default function AdminDashboard() {
  const [overview, setOverview] = useState(null);
  const [signupTrend, setSignupTrend] = useState(null);
  const [systemHealth, setSystemHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const fetchAllData = useCallback(async () => {
    try {
      setError(false);
      const [ov, trend, health] = await Promise.all([
        getAdminOverview().catch(() => null),
        getAdminSignupTrend(7).catch(() => null),
        getAdminSystemHealth().catch(() => null),
      ]);
      setOverview(ov);
      setSignupTrend(trend);
      setSystemHealth(health);
    } catch (e) {
      setError(true);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  const handleRefresh = () => {
    setRefreshing(true);
    setLoading(true);
    fetchAllData();
  };

  const totalPatients = overview?.total_patients ?? 0;
  const totalNurses = overview?.total_nurses ?? 0;
  const totalAdmins = overview?.total_admins ?? 0;
  const newThisWeek = overview?.new_signups_this_week ?? 0;

  const channelWeb = overview?.channel_split?.web ?? 0;
  const channelUssd = overview?.channel_split?.ussd ?? 0;
  const channelTotal = channelWeb + channelUssd;

  const ussdTracked = overview?.ussd_sessions?.tracked;
  const ussdTotal = overview?.ussd_sessions?.total ?? 0;
  const ussdActive = overview?.ussd_sessions?.active ?? 0;

  const activePath = systemHealth?.recommendation_engine?.active_path;
  const bannerVariant = engineBannerStyles[activePath] ?? 'bg-muted border-muted text-muted-foreground';
  const bannerMessage = engineBannerMessages[activePath] ?? 'Recommendation engine status unknown';

  const trendData = Array.isArray(signupTrend) ? signupTrend : [];
  const maxTrendVal = trendData.reduce((m, d) => Math.max(m, d?.total ?? 0), 0);

  const statCards = [
    { title: 'Total Patients', value: totalPatients, icon: Users, color: 'text-primary bg-primary/10' },
    { title: 'Total Nurses', value: totalNurses, icon: UserPlus, color: 'text-secondary bg-secondary/10' },
    { title: 'Total Admins', value: totalAdmins, icon: Shield, color: 'text-accent bg-accent/10' },
    { title: 'New This Week', value: newThisWeek, icon: TrendingUp, color: 'text-emerald-600 bg-emerald-500/10' },
  ];

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-start justify-between flex-wrap gap-4"
      >
        <div>
          <h1 className="font-heading text-2xl font-bold">Admin Dashboard</h1>
          <p className="text-muted-foreground text-sm mt-1">System-wide overview and platform metrics.</p>
        </div>
        <Button variant="outline" size="sm" onClick={handleRefresh} disabled={refreshing}>
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.05 }}
      >
        <Card className={`border ${bannerVariant} rounded-2xl`}>
          <CardContent className="p-4 flex items-center gap-3">
            <Activity className="w-5 h-5 shrink-0" />
            <div className="flex-1">
              <p className="text-sm font-medium">{bannerMessage}</p>
              {error && (
                <p className="text-xs opacity-70 mt-0.5">Live data unavailable — showing last known or zero values.</p>
              )}
            </div>
            {activePath && <Badge variant="outline" className="capitalize text-xs">{activePath.replace(/_/g, ' ')}</Badge>}
          </CardContent>
        </Card>
      </motion.div>

      {loading && !refreshing ? (
        <div className="flex items-center gap-2 text-muted-foreground text-sm">
          <Loader2 className="w-4 h-4 animate-spin" /> Loading live data…
        </div>
      ) : null}

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((s, i) => (
          <motion.div
            key={s.title}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 + i * 0.05 }}
          >
            <Card className="p-4 rounded-2xl">
              <div className="flex items-center justify-between mb-3">
                <div className={`w-10 h-10 rounded-xl ${s.color} flex items-center justify-center`}>
                  <s.icon className="w-5 h-5" />
                </div>
              </div>
              <p className="text-2xl font-heading font-bold">{s.value}</p>
              <p className="text-xs text-muted-foreground mt-1">{s.title}</p>
              {error && s.value === 0 && (
                <p className="text-[11px] text-muted-foreground mt-1 opacity-70">Live data unavailable</p>
              )}
              {!error && !loading && s.value === 0 && (
                <p className="text-[11px] text-muted-foreground mt-1 opacity-70">No data yet</p>
              )}
            </Card>
          </motion.div>
        ))}
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card className="p-5 rounded-2xl h-full">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-9 h-9 rounded-lg bg-secondary/10 text-secondary flex items-center justify-center">
                <Globe className="w-4.5 h-4.5" />
              </div>
              <div>
                <h3 className="font-heading font-semibold leading-tight">Intake Channel Split</h3>
                <p className="text-xs text-muted-foreground">Web vs USSD profile creation</p>
              </div>
            </div>

            {channelTotal === 0 ? (
              <div className="py-10 text-center">
                <p className="text-sm text-muted-foreground">No profiles yet.</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Globe className="w-4 h-4 text-primary" />
                    <span className="text-sm">Web</span>
                  </div>
                  <span className="font-semibold">{channelWeb}</span>
                </div>
                <div className="h-2.5 w-full bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary rounded-full transition-all duration-500"
                    style={{ width: `${channelTotal > 0 ? (channelWeb / channelTotal) * 100 : 0}%` }}
                  />
                </div>

                <div className="flex items-center justify-between pt-2">
                  <div className="flex items-center gap-2">
                    <Smartphone className="w-4 h-4 text-secondary" />
                    <span className="text-sm">USSD</span>
                  </div>
                  <span className="font-semibold">{channelUssd}</span>
                </div>
                <div className="h-2.5 w-full bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-secondary rounded-full transition-all duration-500"
                    style={{ width: `${channelTotal > 0 ? (channelUssd / channelTotal) * 100 : 0}%` }}
                  />
                </div>

                <div className="pt-2 flex items-center justify-between text-xs text-muted-foreground border-t pt-3 mt-2">
                  <span>Total intakes</span>
                  <span className="font-medium text-foreground">{channelTotal}</span>
                </div>
              </div>
            )}
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
        >
          <Card className="p-5 rounded-2xl h-full">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-9 h-9 rounded-lg bg-accent/10 text-accent flex items-center justify-center">
                <Smartphone className="w-4.5 h-4.5" />
              </div>
              <div>
                <h3 className="font-heading font-semibold leading-tight">USSD Sessions</h3>
                <p className="text-xs text-muted-foreground">Live USSD session metrics</p>
              </div>
            </div>

            {ussdTracked === false ? (
              <div className="py-10 text-center">
                <p className="text-sm text-muted-foreground">USSD sessions: not yet tracked</p>
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-4">
                <div className="rounded-xl border p-4">
                  <p className="text-xs text-muted-foreground">Total</p>
                  <p className="text-2xl font-heading font-bold mt-1">{ussdTotal}</p>
                  {error && ussdTotal === 0 && (
                    <p className="text-[11px] text-muted-foreground mt-1 opacity-70">Live data unavailable</p>
                  )}
                  {!error && !loading && ussdTotal === 0 && ussdTracked !== false && (
                    <p className="text-[11px] text-muted-foreground mt-1 opacity-70">No data yet</p>
                  )}
                </div>
                <div className="rounded-xl border p-4">
                  <p className="text-xs text-muted-foreground">Active now</p>
                  <p className="text-2xl font-heading font-bold mt-1">{ussdActive}</p>
                  {error && ussdActive === 0 && (
                    <p className="text-[11px] text-muted-foreground mt-1 opacity-70">Live data unavailable</p>
                  )}
                  {!error && !loading && ussdActive === 0 && ussdTracked !== false && (
                    <p className="text-[11px] text-muted-foreground mt-1 opacity-70">No data yet</p>
                  )}
                </div>
                <div className="col-span-2 flex items-center justify-between text-xs text-muted-foreground border-t pt-3">
                  <span>Tracking status</span>
                  <Badge variant="outline" className={ussdTracked ? 'text-green-700 border-green-500/30 bg-green-500/10' : ''}>
                    {ussdTracked ? 'Tracked' : 'Untracked'}
                  </Badge>
                </div>
              </div>
            )}
          </Card>
        </motion.div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Card className="p-5 rounded-2xl">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-9 h-9 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
              <BarChart3 className="w-4.5 h-4.5" />
            </div>
            <div>
              <h3 className="font-heading font-semibold leading-tight">Signup Trend — Last 7 Days</h3>
              <p className="text-xs text-muted-foreground">Daily new user registrations</p>
            </div>
          </div>

          {trendData.length === 0 || maxTrendVal === 0 ? (
            <div className="py-14 text-center">
              <BarChart3 className="w-10 h-10 mx-auto text-muted-foreground/40 mb-3" />
              <p className="text-sm text-muted-foreground">
                {error ? 'Live data unavailable' : 'No signup data yet for the last 7 days.'}
              </p>
            </div>
          ) : (
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={trendData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} className="stroke-muted" />
                  <XAxis
                    dataKey="date"
                    tickLine={false}
                    axisLine={false}
                    tick={{ fontSize: 12, fill: 'currentColor' }}
                    className="text-muted-foreground"
                  />
                  <YAxis
                    tickLine={false}
                    axisLine={false}
                    tick={{ fontSize: 12, fill: 'currentColor' }}
                    className="text-muted-foreground"
                    allowDecimals={false}
                  />
                  <Tooltip
                    cursor={{ fill: 'rgba(0,0,0,0.04)' }}
                    contentStyle={{ borderRadius: 12, border: '1px solid hsl(var(--border))', background: 'hsl(var(--card))' }}
                  />
                  <Bar
                    dataKey="total"
                    fill="hsl(var(--primary))"
                    radius={[6, 6, 0, 0]}
                    maxBarSize={42}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </Card>
      </motion.div>
    </div>
  );
}
