const cbor = require('cbor');

const data = { count: 5, duration: 1532908320173, duration_unit: 'min', activated_at: 1779457635 };
const encoded = cbor.encode(data);
console.log('Hex:', encoded.toString('hex'));
console.log('Buffer:', encoded)

const base64String = encoded.toString('base64');
console.log('Base64:', base64String);
