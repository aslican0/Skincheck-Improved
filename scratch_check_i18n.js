const fs = require('fs');

const app = fs.readFileSync('js/app.js', 'utf8');
const routine = fs.readFileSync('js/routine.js', 'utf8');
const i18n = fs.readFileSync('js/i18n.js', 'utf8');
const encyclopedia = fs.readFileSync('js/encyclopedia.js', 'utf8');

global.window = {};
global.document = { querySelectorAll: () => [], getElementById: () => null };
global.navigator = { language: 'tr' };
global.localStorage = { getItem: () => null, setItem: () => {} };
eval(i18n.replace('const I18N =', 'global.I18N ='));

// Check 1: What keys are in Turkish but not translated in other languages (German, French, Spanish, Russian, Arabic, Japanese, Korean, Chinese)?
const supported = Object.keys(I18N.supportedLanguages);
const trKeys = Object.keys(I18N.translations.tr);

console.log('--- Missing keys compared to Turkish ---');
supported.forEach(lang => {
  if (lang === 'tr') return;
  const missing = trKeys.filter(k => !I18N.translations[lang] || !(k in I18N.translations[lang]));
  console.log(`Lang ${lang} has ${Object.keys(I18N.translations[lang] || {}).length} keys. Missing from TR: ${missing.length}`);
  if (missing.length > 0) {
    console.log(`  Missing in ${lang}:`, missing);
  }
});

// Check 2: Check EN keys compared to TR
const enMissing = trKeys.filter(k => !(k in I18N.translations.en));
console.log('Missing in EN compared to TR:', enMissing);

// Check 3: Check how encyclopedia handles languages
eval(encyclopedia.replace('const ENCYCLOPEDIA =', 'global.ENCYCLOPEDIA ='));
console.log('--- Encyclopedia check ---');
if (global.ENCYCLOPEDIA && global.ENCYCLOPEDIA.ingredients) {
  const sample = global.ENCYCLOPEDIA.ingredients[0];
  console.log('Sample ingredient localized keys:', Object.keys(sample.name_localized || {}));
  console.log('Sample ingredient desc localized keys:', Object.keys(sample.desc || {}));
  console.log('Sample ingredient howToUse localized keys:', Object.keys(sample.howToUse || {}));
}

// Check 4: In app.js, where are things displayed that might be English?
// e.g. day names in schedule:
// 'dayMonday', 'dayTuesday', etc.
console.log('--- Checking routine step keys across languages ---');
const routineKeys = [
  'stepCleanser', 'stepWaterCleanser', 'stepOilCleanser', 'stepToner', 'stepSerum',
  'stepVitaminC', 'stepRetinol', 'stepNiacinamide', 'stepExfoliant', 'stepMoisturizer',
  'stepSPF', 'stepMask', 'categoryOther', 'stepTreatment', 'stepNightMoisturizer',
  'stepGelOrFoam', 'stepOilOrMicellar', 'descOilOrMicellar', 'descGelOrFoam',
  'descNightMoisturizer', 'descSPFGuidance', 'stepMorningCleanser',
  'descCleanserDry', 'descCleanserOily', 'descCleanserCombo', 'descCleanserSensitive',
  'descCleanserAcne', 'descCleanserNormal', 'descMoisturizerDry', 'descMoisturizerOily',
  'descMoisturizerCombo', 'descMoisturizerSensitive', 'descMoisturizerAcne', 'descMoisturizerNormal'
];

supported.forEach(lang => {
  const missingInLang = routineKeys.filter(k => !I18N.translations[lang] || !(k in I18N.translations[lang]));
  if (missingInLang.length > 0) {
    console.log(`Lang ${lang} missing ${missingInLang.length} routine keys:`, missingInLang);
  } else {
    console.log(`Lang ${lang} has ALL ${routineKeys.length} routine keys!`);
  }
});
