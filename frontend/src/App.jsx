import { Toaster } from "@/components/ui/toaster"
import { QueryClientProvider } from '@tanstack/react-query'
import { queryClientInstance } from '@/lib/query-client'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import PageNotFound from './lib/PageNotFound';
import { AuthProvider, useAuth } from '@/lib/AuthContext';
import UserNotRegisteredError from '@/components/UserNotRegisteredError';

import AppLayout from './components/layout/AppLayout';
import NurseLayout from './components/nurse/NurseLayout';
import Landing from './pages/Landing';
import RoleSelection from './pages/RoleSelection';
import FemaleIntake from './pages/FemaleIntake';
import Education from './pages/Education';
import SessionKey from './pages/SessionKey';
import PartnerSync from './pages/PartnerSync';
import MaleDashboard from './pages/MaleDashboard';
import NurseDashboard from './pages/nurse/NurseDashboard';
import PatientLookup from './pages/nurse/PatientLookup';
import NurseAnalytics from './pages/nurse/NurseAnalytics';

const AuthenticatedApp = () => {
  const { isLoadingAuth, isLoadingPublicSettings, authError, navigateToLogin } = useAuth();

  if (isLoadingPublicSettings || isLoadingAuth) {
    return (
      <div className="fixed inset-0 flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-slate-200 border-t-slate-800 rounded-full animate-spin"></div>
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
        <Route path="/" element={<Landing />} />
        <Route path="/roles" element={<RoleSelection />} />
        <Route path="/female/intake" element={<FemaleIntake />} />
        <Route path="/female/session" element={<SessionKey />} />
        <Route path="/female/sync" element={<PartnerSync />} />
        <Route path="/education" element={<Education />} />
        <Route path="/male/dashboard" element={<MaleDashboard />} />
        <Route path="/partner-sync" element={<PartnerSync />} />
      </Route>
      <Route element={<NurseLayout />}>
        <Route path="/nurse/dashboard" element={<NurseDashboard />} />
        <Route path="/nurse/lookup" element={<PatientLookup />} />
        <Route path="/nurse/analytics" element={<NurseAnalytics />} />
      </Route>
      <Route path="*" element={<PageNotFound />} />
    </Routes>
  );
};


function App() {
  return (
    <AuthProvider>
      <QueryClientProvider client={queryClientInstance}>
        <Router>
          <AuthenticatedApp />
        </Router>
        <Toaster />
      </QueryClientProvider>
    </AuthProvider>
  )
}

export default App