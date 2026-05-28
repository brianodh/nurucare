import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
// Change this line:
import { useLang } from '@/lib/i18n.jsx'; // 🚀 Added .jsx extension explicitly


export default function LanguageSwitcher() {
  const langContext = useLang();
  
  // 🚀 HACKATHON LOCAL BYPASS: Fallback to local state if translation context is null
  const [localLang, setLocalLang] = useState('en');
  
  const lang = langContext ? langContext.lang : localLang;
  const setLang = langContext ? langContext.setLang : (val) => setLocalLang(val);

  return (
    <div className="flex items-center gap-1 rounded-full border bg-muted/50 p-0.5">
      <button
        onClick={() => setLang('en')}
        className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
          lang === 'en' ? 'bg-card shadow text-foreground' : 'text-muted-foreground hover:text-foreground'
        }`}
      >
        EN
      </button>
      <button
        onClick={() => setLang('sw')}
        className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
          lang === 'sw' ? 'bg-card shadow text-foreground' : 'text-muted-foreground hover:text-foreground'
        }`}
      >
        SW
      </button>
    </div>
  );
}
