---
title: JS code test
date: 2026-08-18
---

```javascript
// Function to calculate a^b
function power(a, b) {
    let result = 1;
    
    for (let i = 0; i < b; i++) {
        result = result * a;
    }
    
    return result;
}

// Example usage
let base = 2;
let exponent = 5;
let result = power(base, exponent);

console.log(`${base}^${exponent} = ${result}`);
```
