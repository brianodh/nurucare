import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Users, Copy, Clock, CheckCircle, Link2, Loader2 } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
import { generateSyncToken, verifySyncToken } from '@/api/apiClient';
import { getSavedProfileId } from '@/lib/useProgress';

// Simple anonymous user id persisted in sessionStorage
function getAnonymousId() {
  let id = sessionStorage.getItem('nuru_anon_id');
  if (!id) {
    id = 'anon_' + Math.random().toString(36).slice(2, 10);
    sessionStorage.setItem('nuru_anon_id', id);
  }
  return id;
}

export default function PartnerSync() {
  const { toast } = useToast();

  const [token, setToken] = useState('');
  const [generated, setGenerated] = useState(false);
  const [generating, setGenerating] = useState(false);

  const [partnerToken, setPartnerToken] = useState('');
  const [connected, setConnected] = useState(false);
  const [connecting, setConnecting] = useState(false);

  const [timeLeft, setTimeLeft] = useState(0);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!generated || timeLeft <= 0) return;
    const timer = setInterval(() => setTimeLeft((t) => t - 1), 1000);
    return () => clearInterval(timer);
  }, [generated, timeLeft]);

  // ── Generate token ─────────────────────────────────────────────────────────
  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const savedProfileId = getSavedProfileId();
      const response = await generateSyncToken(savedProfileId);
      setToken(response.token);
      setGenerated(true);
      setTimeLeft((response.expires_in_hours ?? 24) * 3600);
    } catch (err) {
      console.error('Token generation failed:', err);
      toast({ title: 'Error', description: 'Could not generate token. Is the backend running?', variant: 'destructive' });
    } finally {
      setGenerating(false);
    }
  };

  // ── Copy token ─────────────────────────────────────────────────────────────
  const copyToken = () => {
    navigator.clipboard.writeText(token).catch(() => {});
    setCopied(true);
    toast({ title: 'Token copied!', description: 'Share this with your partner.' });
    setTimeout(() => setCopied(false), 2000);
  };

  // ── Verify / connect ───────────────────────────────────────────────────────
  const connectPartner = async () => {
    const trimmedToken = partnerToken.trim();
    if (trimmedToken.length < 6) return;
    setConnecting(true);
    try {
      const response = await verifySyncToken(trimmedToken, getAnonymousId());
      if (response.success) {
        setConnected(true);
        toast({ title: 'Partner connected!', description: 'You can now share health decisions together.' });
      } else {
        toast({ title: 'Invalid token', description: response.message || 'Please check the token and try again.', variant: 'destructive' });
      }
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Token invalid or expired.';
      toast({ title: 'Connection failed', description: msg, variant: 'destructive' });
    } finally {
      setConnecting(false);
    }
  };

  const hours = Math.floor(timeLeft / 3600);
  const minutes = Math.floor((timeLeft % 3600) / 60);
  const seconds = timeLeft % 60;
  const timerDisplay = hours > 0
    ? `${hours}h ${minutes}m`
    : `${minutes}:${seconds.toString().padStart(2, '0')}`;

  return (
    <div className="min-h-[85vh] py-12">
      <div className="max-w-lg mx-auto px-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-accent/10 flex items-center justify-center mx-auto mb-4">
            <Users className="w-7 h-7 text-accent" />
          </div>
          <h1 className="font-heading font-bold text-2xl">Partner Sync</h1>
          <p className="text-muted-foreground text-sm mt-2">Share health decisions securely with your partner using a sync token.</p>
        </motion.div>

        <div className="space-y-6">
          {/* Generate token */}
          <Card className="p-6 rounded-2xl">
            <h3 className="font-heading font-semibold mb-4">Generate Partner Sync Token</h3>
            {!generated ? (
              <Button onClick={handleGenerate} disabled={generating} className="w-full rounded-full gap-2">
                {generating && <Loader2 className="w-4 h-4 animate-spin" />}
                {generating ? 'Generating…' : 'Generate Sync Token'}
              </Button>
            ) : (
              <div className="space-y-4">
                <div className="bg-muted rounded-xl p-4 text-center overflow-x-auto">
                  <p className="text-lg sm:text-xl font-heading font-bold tracking-wider break-all">{token}</p>
                </div>
                <p className="text-sm text-muted-foreground text-center">
                  This token expires in {timerDisplay}. Share it with your partner to connect.
                </p>
                <Button onClick={copyToken} variant="outline" className="w-full rounded-full gap-2">
                  {copied ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  {copied ? 'Copied!' : 'Copy Token'}
                </Button>
              </div>
            )}
          </Card>

          {/* Connect with partner */}
          <Card className="p-6 rounded-2xl">
            <h3 className="font-heading font-semibold mb-4">Connect with Partner</h3>
            {!connected ? (
              <div className="space-y-3">
                <Input
                  placeholder="Enter your partner's sync token (e.g., NX-7K9-2M4)"
                  value={partnerToken}
                  onChange={(e) => setPartnerToken(e.target.value)}
                  className="font-mono"
                />
                <Button
                  onClick={connectPartner}
                  variant="secondary"
                  disabled={connecting || partnerToken.trim().length < 6}
                  className="w-full rounded-full gap-2"
                >
                  {connecting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Link2 className="w-4 h-4" />}
                  {connecting ? 'Connecting…' : 'Connect to Partner'}
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
