fetch("/info").then(a=>a.json()).then(result =>{
    if(result.error) {
        window.location = "/"
        return;
    }
    balance.innerText = `Saldo: $ ${result.balance}`
    username.innerText = `Witaj ${result.username},`
    nonce.innerText = result.nonce
    serverSeedHash.innerText = result.serverSeedHash
})
