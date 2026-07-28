import React, { useEffect, useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from '@/components/ui/table';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import {
  KeyRound,
  RefreshCw,
  Repeat,
  ShieldAlert,
  CheckCircle2,
  XCircle,
  Clock,
  Trash2,
  Loader2,
} from 'lucide-react';
import {
  getNurseSessionMonitor,
  forceExpireNurseSession,
  getPartnerSyncMonitor,
} from '@/api/apiClient';

const nurseStatusStyles = {
  active: 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border-emerald-500/30',
  used: 'bg-sky-500/15 text-sky-700 dark:text-sky-400 border-sky-500/30',
  force_expired: 'bg-amber-500/15 text-amber-700 dark:text-amber-400 border-amber-500/30',
  expired: 'bg-rose-500/15 text-rose-700 dark:text-rose-400 border-rose-500/30',
};

const partnerStatusStyles = {
  active: 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border-emerald-500/30',
  used: 'bg-sky-500/15 text-sky-700 dark:text-sky-400 border-sky-500/30',
  expired: 'bg-rose-500/15 text-rose-700 dark:text-rose-400 border-rose-500/30',
};

const formatDate = (iso) => {
  if (!iso) return '—';
  try {
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return String(iso);
    return d.toLocaleString(undefined, {
      year: 'numeric',
      month: 'short',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return String(iso);
  }
};

const shortId = (id, len = 8) => {
  if (!id) return '—';
  const s = String(id);
  return s.length > len ? s.slice(0, len) : s;
};

function StatCardSkeleton() {
  return (
    <Card className="p-4 rounded-2xl">
      <div className="flex items-center justify-between mb-3">
        <Skeleton className="w-10 h-10 rounded-xl" />
      </div>
      <Skeleton className="h-7 w-16 rounded-md mb-2" />
      <Skeleton className="h-3 w-24 rounded-md" />
    </Card>
  );
}

function TableSkeleton({ rows = 4, cols = 6 }) {
  return (
    <div className="space-y-2">
      <Skeleton className="h-9 w-full rounded-md" />
      {Array.from({ length: rows }).map((_, i) => (
        <Skeleton key={i} className="h-14 w-full rounded-md" />
      ))}
    </div>
  );
}

export default function SessionMonitor() {
  const [nurseData, setNurseData] = useState(null);
  const [nurseLoading, setNurseLoading] = useState(true);
  const [nurseError, setNurseError] = useState(false);
  const [nurseRefreshing, setNurseRefreshing] = useState(false);

  const [partnerData, setPartnerData] = useState(null);
  const [partnerLoading, setPartnerLoading] = useState(true);
  const [partnerError, setPartnerError] = useState(false);
  const [partnerRefreshing, setPartnerRefreshing] = useState(false);

  const [forceExpireTarget, setForceExpireTarget] = useState(null);
  const [forceExpireLoading, setForceExpireLoading] = useState(false);

  const fetchNurseSessions = useCallback(async (isRefresh = false) => {
    if (isRefresh) setNurseRefreshing(true);
    setNurseLoading(!isRefresh);
    try {
      setNurseError(false);
      const data = await getNurseSessionMonitor();
      setNurseData(data);
    } catch (e) {
      setNurseError(true);
    } finally {
      setNurseLoading(false);
      setNurseRefreshing(false);
    }
  }, []);

  const fetchPartnerSync = useCallback(async (isRefresh = false) => {
    if (isRefresh) setPartnerRefreshing(true);
    setPartnerLoading(!isRefresh);
    try {
      setPartnerError(false);
      const data = await getPartnerSyncMonitor();
      setPartnerData(data);
    } catch (e) {
      setPartnerError(true);
    } finally {
      setPartnerLoading(false);
      setPartnerRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchNurseSessions();
    fetchPartnerSync();
  }, [fetchNurseSessions, fetchPartnerSync]);

  const handleForceExpire = async () => {
    if (!forceExpireTarget) return;
    try {
      setForceExpireLoading(true);
      await forceExpireNurseSession(forceExpireTarget);
      setForceExpireTarget(null);
      fetchNurseSessions(true);
    } catch (e) {
      console.error('Force expire failed', e);
    } finally {
      setForceExpireLoading(false);
    }
  };

  const nurseActiveCount = nurseData?.active_count ?? 0;
  const nurseExpiredCount = nurseData?.expired_count ?? 0;
  const nurseUsedCount = nurseData?.used_count ?? 0;
  const nurseForceExpiredCount = nurseData?.force_expired_count ?? 0;
  const nurseSessions = Array.isArray(nurseData?.sessions) ? nurseData.sessions : [];

  const partnerActiveCount = partnerData?.active_count ?? 0;
  const partnerExpiredCount = partnerData?.expired_count ?? 0;
  const partnerUsedCount = partnerData?.used_count ?? 0;
  const partnerTokens = Array.isArray(partnerData?.tokens) ? partnerData.tokens : [];

  const nurseStatCards = [
    { title: 'Active', value: nurseActiveCount, icon: CheckCircle2, color: 'text-emerald-600 bg-emerald-500/10' },
    { title: 'Used', value: nurseUsedCount, icon: XCircle, color: 'text-sky-600 bg-sky-500/10' },
    { title: 'Force-Expired', value: nurseForceExpiredCount, icon: ShieldAlert, color: 'text-amber-600 bg-amber-500/10' },
    { title: 'Expired', value: nurseExpiredCount, icon: Clock, color: 'text-rose-600 bg-rose-500/10' },
  ];

  const partnerStatCards = [
    { title: 'Active', value: partnerActiveCount, icon: CheckCircle2, color: 'text-emerald-600 bg-emerald-500/10' },
    { title: 'Used', value: partnerUsedCount, icon: XCircle, color: 'text-sky-600 bg-sky-500/10' },
    { title: 'Expired', value: partnerExpiredCount, icon: Clock, color: 'text-rose-600 bg-rose-500/10' },
  ];

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="font-heading text-2xl font-bold">Session &amp; Sync Monitor</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Track nurse access codes and partner sync tokens. Addresses 6-digit nurse-code abuse risk via
          force-expire controls.
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.05 }}
      >
        <Card className="rounded-2xl">
          <CardHeader className="pb-3">
            <div className="flex items-start justify-between flex-wrap gap-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
                  <KeyRound className="w-5 h-5" />
                </div>
                <div>
                  <CardTitle className="font-heading text-lg leading-tight">Nurse Access Codes</CardTitle>
                  <CardDescription className="text-xs mt-0.5">
                    6-character session keys for nurse-to-patient handoff
                  </CardDescription>
                </div>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => fetchNurseSessions(true)}
                disabled={nurseRefreshing || nurseLoading}
              >
                <RefreshCw className={`w-4 h-4 mr-1.5 ${nurseRefreshing ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-5">
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              {nurseLoading && !nurseData ? (
                Array.from({ length: 4 }).map((_, i) => <StatCardSkeleton key={i} />)
              ) : (
                nurseStatCards.map((s, i) => (
                  <motion.div
                    key={s.title}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 + i * 0.03 }}
                  >
                    <Card className="p-4 rounded-2xl">
                      <div className="flex items-center justify-between mb-3">
                        <div className={`w-10 h-10 rounded-xl ${s.color} flex items-center justify-center`}>
                          <s.icon className="w-5 h-5" />
                        </div>
                      </div>
                      <p className="text-2xl font-heading font-bold">{s.value}</p>
                      <p className="text-xs text-muted-foreground mt-1">{s.title}</p>
                      {nurseError && s.value === 0 && (
                        <p className="text-[11px] text-muted-foreground mt-1 opacity-70">Live data unavailable</p>
                      )}
                    </Card>
                  </motion.div>
                ))
              )}
            </div>

            {nurseError ? (
              <Card className="rounded-xl border-destructive/40 bg-destructive/5">
                <CardContent className="p-4 flex items-center gap-3">
                  <ShieldAlert className="w-5 h-5 text-destructive shrink-0" />
                  <div>
                    <p className="text-sm font-medium text-destructive">
                      Could not load nurse session monitor
                    </p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      Backend may be unreachable or permissions insufficient.
                    </p>
                  </div>
                </CardContent>
              </Card>
            ) : nurseLoading && !nurseData ? (
              <TableSkeleton rows={4} cols={6} />
            ) : nurseSessions.length === 0 ? (
              <div className="py-12 text-center rounded-xl border border-dashed border-muted">
                <KeyRound className="w-10 h-10 mx-auto text-muted-foreground/40 mb-3" />
                <p className="text-sm text-muted-foreground">No nurse sessions yet.</p>
              </div>
            ) : (
              <div className="overflow-x-auto rounded-xl border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="pl-4">Access Code</TableHead>
                      <TableHead>Profile ID</TableHead>
                      <TableHead>Created At</TableHead>
                      <TableHead>Expires At</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="pr-4 text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {nurseSessions.map((s) => {
                      const isActive = s.status === 'active';
                      const statusClass = nurseStatusStyles[s.status] || 'bg-muted text-muted-foreground';
                      return (
                        <TableRow key={s.session_id || s.id || s.access_code}>
                          <TableCell className="pl-4">
                            <Badge variant="outline" className="font-mono text-xs tracking-wider">
                              {s.access_code || '—'}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <span className="font-mono text-xs">{shortId(s.profile_id)}</span>
                          </TableCell>
                          <TableCell className="text-xs text-muted-foreground whitespace-nowrap">
                            {formatDate(s.created_at)}
                          </TableCell>
                          <TableCell className="text-xs text-muted-foreground whitespace-nowrap">
                            {formatDate(s.expires_at)}
                          </TableCell>
                          <TableCell>
                            <Badge variant="outline" className={`${statusClass} capitalize text-xs`}>
                              {String(s.status || 'unknown').replace(/_/g, ' ')}
                            </Badge>
                          </TableCell>
                          <TableCell className="pr-4 text-right">
                            {isActive ? (
                              <AlertDialog>
                                <AlertDialogTrigger asChild>
                                  <Button
                                    variant="destructive"
                                    size="sm"
                                    className="h-8 text-xs"
                                    onClick={() => setForceExpireTarget(s.session_id || s.id)}
                                  >
                                    <Trash2 className="w-3.5 h-3.5 mr-1" />
                                    Force Expire
                                  </Button>
                                </AlertDialogTrigger>
                                <AlertDialogContent>
                                  <AlertDialogHeader>
                                    <AlertDialogTitle className="flex items-center gap-2">
                                      <ShieldAlert className="w-5 h-5 text-amber-600" />
                                      Force-expire this access code?
                                    </AlertDialogTitle>
                                    <AlertDialogDescription>
                                      Access code{' '}
                                      <span className="font-mono font-semibold">
                                        {s.access_code || '(unknown)'}
                                      </span>{' '}
                                      will be immediately revoked and cannot be reused. Any nurse currently
                                      relying on it will lose access.
                                    </AlertDialogDescription>
                                  </AlertDialogHeader>
                                  <AlertDialogFooter>
                                    <AlertDialogCancel onClick={() => setForceExpireTarget(null)}>
                                      Cancel
                                    </AlertDialogCancel>
                                    <AlertDialogAction
                                      onClick={(e) => {
                                        e.preventDefault();
                                        handleForceExpire();
                                      }}
                                      className="bg-destructive hover:bg-destructive/90 text-destructive-foreground"
                                      disabled={forceExpireLoading}
                                    >
                                      {forceExpireLoading ? (
                                        <>
                                          <Loader2 className="w-4 h-4 mr-1.5 animate-spin" />
                                          Expiring…
                                        </>
                                      ) : (
                                        <>
                                          <Trash2 className="w-4 h-4 mr-1.5" />
                                          Force Expire
                                        </>
                                      )}
                                    </AlertDialogAction>
                                  </AlertDialogFooter>
                                </AlertDialogContent>
                              </AlertDialog>
                            ) : (
                              <span className="text-xs text-muted-foreground italic">—</span>
                            )}
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card className="rounded-2xl">
          <CardHeader className="pb-3">
            <div className="flex items-start justify-between flex-wrap gap-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-secondary/10 text-secondary flex items-center justify-center">
                  <Repeat className="w-5 h-5" />
                </div>
                <div>
                  <CardTitle className="font-heading text-lg leading-tight">Partner Sync Tokens</CardTitle>
                  <CardDescription className="text-xs mt-0.5">
                    Anonymous tokens used to link patient profiles with partners
                  </CardDescription>
                </div>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => fetchPartnerSync(true)}
                disabled={partnerRefreshing || partnerLoading}
              >
                <RefreshCw className={`w-4 h-4 mr-1.5 ${partnerRefreshing ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-5">
            <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
              {partnerLoading && !partnerData ? (
                Array.from({ length: 3 }).map((_, i) => <StatCardSkeleton key={i} />)
              ) : (
                partnerStatCards.map((s, i) => (
                  <motion.div
                    key={s.title}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.15 + i * 0.03 }}
                  >
                    <Card className="p-4 rounded-2xl">
                      <div className="flex items-center justify-between mb-3">
                        <div className={`w-10 h-10 rounded-xl ${s.color} flex items-center justify-center`}>
                          <s.icon className="w-5 h-5" />
                        </div>
                      </div>
                      <p className="text-2xl font-heading font-bold">{s.value}</p>
                      <p className="text-xs text-muted-foreground mt-1">{s.title}</p>
                      {partnerError && s.value === 0 && (
                        <p className="text-[11px] text-muted-foreground mt-1 opacity-70">Live data unavailable</p>
                      )}
                    </Card>
                  </motion.div>
                ))
              )}
            </div>

            {partnerError ? (
              <Card className="rounded-xl border-destructive/40 bg-destructive/5">
                <CardContent className="p-4 flex items-center gap-3">
                  <ShieldAlert className="w-5 h-5 text-destructive shrink-0" />
                  <div>
                    <p className="text-sm font-medium text-destructive">
                      Could not load partner sync monitor
                    </p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      Backend may be unreachable or permissions insufficient.
                    </p>
                  </div>
                </CardContent>
              </Card>
            ) : partnerLoading && !partnerData ? (
              <TableSkeleton rows={4} cols={5} />
            ) : partnerTokens.length === 0 ? (
              <div className="py-12 text-center rounded-xl border border-dashed border-muted">
                <Repeat className="w-10 h-10 mx-auto text-muted-foreground/40 mb-3" />
                <p className="text-sm text-muted-foreground">No partner sync tokens yet.</p>
              </div>
            ) : (
              <div className="overflow-x-auto rounded-xl border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="pl-4">Sync ID</TableHead>
                      <TableHead>Profile ID</TableHead>
                      <TableHead>Created At</TableHead>
                      <TableHead>Expires At</TableHead>
                      <TableHead className="pr-4">Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {partnerTokens.map((t) => {
                      const statusClass = partnerStatusStyles[t.status] || 'bg-muted text-muted-foreground';
                      return (
                        <TableRow key={t.sync_id || t.token || t.id}>
                          <TableCell className="pl-4">
                            <span className="font-mono text-xs">{shortId(t.sync_id || t.token)}</span>
                          </TableCell>
                          <TableCell>
                            <span className="font-mono text-xs">{shortId(t.profile_id)}</span>
                          </TableCell>
                          <TableCell className="text-xs text-muted-foreground whitespace-nowrap">
                            {formatDate(t.created_at)}
                          </TableCell>
                          <TableCell className="text-xs text-muted-foreground whitespace-nowrap">
                            {formatDate(t.expires_at)}
                          </TableCell>
                          <TableCell className="pr-4">
                            <Badge variant="outline" className={`${statusClass} capitalize text-xs`}>
                              {String(t.status || 'unknown').replace(/_/g, ' ')}
                            </Badge>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
