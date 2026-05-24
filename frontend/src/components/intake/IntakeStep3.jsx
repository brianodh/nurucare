import React from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

export default function IntakeStep3({ data, onChange }) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="font-heading font-semibold text-xl mb-1">Menstrual & Fertility Profile</h3>
        <p className="text-sm text-muted-foreground">Understanding your cycle helps personalize recommendations.</p>
      </div>
      <div className="space-y-4">
        <div>
          <Label htmlFor="lmp">Last Menstrual Period</Label>
          <Input
            id="lmp"
            type="date"
            value={data.lastPeriod || ''}
            onChange={e => onChange({ ...data, lastPeriod: e.target.value })}
            className="mt-1.5"
          />
        </div>
        <div>
          <Label htmlFor="cycleLength">Cycle Length (days)</Label>
          <Input
            id="cycleLength"
            type="number"
            min="21"
            max="45"
            placeholder="e.g. 28"
            value={data.cycleLength || ''}
            onChange={e => onChange({ ...data, cycleLength: e.target.value })}
            className="mt-1.5"
          />
        </div>
        <div className="space-y-3">
          <div className="flex items-center space-x-3 bg-muted/50 rounded-xl p-3">
            <Checkbox
              id="irregular"
              checked={data.irregularPeriods || false}
              onCheckedChange={v => onChange({ ...data, irregularPeriods: v })}
            />
            <Label htmlFor="irregular" className="cursor-pointer font-normal">I have irregular periods</Label>
          </div>
          <div className="flex items-center space-x-3 bg-muted/50 rounded-xl p-3">
            <Checkbox
              id="hormonal"
              checked={data.hormonalImbalance || false}
              onCheckedChange={v => onChange({ ...data, hormonalImbalance: v })}
            />
            <Label htmlFor="hormonal" className="cursor-pointer font-normal">Suspected hormonal imbalance</Label>
          </div>
        </div>
        <div>
          <Label>Fertility Intentions</Label>
          <Select value={data.fertilityIntention || ''} onValueChange={v => onChange({ ...data, fertilityIntention: v })}>
            <SelectTrigger className="mt-1.5">
              <SelectValue placeholder="Select timeline" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="short_term">Short-term (want children within 1–2 years)</SelectItem>
              <SelectItem value="long_term">Long-term (no plans for children soon)</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="flex items-center justify-between bg-muted/50 rounded-xl p-4">
          <div>
            <Label>Currently Breastfeeding</Label>
            <p className="text-xs text-muted-foreground mt-0.5">This affects method eligibility</p>
          </div>
          <Switch
            checked={data.breastfeeding || false}
            onCheckedChange={v => onChange({ ...data, breastfeeding: v })}
          />
        </div>
        {data.breastfeeding && (
          <div>
            <Label htmlFor="infantAge">Infant Age (weeks)</Label>
            <Input
              id="infantAge"
              type="number"
              min="0"
              max="104"
              placeholder="e.g. 12"
              value={data.infantAge || ''}
              onChange={e => onChange({ ...data, infantAge: e.target.value })}
              className="mt-1.5"
            />
          </div>
        )}
      </div>
    </div>
  );
}