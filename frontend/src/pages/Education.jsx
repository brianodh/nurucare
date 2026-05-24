import React from 'react';
import { motion } from 'framer-motion';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Badge } from '@/components/ui/badge';
import { BookOpen, Clock, CheckCircle, XCircle } from 'lucide-react';
import { mockMythsFacts, sideEffectTimeline } from '@/lib/mockData';

export default function Education() {
  return (
    <div className="min-h-[85vh] py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center gap-2 mb-2">
            <BookOpen className="w-5 h-5 text-primary" />
            <p className="text-sm font-medium text-primary">Educational Resources</p>
          </div>
          <h1 className="font-heading text-3xl font-bold">Learn the Facts</h1>
          <p className="text-muted-foreground mt-2">Evidence-based education to support your reproductive health decisions.</p>
        </motion.div>

        <Tabs defaultValue="myths" className="space-y-6">
          <TabsList className="w-full sm:w-auto">
            <TabsTrigger value="myths">Myths vs Facts</TabsTrigger>
            <TabsTrigger value="timeline">Side Effect Timeline</TabsTrigger>
          </TabsList>

          <TabsContent value="myths">
            <Accordion type="single" collapsible className="space-y-3">
              {mockMythsFacts.map((mf, i) => (
                <AccordionItem key={i} value={`myth-${i}`} className="bg-card rounded-2xl border px-5">
                  <AccordionTrigger className="py-4 hover:no-underline">
                    <div className="flex items-start gap-3 text-left">
                      <XCircle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="font-medium text-sm">Myth: "{mf.myth}"</p>
                      </div>
                    </div>
                  </AccordionTrigger>
                  <AccordionContent className="pb-4">
                    <div className="ml-8 space-y-3">
                      <div className="flex items-start gap-2">
                        <CheckCircle className="w-4 h-4 text-secondary flex-shrink-0 mt-0.5" />
                        <p className="text-sm text-foreground leading-relaxed"><strong>Fact:</strong> {mf.fact}</p>
                      </div>
                      <Badge variant="secondary" className="text-xs">{mf.source}</Badge>
                    </div>
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          </TabsContent>

          <TabsContent value="timeline">
            <div className="space-y-6">
              {sideEffectTimeline.map((phase, i) => (
                <motion.div
                  key={phase.period}
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="bg-card rounded-2xl border p-6"
                >
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                      <Clock className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                      <p className="font-heading font-semibold">{phase.title}</p>
                      <p className="text-sm text-muted-foreground">{phase.period}</p>
                    </div>
                  </div>
                  <ul className="space-y-2 mb-4">
                    {phase.items.map((item, j) => (
                      <li key={j} className="flex items-start gap-2 text-sm">
                        <div className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5 flex-shrink-0" />
                        {item}
                      </li>
                    ))}
                  </ul>
                  <div className="bg-secondary/10 rounded-xl p-3">
                    <p className="text-sm text-secondary font-medium">💡 {phase.guidance}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}