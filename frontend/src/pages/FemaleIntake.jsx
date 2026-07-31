import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { ArrowLeft, ArrowRight, CheckCircle, RotateCcw, Loader2, Users } from 'lucide-react';
import IntakeStep1 from '../components/intake/IntakeStep1';
import IntakeStep2 from '../components/intake/IntakeStep2';
import IntakeStep3 from '../components/intake/IntakeStep3';
import IntakeStep4 from '../components/intake/IntakeStep4';
import IntakeStep5 from '../components/intake/IntakeStep5';
import { Link, useNavigate } from 'react-router-dom';
import { submitIntake, getRecommendations, generateSessionKey } from '@/api/apiClient';
import { useToast } from '@/components/ui/use-toast';
import { useProgress } from '../lib/useProgress';

const stepLabels = ['Basic Info', 'Health Metrics', 'Fertility Profile', 'Side Effects', 'Results'];

// ── Generate session key button ────────────────────────────
function GenerateKeyButton({ profileId, data, onSaved }) {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      let pid = profileId;

      // If we don't have a profile yet, save intake first
      if (!pid) {
        const payload = buildPayload(data);
        const intakeResult = await submitIntake(payload);
        pid = intakeResult.profile_id || intakeResult.session_id;
        if (onSaved) onSaved(pid);
      }

      const keyResult = await generateSessionKey(pid);
      navigate('/female/session', { state: { sessionKey: keyResult.session_key, patientId: pid } });
    } catch (err) {
      toast({ title: 'Error', description: 'Could not generate session key. Please try again.', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button onClick={handleGenerate} disabled={loading} className="gap-2 rounded-full">
      {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle className="w-4 h-4" />}
      {loading ? 'Saving…' : 'Generate Session Key'}
    </Button>
  );
}

function buildPayload(data) {
  return {
    age: Number(data.age) || 0,
    gender: 'female',
    systolic_bp: Number(data.systolic) || 120,
    diastolic_bp: Number(data.diastolic) || 80,
    smoking: data.smoking || false,
    migraine_type: data.migraine || 'none',
    is_pregnant: false,
    breastfeeding: data.breastfeeding || false,
    fertility_intention: data.fertilityIntention || 'short_term',
    parity: 0,
  };
}

export default function FemaleIntake() {
  const { progress, update, clear, markCompleted } = useProgress();
  const { toast } = useToast();
  const navigate = useNavigate();

  const [step, setStep] = useState(progress.intakeStep ?? 0);
  const [data, setData] = useState(progress.intakeData ?? {});
  const [loading, setLoading] = useState(false);
  const [apiResult, setApiResult] = useState(progress.results ?? null);
  const [profileId, setProfileId] = useState(progress.profileId ?? null);

  // If already completed, jump straight to results step
  const [showResults, setShowResults] = useState(!!progress.completed && !!progress.results);

  const totalSteps = 5;

  const handleDataChange = (next) => {
    setData(next);
    update({ intakeData: next });
  };

  const handleStepChange = (next) => {
    const n = typeof next === 'function' ? next(step) : next;
    setStep(n);
    update({ intakeStep: n });
  };

  const canNext = () => {
    if (step === 0) return data.age && data.relationshipStatus;
    return true;
  };

  // Step 3 → Step 4: submit to backend
  const handleNext = async () => {
    if (step === 3) {
      setLoading(true);
      try {
        const payload = buildPayload(data);
        const [intakeRes, recRes] = await Promise.all([
          submitIntake(payload),
          getRecommendations(payload),
        ]);
        const pid = intakeRes.profile_id || intakeRes.session_id;
        setProfileId(pid);
        setApiResult(recRes);
        markCompleted(pid, recRes);
      } catch (err) {
        toast({ title: 'Error', description: 'Could not get recommendations. Please try again.', variant: 'destructive' });
        setLoading(false);
        return;
      }
      setLoading(false);
    }
    handleStepChange((s) => s + 1);
  };

  const handleStartOver = () => {
    clear();
    setStep(0);
    setData({});
    setApiResult(null);
    setProfileId(null);
    setShowResults(false);
  };

  // ── Returning user: show saved results ──────────────────
  if (showResults && apiResult) {
    return (
      <div className="min-h-[85vh] py-8">
        <div className="max-w-2xl mx-auto px-4">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="font-heading font-bold text-lg">Your Health Assessment</h2>
              <p className="text-xs text-muted-foreground mt-0.5">
                Saved {progress.completedAt ? new Date(progress.completedAt).toLocaleDateString() : ''}
              </p>
            </div>
            <Button variant="outline" size="sm" onClick={handleStartOver} className="gap-2 rounded-full">
              <RotateCcw className="w-3.5 h-3.5" /> Start Over
            </Button>
          </div>

          <div className="bg-card rounded-2xl border shadow-sm p-6 sm:p-8">
            <IntakeStep5 data={data} apiResult={apiResult} online={true} />
          </div>

          <div className="flex gap-3 mt-6 justify-end flex-wrap">
            <Link to="/education">
              <Button variant="outline" className="rounded-full">Learn More</Button>
            </Link>
            <Link to="/patient/dashboard">
              <Button variant="secondary" className="rounded-full">Go to Dashboard</Button>
            </Link>
            <Link to="/female/sync">
              <Button variant="outline" className="rounded-full gap-2">
                <Users className="w-4 h-4" /> Partner Sync
              </Button>
            </Link>
            <GenerateKeyButton
              profileId={profileId}
              data={data}
              onSaved={setProfileId}
            />
          </div>
        </div>
      </div>
    );
  }

  // ── New user: show the form ──────────────────────────────
  return (
    <div className="min-h-[85vh] py-8">
      <div className="max-w-2xl mx-auto px-4">
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-heading font-bold text-lg">Health Assessment</h2>
            <span className="text-sm text-muted-foreground">Step {step + 1} of {totalSteps}</span>
          </div>
          <Progress value={((step + 1) / totalSteps) * 100} className="h-2" />
          <div className="flex justify-between mt-2">
            {stepLabels.map((l, i) => (
              <span key={i} className={`text-xs hidden sm:block ${i <= step ? 'text-primary font-medium' : 'text-muted-foreground'}`}>
                {l}
              </span>
            ))}
          </div>
        </div>

        <div className="bg-card rounded-2xl border shadow-sm p-6 sm:p-8 min-h-[400px]">
          <AnimatePresence mode="wait">
            <motion.div
              key={step}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
            >
              {step === 0 && <IntakeStep1 data={data} onChange={handleDataChange} />}
              {step === 1 && <IntakeStep2 data={data} onChange={handleDataChange} />}
              {step === 2 && <IntakeStep3 data={data} onChange={handleDataChange} />}
              {step === 3 && <IntakeStep4 data={data} onChange={handleDataChange} />}
              {step === 4 && <IntakeStep5 data={data} apiResult={apiResult} online={true} />}
            </motion.div>
          </AnimatePresence>
        </div>

        <div className="flex justify-between mt-6">
          <Button
            variant="outline"
            onClick={() => handleStepChange((s) => s - 1)}
            disabled={step === 0 || loading}
            className="gap-2 rounded-full"
          >
            <ArrowLeft className="w-4 h-4" /> Back
          </Button>

          {step < totalSteps - 1 ? (
            <Button
              onClick={handleNext}
              disabled={!canNext() || loading}
              className="gap-2 rounded-full"
            >
              {loading ? (
                <><Loader2 className="w-4 h-4 animate-spin" /> Analysing...</>
              ) : (
                <>{step === 3 ? 'Get Results' : 'Next'} <ArrowRight className="w-4 h-4" /></>
              )}
            </Button>
          ) : (
            <div className="flex gap-3 flex-wrap justify-end">
              <Link to="/education">
                <Button variant="outline" className="rounded-full">Learn More</Button>
              </Link>
              <Link to="/female/sync">
                <Button variant="outline" className="rounded-full gap-2">
                  <Users className="w-4 h-4" /> Partner Sync
                </Button>
              </Link>
              <GenerateKeyButton
                profileId={profileId}
                data={data}
                onSaved={setProfileId}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
