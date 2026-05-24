import React from 'react';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';

const sideEffects = [
  { id: 'weight_gain', label: 'Weight gain', desc: 'Prefer methods with minimal weight change' },
  { id: 'mood_shifts', label: 'Mood shifts', desc: 'Sensitive to hormonal mood changes' },
  { id: 'acne', label: 'Acne', desc: 'Concerned about skin changes' },
  { id: 'irregular_bleeding', label: 'Irregular bleeding', desc: 'Prefer predictable bleeding patterns' },
  { id: 'low_libido', label: 'Low libido', desc: 'Prefer methods that don\'t affect desire' },
];

export default function IntakeStep4({ data, onChange }) {
  const selected = data.sideEffectConcerns || [];

  const toggleEffect = (id) => {
    const next = selected.includes(id)
      ? selected.filter(s => s !== id)
      : [...selected, id];
    onChange({ ...data, sideEffectConcerns: next });
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="font-heading font-semibold text-xl mb-1">Side Effect Preferences</h3>
        <p className="text-sm text-muted-foreground">
          Select any side effects you'd like to avoid. This helps us prioritize methods that match your comfort.
        </p>
      </div>
      <div className="space-y-3">
        {sideEffects.map(se => (
          <div
            key={se.id}
            onClick={() => toggleEffect(se.id)}
            className={`flex items-start space-x-3 rounded-xl p-4 border cursor-pointer transition-all ${
              selected.includes(se.id)
                ? 'border-primary bg-primary/5'
                : 'border-border bg-muted/30 hover:bg-muted/50'
            }`}
          >
            <Checkbox
              checked={selected.includes(se.id)}
              onCheckedChange={() => toggleEffect(se.id)}
              className="mt-0.5"
            />
            <div>
              <Label className="cursor-pointer font-medium">{se.label}</Label>
              <p className="text-xs text-muted-foreground mt-0.5">{se.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}