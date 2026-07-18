import React, { createContext, useContext, useState } from 'react';

// Complete translation dictionaries
const translations = {
  en: {
    // Navigation
    home: 'Home',
    getStarted: 'Get Started',
    education: 'Education',
    startFree: 'Start Free',
    signIn: 'Sign in',
    signOut: 'Sign out',

    // Landing Page
    heroTitle: 'Your Personalized Contraceptive Guide',
    heroSubtitle: 'NuruCare provides evidence-based contraceptive recommendations tailored to your unique health profile, developed with WHO guidelines.',
    getStartedBtn: 'Get Started Free',
    learnMoreBtn: 'Learn More',
    problemTitle: 'Making informed choices should be simple',
    problemSubtitle: 'Many people struggle to find contraceptive options that work for them. NuruCare simplifies this with personalized guidance.',
    howItWorksTitle: 'How It Works',
    howItWorksStep1: 'Complete Your Profile',
    howItWorksStep1Desc: 'Answer a few simple questions about your health and preferences.',
    howItWorksStep2: 'Get Personalized Recommendations',
    howItWorksStep2Desc: 'Our AI analyzes your profile using WHO MEC guidelines.',
    howItWorksStep3: 'Learn & Decide',
    howItWorksStep3Desc: 'Explore your options with educational content and decide what is best for you.',
    featuresTitle: 'Why Choose NuruCare?',
    featuresPersonalized: 'Personalized Recommendations',
    featuresPersonalizedDesc: 'Tailored to your unique health profile and preferences.',
    featuresEvidence: 'Evidence-Based',
    featuresEvidenceDesc: 'Powered by WHO medical eligibility criteria.',
    featuresPrivacy: 'Privacy First',
    featuresPrivacyDesc: 'Your data is encrypted and never shared without consent.',
    featuresPartner: 'Partner Sync',
    featuresPartnerDesc: 'Share your profile with your partner for shared decision-making.',
    faqTitle: 'Frequently Asked Questions',
    faq1Q: 'Is NuruCare free to use?',
    faq1A: 'Yes, NuruCare is completely free for all users.',
    faq2Q: 'Is my data secure?',
    faq2A: 'Absolutely. We use end-to-end encryption and never share your data without explicit consent.',
    faq3Q: 'Can I use NuruCare without a partner?',
    faq3A: 'Yes, NuruCare works perfectly for individual use as well.',
    testimonialsTitle: 'What Our Users Say',
    footerTagline: 'Empowering informed health decisions.',

    // Auth
    loginTitle: 'Welcome Back',
    loginSubtitle: 'Sign in to continue your journey with NuruCare',
    signupTitle: 'Create Your Account',
    signupSubtitle: 'Join NuruCare to get personalized contraceptive recommendations',
    usernameLabel: 'Username',
    emailLabel: 'Email',
    passwordLabel: 'Password',
    fullNameLabel: 'Full Name',
    consentLabel: 'I agree to the privacy policy and consent to data processing',
    alreadyHaveAccount: 'Already have an account?',
    dontHaveAccount: "Don't have an account?",
    signUpBtn: 'Sign Up',
    loginBtn: 'Log In',
    roleLabel: 'Role',
    genderLabel: 'Gender',
    institutionNameLabel: 'Institution Name',
    institutionAddressLabel: 'Institution Address',

    // Role Selection
    roleSelectionTitle: 'Choose Your Role',
    patientRole: 'Patient',
    nurseRole: 'Nurse',
    patientRoleDesc: 'Get personalized contraceptive recommendations',
    nurseRoleDesc: 'Support patients with contraceptive counseling',
    continueBtn: 'Continue',

    // Intake
    intakeStep1Title: 'Welcome',
    intakeStep1Desc: 'Let\'s get to know you better to provide personalized recommendations.',
    intakeStep2Title: 'Basic Information',
    intakeStep3Title: 'Health Profile',
    intakeStep4Title: 'Contraceptive History',
    intakeStep5Title: 'Preferences',
    nextBtn: 'Next',
    backBtn: 'Back',
    submitBtn: 'Submit',
    skipBtn: 'Skip',

    // Dashboard
    dashboardWelcome: 'Welcome back',
    healthScore: 'Health Score',
    recentActivity: 'Recent Activity',
    upcomingMilestones: 'Upcoming Milestones',
    quickActions: 'Quick Actions',
    partnerSync: 'Partner Sync',
    dashboardEducation: 'Education',
    findProvider: 'Find a Provider',
    healthTrends: 'Health Trends',
    notifications: 'Notifications',
    markAllRead: 'Mark All Read',
    clearAll: 'Clear All',
    noNotifications: 'No notifications',
    viewAll: 'View All',

    // Education
    educationTitle: 'Educational Resources',
    contraceptiveMethods: 'Contraceptive Methods',
    mythsAndFacts: 'Myths & Facts',
    cycleTracking: 'Cycle Tracking',
    vasectomyMyths: 'Vasectomy Myths',

    // Partner Sync
    partnerSyncTitle: 'Partner Sync',
    partnerSyncSubtitle: 'Share health decisions securely with your partner using a sync token.',
    generateToken: 'Generate Partner Sync Token',
    generating: 'Generating…',
    tokenCopied: 'Token copied!',
    copyToken: 'Copy Token',
    copied: 'Copied!',
    connectPartner: 'Connect with Partner',
    enterToken: 'Enter your partner\'s sync token (e.g., NX-7K9-2M4)',
    connecting: 'Connecting…',
    connectBtn: 'Connect to Partner',
    partnerConnected: 'Partner Connected!',
    partnerConnectedDesc: 'You can now view shared health decisions together.',
    tokenExpiresIn: 'This token expires in',
    invalidToken: 'Invalid token',
    connectionFailed: 'Connection failed',

    // Onboarding Tour
    tourWelcomeTitle: 'Welcome to NuruCare!',
    tourWelcomeDesc: 'Let\'s take a quick tour of your dashboard.',
    tourHealthScoreTitle: 'Health Score',
    tourHealthScoreDesc: 'See your personalized health score based on your profile.',
    tourQuickActionsTitle: 'Quick Actions',
    tourQuickActionsDesc: 'Quickly access key features from here.',
    tourNotificationsTitle: 'Notifications',
    tourNotificationsDesc: 'Stay updated with important notifications.',
    tourEducationTitle: 'Education',
    tourEducationDesc: 'Explore personalized educational content.',
    tourGetStarted: 'Get Started',
    tourNext: 'Next',
    tourBack: 'Back',
    tourStep: 'Step',

    // General
    loading: 'Loading…',
    error: 'Error',
    success: 'Success',
    save: 'Save',
    cancel: 'Cancel',
    yes: 'Yes',
    no: 'No',
    close: 'Close',
    confirm: 'Confirm',
    delete: 'Delete',
    edit: 'Edit',
    add: 'Add',
    remove: 'Remove',
    search: 'Search',
    filter: 'Filter',
    sort: 'Sort',
    week: 'Week',
    month: 'Month',
    year: 'Year',
  },
  sw: {
    // Navigation
    home: 'Nyumbani',
    getStarted: 'Anza Sasa',
    education: 'Elimu',
    startFree: 'Anza Bila Malipo',
    signIn: 'Ingia',
    signOut: 'Toka',

    // Landing Page
    heroTitle: 'Mwongozo Wako wa Kuzalisha bila Kusema',
    heroSubtitle: 'NuruCare hutoa mapendekezo ya kuzalisha bila kusema ya ushahidi uliyobadilika kulingana na profili yako ya afya, ilioundwa na miongozo ya WHO.',
    getStartedBtn: 'Anza Bila Malipo',
    learnMoreBtn: 'Jifunze Zaidi',
    problemTitle: 'Kuchagua makosa ya kujua lazima iwe rahisi',
    problemSubtitle: 'Watu wengi hupata shida kupata chaguzi za kuzalisha bila kusema ambazo zinaweza kufanya kazi kwao. NuruCare inarahisha hii na mwongozo wa kibinafsi.',
    howItWorksTitle: 'Jinsi Inavyofanya Kazi',
    howItWorksStep1: 'Kamilisha Profili Yako',
    howItWorksStep1Desc: 'Jibu maswali machache rahisi kuhusu afya yako na mapendekezo yako.',
    howItWorksStep2: 'Pata Mapendekezo ya Kibinafsi',
    howItWorksStep2Desc: 'AI yetu inachambua profili yako kwa kutumia miongozo ya WHO MEC.',
    howItWorksStep3: 'Jifunze na Uchague',
    howItWorksStep3Desc: 'Chunguza chaguzi zako na maudhui ya elimu na uamke ni nini bora kwako.',
    featuresTitle: 'Kwa Nini Kuchagua NuruCare?',
    featuresPersonalized: 'Mapendekezo ya Kibinafsi',
    featuresPersonalizedDesc: 'Yaliyobadilika kulingana na profili yako ya afya na mapendekezo yako.',
    featuresEvidence: 'Inategemea Ushahidi',
    featuresEvidenceDesc: 'Inatumia vigezo vya uwezo wa matibabu ya WHO.',
    featuresPrivacy: 'Usiri Kwanza',
    featuresPrivacyDesc: 'Data yako imewewa usiri na haitashirikiwa bila idhini.',
    featuresPartner: 'Usahihi wa Mwenyewe',
    featuresPartnerDesc: 'Shiriki profili yako na mwenyewe wako kwa ajili ya uamuzi wa kushirikiana.',
    faqTitle: 'Maswali Yanayoulizwa Mara kwa Mara',
    faq1Q: 'Je, NuruCare ni bure kutumia?',
    faq1A: 'Ndio, NuruCare ni bure kabisa kwa wote.',
    faq2Q: 'Je, data yangu ni salama?',
    faq2A: 'Hakika. Tunatumia usiri wa mazingira ya kuzungumzia na haitashiriki data yako bila idhini wazi.',
    faq3Q: 'Je, naweza kutumia NuruCare bila mwenyewe wangu?',
    faq3A: 'Ndio, NuruCare inafanya kazi vizuri kwa ajili ya matumizi ya kibinafsi pia.',
    testimonialsTitle: 'Machunguzi ya Watumiaji Wetu',
    footerTagline: 'Kutoa uwezo wa uamuzi wa afya wa kujua.',

    // Auth
    loginTitle: 'Karibu Tena',
    loginSubtitle: 'Ingia ili kuendelea safari yako na NuruCare',
    signupTitle: 'Unda Akaunti Yako',
    signupSubtitle: 'Jiunge na NuruCare kupata mapendekezo ya kuzalisha bila kusema ya kibinafsi',
    usernameLabel: 'Jina la Mtumiaji',
    emailLabel: 'Barua pepe',
    passwordLabel: 'Neno la Siri',
    fullNameLabel: 'Jina Kamili',
    consentLabel: 'Nakubali sera ya usiri na naidhini usindikaji wa data',
    alreadyHaveAccount: 'Tayari una akaunti?',
    dontHaveAccount: 'Huna akaunti?',
    signUpBtn: 'Jiunge',
    loginBtn: 'Ingia',
    roleLabel: 'Jukumu',
    genderLabel: 'Jinsia',
    institutionNameLabel: 'Jina la Taasisi',
    institutionAddressLabel: 'Anwani ya Taasisi',

    // Role Selection
    roleSelectionTitle: 'Chagua Jukumu Lako',
    patientRole: 'Mgonjwa',
    nurseRole: 'Muuguzi',
    patientRoleDesc: 'Pata mapendekezo ya kuzalisha bila kusema ya kibinafsi',
    nurseRoleDesc: 'Wasaidia wagonjwa na ushauri wa kuzalisha bila kusema',
    continueBtn: 'Endelea',

    // Intake
    intakeStep1Title: 'Karibu',
    intakeStep1Desc: 'Hebu kujua zaidi ili kutoa mapendekezo ya kibinafsi.',
    intakeStep2Title: 'Maelezo ya Kimsingi',
    intakeStep3Title: 'Profili ya Afya',
    intakeStep4Title: 'Historia ya Kuzalisha bila Kusema',
    intakeStep5Title: 'Mapendekezo',
    nextBtn: 'Endelea',
    backBtn: 'Nyuma',
    submitBtn: 'Wasilisha',
    skipBtn: 'Ruka',

    // Dashboard
    dashboardWelcome: 'Karibu tena',
    healthScore: 'Alama ya Afya',
    recentActivity: 'Shughuli za Hivi Karibuni',
    upcomingMilestones: 'Alama Zilizokuja',
    quickActions: 'Hatua Haraka',
    partnerSync: 'Usahihi wa Mwenyewe',
    dashboardEducation: 'Elimu',
    findProvider: 'Tafuta Mtoa Huduma',
    healthTrends: 'Mwenyewe wa Afya',
    notifications: 'Maarifa',
    markAllRead: 'Weka Yote kama Zilizosomwa',
    clearAll: 'Futa Yote',
    noNotifications: 'Hakuna maarifa',
    viewAll: 'Tazama Yote',

    // Education
    educationTitle: 'Rasilimali za Elimu',
    contraceptiveMethods: 'Njia za Kuzalisha bila Kusema',
    mythsAndFacts: 'Dhuluma na Ukweli',
    cycleTracking: 'Ufuatiliaji wa Mzunguko',
    vasectomyMyths: 'Dhuluma za Vasectomy',

    // Partner Sync
    partnerSyncTitle: 'Usahihi wa Mwenyewe',
    partnerSyncSubtitle: 'Shiriki uamuzi wa afya salama na mwenyewe wako kwa kutumia alama ya usahihi.',
    generateToken: 'Tengeneza Alama ya Usahihi wa Mwenyewe',
    generating: 'Inatengeneza…',
    tokenCopied: 'Alama imekopwa!',
    copyToken: 'Nakili Alama',
    copied: 'Imenakiliwa!',
    connectPartner: 'Ungana na Mwenyewe',
    enterToken: 'Ingiza alama ya usahihi ya mwenyewe wako (kwa mfano, NX-7K9-2M4)',
    connecting: 'Inaunganisha…',
    connectBtn: 'Ungana na Mwenyewe',
    partnerConnected: 'Mwenyewe Wangu Amekuwa Ungana!',
    partnerConnectedDesc: 'Sasa unaweza kutazama uamuzi wa afya wa kushirikiana pamoja.',
    tokenExpiresIn: 'Alama hii itakamilika katika',
    invalidToken: 'Alama batili',
    connectionFailed: 'Unganeshaji haujafanikiwa',

    // Onboarding Tour
    tourWelcomeTitle: 'Karibu NuruCare!',
    tourWelcomeDesc: 'Hebu tupe machozi ya haraka kwenye dashibodi yako.',
    tourHealthScoreTitle: 'Alama ya Afya',
    tourHealthScoreDesc: 'Ona alama yako ya afya ya kibinafsi kulingana na profili yako.',
    tourQuickActionsTitle: 'Hatua Haraka',
    tourQuickActionsDesc: 'Fikiria haraka vipengele vikuu kutoka hapa.',
    tourNotificationsTitle: 'Maarifa',
    tourNotificationsDesc: 'Endelea kuwa na maarifa na maarifa muhimu.',
    tourEducationTitle: 'Elimu',
    tourEducationDesc: 'Chunguza maudhui ya elimu ya kibinafsi.',
    tourGetStarted: 'Anza',
    tourNext: 'Endelea',
    tourBack: 'Nyuma',
    tourStep: 'Hatua',

    // General
    loading: 'Inapakia…',
    error: 'Hitilafu',
    success: 'Mafanikio',
    save: 'Hifadhi',
    cancel: 'Ghairi',
    yes: 'Ndio',
    no: 'Hapana',
    close: 'Funga',
    confirm: 'Thibitisha',
    delete: 'Futa',
    edit: 'Hariri',
    add: 'Ongeza',
    remove: 'Toa',
    search: 'Tafuta',
    filter: 'Chuja',
    sort: 'Panga',
    week: 'Wiki',
    month: 'Mwezi',
    year: 'Mwaka',
  },
};

const LanguageContext = createContext();

export const LanguageProvider = ({ children }) => {
  const [lang, setLang] = useState(localStorage.getItem('nurucare_lang') || 'en');

  // Update localStorage when language changes
  const updateLang = (newLang) => {
    setLang(newLang);
    localStorage.setItem('nurucare_lang', newLang);
  };

  const t = (key) => {
    return translations[lang]?.[key] || key;
  };

  const value = {
    lang,
    setLang: updateLang,
    t,
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLang = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLang must be used within a LanguageProvider');
  }
  return context;
};
