import React from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { useLang } from '@/lib/i18n';

export default function IntakeStep2({ data, onChange }) {
  const { t } = useLang();
  return (
    <div className="space-y-6">
      <div>
        <h3 className="font-heading font-semibold text-xl mb-1">{t('s2_title')}</h3>
        <p className="text-sm text-muted-foreground">{t('s2_sub')}</p>
      </div>
      <div className="space-y-4">
        <div>
          <Label>{t('s2_bp')}</Label>
          <div className="grid grid-cols-2 gap-3 mt-1.5">
            <div>
              <Input
                type="number"
                placeholder={t('s2_systolic_ph')}
                value={data.systolic || ''}
                onChange={e => onChange({ ...data, systolic: e.target.value })}
              />
              <p className="text-xs text-muted-foreground mt-1">{t('s2_systolic_label')}</p>
            </div>
            <div>
              <Input
                type="number"
                placeholder={t('s2_diastolic_ph')}
                value={data.diastolic || ''}
                onChange={e => onChange({ ...data, diastolic: e.target.value })}
              />
              <p className="text-xs text-muted-foreground mt-1">{t('s2_diastolic_label')}</p>
            </div>
          </div>
        </div>
        <div className="flex items-center justify-between bg-muted/50 rounded-xl p-4">
          <div>
            <Label>{t('s2_smoking')}</Label>
            <p className="text-xs text-muted-foreground mt-0.5">{t('s2_smoking_sub')}</p>
          </div>
          <Switch
            checked={data.smoking || false}
            onCheckedChange={v => onChange({ ...data, smoking: v })}
          />
        </div>
        <div>
          <Label>{t('s2_migraine')}</Label>
          <RadioGroup
            value={data.migraine || 'none'}
            onValueChange={v => onChange({ ...data, migraine: v })}
            className="mt-2 space-y-2"
          >
            {[
              { value: 'none', labelKey: 's2_mig_none' },
              { value: 'without_aura', labelKey: 's2_mig_without' },
              { value: 'with_aura', labelKey: 's2_mig_with' },
            ].map(opt => (
              <div key={opt.value} className="flex items-center space-x-3 bg-muted/50 rounded-xl p-3">
                <RadioGroupItem value={opt.value} id={opt.value} />
                <Label htmlFor={opt.value} className="cursor-pointer font-normal">{t(opt.labelKey)}</Label>
              </div>
            ))}
          </RadioGroup>
        </div>
      </div>
    </div>
  );
}