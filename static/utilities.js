const GLOBALS = {};

function oFromPairList(pairList) {
  const o = {};
  pairList.forEach((pair) => {
    o[pair[0]] = pair[1];
  });
  return o;
}

function parseCookie(rawCookie) {
  const entries = rawCookie.split('; ');
  const pairList = entries.
    map((s) => s.split('=')).
    filter((a) => a.length == 2).
    map((p) => [p[0], p[1].replace(/"/g,'')]);
  return oFromPairList(pairList);
}

function renderCookie(cookies) {
  return Object.entries(cookies).map(e => e.join('=')).join("; ");
}

function makeTable(table, data) {
  const thead = $('<thead/>');
  thead.append('<tr/>');
  const headrow = thead.find('tr');
  data.headers.forEach((header) => {
    const h = $('<th/>');
    h.html(header.html);
    headrow.append(h);
  });

  const tbody = $('<tbody/>');
  data.rows.forEach((row) => {
    const tr = $('<tr/>');
    tbody.append(tr);
    row.forEach((e) => {
      const td = $('<td/>');
      e.attr.forEach((attr) => {
        td.attr(attr.name, attr.value);
      });
      td.html(e.html);
      tr.append(td);
    });
  });

  table.empty();

  table.append(thead);
  table.append(tbody);
}

function parseTable(element) {
  return {
    headers: element.find('thead').find('th').toArray().map((h) => $(h).text()),

    rows: element.find('tbody').find('tr').toArray().map((r) => $(r))
      .map((r) => r.find('td').toArray().map((c) => $(c).text())),
  };
}

// return random int between 0 and n-1
function randInt(n) {
  return Math.floor(n * Math.random());
}

function randomString(n) {
  const chars = "ABCDEFGHJKMNPQRSTUVWXYZ0123456789";
  var s = "";
  for(var i = 0; i < n; i++) {
    s += chars[randInt(chars.length)];
  }
  return s;

}

async function betterFetch(f) {
  const response = await f;
  response.jsonBody = await response.json();
  return response;
}
async function postHTTPJSON(url, body) {
  return await betterFetch(fetch(url, {
    method: 'POST',
    body: JSON.stringify(body),
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: "include",
  }));
}

function alertElementFromResponse(response) {
  const e = $("<div>");
  e.attr("role", "alert");
  e.addClass("alert");
  e.addClass("alert-dismissible");
  e.addClass("fade");
  e.addClass("show");
  if (200 <= response.status && response.status < 300) {
    e.addClass("alert-success");
    e.text("Success!");
  } else if (400 <= response.status && response.status < 500) {
    e.addClass("alert-warning");
    e.text(response.jsonBody.message);
  } else if (500 <= response.status && response.status < 600) {
    e.addClass("alert-warning");
    e.text(response.jsonBody.message);
  // Defensive-else
  } else {
    e.addClass("alert-warning");
    e.text("We messed up, please email support and we'll help you out.");
  }
  return e;
}

function spinner() {
  const e = $("<div>");
  e.addClass("spinner-border");
  e.attr("role", "status");
  return e;
}
