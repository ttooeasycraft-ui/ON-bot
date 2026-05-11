function onFormSubmit(e) {
  var r = e.response.getItemResponses();
  var nick   = r[0].getResponse();
  var horas  = r[1].getResponse();
  var regras = r[2].getResponse();
  var mundo  = r[3].getResponse();
  var motivo = r[4].getResponse();

  var payload = JSON.stringify({
    secret: "clan-on-secret-2025",
    nick:   nick,
    horas:  horas,
    regras: regras,
    mundo:  mundo,
    motivo: motivo
  });

  UrlFetchApp.fetch(
    "https://worker-production-e527.up.railway.app/webhook/forms",
    {
      method: "post",
      contentType: "application/json",
      payload: payload,
      muteHttpExceptions: true
    }
  );
}
