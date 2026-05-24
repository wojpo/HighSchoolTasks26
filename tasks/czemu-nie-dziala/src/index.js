const express = require('express');

const app = express();
const PORT = 6969;

app.get('/', async (req, res) => {
  const isFromCloudflare = req.headers['cf-ray'] || req.headers['cf-connecting-ip'] || req.headers['cf-visitor'];
  const hasUserAgent = req.headers['user-agent'];

  if (isFromCloudflare) {
    res.status(418)
  } else if (hasUserAgent) {
    res.status(406)
    res.write("Your browser has been blocked due to security rules. Please try again later.")
  } else {
    res.write('hack4KrakCTF{n0-jak-N13-DzI@lA-J@k-prz3ciez-dz1alA}');
  }

  res.end();
})

app.listen(PORT, (err) => {
  if (err) {
    console.error(err)
  } else {
    console.log(`Listening on 0.0.0.0:${PORT}`)
  }
})
