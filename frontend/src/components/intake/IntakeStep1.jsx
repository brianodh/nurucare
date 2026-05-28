import React from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useLang } from '@/lib/i18n';

export default function IntakeStep1({ data, onChange }) {
  const { t } = useLang();
  return (
    <div className="space-y-6">
      <div>
        <h3 className="font-heading font-semibold text-xl mb-1">{t('s1_title')}</h3>
        <p className="text-sm text-muted-foreground">{t('s1_sub')}</p>
      </div>
      <div className="space-y-4">
        <div>
          <Label htmlFor="age">{t('s1_age')}</Label>
          <Input
            id="age"
            type="number"
            min="15"
            max="55"
            placeholder={t('s1_age_placeholder')}
            value={data.age || ''}
            onChange={e => onChange({ ...data, age: e.target.value })}
            className="mt-1.5"
          />
        </div>
        <div>
          <Label>{t('s1_relationship')}</Label>
          <Select value={data.relationshipStatus || ''} onValueChange={v => onChange({ ...data, relationshipStatus: v })}>
            <SelectTrigger className="mt-1.5">
              <SelectValue placeholder={t('s1_rel_placeholder')} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="single">{t('s1_single')}</SelectItem>
              <SelectItem value="in_relationship">{t('s1_relationship_val')}</SelectItem>
              <SelectItem value="married">{t('s1_married')}</SelectItem>
              <SelectItem value="prefer_not_say">{t('s1_prefer_not')}</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  );
}