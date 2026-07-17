
import React from 'react';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

export default function MaleIntakeStep3({ data, onChange }) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="font-heading font-semibold text-xl mb-1">Reproductive Health Profile</h3>
        <p className="text-sm text-muted-foreground">Understanding your goals helps personalize recommendations.</p>
      </div>
      <div className="space-y-4">
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
      </div>
    </div>
  );
}
