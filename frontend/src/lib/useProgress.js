/**
 * useProgress.js - Progress tracking hook for multi-step intake form
 * 
 * This hook manages the state of multi-step forms like the contraceptive intake form.
 * It tracks which step the user is on and which steps they've completed.
 */

import { useState } from 'react';

/**
 * Custom hook for tracking progress through a multi-step form
 * @param {number} totalSteps - Total number of steps in the form (default: 5)
 * @returns {Object} Progress state and control functions
 */
export function useProgress(totalSteps = 5) {
  // Current step index (0-based)
  const [currentStep, setCurrentStep] = useState(0);
  
  // Array of completed step indices
  const [completedSteps, setCompletedSteps] = useState([]);
  
  // Whether the form is fully completed
  const [isCompleted, setIsCompleted] = useState(false);

  /**
   * Go to the next step
   */
  const nextStep = () => {
    if (currentStep < totalSteps - 1) {
      setCurrentStep(prev => prev + 1);
    } else {
      setIsCompleted(true);
    }
  };

  /**
   * Go to the previous step
   */
  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  /**
   * Go to a specific step
   * @param {number} step - Step index to jump to
   */
  const goToStep = (step) => {
    if (step >= 0 && step < totalSteps) {
      setCurrentStep(step);
    }
  };

  /**
   * Mark a step as completed
   * @param {number} step - Step index to mark as complete
   */
  const completeStep = (step) => {
    if (!completedSteps.includes(step)) {
      setCompletedSteps([...completedSteps, step]);
    }
  };

  /**
   * Check if a specific step is completed
   * @param {number} step - Step index to check
   * @returns {boolean} True if step is completed
   */
  const isStepComplete = (step) => {
    return completedSteps.includes(step);
  };

  /**
   * Get the progress percentage (0-100)
   * @returns {number} Progress percentage
   */
  const getProgressPercentage = () => {
    return (completedSteps.length / totalSteps) * 100;
  };

  /**
   * Reset all progress (start over)
   */
  const resetProgress = () => {
    setCurrentStep(0);
    setCompletedSteps([]);
    setIsCompleted(false);
  };

  /**
   * Check if all steps are completed
   * @returns {boolean} True if all steps are completed
   */
  const isAllStepsCompleted = () => {
    return completedSteps.length === totalSteps;
  };

  return {
    // State
    currentStep,
    completedSteps,
    isCompleted,
    
    // Navigation
    nextStep,
    prevStep,
    goToStep,
    
    // Completion tracking
    completeStep,
    isStepComplete,
    getProgressPercentage,
    resetProgress,
    isAllStepsCompleted,
    
    // Constants
    totalSteps
  };
}

// Also export as default for flexibility
export default useProgress;