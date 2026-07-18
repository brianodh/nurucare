import { Toaster } from "@/components/ui/toaster"
import { QueryClientProvider } from '@tanstack/react-query'
import { queryClientInstance } from '@/lib/query-client'
import { BrowserRouter as Router, Route, Routes, Navigate, useLocation } from 'react-router-dom';
import PageNotFound from './lib/PageNotFound';
import { AuthProvider, useAuth } from '@/lib/AuthContext';
import UserNotRegisteredError from '@/components/UserNotRegisteredError';
import { LanguageProvider } from "@/lib/i18n";

import AppLayout from './components/layout/AppLayout';
import NurseLayout from './components/nurse/NurseLayout';
import Landing from './pages/Landing';
import RoleSelection from './pages/RoleSelection';
import FemaleIntake from './pages/FemaleIntake';
import MaleIntake from './pages/MaleIntake';
import Education from './pages/Education';
import SessionKey from './pages/SessionKey';
import PartnerSync from './pages/PartnerSync';
import MaleDashboard from './pages/MaleDashboard';
import UnifiedDashboard from './pages/UnifiedDashboard';
import NurseDashboard from './pages/nurse/NurseDashboard';
import PatientLookup from './pages/nurse/PatientLookup';
import NurseAnalytics from './pages/nurse/NurseAnalytics';
import SignUp from './pages/SignUp';
import Login from './pages/Login';

// ─── Route guard: patients must be signed in ──────────────────────────────────
function RequirePatientAuth({ children }) {
  const { isAuthenticated, user, isLoadingAuth } = useAuth();
  const location = useLocation();

  if (isLoadingAuth) {
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-background">
        <div className="w-8 h-8 border-4 border-slate-200 border-t-slate-800 rounded-full animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated || user?.role !== 'patient') {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }

  return children;
}

// ─── Route guard: nurses must be signed in ─────────────────────────────────────
function RequireNurseAuth({ children }) {
  const { isAuthenticated, user, isLoadingAuth } = useAuth();
  const location = useLocation();

  if (isLoadingAuth) {
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-background">
        <div className="w-8 h-8 border-4 border-slate-200 border-t-slate-800 rounded-full animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated || user?.role !== 'nurse') {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }

  return children;
}

const AuthenticatedApp = () => {
  const { isLoadingAuth, isLoadingPublicSettings, authError, navigateToLogin } = useAuth();

  if (isLoadingPublicSettings || isLoadingAuth) {
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-background">
        <div className="w-8 h-8 border-4 border-slate-200 border-t-slate-800 rounded-full animate-spin" />
      </div>
    );
  }

  if (authError) {
    if (authError.type === 'user_not_registered') {
      return <UserNotRegisteredError />;
    } else if (authError.type === 'auth_required') {
      navigateToLogin();
      return null;
    }
  }

  return (
    <Routes>
      <Route element={<AppLayout />}>
        {/* Public routes */}
        <Route path="/" element={<Landing />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/login" element={<Login />} />
        <Route path="/education" element={<Education />} />

        {/* Patient-protected routes */}
        <Route path="/roles" element={<RequirePatientAuth><RoleSelection /></RequirePatientAuth>} />
        <Route path="/female/intake" element={<RequirePatientAuth><FemaleIntake /></RequirePatientAuth>} />
              <Route path="/male/intake" element={<RequirePatientAuth><MaleIntake /></RequirePatientAuth>} />
              <Route path="/female/session" element={<RequirePatientAuth><SessionKey /></RequirePatientAuth>} />
              <Route path="/female/sync" element={<RequirePatientAuth><PartnerSync /></RequirePatientAuth>} />
              <Route path="/male/dashboard" element={<RequirePatientAuth><UnifiedDashboard gender="male" /></RequirePatientAuth>} />
        <Route path="/female/dashboard" element={<RequirePatientAuth><UnifiedDashboard gender="female" /></RequirePatientAuth>} />
        <Route path="/partner-sync" element={<RequirePatientAuth><PartnerSync /></RequirePatientAuth>} />
      </Route>

      {/* Nurse routes (protected) */}
      <Route element={<RequireNurseAuth><NurseLayout /></RequireNurseAuth>}>
        <Route path="/nurse/dashboard" element={<NurseDashboard />} />
        <Route path="/nurse/lookup" element={<PatientLookup />} />
        <Route path="/nurse/analytics" element={<NurseAnalytics />} />
      </Route>

      <Route path="*" element={<PageNotFound />} />
    </Routes>
  );
};

export default function App() {
  return (
    <LanguageProvider>
      <AuthProvider>
        <QueryClientProvider client={queryClientInstance}>
          <Router>
            <AuthenticatedApp />
          </Router>
          <Toaster />
        </QueryClientProvider>
      </AuthProvider>
    </LanguageProvider>
  );
}
