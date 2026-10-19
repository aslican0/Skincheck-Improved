const fs = require('fs');
const enc = fs.readFileSync('js/encyclopedia.js', 'utf8');
global.window = {};
eval(enc.replace('const ENCYCLOPEDIA =', 'global.ENCYCLOPEDIA ='));

let hasEnHowToOnly = 0;
let hasTrHowTo = 0;
global.ENCYCLOPEDIA.ingredients.forEach(i => {
  if (typeof i.howToUse === 'object') {
    if (i.howToUse.tr) hasTrHowTo++;
    if (!i.howToUse.tr && i.howToUse.en) hasEnHowToOnly++;
  } else if (typeof i.howToUse === 'string') {
    // string in what language?
  }
});
console.log('Total ingredients:', global.ENCYCLOPEDIA.ingredients.length);
console.log('Ingredients with TR howToUse:', hasTrHowTo);
console.log('Ingredients with only EN howToUse:', hasEnHowToOnly);

// Check sample ingredient howToUse
const sample = global.ENCYCLOPEDIA.ingredients.find(i => i.name.toLowerCase().includes('retinol') || i.name.toLowerCase().includes('salicylic') || i.name.toLowerCase().includes('hyaluronic'));
console.log('Retinol/Salicylic sample:', sample.name);
console.log('howToUse:', sample.howToUse);
console.log('frequency:', sample.frequency);
console.log('desc:', sample.desc);
