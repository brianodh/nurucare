import React, { useEffect, useState, useCallback } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { Button } from '@/components/ui/button';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';
import {
  BookOpen,
  RefreshCw,
  Info,
  AlertTriangle,
  CheckCircle2,
  Loader2,
} from 'lucide-react';
import { getWHOMECRules } from '@/api/apiClient';

const categoryStyles = {
  1: 'bg-green-500/15 text-green-700 border-green-500/30',
  2: 'bg-blue-500/15 text-blue-700 border-blue-500/30',
  3: 'bg-amber-500/15 text-amber-700 border-amber-500/30',
  4: 'bg-rose-500/15 text-rose-700 border-rose-500/30',
};

const categoryLabels = {
  1: 'Category 1 — No restrictions',
  2: 'Category 2 — Advantages outweigh risks',
  3: 'Category 3 — Risks may outweigh advantages',
  4: 'Category 4 — Unacceptable risk',
};

export default function WHORulesConsole() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchRules = useCallback(() => {
    setLoading(true);
    setError(null);
    getWHOMECRules()
      .then((res) => {
        setData(res);
      })
      .catch((err) => {
        setError(err?.message || 'Failed to fetch WHO MEC rules');
        setData(null);
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    fetchRules();
  }, [fetchRules]);

  const rules = data?.rules?.rules || [];
  const rulesMeta = data?.rules || {};
  const methodMapping = data?.rules?.method_mapping || {};
  const guardrail = data?.guardrail || null;

  const rulesCount = rules.length;
  const methodCount = Object.keys(methodMapping).length;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <BookOpen className="w-6 h-6 text-primary" />
            <h1 className="font-heading text-2xl font-bold">
              WHO MEC Rules Engine — Read-Only View
            </h1>
          </div>
          <p className="text-muted-foreground text-sm mt-1 max-w-2xl">
            This console displays the exact ruleset that drives contraceptive
            eligibility decisions. Every rule shown here is applied in real time
            during patient intake and recommendation generation. No edits are
            possible from this view.
          </p>
        </div>
        <Button
          variant="outline"
          onClick={fetchRules}
          disabled={loading}
          className="shrink-0"
        >
          <RefreshCw
            className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`}
          />
          Refresh
        </Button>
      </div>

      {error && (
        <Card className="border-rose-200 bg-rose-50/50">
          <CardHeader>
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-rose-600" />
              <CardTitle className="text-rose-800 text-lg">
                WHO MEC rules not available.
              </CardTitle>
            </div>
            <CardDescription className="text-rose-700/80">
              The rules engine data could not be loaded. The backend may be
              unreachable or the admin endpoint returned an error.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <details className="text-sm text-rose-800">
              <summary className="cursor-pointer font-medium underline-offset-2 hover:underline">
                Show error details
              </summary>
              <pre className="mt-2 p-3 bg-rose-100/60 rounded-md overflow-x-auto text-xs whitespace-pre-wrap font-mono">
                {String(error)}
              </pre>
            </details>
          </CardContent>
        </Card>
      )}

      {!error && (
        <>
          <Tabs defaultValue="summary" className="space-y-6">
            <TabsList>
              <TabsTrigger value="summary">Summary</TabsTrigger>
              <TabsTrigger value="rules">
                Rules{' '}
                {!loading && rulesCount > 0 && (
                  <span className="ml-1.5 text-xs text-muted-foreground">
                    ({rulesCount})
                  </span>
                )}
              </TabsTrigger>
              <TabsTrigger value="methods">
                Method Mapping{' '}
                {!loading && methodCount > 0 && (
                  <span className="ml-1.5 text-xs text-muted-foreground">
                    ({methodCount})
                  </span>
                )}
              </TabsTrigger>
              <TabsTrigger value="guardrail">Guardrail</TabsTrigger>
            </TabsList>

            <TabsContent value="summary" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Ruleset Summary</CardTitle>
                  <CardDescription>
                    Overview of the loaded WHO MEC rules engine configuration.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <div className="flex items-center gap-2 text-muted-foreground text-sm py-4">
                      <Loader2 className="w-4 h-4 animate-spin" /> Loading
                      ruleset…
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                      <div className="p-4 rounded-lg border bg-muted/30">
                        <div className="flex items-center gap-2 text-muted-foreground text-xs mb-1">
                          <Info className="w-3.5 h-3.5" />
                          Source
                        </div>
                        <p className="font-semibold">
                          {rulesMeta.source || 'WHO MEC 5th ed 2024'}
                        </p>
                      </div>
                      <div className="p-4 rounded-lg border bg-muted/30">
                        <div className="text-xs text-muted-foreground mb-1">
                          Version
                        </div>
                        <p className="font-semibold font-mono">
                          {rulesMeta.version || '—'}
                        </p>
                      </div>
                      <div className="p-4 rounded-lg border bg-muted/30">
                        <div className="text-xs text-muted-foreground mb-1">
                          Rules Count
                        </div>
                        <p className="font-semibold text-2xl">{rulesCount}</p>
                      </div>
                      <div className="p-4 rounded-lg border bg-muted/30">
                        <div className="text-xs text-muted-foreground mb-1">
                          Methods Mapped
                        </div>
                        <p className="font-semibold text-2xl">{methodCount}</p>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Guardrail Status</CardTitle>
                  <CardDescription>
                    Runtime integrity check on the WHOMECGuardrail evaluation
                    layer.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <div className="flex items-center gap-2 text-muted-foreground text-sm py-4">
                      <Loader2 className="w-4 h-4 animate-spin" /> Checking
                      guardrail…
                    </div>
                  ) : guardrail ? (
                    <div className="space-y-3">
                      <div className="flex flex-wrap gap-3">
                        {guardrail.file_size_bytes != null && (
                          <Badge variant="outline" className="text-xs py-1">
                            File size:{' '}
                            {(guardrail.file_size_bytes / 1024).toFixed(1)} KB
                          </Badge>
                        )}
                        <Badge
                          variant="outline"
                          className={`text-xs py-1 ${
                            guardrail.has_guardrail_class
                              ? 'border-green-500/30 text-green-700 bg-green-50'
                              : 'border-rose-500/30 text-rose-700 bg-rose-50'
                          }`}
                        >
                          {guardrail.has_guardrail_class ? (
                            <span className="flex items-center gap-1">
                              <CheckCircle2 className="w-3 h-3" />
                              WHOMECGuardrail class present
                            </span>
                          ) : (
                            <span className="flex items-center gap-1">
                              <AlertTriangle className="w-3 h-3" />
                              WHOMECGuardrail class MISSING
                            </span>
                          )}
                        </Badge>
                        <Badge
                          variant="outline"
                          className={`text-xs py-1 ${
                            guardrail.has_evaluate_method
                              ? 'border-green-500/30 text-green-700 bg-green-50'
                              : 'border-rose-500/30 text-rose-700 bg-rose-50'
                          }`}
                        >
                          {guardrail.has_evaluate_method ? (
                            <span className="flex items-center gap-1">
                              <CheckCircle2 className="w-3 h-3" />
                              evaluate() method present
                            </span>
                          ) : (
                            <span className="flex items-center gap-1">
                              <AlertTriangle className="w-3 h-3" />
                              evaluate() method MISSING
                            </span>
                          )}
                        </Badge>
                      </div>
                      {guardrail.summary && (
                        <p className="text-sm text-muted-foreground mt-2">
                          {guardrail.summary}
                        </p>
                      )}
                    </div>
                  ) : (
                    <div className="flex items-center gap-2 text-muted-foreground text-sm py-2">
                      <AlertTriangle className="w-4 h-4 text-amber-500" />
                      No guardrail metadata available.
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Category Legend</CardTitle>
                  <CardDescription>
                    WHO Medical Eligibility Criteria risk categories.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {[1, 2, 3, 4].map((cat) => (
                      <div
                        key={cat}
                        className="flex items-start gap-3 p-3 rounded-lg border"
                      >
                        <Badge
                          variant="outline"
                          className={`shrink-0 ${categoryStyles[cat]}`}
                        >
                          Cat {cat}
                        </Badge>
                        <p className="text-sm text-foreground pt-0.5">
                          {categoryLabels[cat]}
                        </p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="rules" className="space-y-4">
              {loading ? (
                <div className="flex items-center gap-2 text-muted-foreground text-sm py-8 justify-center">
                  <Loader2 className="w-4 h-4 animate-spin" /> Loading rules…
                </div>
              ) : rulesCount === 0 ? (
                <Card>
                  <CardContent className="py-8 text-center text-muted-foreground">
                    No rules loaded.
                  </CardContent>
                </Card>
              ) : (
                rules.map((rule, idx) => {
                  const cat = Number(rule.category) || 0;
                  const catStyle =
                    categoryStyles[cat] ||
                    'bg-muted text-muted-foreground border-muted';
                  const restricted = rule.restricted_methods || [];
                  return (
                    <Card key={rule.id || idx} className="overflow-hidden">
                      <CardHeader className="pb-4">
                        <div className="flex flex-wrap items-start justify-between gap-3">
                          <div className="flex items-center gap-3">
                            <Badge variant="outline" className="font-mono text-xs">
                              {rule.id || `#${idx + 1}`}
                            </Badge>
                            <Badge
                              variant="outline"
                              className={`${catStyle}`}
                            >
                              Category {cat}
                            </Badge>
                          </div>
                          {restricted.length > 0 && (
                            <div className="flex flex-wrap gap-1.5 justify-end">
                              {restricted.map((m) => (
                                <Badge
                                  key={m}
                                  variant="secondary"
                                  className="text-xs"
                                >
                                  {methodMapping[m] || m}
                                </Badge>
                              ))}
                            </div>
                          )}
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div>
                          <div className="text-xs uppercase tracking-wide text-muted-foreground mb-1.5">
                            Condition
                          </div>
                          <pre className="p-3 bg-muted/40 rounded-md text-xs font-mono whitespace-pre-wrap overflow-x-auto text-foreground border">
{rule.condition != null ? String(rule.condition) : '—'}
                          </pre>
                        </div>
                        {rule.explanation && (
                          <div>
                            <div className="text-xs uppercase tracking-wide text-muted-foreground mb-1.5">
                              Explanation
                            </div>
                            <p className="text-sm leading-relaxed text-foreground">
                              {rule.explanation}
                            </p>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  );
                })
              )}
            </TabsContent>

            <TabsContent value="methods">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Method Mapping</CardTitle>
                  <CardDescription>
                    Internal method keys resolved to their display names. Expand
                    any item to inspect details.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <div className="flex items-center gap-2 text-muted-foreground text-sm py-4">
                      <Loader2 className="w-4 h-4 animate-spin" /> Loading
                      method mapping…
                    </div>
                  ) : methodCount === 0 ? (
                    <div className="text-muted-foreground text-sm py-4">
                      No method mapping data available.
                    </div>
                  ) : (
                    <Accordion type="single" collapsible className="w-full">
                      {Object.entries(methodMapping).map(([key, value]) => (
                        <AccordionItem key={key} value={key}>
                          <AccordionTrigger>
                            <span className="flex items-center gap-3 text-left">
                              <Badge
                                variant="outline"
                                className="font-mono text-xs shrink-0"
                              >
                                {key}
                              </Badge>
                              <span className="font-medium">
                                {typeof value === 'string'
                                  ? value
                                  : value?.display_name ||
                                    value?.name ||
                                    JSON.stringify(value)}
                              </span>
                            </span>
                          </AccordionTrigger>
                          <AccordionContent>
                            {typeof value === 'string' ? (
                              <div className="text-sm text-muted-foreground space-y-1">
                                <div>
                                  <span className="text-xs uppercase tracking-wide mr-2">
                                    Key:
                                  </span>
                                  <code className="font-mono">{key}</code>
                                </div>
                                <div>
                                  <span className="text-xs uppercase tracking-wide mr-2">
                                    Display:
                                  </span>
                                  <span>{value}</span>
                                </div>
                              </div>
                            ) : (
                              <pre className="p-3 bg-muted/40 rounded-md text-xs font-mono whitespace-pre-wrap overflow-x-auto border">
{JSON.stringify(value, null, 2)}
                              </pre>
                            )}
                          </AccordionContent>
                        </AccordionItem>
                      ))}
                    </Accordion>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="guardrail">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Guardrail Integrity</CardTitle>
                  <CardDescription>
                    Detailed guardrail metadata as reported by the backend
                    rules engine.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <div className="flex items-center gap-2 text-muted-foreground text-sm py-4">
                      <Loader2 className="w-4 h-4 animate-spin" /> Loading
                      guardrail info…
                    </div>
                  ) : guardrail ? (
                    <div className="space-y-5">
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                        <div className="p-4 rounded-lg border bg-muted/30">
                          <div className="text-xs text-muted-foreground mb-1">
                            File size
                          </div>
                          <p className="font-semibold">
                            {guardrail.file_size_bytes != null
                              ? `${(guardrail.file_size_bytes / 1024).toFixed(2)} KB`
                              : '—'}
                          </p>
                        </div>
                        <div className="p-4 rounded-lg border bg-muted/30">
                          <div className="text-xs text-muted-foreground mb-1">
                            WHOMECGuardrail class
                          </div>
                          <p className="font-semibold flex items-center gap-1.5">
                            {guardrail.has_guardrail_class ? (
                              <>
                                <CheckCircle2 className="w-4 h-4 text-green-600" />
                                Present
                              </>
                            ) : (
                              <>
                                <AlertTriangle className="w-4 h-4 text-rose-600" />
                                Missing
                              </>
                            )}
                          </p>
                        </div>
                        <div className="p-4 rounded-lg border bg-muted/30">
                          <div className="text-xs text-muted-foreground mb-1">
                            evaluate() method
                          </div>
                          <p className="font-semibold flex items-center gap-1.5">
                            {guardrail.has_evaluate_method ? (
                              <>
                                <CheckCircle2 className="w-4 h-4 text-green-600" />
                                Present
                              </>
                            ) : (
                              <>
                                <AlertTriangle className="w-4 h-4 text-rose-600" />
                                Missing
                              </>
                            )}
                          </p>
                        </div>
                      </div>

                      <div>
                        <div className="text-xs uppercase tracking-wide text-muted-foreground mb-2">
                          Full guardrail payload
                        </div>
                        <pre className="p-4 bg-muted/40 rounded-md text-xs font-mono whitespace-pre-wrap overflow-x-auto border max-h-96 overflow-y-auto">
{JSON.stringify(guardrail, null, 2)}
                        </pre>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2 text-muted-foreground text-sm py-4">
                      <AlertTriangle className="w-4 h-4 text-amber-500" />
                      Guardrail data not available. The backend may not be
                      exposing guardrail metadata.
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </>
      )}
    </div>
  );
}
