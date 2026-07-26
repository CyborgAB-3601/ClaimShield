// Static, insurer-flavoured step list shown alongside the filled-form download.
// Cosmetic guidance only — no scraping/automation of the insurer's real portal.

const STEPS_TEMPLATE = {
  en: (portal) => [
    `Log in to the ${portal}.`,
    'Go to "Claims" → "Submit Reimbursement Claim".',
    'Select the policy and upload the filled claim form you just downloaded.',
    'Attach the discharge summary, itemised bill, and payment receipts.',
    'Enter your bank details for reimbursement and review the claimed amount.',
    'Submit and save the claim reference number for tracking.',
  ],
  hi: (portal) => [
    `${portal} में लॉग इन करें।`,
    '"Claims" → "Submit Reimbursement Claim" पर जाएं।',
    'पॉलिसी चुनें और अभी डाउनलोड किया गया भरा हुआ क्लेम फ़ॉर्म अपलोड करें।',
    'डिस्चार्ज सारांश, विस्तृत बिल और भुगतान रसीदें संलग्न करें।',
    'प्रतिपूर्ति के लिए अपने बैंक विवरण भरें और दावा राशि जांचें।',
    'सबमिट करें और ट्रैकिंग के लिए क्लेम संदर्भ संख्या सुरक्षित रखें।',
  ],
  ta: (portal) => [
    `${portal}-இல் உள்நுழையவும்.`,
    '"Claims" → "Submit Reimbursement Claim" க்கு செல்லவும்.',
    'பாலிசியைத் தேர்ந்தெடுத்து, இப்போது பதிவிறக்கிய நிரப்பப்பட்ட கோரிக்கை படிவத்தைப் பதிவேற்றவும்.',
    'டிஸ்சார்ஜ் சுருக்கம், விரிவான பில் மற்றும் கட்டண ரசீதுகளை இணைக்கவும்.',
    'திருப்பிச் செலுத்துவதற்கான வங்கி விவரங்களை உள்ளிட்டு கோரும் தொகையை சரிபார்க்கவும்.',
    'சமர்ப்பித்து, கண்காணிப்பிற்காக கோரிக்கை குறிப்பு எண்ணைச் சேமிக்கவும்.',
  ],
  te: (portal) => [
    `${portal}లో లాగిన్ అవ్వండి.`,
    '"Claims" → "Submit Reimbursement Claim"కి వెళ్లండి.',
    'పాలసీని ఎంచుకుని, ఇప్పుడే డౌన్‌లోడ్ చేసిన నింపిన క్లెయిమ్ ఫారాన్ని అప్‌లోడ్ చేయండి.',
    'డిశ్చార్జ్ సారాంశం, వివరణాత్మక బిల్లు మరియు చెల్లింపు రసీదులను జతచేయండి.',
    'రీయింబర్స్‌మెంట్ కోసం మీ బ్యాంక్ వివరాలు నమోదు చేసి క్లెయిమ్ మొత్తాన్ని సమీక్షించండి.',
    'సమర్పించి, ట్రాకింగ్ కోసం క్లెయిమ్ రిఫరెన్స్ నంబర్‌ను భద్రపరచుకోండి.',
  ],
  bn: (portal) => [
    `${portal}-এ লগ ইন করুন।`,
    '"Claims" → "Submit Reimbursement Claim"-এ যান।',
    'পলিসি নির্বাচন করুন এবং এইমাত্র ডাউনলোড করা পূরণকৃত ক্লেইম ফর্ম আপলোড করুন।',
    'ডিসচার্জ সারাংশ, বিস্তারিত বিল এবং পেমেন্ট রসিদ সংযুক্ত করুন।',
    'প্রতিপূরণের জন্য আপনার ব্যাংক বিবরণ দিন এবং দাবির পরিমাণ পর্যালোচনা করুন।',
    'জমা দিন এবং ট্র্যাকিংয়ের জন্য ক্লেইম রেফারেন্স নম্বর সংরক্ষণ করুন।',
  ],
  mr: (portal) => [
    `${portal} मध्ये लॉग इन करा.`,
    '"Claims" → "Submit Reimbursement Claim" वर जा.',
    'पॉलिसी निवडा आणि आत्ताच डाउनलोड केलेला भरलेला क्लेम फॉर्म अपलोड करा.',
    'डिस्चार्ज सारांश, तपशीलवार बिल आणि पेमेंट पावत्या जोडा.',
    'परतफेडीसाठी तुमचे बँक तपशील भरा आणि दाव्याची रक्कम तपासा.',
    'सबमिट करा आणि ट्रॅकिंगसाठी क्लेम संदर्भ क्रमांक जपून ठेवा.',
  ],
};

export function getSubmissionSteps(lang, portalName) {
  const build = STEPS_TEMPLATE[lang] || STEPS_TEMPLATE.en;
  return build(portalName);
}
