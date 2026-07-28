import React, { useEffect, useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { Collapsible, CollapsibleTrigger, CollapsibleContent } from '@/components/ui/collapsible';
import {
  Database,
  BrainCircuit,
  Cpu,
  Server,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  Info,
  ShieldCheck,
  ShieldAlert,
  ChevronDown,
} from 'lucide-react';
import { getAdminSystemHealth } from '@/api/apiClient';

function formatTimestamp(iso) {
  if (!iso) return '—';
  try {
    const d = new Date(iso);
    return d.toLocaleString();
  } catch {
    return iso;
  }
}

function SkeletonCards() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      {[0, 1, 2, 3, 4].map((i) => (
        <Card key={i} className="rounded-2xl">
          <CardHeader className="pb-3">
            <Skeleton className="h-5 w-40" />
            <Skeleton className="h-3 w-56 mt-2" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-10 w-full" />
            <div className="mt-3 space-y-2">
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-4 w-1/2" />
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

export default function SystemHealth() {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [dbErrorOpen, setDbErrorOpen] = useState(false);
  const [lastRefreshed, setLastRefreshed] = useState(null);

  const fetchHealth = useCallback(async () => {
    try {
      setError(false);
      const data = await getAdminSystemHealth();
      setHealth(data);
      setLastRefreshed(new Date().toISOString());
    } catch (e) {
      setError(true);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchHealth();
  }, [fetchHealth]);

  const handleRefresh = () => {
    setRefreshing(true);
    setLoading(true);
    fetchHealth();
  };

  const db = health?.database;
  const gemini = health?.gemini_api;
  const engine = health?.recommendation_engine;
  const entrypoint = health?.entrypoint;
  const timestamp = health?.timestamp;

  const geminiNotConfigured = gemini?.configured === false;
  const enginePath = engine?.active_path;

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-start justify-between flex-wrap gap-4"
      >
        <div>
          <h1 className="font-heading text-2xl font-bold">System Health</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Live backend diagnostics — database, Gemini API, recommendation engine.
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            Last refreshed: {lastRefreshed ? formatTimestamp(lastRefreshed) : 'Loading…'}
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={handleRefresh} disabled={refreshing}>
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </motion.div>

      {error && !loading ? (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
          <Alert variant="destructive" className="rounded-2xl">
            <ShieldAlert className="w-5 h-5" />
            <AlertTitle className="font-bold">Couldn't retrieve system health.</AlertTitle>
            <AlertDescription className="flex items-center gap-3 flex-wrap mt-2">
              <span>The backend may be offline or unreachable.</span>
              <Button variant="destructive" size="sm" onClick={handleRefresh} disabled={refreshing}>
                <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
                Retry
              </Button>
            </AlertDescription>
          </Alert>
        </motion.div>
      ) : null}

      {loading ? (
        <SkeletonCards />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* 1) DATABASE CARD */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 }}
          >
            <Card className="rounded-2xl h-full">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                  <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${db?.ok ? 'bg-emerald-500/10 text-emerald-600' : 'bg-rose-500/10 text-rose-600'}`}>
                    <Database className="w-4.5 h-4.5" />
                  </div>
                  <div className="flex-1">
                    <CardTitle className="text-base">Database</CardTitle>
                    <CardDescription className="text-xs mt-0.5">Backend connectivity & status</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center gap-2">
                  {db?.ok ? (
                    <>
                      <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
                      <span className="font-semibold text-emerald-700 dark:text-emerald-400">Connected</span>
                    </>
                  ) : (
                    <>
                      <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0" />
                      <span className="font-semibold text-rose-700 dark:text-rose-400">Disconnected</span>
                    </>
                  )}
                  <Badge variant="outline" className="ml-auto capitalize text-xs">
                    {db?.backend === 'supabase' ? 'Supabase' : db?.backend === 'local_postgres' ? 'Local Postgres' : 'Unknown'}
                  </Badge>
                </div>

                {db?.error ? (
                  <Collapsible open={dbErrorOpen} onOpenChange={setDbErrorOpen}>
                    <Alert variant="destructive" className="rounded-xl mt-2">
                      <AlertTriangle className="w-4 h-4" />
                      <AlertTitle className="text-sm font-semibold">Connection error</AlertTitle>
                      <CollapsibleContent className="mt-2">
                        <AlertDescription className="font-mono text-xs break-all bg-rose-950/20 dark:bg-rose-950/40 p-2 rounded-md">
                          {db.error}
                        </AlertDescription>
                      </CollapsibleContent>
                      <CollapsibleTrigger asChild>
                        <Button variant="ghost" size="sm" className="mt-2 -ml-2 h-7 text-xs w-full justify-start gap-1 hover:bg-transparent">
                          <ChevronDown className={`w-3 h-3 transition-transform ${dbErrorOpen ? 'rotate-180' : ''}`} />
                          {dbErrorOpen ? 'Hide error details' : 'Show error details'}
                        </Button>
                      </CollapsibleTrigger>
                    </Alert>
                  </Collapsible>
                ) : null}
              </CardContent>
            </Card>
          </motion.div>

          {/* 2) GEMINI API CARD */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card className={`rounded-2xl h-full ${geminiNotConfigured ? 'border-rose-400/60 bg-rose-50/60 dark:bg-rose-950/20' : ''}`}>
              <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                  <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${geminiNotConfigured ? 'bg-rose-500/15 text-rose-600' : 'bg-emerald-500/10 text-emerald-600'}`}>
                    <BrainCircuit className="w-4.5 h-4.5" />
                  </div>
                  <div className="flex-1">
                    <CardTitle className="text-base">Gemini API</CardTitle>
                    <CardDescription className="text-xs mt-0.5">AI provider configuration</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                {geminiNotConfigured ? (
                  <div>
                    <div className="flex items-center gap-2">
                      <ShieldAlert className="w-5 h-5 text-rose-600 shrink-0" />
                      <span className="font-bold text-rose-700 dark:text-rose-400 text-base uppercase tracking-wide">
                        NOT CONFIGURED
                      </span>
                    </div>
                    <Alert variant="destructive" className="mt-3 rounded-xl bg-rose-100/80 dark:bg-rose-950/40 border-rose-400/60">
                      <AlertTriangle className="w-4 h-4" />
                      <AlertTitle className="font-bold text-sm">ai_client.py is in mock mode.</AlertTitle>
                      <AlertDescription className="text-sm mt-1">
                        Recommendations use canned text, not real Gemini. Set a valid <code className="font-mono text-xs bg-rose-950/20 px-1 rounded">GEMINI_API_KEY</code> in backend env.
                      </AlertDescription>
                    </Alert>
                  </div>
                ) : (
                  <>
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
                      <span className="font-semibold text-emerald-700 dark:text-emerald-400">Configured</span>
                      <Badge variant="outline" className={`ml-auto text-xs ${gemini?.key_present ? 'text-emerald-700 border-emerald-500/30 bg-emerald-500/10' : ''}`}>
                        {gemini?.key_present ? 'Key present' : 'No key'}
                      </Badge>
                    </div>
                    {gemini?.redacted_key ? (
                      <div className="rounded-lg border bg-muted/40 px-3 py-2">
                        <p className="text-xs text-muted-foreground mb-1">Redacted key</p>
                        <p className="font-mono text-sm">{gemini.redacted_key}</p>
                      </div>
                    ) : null}
                  </>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* 3) RECOMMENDATION ENGINE CARD */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
          >
            <Card className="rounded-2xl h-full">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                  <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${
                    enginePath === 'connected' ? 'bg-emerald-500/10 text-emerald-600'
                    : enginePath === 'engine_available_but_not_connected' ? 'bg-blue-500/10 text-blue-600'
                    : 'bg-amber-500/10 text-amber-600'
                  }`}>
                    <Cpu className="w-4.5 h-4.5" />
                  </div>
                  <div className="flex-1">
                    <CardTitle className="text-base">Recommendation Engine</CardTitle>
                    <CardDescription className="text-xs mt-0.5">WHO MEC + RAG pipeline status</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                {enginePath === 'hardcoded_fallback' ? (
                  <Alert className="rounded-xl bg-amber-500/10 border-amber-500/30 text-amber-800 dark:text-amber-300">
                    <AlertTriangle className="w-4 h-4" />
                    <AlertTitle className="font-semibold text-sm">Active: Hardcoded fallback</AlertTitle>
                    <AlertDescription className="text-sm mt-1">
                      /recommend endpoint in main.py does NOT use WHO MEC engine/guardrail.py. Eligibility decisions are based on simple if/else blocks.
                    </AlertDescription>
                  </Alert>
                ) : enginePath === 'engine_available_but_not_connected' ? (
                  <Alert className="rounded-xl bg-blue-500/10 border-blue-500/30 text-blue-800 dark:text-blue-300">
                    <Info className="w-4 h-4" />
                    <AlertTitle className="font-semibold text-sm">Active: Engine code loaded, not wired</AlertTitle>
                    <AlertDescription className="text-sm mt-1">
                      Engine code exists (guardrail.py loads) but /recommend endpoint has not been reconnected yet. See file 07 work.
                    </AlertDescription>
                  </Alert>
                ) : enginePath === 'connected' ? (
                  <Alert className="rounded-xl bg-emerald-500/10 border-emerald-500/30 text-emerald-800 dark:text-emerald-300">
                    <ShieldCheck className="w-4 h-4" />
                    <AlertTitle className="font-semibold text-sm">Active: WHO MEC + RAG pipeline</AlertTitle>
                    <AlertDescription className="text-sm mt-1">
                      WHO MEC + RAG pipeline active.
                    </AlertDescription>
                  </Alert>
                ) : (
                  <div className="text-sm text-muted-foreground">Unknown engine state.</div>
                )}

                <div className="flex items-center justify-between pt-1">
                  <span className="text-xs text-muted-foreground">guardrail_loaded</span>
                  <Badge
                    variant="outline"
                    className={engine?.guardrail_loaded ? 'text-emerald-700 border-emerald-500/30 bg-emerald-500/10' : 'text-amber-700 border-amber-500/30 bg-amber-500/10'}
                  >
                    {engine?.guardrail_loaded ? 'True' : 'False'}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* 4) ENTRYPOINT / CONFIRMATION CARD */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card className="rounded-2xl h-full">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                  <div className="w-9 h-9 rounded-lg bg-slate-500/10 text-slate-600 dark:text-slate-400 flex items-center justify-center">
                    <Server className="w-4.5 h-4.5" />
                  </div>
                  <div className="flex-1">
                    <CardTitle className="text-base">Entrypoint</CardTitle>
                    <CardDescription className="text-xs mt-0.5">Backend main & runtime metadata</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center gap-2">
                  <Badge variant="secondary" className="font-mono text-xs">
                    {entrypoint?.backend_main || 'main.py'}
                  </Badge>
                  <span className="text-xs text-muted-foreground">FastAPI entrypoint</span>
                </div>
                {entrypoint?.note ? (
                  <p className="text-sm text-muted-foreground bg-muted/40 rounded-lg px-3 py-2">
                    {entrypoint.note}
                  </p>
                ) : null}

                <div className="flex items-center justify-between pt-1 border-t pt-3">
                  <span className="text-xs text-muted-foreground">Last-checked (backend)</span>
                  <span className="font-mono text-xs">{formatTimestamp(timestamp)}</span>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* 5) EXTRA CARD SLOT — timestamp / summary confirmation */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
            className="lg:col-span-2"
          >
            <Card className="rounded-2xl">
              <CardContent className="p-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    {db?.ok && gemini?.configured && enginePath === 'connected' ? (
                      <>
                        <div className="w-10 h-10 rounded-full bg-emerald-500/15 flex items-center justify-center">
                          <ShieldCheck className="w-5 h-5 text-emerald-600" />
                        </div>
                        <div>
                          <p className="font-semibold text-emerald-700 dark:text-emerald-400">All systems operational</p>
                          <p className="text-xs text-muted-foreground">Database, Gemini API and WHO MEC engine are connected.</p>
                        </div>
                      </>
                    ) : (
                      <>
                        <div className="w-10 h-10 rounded-full bg-amber-500/15 flex items-center justify-center">
                          <ShieldAlert className="w-5 h-5 text-amber-600" />
                        </div>
                        <div>
                          <p className="font-semibold text-amber-800 dark:text-amber-400">Degraded — check red flags above</p>
                          <p className="text-xs text-muted-foreground">
                            {!db?.ok && 'Database unreachable. '}
                            {geminiNotConfigured && 'Gemini API missing — AI in mock mode. '}
                            {enginePath === 'hardcoded_fallback' && 'Engine fallback active — no WHO MEC checks. '}
                            {enginePath === 'engine_available_but_not_connected' && 'Engine loaded but not wired to /recommend. '}
                          </p>
                        </div>
                      </>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-xs">
                      {formatTimestamp(lastRefreshed)}
                    </Badge>
                    <Button variant="outline" size="sm" onClick={handleRefresh} disabled={refreshing}>
                      <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
                      Re-check
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      )}
    </div>
  );
}
