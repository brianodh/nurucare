import React from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

export default function IntakeStep1({ data, onChange }) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="font-heading font-semibold text-xl mb-1">Basic Information</h3>
        <p className="text-sm text-muted-foreground">Let's start with some basic details about you.</p>
      </div>
      <div className="space-y-4">
        <div>
          <Label htmlFor="age">Age</Label>
          <Input
            id="age"
            type="number"
            min="15"
            max="55"
            placeholder="Enter your age"
            value={data.age || ''}
            onChange={e => onChange({ ...data, age: e.target.value })}
            className="mt-1.5"
          />
        </div>
        <div>
          <Label>Relationship Status</Label>
          <Select value={data.relationshipStatus || ''} onValueChange={v => onChange({ ...data, relationshipStatus: v })}>
            <SelectTrigger className="mt-1.5">
              <SelectValue placeholder="Select status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="single">Single</SelectItem>
              <SelectItem value="in_relationship">In a Relationship</SelectItem>
              <SelectItem value="married">Married</SelectItem>
              <SelectItem value="prefer_not_say">Prefer not to say</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  );
}