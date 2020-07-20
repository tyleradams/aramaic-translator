$('.js-click-logout').on('click', () => {
  const cookies = parseCookie(document.cookie);
  if (Object.keys(cookies).length >= 1) {
    cookies.expires="Thu, 01 Jan 1970 00:00:00 UTC";
    cookies.path="/";
    document.cookie = renderCookie(cookies);
  }
  location.href='/static/sign-in.html';
});

$('.js-click-update-user').on('click', () => {
  patchUser(parseUser()).then(r => {
    return loadUser();
  }).then(user => {
    renderUser(user);
  });
});

$('.js-click-update-email').on('click', () => {
  patchUser({
    email: $('.input-email').val()
  }).then( r => {
    $(".message--container").empty();
    $(".message--container").append(alertElementFromResponse(r));
  });
});

$('.js-click-update-password').on('click', () => {
  postHTTPJSON("/user/update-password", {
    oldPassword: $('.user-old-password').val(),
    newPassword: $('.user-new-password').val(),
  }).then( r => {
    $(".message--container").empty();
    $(".message--container").append(alertElementFromResponse(r));
  });
});

$('.js-click-toggle-showable-password').on('click', () => {
  const inputElement = $('.showable-password--input');
  const imgElement = $('.showable-password--img');

  if (inputElement.attr('type') === 'password') {
    inputElement.attr('type', 'text');
    imgElement.attr('src', '/static/icons/eye-slash-fill.svg');
  } else if (inputElement.attr('type') === 'text') {
    inputElement.attr('type', 'password');
    imgElement.attr('src', '/static/icons/eye-fill.svg');
  // This shouldn't happen, but if it does, play it safe
  } else {
    inputElement.attr('type', 'password');
    imgElement.attr('src', '/static/icons/eye-fill.svg');
  }
});

$('.js-click-user-signup').on('click', () => {
  attributes = {
    email: $(".user-signup--email-input").val(),
    password: $(".user-signup--password-input").val(),
    token: randomString(12),
  };

  postHTTPJSON("/user", attributes);

  userSignIn({
    email: attributes.email,
    password: attributes.password
  });
});

$('.js-click-user-sign-in').on('click', () => {
  userSignIn({
    email: $(".user-sign-in--input-email").val(),
    password: $(".user-sign-in--input-password").val(),
  });
});
