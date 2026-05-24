import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Users, Copy, Clock, CheckCircle, Link2 } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

export default function PartnerSync() {
  const [token, setToken] = useState('');
  const [generated, setGenerated] = useState(false);
  const [partnerToken, setPartnerToken] = useState('');
  const [connected, setConnected] = useState(false);
  const [timeLeft, setTimeLeft] = useState(0);
  const [copied, setCopied] = useState(false);
  const { toast } = useToast();

  const generateToken = () => {
    const t = 'SC-' + Math.random().toString(36).substring(2, 8).toUpperCase();
    setToken(t);
    setGenerated(true);
    setTimeLeft(1800);
  };

  useEffect(() => {
    if (!generated || timeLeft <= 0) return;
    const timer = setInterval(() => setTimeLeft(t => t - 1), 1000);
    return () => clearInterval(timer);
  }, [generated, timeLeft]);

  const copyToken = () => {
    navigator.clipboard.writeText(token);
    setCopied(true);
    toast({ title: 'Token copied!', description: 'Share this with your partner.' });
    setTimeout(() => setCopied(false), 2000);
  };

  const connectPartner = () => {
    if (partnerToken.length >= 6) {
      setConnected(true);
      toast({ title: 'Partner connected!', description: 'You can now share health decisions together.' });
    }
  };

  const minutes = Math.floor(timeLeft / 60);
  const seconds = timeLeft % 60;

  return (
    <div className="min-h-[85vh] py-12">
      <div className="max-w-lg mx-auto px-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-accent/10 flex items-center justify-center mx-auto mb-4">
            <Users className="w-7 h-7 text-accent" />
          </div>
          <h1 className="font-heading font-bold text-2xl">Partner Sync</h1>
          <p className="text-muted-foreground text-sm mt-2">Securely share health decisions with your partner.</p>
        </motion.div>

        <div className="space-y-6">
          <Card className="p-6 rounded-2xl">
            <h3 className="font-heading font-semibold mb-4">Generate Sync Token</h3>
            {!generated ? (
              <Button onClick={generateToken} className="w-full rounded-full">Generate Anonymous Token</Button>
            ) : (
              <div className="space-y-4">
                <div className="bg-muted rounded-xl p-4 text-center">
                  <p className="text-2xl font-heading font-bold tracking-wider">{token}</p>
                </div>
                <div className="flex items-center justify-center gap-2 text-muted-foreground text-sm">
                  <Clock className="w-4 h-4" />
                  <span className={`font-mono ${timeLeft < 300 ? 'text-destructive' : ''}`}>
                    {minutes}:{seconds.toString().padStart(2, '0')}
                  </span>
                </div>
                <Button onClick={copyToken} variant="outline" className="w-full rounded-full gap-2">
                  {copied ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  {copied ? 'Copied!' : 'Copy Token'}
                </Button>
              </div>
            )}
          </Card>

          <Card className="p-6 rounded-2xl">
            <h3 className="font-heading font-semibold mb-4">Connect with Partner</h3>
            {!connected ? (
              <div className="space-y-3">
                <Input
                  placeholder="Enter partner's sync token"
                  value={partnerToken}
                  onChange={e => setPartnerToken(e.target.value)}
                />
                <Button onClick={connectPartner} variant="secondary" className="w-full rounded-full gap-2">
                  <Link2 className="w-4 h-4" /> Connect
                </Button>
              </div>
            ) : (
              <div className="text-center py-4">
                <div className="w-12 h-12 rounded-full bg-secondary/10 flex items-center justify-center mx-auto mb-3">
                  <CheckCircle className="w-6 h-6 text-secondary" />
                </div>
                <p className="font-heading font-semibold text-secondary">Partner Connected!</p>
                <p className="text-sm text-muted-foreground mt-1">You can now view shared health decisions together.</p>
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}