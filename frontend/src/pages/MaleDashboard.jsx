import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Users, Shield, Heart, BookOpen, CheckCircle, XCircle, ArrowRight, Link2 } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

const educationCards = [
  { title: 'Condom Guidance', desc: 'Proper use increases effectiveness from 85% to 98%. Learn the correct steps.', color: 'bg-primary/10 text-primary' },
  { title: 'Fertility Window', desc: 'Understanding your partner\'s fertile window helps with shared planning.', color: 'bg-secondary/10 text-secondary' },
  { title: 'Male Clinical Trials', desc: 'New male contraceptive methods are in development. Stay informed.', color: 'bg-accent/10 text-accent' },
  { title: 'Shared Responsibility', desc: 'Contraception is a shared decision. Open communication builds trust.', color: 'bg-primary/10 text-primary' },
];

const vasectomyMyths = [
  { myth: 'Vasectomy affects masculinity or performance', fact: 'Vasectomy only blocks sperm transport. It does not affect hormone levels, libido, or sexual performance.' },
  { myth: 'Vasectomy is permanent and cannot be reversed', fact: 'Vasectomy reversal is possible, though success rates vary. It\'s best considered a permanent decision with reversal as a possibility.' },
  { myth: 'Vasectomy is painful and requires long recovery', fact: 'Modern no-scalpel vasectomy is minimally invasive. Most men return to normal activities within a few days.' },
];

export default function MaleDashboard() {
  const [partnerToken, setPartnerToken] = useState('');
  const [connected, setConnected] = useState(false);
  const { toast } = useToast();

  const connectPartner = () => {
    if (partnerToken.length >= 6) {
      setConnected(true);
      toast({ title: 'Connected!', description: 'Partner sync established.' });
    }
  };

  return (
    <div className="min-h-[85vh] py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <Badge className="mb-3 bg-primary/10 text-primary border-primary/20">Bro-Talk</Badge>
          <h1 className="font-heading text-3xl font-bold">Male Health Hub</h1>
          <p className="text-muted-foreground mt-2">Your space for contraceptive education and partner support.</p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {educationCards.map((c, i) => (
            <motion.div
              key={c.title}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.08 }}
            >
              <Card className="p-5 rounded-2xl h-full hover:shadow-md transition-shadow">
                <div className={`w-10 h-10 rounded-xl ${c.color} flex items-center justify-center mb-3`}>
                  {i === 0 ? <Shield className="w-5 h-5" /> : i === 1 ? <Heart className="w-5 h-5" /> : i === 2 ? <BookOpen className="w-5 h-5" /> : <Users className="w-5 h-5" />}
                </div>
                <h3 className="font-heading font-semibold mb-1">{c.title}</h3>
                <p className="text-sm text-muted-foreground">{c.desc}</p>
              </Card>
            </motion.div>
          ))}
        </div>

        <Card className="p-6 rounded-2xl mb-8">
          <h3 className="font-heading font-semibold text-lg mb-4 flex items-center gap-2">
            <Link2 className="w-5 h-5 text-accent" /> Partner Sync
          </h3>
          {!connected ? (
            <div className="flex gap-3">
              <Input
                placeholder="Enter partner's sync token"
                value={partnerToken}
                onChange={e => setPartnerToken(e.target.value)}
                className="flex-1"
              />
              <Button onClick={connectPartner} className="rounded-full">Connect</Button>
            </div>
          ) : (
            <div className="flex items-center gap-3 bg-secondary/10 rounded-xl p-4">
              <CheckCircle className="w-5 h-5 text-secondary" />
              <div>
                <p className="font-medium text-sm text-secondary">Partner Connected</p>
                <p className="text-xs text-muted-foreground">Shared health decisions are now accessible.</p>
              </div>
            </div>
          )}
        </Card>

        <Card className="p-6 rounded-2xl">
          <h3 className="font-heading font-semibold text-lg mb-4">Vasectomy: Myths vs Facts</h3>
          <Accordion type="single" collapsible className="space-y-2">
            {vasectomyMyths.map((vm, i) => (
              <AccordionItem key={i} value={`vm-${i}`} className="bg-muted/30 rounded-xl border px-4">
                <AccordionTrigger className="py-3 hover:no-underline text-left">
                  <div className="flex items-center gap-2 text-sm">
                    <XCircle className="w-4 h-4 text-destructive flex-shrink-0" />
                    <span className="font-medium">{vm.myth}</span>
                  </div>
                </AccordionTrigger>
                <AccordionContent className="pb-3">
                  <div className="flex items-start gap-2 ml-6 text-sm">
                    <CheckCircle className="w-4 h-4 text-secondary flex-shrink-0 mt-0.5" />
                    <p className="text-muted-foreground">{vm.fact}</p>
                  </div>
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </Card>
      </div>
    </div>
  );
}