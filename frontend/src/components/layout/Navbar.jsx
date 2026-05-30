import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { Menu, Heart, Moon, Sun } from 'lucide-react';
// Change this line:
import { useLang } from '@/lib/i18n.jsx'; // 🚀 Added .jsx extension explicitly

import LanguageSwitcher from '@/components/LanguageSwitcher';

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [dark, setDark] = useState(false);
  const location = useLocation();
  const isLanding = location.pathname === '/';
  
// Ensure useLang is imported at the top of the file
const langContext = useLang(); 
const t = langContext ? langContext.t : (key) => key;


  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handler);
    return () => window.removeEventListener('scroll', handler);
  }, []);

  const toggleDark = () => {
    setDark(!dark);
    document.documentElement.classList.toggle('dark');
  };

  const navLinks = [
    { label: t('nav_home'), to: '/' },
    { label: t('nav_get_started'), to: '/roles' },
    { label: t('nav_education'), to: '/education' },
  ];

  return (
    <header className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
      scrolled ? 'bg-card/90 backdrop-blur-xl shadow-sm border-b' : 'bg-transparent'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
              <Heart className="w-4 h-4 text-primary-foreground" />
            </div>
            <span className="font-heading font-bold text-lg">NuruCare</span>
          </Link>

          <nav className="hidden md:flex items-center gap-1">
            {navLinks.map(l => (
              <Link key={l.to} to={l.to}>
                <Button variant={location.pathname === l.to ? 'secondary' : 'ghost'} size="sm">
                  {l.label}
                </Button>
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-2">
            <LanguageSwitcher />
            <Button variant="ghost" size="icon" onClick={toggleDark} className="rounded-full">
              {dark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </Button>
            <Link to="/roles" className="hidden md:block">
              <Button size="sm" className="rounded-full px-5">{t('nav_start_free')}</Button>
            </Link>
            <Sheet>
              <SheetTrigger asChild className="md:hidden">
                <Button variant="ghost" size="icon"><Menu className="w-5 h-5" /></Button>
              </SheetTrigger>
              <SheetContent side="right" className="w-72">
                <div className="flex flex-col gap-4 mt-8">
                  {navLinks.map(l => (
                    <Link key={l.to} to={l.to}>
                      <Button variant="ghost" className="w-full justify-start">{l.label}</Button>
                    </Link>
                  ))}
                  <Link to="/roles">
                    <Button className="w-full rounded-full">{t('nav_start_free')}</Button>
                  </Link>
                </div>
              </SheetContent>
            </Sheet>
          </div>
        </div>
      </div>
    </header>
  );
}