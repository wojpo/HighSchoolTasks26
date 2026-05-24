const express = require('express');

const app = express();
const PORT = 6969;

app.options('/', async (req, res) => {
  const isFromCloudflare = req.headers['cf-ray'] || req.headers['cf-connecting-ip'] || req.headers['cf-visitor'];
  const hasUserAgent = req.headers['user-agent'];
  const cors = !req.headers['origin']

  if (isFromCloudflare) {
    res.status(407)
  } else if (hasUserAgent) {
    res.status(406)
    res.write("Your device has been blocked due to security rules. Please try again later.")
  } else if (cors) {
      res.status(418)
      res.write("CORS are required")
  } else {
    return res.write('hack4KrakCTF{n0-jak-N13-DzI@lA-J@k-prz3ciez-dz1alA}');
  }

  res.end();
})

app.get('/', async (req, res) => {
  res.status(418)
  res.end()
})

app.listen(PORT, (err) => {
  if (err) {
    console.error(err)
  } else {
    console.log(`Listening on 0.0.0.0:${PORT}`)
  }
})
