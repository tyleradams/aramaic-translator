async function loadUser() {
  return betterFetch(fetch('/user')).then(r => r.jsonBody);
}

async function patchUser(new_attributes) {
  return await betterFetch(fetch('/user', {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(new_attributes),
  }));
}

async function userSignIn(credentials) {
  const r = await postHTTPJSON("/user/sign-in", credentials);
  if (r.status == 200) {
    const cookies = {
      token: r.jsonBody.token,
      path: "/",
    }
    document.cookie = renderCookie(cookies);


    location.href='/static/dashboard.html';
  } else {
    $(".message--container").empty();
    $(".message--container").append(alertElementFromResponse(r));
  }
}
