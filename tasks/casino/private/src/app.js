const express = require('express')
const crypto = require('crypto')
const seedrandom = require('seedrandom')
const session = require('express-session')
let users = {}
let app = new express()
app.use(express.urlencoded( { extended: false }));
app.use(express.static("./static/"))
app.use(
    session({
      cookie: {
        httpOnly: true,
        maxAge: 1000 * 60 * 60 * 24 * 7,
      },
      resave: false,
      saveUninitialized: true,
      secret: crypto.randomBytes(32).toString("hex"),
    })
  );
app.post("/register", (req, res) => {
    let { username, password } = req.body;
    if (typeof username != "string" || typeof password != "string") {
        res.end("Nazwa uzytkownika i haslo musza byc tekstem")
        return
    }
    if(password.length < 8) {
        res.end("Haslo za krotkie! Musi miec co najmniej 8 znakow")
        return;
    }
    if(username.length < 4) {
        res.end("Nazwa uzytkownika za krotka! Musi miec co najmniej 4 znaki")
        return;
    }
    if (users[username]) {
        res.end("Uzytkownik juz istnieje!")
        return
    }
    users[username] = {
        username,
        password,
        balance: 1000,
        nonce: 0,
        serverSeed: crypto.randomBytes(32).toString("hex")
    }
    req.session.username = username
    res.redirect("home.html")
})
app.post("/login", (req, res) => {
    let { username, password } = req.body;
    if (typeof username != "string" || typeof password != "string") {
        res.end("Nazwa uzytkownika i haslo musza byc tekstem")
        return
    }
    if (users[username]?.password == password &&
        users[username]?.username == username
    ) {
        req.session.username = username
        res.redirect("home.html")
    } else {
        res.end("Nieprawidlowa nazwa uzytkownika/haslo!")
    }
})
app.use((req, res, next) => {
    if (!req.session.username) {
        res.json({ "error": "Brak autoryzacji" })
    } else {
        req.user = users[req.session.username];
        next()
    }
})
app.get("/signout", (req, res) => {
    delete req.session.username;
    res.redirect("/")
})
app.get("/info", (req, res) => {
    res.json({
        username: req.user.username,
        serverSeedHash: crypto.createHash("sha256").update(req.user.serverSeed).digest("hex"),
        balance: req.user.balance,
        nonce: req.user.nonce
    })
})
app.get("/flag", (req, res) => {
    if(req.user.balance > 1e9) {
        res.end(`Masz ogromne szczescie, oto twoja flaga: ${process.env.FLAG}`)
    } else {
        res.end("Potrzebujesz co najmniej 1000000000 $ zeby odkryc flage")
    }
})
app.post("/bet", async (req, res) => {
    let { clientSeed, guess, bet } = req.body;
    if (typeof clientSeed != "string" || clientSeed.length != 64 || !/^[\x20-\x7f]{64}$/.test(clientSeed)) {
        res.json({ "error": "Nieprawidlowy seed klienta!" })
        return
    }
    const validGuesses = ["1", "2", "3", "4", "5", "6"]
    if (typeof guess != "string" || !validGuesses.includes(guess)) {
        res.json({ "error": "Nieprawidlowy wybor!" })
        return
    }
    bet = parseInt(bet);
    if (!Number.isInteger(bet) || bet < 1 || bet > req.user.balance) {
        res.json({ "error": "Nieprawidlowa kwota zakladu!" })
        return
    }
    let nonce = req.user.nonce;
    let roll = (seedrandom(JSON.stringify({
        serverSeed: req.user.serverSeed,
        clientSeed,
        nonce
    })).int32() >>> 0) % 6 + 1
    await new Promise(resolve => setTimeout(resolve, 50));
    req.user.nonce = nonce + 1;
    if(guess == roll) {
        req.user.balance += 2 * bet;
    } else {
        req.user.balance -= bet;
    }
    res.json({
        roll,
        balance: req.user.balance,
        nonce: req.user.nonce
    })
});
app.listen(3000)
