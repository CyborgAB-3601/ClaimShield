// Static demo catalog of insurers + policy types + where-to-submit portal names.
// Purely cosmetic: selecting a value here does not change the extraction/audit
// pipeline, it just demonstrates that the product isn't hardcoded to one insurer.

export const INSURERS = [
  {
    id: 'hdfc',
    name: 'HDFC ERGO',
    portalName: 'HDFC ERGO customer portal (PHS App)',
    policyTypes: [
      'Optima Secure',
      'my:health Suraksha',
      'Health Suraksha Gold',
      'my:health Medisure Super Top-up',
      'Optima Restore',
    ],
  },
  {
    id: 'star',
    name: 'Star Health',
    portalName: 'Star Health customer portal (Star Health App)',
    policyTypes: [
      'Star Comprehensive Insurance Policy',
      'Family Health Optima Insurance Plan',
      'Senior Citizens Red Carpet Health Insurance Policy',
      'Star Cardiac Care Insurance Policy',
      'Star Cancer Care Platinum Insurance Policy',
      'Star Health Assure Insurance Policy',
    ],
  },
];
