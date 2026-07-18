import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { Menu, Heart, Moon, Sun, LogOut, UserCircle } from 'lucide-react';
import { useLang } from '@/lib/i18n.jsx';
import LanguageSwitcher from '@/components/LanguageSwitcher';
import { useAuth } from '@/lib/AuthContext';

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [dark, setDark] = useState(false);
  const location = useLocation();
  const isLanding = location.pathname === '/';
  const langContext = useLang();
  const t = langContext ? langContext.t : (key) => key;
  const { isAuthenticated, user, logout } = useAuth();

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
    { label: t('home'), to: '/' },
    { label: t('getStarted'), to: isAuthenticated ? '/roles' : '/signup' },
    { label: t('education'), to: '/education' },
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

            {isAuthenticated ? (
              /* ── Signed-in state ── */
              <div className="hidden md:flex items-center gap-2">
                <Link to="/profile" className="flex items-center gap-1.5 text-sm text-muted-foreground px-2 hover:text-primary transition-colors">
                  <UserCircle className="w-4 h-4 text-primary" />
                  <span className="font-medium text-foreground">
                    {user?.name?.split(' ')[0] ?? 'Patient'}
                  </span>
                </Link>
                <Button
                  variant="ghost"
                  size="sm"
                  className="rounded-full gap-1.5 text-muted-foreground hover:text-destructive"
                  onClick={logout}
                >
                  <LogOut className="w-4 h-4" /> Sign out
                </Button>
              </div>
            ) : (
              /* ── Signed-out state ── */
              <div className="hidden md:flex items-center gap-2">
                <Link to="/login">
                  <Button variant="ghost" size="sm" className="rounded-full px-4">Sign in</Button>
                </Link>
                <Link to="/signup">
                  <Button size="sm" className="rounded-full px-5">{t('startFree')}</Button>
                </Link>
              </div>
            )}

            {/* Mobile hamburger */}
            <Sheet>
              <SheetTrigger asChild className="md:hidden">
                <Button variant="ghost" size="icon"><Menu className="w-5 h-5" /></Button>
              </SheetTrigger>
              <SheetContent side="right" className="w-72">
                <div className="flex flex-col gap-4 mt-8">
                  {isAuthenticated && (
                    <Link to="/profile" className="flex items-center gap-2 px-2 pb-2 border-b hover:text-primary transition-colors">
                      <UserCircle className="w-5 h-5 text-primary" />
                      <span className="font-medium">{user?.name ?? 'Patient'}</span>
                    </Link>
                  )}
                  {navLinks.map(l => (
                    <Link key={l.to} to={l.to}>
                      <Button variant="ghost" className="w-full justify-start">{l.label}</Button>
                    </Link>
                  ))}
                  {isAuthenticated ? (
                    <Button
                      variant="outline"
                      className="w-full rounded-full gap-2 text-destructive border-destructive/30"
                      onClick={logout}
                    >
                      <LogOut className="w-4 h-4" /> Sign out
                    </Button>
                  ) : (
                    <>
                      <Link to="/login">
                        <Button variant="outline" className="w-full rounded-full">Sign in</Button>
                      </Link>
                      <Link to="/signup">
                    <Button className="w-full rounded-full">{t('startFree')}</Button>
                  </Link>
                    </>
                  )}
                </div>
              </SheetContent>
            </Sheet>
          </div>
        </div>
      </div>
    </header>
  );
}
