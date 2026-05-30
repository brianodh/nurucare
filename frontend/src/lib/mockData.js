export const mockRecommendations = {
  safe: [
    { name: 'Copper IUD', confidence: 95, description: 'Long-acting, hormone-free method. Effective for up to 12 years. Does not affect breastfeeding.', category: 'Long-acting' },
    { name: 'Hormonal Implant', confidence: 88, description: 'Small rod placed under the skin of the upper arm. Effective for 3-5 years with minimal maintenance.', category: 'Long-acting' },
    { name: 'Injectable (DMPA)', confidence: 82, description: 'Injection given every 3 months. Does not require daily action. May reduce menstrual cramps.', category: 'Short-acting' },
    { name: 'Progestin-Only Pill', confidence: 76, description: 'Daily pill without estrogen. Suitable for breastfeeding mothers and those with estrogen contraindications.', category: 'Short-acting' },
  ],
  restricted: [
    { name: 'Combined Oral Contraceptive', reason: 'Contains estrogen — may not be suitable based on your health profile.', severity: 'caution' },
    { name: 'Combined Patch', reason: 'Estrogen-based method. Restricted due to cardiovascular risk factors.', severity: 'restricted' },
  ],
  explanation: 'Based on your health profile, we recommend long-acting reversible contraceptives (LARCs) as your primary options. These methods have the highest effectiveness rates and require minimal ongoing action. The Copper IUD scored highest due to its hormone-free nature, which aligns well with your side effect preferences.',
  warnings: [
    'This is educational guidance only — please consult a healthcare provider before making any contraceptive decision.',
  ],
};

export const mockMythsFacts = [
  { myth: 'Emergency contraception (P2) causes infertility', fact: 'Emergency contraception does not cause infertility. It works by delaying ovulation and does not affect future fertility.', source: 'WHO 2023' },
  { myth: 'Withdrawal method is effective contraception', fact: 'Withdrawal has a typical-use failure rate of about 20%. It is significantly less effective than modern contraceptive methods.', source: 'WHO MEC' },
  { myth: 'The pill makes you gain a lot of weight', fact: 'Research shows minimal weight change with most hormonal contraceptives. Individual responses vary, but significant weight gain is uncommon.', source: 'Cochrane Review' },
  { myth: 'IUDs are only for women who have had children', fact: 'IUDs are safe and effective for women of all ages, including those who have never been pregnant. WHO recommends them as first-line options.', source: 'WHO 2023' },
  { myth: 'Contraceptives cause cancer', fact: 'Some contraceptives slightly reduce the risk of certain cancers (ovarian, endometrial). Any small increased risk for other types decreases after discontinuation.', source: 'IARC' },
  { myth: 'You need to take a break from the pill', fact: 'There is no medical reason to take a break from hormonal contraception. Continuous use is safe for most women.', source: 'ACOG' },
];

export const sideEffectTimeline = [
  { period: 'First 30 Days', title: 'Adjustment Phase', items: ['Spotting or irregular bleeding is common', 'Mild headaches may occur', 'Breast tenderness possible', 'Mood fluctuations as hormones adjust'], guidance: 'These are normal adjustment symptoms. Most resolve within 3 months. Stay hydrated and maintain regular sleep.' },
  { period: '30–60 Days', title: 'Stabilization', items: ['Bleeding patterns begin to regulate', 'Headaches typically diminish', 'Mood stabilizes for most users', 'Skin changes may appear (can improve or worsen acne)'], guidance: 'Your body is adapting. If symptoms persist or worsen, consider scheduling a follow-up with your provider.' },
  { period: '60–90 Days', title: 'Settled Phase', items: ['Most side effects have resolved', 'Menstrual pattern becomes predictable', 'Full contraceptive effectiveness established', 'Long-term benefits begin (reduced cramps, lighter periods)'], guidance: 'By now, most users feel comfortable with their method. If significant side effects persist, discuss alternatives with your provider.' },
];

export const mockNursePatients = [
  { id: 'SC-482901', age: 24, status: 'Active', riskLevel: 'Low', recommendation: 'Copper IUD', lastVisit: '2026-05-18' },
  { id: 'SC-371045', age: 32, status: 'Active', riskLevel: 'Medium', recommendation: 'Injectable', lastVisit: '2026-05-17' },
  { id: 'SC-559823', age: 19, status: 'Pending', riskLevel: 'Low', recommendation: 'Implant', lastVisit: '2026-05-16' },
  { id: 'SC-204716', age: 38, status: 'Flagged', riskLevel: 'High', recommendation: 'Restricted - COC', lastVisit: '2026-05-15' },
];

export const mockDashboardStats = {
  activeConsultations: 24,
  riskFlags: 3,
  dailySessions: 18,
  recommendationDistribution: [
    { name: 'IUD', value: 35 },
    { name: 'Implant', value: 28 },
    { name: 'Injectable', value: 20 },
    { name: 'POP', value: 12 },
    { name: 'Other', value: 5 },
  ],
  riskDistribution: [
    { name: 'Low', value: 65, fill: 'hsl(174, 52%, 46%)' },
    { name: 'Medium', value: 25, fill: 'hsl(43, 74%, 66%)' },
    { name: 'High', value: 10, fill: 'hsl(0, 72%, 55%)' },
  ],
  ageDemographics: [
    { range: '15-19', count: 15 },
    { range: '20-24', count: 32 },
    { range: '25-29', count: 28 },
    { range: '30-34', count: 18 },
    { range: '35-39', count: 12 },
    { range: '40+', count: 5 },
  ],
};