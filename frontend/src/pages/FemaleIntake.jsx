import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { ArrowLeft, ArrowRight, CheckCircle } from 'lucide-react';
import IntakeStep1 from '../components/intake/IntakeStep1';
import IntakeStep2 from '../components/intake/IntakeStep2';
import IntakeStep3 from '../components/intake/IntakeStep3';
import IntakeStep4 from '../components/intake/IntakeStep4';
import IntakeStep5 from '../components/intake/IntakeStep5';
import { Link } from 'react-router-dom';

const stepLabels = ['Basic Info', 'Health Metrics', 'Fertility Profile', 'Side Effects', 'Results'];

export default function FemaleIntake() {
  const [step, setStep] = useState(0);
  const [data, setData] = useState({});
  const totalSteps = 5;

  const canNext = () => {
    if (step === 0) return data.age && data.relationshipStatus;
    if (step === 1) return true;
    if (step === 2) return true;
    if (step === 3) return true;
    return false;
  };

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
              {step === 0 && <IntakeStep1 data={data} onChange={setData} />}
              {step === 1 && <IntakeStep2 data={data} onChange={setData} />}
              {step === 2 && <IntakeStep3 data={data} onChange={setData} />}
              {step === 3 && <IntakeStep4 data={data} onChange={setData} />}
              {step === 4 && <IntakeStep5 data={data} />}
            </motion.div>
          </AnimatePresence>
        </div>

        <div className="flex justify-between mt-6">
          <Button
            variant="outline"
            onClick={() => setStep(s => s - 1)}
            disabled={step === 0}
            className="gap-2 rounded-full"
          >
            <ArrowLeft className="w-4 h-4" /> Back
          </Button>
          {step < totalSteps - 1 ? (
            <Button
              onClick={() => setStep(s => s + 1)}
              disabled={!canNext()}
              className="gap-2 rounded-full"
            >
              Next <ArrowRight className="w-4 h-4" />
            </Button>
          ) : (
            <div className="flex gap-3">
              <Link to="/education">
                <Button variant="outline" className="rounded-full">Learn More</Button>
              </Link>
              <Link to="/female/session">
                <Button className="gap-2 rounded-full">
                  <CheckCircle className="w-4 h-4" /> Generate Session Key
                </Button>
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}