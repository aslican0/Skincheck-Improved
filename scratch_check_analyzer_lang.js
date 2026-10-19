const fs = require('fs');

const i18n = fs.readFileSync('js/i18n.js', 'utf8');
const analyzer = fs.readFileSync('js/analyzer.js', 'utf8');
const encyclopedia = fs.readFileSync('js/encyclopedia.js', 'utf8');

global.window = {};
global.document = { querySelectorAll: () => [], getElementById: () => null };
global.navigator = { language: 'tr' };
global.localStorage = { getItem: () => null, setItem: () => {} };
eval(i18n.replace('const I18N =', 'global.I18N ='));
eval(encyclopedia.replace('const ENCYCLOPEDIA =', 'global.ENCYCLOPEDIA ='));
const database = fs.readFileSync('js/database.js', 'utf8');
eval(database.replace('const DATABASE =', 'global.DATABASE ='));
eval(analyzer.replace('const ANALYZER =', 'global.ANALYZER ='));

const sampleText = 'Aqua, Niacinamide, Glycerin, Salicylic Acid, Fragrance, Retinol';
const product = { name: 'Test Product', ingredientsText: sampleText };

['tr', 'en', 'de', 'fr', 'es', 'ru', 'ar', 'ja', 'ko', 'zh'].forEach(lang => {
  I18N.currentLang = lang;
  const res = ANALYZER.analyzeProduct(product);
  console.log(`\n=== Lang: ${lang} ===`);
  console.log('Overall summary title:', res.overallRecommendation?.title || res.overallTitle);
  console.log('Warnings count:', res.warnings.length);
  if (res.warnings.length > 0) {
    console.log('Warning 0 title:', res.warnings[0].title);
    console.log('Warning 0 desc:', res.warnings[0].desc);
  }
  if (res.ingredients.length > 0) {
    console.log('Ing 0 name:', res.ingredients[0].name);
    console.log('Ing 0 role:', res.ingredients[0].role);
    console.log('Ing 0 desc:', res.ingredients[0].desc);
  }
});
