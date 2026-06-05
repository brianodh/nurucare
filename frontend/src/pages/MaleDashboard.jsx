import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Users, Shield, Heart, BookOpen, CheckCircle, XCircle, Link2, Loader2 } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
import { useLang } from '@/lib/i18n';
import { verifySyncToken } from '@/api/apiClient';

const vasectomyMyths = [
  { myth: 'Vasectomy affects masculinity or performance', fact: 'Vasectomy only blocks sperm transport. It does not affect hormone levels, libido, or sexual performance.' },
  { myth: 'Vasectomy is permanent and cannot be reversed', fact: "Vasectomy reversal is possible, though success rates vary. It's best considered a permanent decision with reversal as a possibility." },
  { myth: 'Vasectomy is painful and requires long recovery', fact: 'Modern no-scalpel vasectomy is minimally invasive. Most men return to normal activities within a few days.' },
];

function getAnonymousId() {
  let id = sessionStorage.getItem('nuru_anon_id');
  if (!id) {
    id = 'anon_' + Math.random().toString(36).slice(2, 10);
    sessionStorage.setItem('nuru_anon_id', id);
  }
  return id;
}

export default function MaleDashboard() {
  const { t } = useLang();
  const { toast } = useToast();
  const [partnerToken, setPartnerToken] = useState('');
  const [connected, setConnected] = useState(false);
  const [connecting, setConnecting] = useState(false);

  const educationCards = [
    { titleKey: 'male_card1_title', descKey: 'male_card1_desc', color: 'bg-primary/10 text-primary', Icon: Shield },
    { titleKey: 'male_card2_title', descKey: 'male_card2_desc', color: 'bg-secondary/10 text-secondary', Icon: Heart },
    { titleKey: 'male_card3_title', descKey: 'male_card3_desc', color: 'bg-accent/10 text-accent', Icon: BookOpen },
    { titleKey: 'male_card4_title', descKey: 'male_card4_desc', color: 'bg-primary/10 text-primary', Icon: Users },
  ];

  const connectPartner = async () => {
    if (partnerToken.trim().length < 6) return;
    setConnecting(true);
    try {
      const response = await verifySyncToken(partnerToken.trim(), getAnonymousId());
      if (response.success) {
        setConnected(true);
        toast({ title: t('male_connected'), description: t('male_connected_sub') });
      } else {
        toast({
          title: 'Connection failed',
          description: response.message || 'Invalid or expired token. Ask your partner to generate a new one.',
          variant: 'destructive',
        });
      }
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Could not connect. Please check the token and try again.';
      toast({ title: 'Connection failed', description: msg, variant: 'destructive' });
    } finally {
      setConnecting(false);
    }
  };

  return (
    <div className="min-h-[85vh] py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <Badge className="mb-3 bg-primary/10 text-primary border-primary/20">{t('male_badge')}</Badge>
          <h1 className="font-heading text-3xl font-bold">{t('male_title')}</h1>
          <p className="text-muted-foreground mt-2">{t('male_sub')}</p>
        </motion.div>

        <div className="grid sm:grid-cols-2 gap-5 mb-8">
          {educationCards.map((c, i) => (
            <motion.div key={c.titleKey} initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}>
              <Card className="p-5 rounded-2xl h-full hover:shadow-md transition-shadow">
                <div className={`w-10 h-10 rounded-xl ${c.color} flex items-center justify-center mb-3`}>
                  <c.Icon className="w-5 h-5" />
                </div>
                <h3 className="font-heading font-semibold mb-1">{t(c.titleKey)}</h3>
                <p className="text-sm text-muted-foreground">{t(c.descKey)}</p>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Partner Sync */}
        <Card className="p-6 rounded-2xl mb-8">
          <h3 className="font-heading font-semibold text-lg mb-4 flex items-center gap-2">
            <Link2 className="w-5 h-5 text-accent" /> {t('male_partner_title')}
          </h3>

          {!connected ? (
            <div className="space-y-3">
              <p className="text-sm text-muted-foreground">
                Ask your partner to open <strong>Partner Sync</strong> and share their token with you.
              </p>
              <div className="flex flex-col sm:flex-row gap-3">
                <Input
                  placeholder="Enter partner's sync token"
                  value={partnerToken}
                  onChange={(e) => setPartnerToken(e.target.value)}
                  className="flex-1 font-mono"
                  onKeyDown={(e) => e.key === 'Enter' && connectPartner()}
                />
                <Button
                  onClick={connectPartner}
                  disabled={connecting || partnerToken.trim().length < 6}
                  className="rounded-full sm:w-auto w-full gap-2"
                >
                  {connecting && <Loader2 className="w-4 h-4 animate-spin" />}
                  {connecting ? 'Connectingâ€¦' : 'Connect'}
                </Button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center gap-3 bg-secondary/10 rounded-xl p-4">
                <CheckCircle className="w-5 h-5 text-secondary flex-shrink-0" />
                <div>
                  <p className="font-medium text-sm text-secondary">{t('male_connected')}</p>
                  <p className="text-xs text-muted-foreground">{t('male_connected_sub')}</p>
                </div>
              </div>
              <div className="bg-muted/50 rounded-xl p-4 text-sm text-muted-foreground">
                <p className="font-medium text-foreground mb-1">View Partner's Health Summary</p>
                <p>Ask your partner to generate a <strong>Session Key</strong> from their assessment results, then enter it to view their summary.</p>
                <Button
                  variant="outline"
                  size="sm"
                  className="mt-3 rounded-full"
                  onClick={() => window.location.href = '/nurse/lookup'}
                >
                  Enter Session Key
                </Button>
              </div>
            </div>
          )}
        </Card>

        {/* Vasectomy myths */}
        <Card className="p-6 rounded-2xl">
          <h3 className="font-heading font-semibold text-lg mb-4">{t('male_myths_title')}</h3>
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
