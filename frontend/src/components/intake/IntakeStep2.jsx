import React from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';

export default function IntakeStep2({ data, onChange }) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="font-heading font-semibold text-xl mb-1">Clinical Health Metrics</h3>
        <p className="text-sm text-muted-foreground">This information helps us assess safety based on WHO criteria.</p>
      </div>
      <div className="space-y-4">
        <div>
          <Label>Blood Pressure</Label>
          <div className="grid grid-cols-2 gap-3 mt-1.5">
            <div>
              <Input
                type="number"
                placeholder="Systolic (e.g. 120)"
                value={data.systolic || ''}
                onChange={e => onChange({ ...data, systolic: e.target.value })}
              />
              <p className="text-xs text-muted-foreground mt-1">Systolic (top)</p>
            </div>
            <div>
              <Input
                type="number"
                placeholder="Diastolic (e.g. 80)"
                value={data.diastolic || ''}
                onChange={e => onChange({ ...data, diastolic: e.target.value })}
              />
              <p className="text-xs text-muted-foreground mt-1">Diastolic (bottom)</p>
            </div>
          </div>
        </div>
        <div className="flex items-center justify-between bg-muted/50 rounded-xl p-4">
          <div>
            <Label>Smoking Status</Label>
            <p className="text-xs text-muted-foreground mt-0.5">Do you currently smoke?</p>
          </div>
          <Switch
            checked={data.smoking || false}
            onCheckedChange={v => onChange({ ...data, smoking: v })}
          />
        </div>
        <div>
          <Label>Migraine History</Label>
          <RadioGroup
            value={data.migraine || 'none'}
            onValueChange={v => onChange({ ...data, migraine: v })}
            className="mt-2 space-y-2"
          >
            {[
              { value: 'none', label: 'No migraines' },
              { value: 'without_aura', label: 'Migraine without aura' },
              { value: 'with_aura', label: 'Migraine with aura' },
            ].map(opt => (
              <div key={opt.value} className="flex items-center space-x-3 bg-muted/50 rounded-xl p-3">
                <RadioGroupItem value={opt.value} id={opt.value} />
                <Label htmlFor={opt.value} className="cursor-pointer font-normal">{opt.label}</Label>
              </div>
            ))}
          </RadioGroup>
        </div>
      </div>
    </div>
  );
}