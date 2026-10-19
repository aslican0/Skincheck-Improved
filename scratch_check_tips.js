const fs = require('fs');
const i18n = fs.readFileSync('js/i18n.js', 'utf8');

global.window = {};
global.document = { querySelectorAll: () => [], getElementById: () => null };
global.navigator = { language: 'tr' };
global.localStorage = { getItem: () => null, setItem: () => {} };
eval(i18n.replace('const I18N =', 'global.I18N ='));

const tips = ['tipSunscreen', 'tipMoisturizeDamp', 'tipAvoidOverDrying', 'tipFocusTZone', 'tipPatchTest', 'tipDontPop'];
const supported = Object.keys(I18N.supportedLanguages);

supported.forEach(lang => {
  tips.forEach(t => {
    if (!I18N.translations[lang] || !I18N.translations[lang][t]) {
      console.log(`Lang ${lang} missing ${t}!`);
    }
  });
});
console.log('Tips check done.');
