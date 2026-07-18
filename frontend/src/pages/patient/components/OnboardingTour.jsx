import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Heart, TrendingUp, Bell, BookOpen, X } from 'lucide-react';

const tourSteps = [
  {
    id: 1,
    title: 'Welcome to NuruCare!',
    description: 'Let\'s take a quick tour of your dashboard.',
    Icon: Heart,
  },
  {
    id: 2,
    title: 'Health Score',
    description: 'See your personalized health score based on your profile.',
    Icon: TrendingUp,
  },
  {
    id: 3,
    title: 'Quick Actions',
    description: 'Quickly access key features from here.',
    Icon: Heart,
  },
  {
    id: 4,
    title: 'Notifications',
    description: 'Stay updated with important notifications.',
    Icon: Bell,
  },
  {
    id: 5,
    title: 'Education',
    description: 'Explore personalized educational content.',
    Icon: BookOpen,
  },
];

export default function OnboardingTour({ currentStep, onNext, onPrev, onClose, totalSteps }) {
  const step = tourSteps[currentStep];
  const StepIcon = step.Icon;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-card rounded-2xl border shadow-xl w-full max-w-md p-6"
      >
        <div className="flex justify-end">
          <Button variant="ghost" size="icon" onClick={onClose} className="rounded-full">
            <X className="w-5 h-5" />
          </Button>
        </div>
        <div className="flex flex-col items-center text-center space-y-4">
          <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
            <StepIcon className="w-8 h-8 text-primary" />
          </div>
          <div className="w-full">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-muted-foreground">
                Step {currentStep + 1} of {totalSteps}
              </span>
              <div className="flex-1 h-1 bg-muted rounded-full overflow-hidden ml-4">
                <motion.div
                  className="h-full bg-primary"
                  initial={{ width: `${(currentStep / totalSteps) * 100}%` }}
                  animate={{ width: `${((currentStep + 1) / totalSteps) * 100}%` }}
                />
              </div>
            </div>
          </div>
          <h3 className="text-xl font-bold">{step.title}</h3>
          <p className="text-muted-foreground">{step.description}</p>
          <div className="flex gap-2 w-full">
            {currentStep > 0 && (
              <Button variant="ghost" onClick={onPrev} className="flex-1">
                Back
              </Button>
            )}
            {currentStep < totalSteps - 1 ? (
              <Button onClick={onNext} className="flex-1">
              Next
            </Button>
            ) : (
              <Button onClick={onClose} className="flex-1">
                Get Started
              </Button>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
