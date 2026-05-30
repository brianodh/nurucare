import React, { createContext, useContext, useState } from 'react';

export const translations = {
  en: {
    // ─── Navbar ─────────────────────────────────
    nav_home: 'Home',
    nav_get_started: 'Get Started',
    nav_education: 'Education',
    nav_start_free: 'Start Free',

    // ─── Hero ────────────────────────────────────
    hero_badge: 'Educational Decision Support',
    hero_h1_1: 'Your body.',
    hero_h1_2: 'Your choice.',
    hero_h1_3: 'Your journey.',
    hero_sub: 'SautiCare empowers African youth, women, and couples with personalized, science-backed contraceptive guidance — free from stigma, rooted in compassion.',
    hero_cta_start: 'Start Assessment',
    hero_cta_learn: 'Learn More',
    hero_privacy: 'Privacy-First',
    hero_who: 'WHO Guidelines',
    hero_card_title: 'Personalized Guidance',
    hero_card_sub: 'Based on your unique health profile',
    hero_card_safe: '✓ Safe for your profile',
    hero_card_who: 'Based on WHO medical eligibility criteria',

    // ─── Problem ─────────────────────────────────
    problem_label: 'The Challenge',
    problem_h2: 'Why contraceptive decisions are hard',
    problem_sub: 'Millions of African women face barriers to informed contraceptive choices every day.',
    problem_1_title: 'Misinformation',
    problem_1_desc: 'Myths and rumors about contraception spread faster than facts, especially on social media.',
    problem_2_title: 'Stigma & Shame',
    problem_2_desc: 'Cultural taboos prevent open conversations about reproductive health and family planning.',
    problem_3_title: 'Side Effect Fears',
    problem_3_desc: 'Unaddressed concerns about side effects lead to contraceptive discontinuation and unplanned pregnancies.',
    problem_4_title: 'Lack of Guidance',
    problem_4_desc: 'Limited access to trained healthcare providers leaves many without personalized contraceptive advice.',

    // ─── Features ────────────────────────────────
    features_label: 'Features',
    features_h2: 'Everything you need for informed choices',
    feature_1_title: 'Smart Recommendation Engine',
    feature_1_desc: 'AI-powered analysis of your health profile against WHO eligibility criteria for personalized guidance.',
    feature_2_title: 'Myth vs Fact Education',
    feature_2_desc: 'Evidence-based content that separates fiction from science, presented in culturally sensitive ways.',
    feature_3_title: 'Partner Sync',
    feature_3_desc: 'Anonymous, secure way for couples to share health decisions and build shared understanding.',
    feature_4_title: 'Privacy-First Consultations',
    feature_4_desc: 'Session-based access with expiring keys ensures your health data stays confidential and secure.',
    feature_5_title: 'Nurse Support Dashboard',
    feature_5_desc: 'Healthcare professionals get streamlined tools to support clients with data-driven insights.',
    feature_6_title: 'AI-Powered Guidance',
    feature_6_desc: 'Natural language explanations of recommendations help you understand the "why" behind each option.',

    // ─── How It Works ────────────────────────────
    how_label: 'How It Works',
    how_h2: 'Simple steps to clarity',
    step_1_title: 'Choose Your Role',
    step_1_desc: 'Select your profile — female client, male client, or healthcare professional.',
    step_2_title: 'Complete Assessment',
    step_2_desc: 'Answer guided health questions in a safe, judgment-free environment.',
    step_3_title: 'Get Recommendations',
    step_3_desc: 'Receive personalized, WHO-aligned contraceptive guidance with clear explanations.',
    step_4_title: 'Take Action',
    step_4_desc: 'Access educational resources, connect with your partner, or consult a nurse.',

    // ─── Testimonials ────────────────────────────
    testimonials_label: 'Testimonials',
    testimonials_h2: 'Voices of empowerment',
    t1_text: 'SautiCare helped me understand my options without judgment. I finally feel confident in my choice.',
    t1_role: 'Female Client',
    t2_text: 'The dashboard saves me hours. I can review patient profiles quickly and provide better-informed consultations.',
    t2_role: 'Healthcare Provider',
    t3_text: 'The Partner Sync feature opened up conversations we never knew how to start. We made the decision together.',
    t3_role: 'Couple',

    // ─── FAQ ─────────────────────────────────────
    faq_label: 'FAQ',
    faq_h2: 'Common questions',
    faq_1_q: 'Is SautiCare a medical diagnosis tool?',
    faq_1_a: 'No. SautiCare is an educational and decision-support platform. Our recommendations are based on WHO medical eligibility criteria but should not replace professional medical advice. Always consult a healthcare provider for medical decisions.',
    faq_2_q: 'How is my data protected?',
    faq_2_a: 'We use session-based access with expiring keys. Your health data is never permanently stored without your explicit consent. All consultations use anonymous identifiers.',
    faq_3_q: 'Can my partner see my health information?',
    faq_3_a: 'Only the information you explicitly choose to share through Partner Sync is visible. You control what gets shared through anonymous sync tokens.',
    faq_4_q: 'Who creates the recommendations?',
    faq_4_a: 'Our recommendation engine is built on WHO Medical Eligibility Criteria for Contraceptive Use (MEC), reviewed by reproductive health professionals.',
    faq_5_q: 'Is this service free?',
    faq_5_a: 'The core assessment, educational content, and recommendation features are free. Premium features like extended nurse consultations may have associated costs in the future.',
    faq_6_q: 'Can healthcare providers use SautiCare?',
    faq_6_a: 'Yes! Nurses and health experts have a dedicated dashboard to review patient profiles (with session-key access), view analytics, and provide data-driven consultations.',

    // ─── Role Selection ──────────────────────────
    roles_title: 'Welcome to SautiCare',
    roles_sub: 'Choose your role to get started with a personalized experience.',
    role_female_title: 'Female Client',
    role_female_desc: 'Get personalized contraceptive recommendations based on your unique health profile.',
    role_male_title: 'Male Client',
    role_male_desc: 'Explore male contraceptive options, support your partner, and access educational resources.',
    role_nurse_title: 'Nurse / Health Expert',
    role_nurse_desc: 'Access your professional dashboard to review patient sessions and provide guided consultations.',
    role_continue: 'Continue',

    // ─── Intake Form ─────────────────────────────
    intake_title: 'Health Assessment',
    intake_step_of: 'Step {n} of {total}',
    intake_step1: 'Basic Info',
    intake_step2: 'Health Metrics',
    intake_step3: 'Fertility Profile',
    intake_step4: 'Side Effects',
    intake_step5: 'Results',
    intake_back: 'Back',
    intake_next: 'Next',
    intake_learn_more: 'Learn More',
    intake_generate_key: 'Generate Session Key',
    intake_saving: 'Saving...',

    // Step 1
    s1_title: 'Basic Information',
    s1_sub: "Let's start with some basic details about you.",
    s1_age: 'Age',
    s1_age_placeholder: 'Enter your age',
    s1_relationship: 'Relationship Status',
    s1_rel_placeholder: 'Select status',
    s1_single: 'Single',
    s1_relationship_val: 'In a Relationship',
    s1_married: 'Married',
    s1_prefer_not: 'Prefer not to say',

    // Step 2
    s2_title: 'Clinical Health Metrics',
    s2_sub: 'This information helps us assess safety based on WHO criteria.',
    s2_bp: 'Blood Pressure',
    s2_systolic_ph: 'Systolic (e.g. 120)',
    s2_systolic_label: 'Systolic (top)',
    s2_diastolic_ph: 'Diastolic (e.g. 80)',
    s2_diastolic_label: 'Diastolic (bottom)',
    s2_smoking: 'Smoking Status',
    s2_smoking_sub: 'Do you currently smoke?',
    s2_migraine: 'Migraine History',
    s2_mig_none: 'No migraines',
    s2_mig_without: 'Migraine without aura',
    s2_mig_with: 'Migraine with aura',

    // Step 5 / Results
    s5_title: 'Your Recommendations',
    s5_sub: 'Based on your health profile and WHO medical eligibility criteria.',
    s5_risk_title: 'Critical Risk Flagged',
    s5_risk_aura: 'Migraine with aura significantly increases stroke risk with estrogen-based contraceptives.',
    s5_risk_smoke: 'Age over 35 combined with smoking increases cardiovascular risk with estrogen-based methods.',
    s5_restricted_label: 'Restricted: Estrogen-based contraceptives',
    s5_consult: 'Please consult a healthcare provider immediately.',
    s5_recommended: 'Recommended Methods',
    s5_restricted: 'Restricted Methods',
    s5_ai_label: 'AI Explanation',
    s5_disclaimer: 'This is educational guidance only — please consult a healthcare provider before making any contraceptive decision.',

    // ─── Session Key ─────────────────────────────
    session_title: 'Secure Session Key',
    session_sub: 'Share this key with your healthcare provider to access your health summary.',
    session_expires: 'Key expires after 15 minutes',
    session_once: 'One-time use only',
    session_anon: 'Your data stays anonymous',
    session_complete_first: 'Complete the health assessment first to get your session key.',
    session_remaining: 'remaining',
    session_copy: 'Copy Key',
    session_copied: 'Copied!',
    session_expired: 'Session key has expired',
    session_new: 'Complete a new assessment to generate a fresh key.',

    // ─── Partner Sync ────────────────────────────
    partner_title: 'Partner Sync',
    partner_sub: 'Securely share health decisions with your partner.',
    partner_generate_title: 'Generate Sync Token',
    partner_generating: 'Generating...',
    partner_generate_btn: 'Generate Anonymous Token',
    partner_copy: 'Copy Token',
    partner_copied: 'Copied!',
    partner_connect_title: 'Connect with Partner',
    partner_token_ph: "Enter partner's sync token (SC-XXXXXX)",
    partner_connect_btn: 'Connect',
    partner_connecting: 'Connecting...',
    partner_connected: 'Partner Connected!',
    partner_connected_sub: 'You can now view shared health decisions together.',
    partner_token_copied: 'Token copied!',
    partner_token_copied_sub: 'Share this with your partner.',
    partner_connected_toast: 'Partner connected!',
    partner_connected_toast_sub: 'You can now share health decisions together.',
    partner_not_found: 'Token not found',
    partner_not_found_sub: 'Check the token and try again.',

    // ─── Education ───────────────────────────────
    edu_label: 'Educational Resources',
    edu_title: 'Learn the Facts',
    edu_sub: 'Evidence-based education to support your reproductive health decisions.',
    edu_tab_myths: 'Myths vs Facts',
    edu_tab_timeline: 'Side Effect Timeline',
    edu_myth_prefix: 'Myth:',
    edu_fact_prefix: 'Fact:',

    // ─── Male Dashboard ──────────────────────────
    male_badge: 'Bro-Talk',
    male_title: 'Male Health Hub',
    male_sub: 'Your space for contraceptive education and partner support.',
    male_card1_title: 'Condom Guidance',
    male_card1_desc: 'Proper use increases effectiveness from 85% to 98%. Learn the correct steps.',
    male_card2_title: 'Fertility Window',
    male_card2_desc: "Understanding your partner's fertile window helps with shared planning.",
    male_card3_title: 'Male Clinical Trials',
    male_card3_desc: 'New male contraceptive methods are in development. Stay informed.',
    male_card4_title: 'Shared Responsibility',
    male_card4_desc: 'Contraception is a shared decision. Open communication builds trust.',
    male_partner_title: 'Partner Sync',
    male_partner_ph: "Enter partner's sync token",
    male_connect_btn: 'Connect',
    male_connected: 'Partner Connected',
    male_connected_sub: 'Shared health decisions are now accessible.',
    male_myths_title: 'Vasectomy: Myths vs Facts',
  },

  sw: {
    // ─── Navbar ─────────────────────────────────
    nav_home: 'Nyumbani',
    nav_get_started: 'Anza',
    nav_education: 'Elimu',
    nav_start_free: 'Anza Bure',

    // ─── Hero ────────────────────────────────────
    hero_badge: 'Msaada wa Maamuzi ya Elimu',
    hero_h1_1: 'Mwili wako.',
    hero_h1_2: 'Chaguo lako.',
    hero_h1_3: 'Safari yako.',
    hero_sub: 'SautiCare inawapa vijana wa Afrika, wanawake, na wanandoa mwongozo wa uzazi wa mpango unaobinafsishwa — bila unyanyapaa, umejengwa juu ya huruma.',
    hero_cta_start: 'Anza Tathmini',
    hero_cta_learn: 'Jifunze Zaidi',
    hero_privacy: 'Faragha Kwanza',
    hero_who: 'Mwongozo wa WHO',
    hero_card_title: 'Mwongozo Unaobinafsishwa',
    hero_card_sub: 'Kulingana na hali yako ya kipekee ya afya',
    hero_card_safe: '✓ Salama kwa hali yako',
    hero_card_who: 'Kulingana na vigezo vya kustahili dawa vya WHO',

    // ─── Problem ─────────────────────────────────
    problem_label: 'Changamoto',
    problem_h2: 'Kwa nini maamuzi ya uzazi wa mpango ni magumu',
    problem_sub: 'Mamilioni ya wanawake wa Afrika wanakabiliwa na vizuizi vya uchaguzi wa uzazi wa mpango kila siku.',
    problem_1_title: 'Taarifa Potofu',
    problem_1_desc: 'Hadithi na uvumi kuhusu uzazi wa mpango unasambaa haraka kuliko ukweli, hasa kwenye mitandao ya kijamii.',
    problem_2_title: 'Unyanyapaa & Aibu',
    problem_2_desc: 'Mwiko wa kijamii unazuia mazungumzo wazi kuhusu afya ya uzazi na upangaji wa familia.',
    problem_3_title: 'Hofu ya Madhara',
    problem_3_desc: 'Wasiwasi usioshughulikiwa kuhusu madhara husababisha kusimamisha uzazi wa mpango na mimba zisizotarajiwa.',
    problem_4_title: 'Ukosefu wa Mwongozo',
    problem_4_desc: 'Ufikiaji mdogo wa watoa huduma wa afya waliofunzwa unawaacha wengi bila ushauri binafsi wa uzazi wa mpango.',

    // ─── Features ────────────────────────────────
    features_label: 'Vipengele',
    features_h2: 'Kila unachohitaji kwa uchaguzi uliojulishwa',
    feature_1_title: 'Injini ya Mapendekezo Mahiri',
    feature_1_desc: 'Uchambuzi wa AI wa wasifu wako wa afya dhidi ya vigezo vya kustahili vya WHO kwa mwongozo unaobinafsishwa.',
    feature_2_title: 'Elimu ya Hadithi dhidi ya Ukweli',
    feature_2_desc: 'Maudhui yanayotegemea ushahidi yanayotenganisha uwongo na sayansi, yaliyowasilishwa kwa njia zinazozingatia utamaduni.',
    feature_3_title: 'Usawazishaji wa Mwenzi',
    feature_3_desc: 'Njia ya faragha na salama kwa wanandoa kushiriki maamuzi ya afya na kujenga uelewa wa pamoja.',
    feature_4_title: 'Mashauriano ya Faragha Kwanza',
    feature_4_desc: 'Ufikiaji unaotegemea kikao na funguo zinazokwisha muda unahakikisha data yako ya afya inabaki siri na salama.',
    feature_5_title: 'Dashibodi ya Msaada wa Muuguzi',
    feature_5_desc: 'Wataalamu wa afya wanapata zana zilizofupishwa kusaidia wateja kwa ufahamu unaotegemea data.',
    feature_6_title: 'Mwongozo wa AI',
    feature_6_desc: 'Maelezo ya lugha ya asili ya mapendekezo yanakusaidia kuelewa "kwa nini" nyuma ya kila chaguo.',

    // ─── How It Works ────────────────────────────
    how_label: 'Jinsi Inavyofanya Kazi',
    how_h2: 'Hatua rahisi za uwazi',
    step_1_title: 'Chagua Jukumu Lako',
    step_1_desc: 'Chagua wasifu wako — mteja wa kike, mteja wa kiume, au mtaalamu wa afya.',
    step_2_title: 'Kamilisha Tathmini',
    step_2_desc: 'Jibu maswali ya afya yanayoongozwa katika mazingira salama, yasiyohukumu.',
    step_3_title: 'Pata Mapendekezo',
    step_3_desc: 'Pokea mwongozo wa uzazi wa mpango unaobinafsishwa, unaolingana na WHO na maelezo wazi.',
    step_4_title: 'Chukua Hatua',
    step_4_desc: 'Fikia rasilimali za elimu, unganika na mwenzi wako, au wasiliana na muuguzi.',

    // ─── Testimonials ────────────────────────────
    testimonials_label: 'Ushuhuda',
    testimonials_h2: 'Sauti za uwezo',
    t1_text: 'SautiCare ilinisaidia kuelewa chaguo zangu bila hukumu. Hatimaye nahisi imara katika uamuzi wangu.',
    t1_role: 'Mteja wa Kike',
    t2_text: 'Dashibodi inaniokolea muda. Ninaweza kupitia wasifu wa wagonjwa haraka na kutoa mashauriano bora zaidi.',
    t2_role: 'Mtoa Huduma za Afya',
    t3_text: 'Kipengele cha Usawazishaji wa Mwenzi kilifungua mazungumzo ambayo hatukujua jinsi ya kuanza. Tulifanya uamuzi pamoja.',
    t3_role: 'Wanandoa',

    // ─── FAQ ─────────────────────────────────────
    faq_label: 'Maswali ya Kawaida',
    faq_h2: 'Maswali yanayoulizwa mara kwa mara',
    faq_1_q: 'Je, SautiCare ni zana ya utambuzi wa matibabu?',
    faq_1_a: 'Hapana. SautiCare ni jukwaa la elimu na msaada wa maamuzi. Mapendekezo yetu yanategemea vigezo vya kustahili dawa vya WHO lakini hayapaswi kuchukua nafasi ya ushauri wa kitaalamu wa matibabu. Daima wasiliana na mtoa huduma wa afya kwa maamuzi ya matibabu.',
    faq_2_q: 'Je, data yangu inalindwaje?',
    faq_2_a: 'Tunatumia ufikiaji unaotegemea kikao na funguo zinazokwisha muda. Data yako ya afya haiwekwi kudumu bila idhini yako wazi. Mashauriano yote yanatumia vitambulisho vya kujificha.',
    faq_3_q: 'Je, mwenzi wangu anaweza kuona maelezo yangu ya afya?',
    faq_3_a: 'Maelezo unayochagua kushiriki kupitia Usawazishaji wa Mwenzi peke yake ndiyo yanayoonekana. Wewe unachagua kinachoshirikiwa kupitia tokeni za kujificha za usawazishaji.',
    faq_4_q: 'Nani anatengeneza mapendekezo?',
    faq_4_a: 'Injini yetu ya mapendekezo imejengwa juu ya Vigezo vya Kustahili Dawa vya WHO kwa Matumizi ya Uzazi wa Mpango (MEC), iliyopitiwa na wataalamu wa afya ya uzazi.',
    faq_5_q: 'Je, huduma hii ni bure?',
    faq_5_a: 'Tathmini ya msingi, maudhui ya elimu, na vipengele vya mapendekezo ni bure. Vipengele vya malipo kama mashauriano ya muuguzi yaliyopanuliwa vinaweza kuwa na gharama zinazohusiana katika siku zijazo.',
    faq_6_q: 'Je, watoa huduma za afya wanaweza kutumia SautiCare?',
    faq_6_a: 'Ndiyo! Wauguzi na wataalamu wa afya wana dashibodi maalum ya kupitia wasifu wa wagonjwa (na ufikiaji wa funguo za kikao), kuona uchambuzi, na kutoa mashauriano yanayotegemea data.',

    // ─── Role Selection ──────────────────────────
    roles_title: 'Karibu SautiCare',
    roles_sub: 'Chagua jukumu lako kuanza uzoefu uliobinafsishwa.',
    role_female_title: 'Mteja wa Kike',
    role_female_desc: 'Pata mapendekezo ya uzazi wa mpango yaliyobinafsishwa kulingana na wasifu wako wa kipekee wa afya.',
    role_male_title: 'Mteja wa Kiume',
    role_male_desc: 'Chunguza chaguo za uzazi wa mpango za kiume, msaidie mwenzi wako, na ufikie rasilimali za elimu.',
    role_nurse_title: 'Muuguzi / Mtaalamu wa Afya',
    role_nurse_desc: 'Fikia dashibodi yako ya kitaalamu ili kupitia vikao vya wagonjwa na kutoa mashauriano yanayoongozwa.',
    role_continue: 'Endelea',

    // ─── Intake Form ─────────────────────────────
    intake_title: 'Tathmini ya Afya',
    intake_step_of: 'Hatua {n} kati ya {total}',
    intake_step1: 'Taarifa za Msingi',
    intake_step2: 'Vipimo vya Afya',
    intake_step3: 'Wasifu wa Uzazi',
    intake_step4: 'Madhara',
    intake_step5: 'Matokeo',
    intake_back: 'Rudi',
    intake_next: 'Endelea',
    intake_learn_more: 'Jifunze Zaidi',
    intake_generate_key: 'Tengeneza Ufunguo wa Kikao',
    intake_saving: 'Inahifadhi...',

    // Step 1
    s1_title: 'Taarifa za Msingi',
    s1_sub: 'Tuanze na maelezo ya msingi kukuhusu wewe.',
    s1_age: 'Umri',
    s1_age_placeholder: 'Ingiza umri wako',
    s1_relationship: 'Hali ya Uhusiano',
    s1_rel_placeholder: 'Chagua hali',
    s1_single: 'Mseja',
    s1_relationship_val: 'Nina Uhusiano',
    s1_married: 'Nimeolewa/Ameoa',
    s1_prefer_not: 'Nipendelea kutosema',

    // Step 2
    s2_title: 'Vipimo vya Afya ya Kliniki',
    s2_sub: 'Taarifa hii inatusaidia kutathmini usalama kulingana na vigezo vya WHO.',
    s2_bp: 'Shinikizo la Damu',
    s2_systolic_ph: 'Sistoli (k.m. 120)',
    s2_systolic_label: 'Sistoli (juu)',
    s2_diastolic_ph: 'Diastoli (k.m. 80)',
    s2_diastolic_label: 'Diastoli (chini)',
    s2_smoking: 'Hali ya Kuvuta Sigara',
    s2_smoking_sub: 'Je, unavuta sigara kwa sasa?',
    s2_migraine: 'Historia ya Maumivu ya Kichwa',
    s2_mig_none: 'Hakuna maumivu ya kichwa',
    s2_mig_without: 'Maumivu ya kichwa bila aura',
    s2_mig_with: 'Maumivu ya kichwa na aura',

    // Step 5 / Results
    s5_title: 'Mapendekezo Yako',
    s5_sub: 'Kulingana na wasifu wako wa afya na vigezo vya kustahili dawa vya WHO.',
    s5_risk_title: 'Hatari Kubwa Imegunduliwa',
    s5_risk_aura: 'Maumivu ya kichwa na aura huongeza sana hatari ya kiharusi na uzazi wa mpango unaotegemea estrojeni.',
    s5_risk_smoke: 'Umri zaidi ya miaka 35 pamoja na kuvuta sigara huongeza hatari ya moyo na mishipa na mbinu zinazotegemea estrojeni.',
    s5_restricted_label: 'Imezuiwa: Uzazi wa mpango wa estrojeni',
    s5_consult: 'Tafadhali wasiliana na mtoa huduma wa afya haraka iwezekanavyo.',
    s5_recommended: 'Mbinu Zinazopendekezwa',
    s5_restricted: 'Mbinu Zilizozuiwa',
    s5_ai_label: 'Maelezo ya AI',
    s5_disclaimer: 'Hii ni mwongozo wa elimu tu — tafadhali wasiliana na mtoa huduma wa afya kabla ya kufanya uamuzi wowote wa uzazi wa mpango.',

    // ─── Session Key ─────────────────────────────
    session_title: 'Ufunguo Salama wa Kikao',
    session_sub: 'Shiriki ufunguo huu na mtoa huduma wako wa afya ili kupata muhtasari wa afya yako.',
    session_expires: 'Ufunguo unaisha baada ya dakika 15',
    session_once: 'Matumizi ya mara moja tu',
    session_anon: 'Data yako inabaki bila jina',
    session_complete_first: 'Kamilisha tathmini ya afya kwanza kupata ufunguo wako wa kikao.',
    session_remaining: 'zimebaki',
    session_copy: 'Nakili Ufunguo',
    session_copied: 'Imenakiliwa!',
    session_expired: 'Ufunguo wa kikao umekwisha muda',
    session_new: 'Kamilisha tathmini mpya ili kutengeneza ufunguo mpya.',

    // ─── Partner Sync ────────────────────────────
    partner_title: 'Usawazishaji wa Mwenzi',
    partner_sub: 'Shiriki maamuzi ya afya salama na mwenzi wako.',
    partner_generate_title: 'Tengeneza Tokeni ya Usawazishaji',
    partner_generating: 'Inatengeneza...',
    partner_generate_btn: 'Tengeneza Tokeni bila Jina',
    partner_copy: 'Nakili Tokeni',
    partner_copied: 'Imenakiliwa!',
    partner_connect_title: 'Unganika na Mwenzi',
    partner_token_ph: 'Ingiza tokeni ya mwenzi wako (SC-XXXXXX)',
    partner_connect_btn: 'Unganika',
    partner_connecting: 'Inaunganika...',
    partner_connected: 'Mwenzi Ameunganishwa!',
    partner_connected_sub: 'Sasa unaweza kuona maamuzi ya pamoja ya afya.',
    partner_token_copied: 'Tokeni imenakiliwa!',
    partner_token_copied_sub: 'Shiriki hii na mwenzi wako.',
    partner_connected_toast: 'Mwenzi ameunganishwa!',
    partner_connected_toast_sub: 'Sasa mnaweza kushiriki maamuzi ya afya pamoja.',
    partner_not_found: 'Tokeni haikupatikana',
    partner_not_found_sub: 'Angalia tokeni na ujaribu tena.',

    // ─── Education ───────────────────────────────
    edu_label: 'Rasilimali za Elimu',
    edu_title: 'Jifunze Ukweli',
    edu_sub: 'Elimu inayotegemea ushahidi kusaidia maamuzi yako ya afya ya uzazi.',
    edu_tab_myths: 'Hadithi dhidi ya Ukweli',
    edu_tab_timeline: 'Ratiba ya Madhara',
    edu_myth_prefix: 'Hadithi:',
    edu_fact_prefix: 'Ukweli:',

    // ─── Male Dashboard ──────────────────────────
    male_badge: 'Mazungumzo ya Wanaume',
    male_title: 'Kituo cha Afya ya Kiume',
    male_sub: 'Nafasi yako ya elimu ya uzazi wa mpango na msaada wa mwenzi.',
    male_card1_title: 'Mwongozo wa Kondom',
    male_card1_desc: 'Matumizi sahihi huongeza ufanisi kutoka 85% hadi 98%. Jifunze hatua sahihi.',
    male_card2_title: 'Dirisha la Uzazi',
    male_card2_desc: 'Kuelewa dirisha la uzazi la mwenzi wako husaidia upangaji wa pamoja.',
    male_card3_title: 'Majaribio ya Kliniki ya Kiume',
    male_card3_desc: 'Mbinu mpya za uzazi wa mpango za kiume zinaendelezwa. Baki umefahamishwa.',
    male_card4_title: 'Jukumu la Pamoja',
    male_card4_desc: 'Uzazi wa mpango ni uamuzi wa pamoja. Mawasiliano ya wazi hujenga uaminifu.',
    male_partner_title: 'Usawazishaji wa Mwenzi',
    male_partner_ph: 'Ingiza tokeni ya usawazishaji ya mwenzi wako',
    male_connect_btn: 'Unganika',
    male_connected: 'Mwenzi Ameunganishwa',
    male_connected_sub: 'Maamuzi ya pamoja ya afya sasa yanapatikana.',
    male_myths_title: 'Vasektomi: Hadithi dhidi ya Ukweli',
  },
};


// ─── 🚀 THE MISSING CODE BASE44 EXPECTS ───────────────────

// 1. Create the React Context
const LanguageContext = createContext(null);

// 2. Create the Provider Component to wrap around your app (usually in App.jsx or main.jsx)
export function LanguageProvider({ children }) {
  const [lang, setLang] = useState('en');

  // Translation helper function
  const t = (key) => {
    return translations[lang]?.[key] || translations['en']?.[key] || key;
  };

  return (
    <LanguageContext.Provider value={{ lang, setLang, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

// 3. Create and export the useLang hook that LanguageSwitcher.jsx is looking for
export function useLang() {
  const context = useContext(LanguageContext);
  return context; // Will return { lang, setLang, t }
}
