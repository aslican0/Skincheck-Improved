const fs = require('fs');
const db = fs.readFileSync('js/database.js', 'utf8');
global.window = {};
eval(db.replace('const DATABASE =', 'global.DATABASE ='));

const functions = new Set();
if (global.DATABASE && global.DATABASE.ingredients) {
  Object.values(global.DATABASE.ingredients).forEach(i => {
    if (i.function) {
      i.function.split(/[,/]/).forEach(f => functions.add(f.trim()));
    }
  });
}
console.log('Total functions in DATABASE:', functions.size);
console.log('Functions list:', Array.from(functions).sort());
