async function renderUser(user) {
  GLOBALS.user = user;
}

function parseUser() {
  const user = GLOBALS.user;
  return user;
}

async function updatePassword() {
  await updateUserPassword($(".user-old-password").val(), $(".user-new-password").val());
}

function showHideNewPassword() {
  const element = $(".user-new-password");
  if (element.attr("type") === "text") {
    element.attr("type", "password");
  } else if (element.attr("type") === "password") {
    element.attr("type", "text");
  // This code shouldn't be reached, if it does, we decided to pick the safe route
  // by hiding the password
  } else {
    element.attr("type", "password");
  }
}

async function setup() {
  const cookie = parseCookie(document.cookie);
  if (!('token' in cookie)) {
    window.location.replace('/static/sign-in.html');
  }
  const user = await loadUser();
  renderUser(user);
}

setup();
