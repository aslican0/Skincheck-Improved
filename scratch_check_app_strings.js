const fs = require('fs');

const app = fs.readFileSync('js/app.js', 'utf8');

// Find all HTML string templates in app.js
// Look for text between tags: >Some English Text< or placeholder="..."
const tagMatches = [...app.matchAll(/>\s*([A-Za-z][A-Za-z0-9 ,.?!':;\-\+]+)\s*</g)];
const englishPhrases = tagMatches
  .map(m => m[1].trim())
  .filter(t => t.length > 3 && /^[A-Za-z0-9 ,.?!':;\-\+]+$/.test(t) && !/^(div|span|button|class|style|true|false|undefined|null|id)$/i.test(t));

console.log('Total English text in tags:', englishPhrases.length);
console.log('Sample English phrases found in HTML in app.js:', [...new Set(englishPhrases)].slice(0, 40));

// Check template literals in app.js
const placeholderMatches = [...app.matchAll(/placeholder=["']([^"']+)["']/g)];
console.log('Placeholders:', [...new Set(placeholderMatches.map(m => m[1]))]);
