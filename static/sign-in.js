async function setup() {
  const cookie = parseCookie(document.cookie);
  if ('token' in cookie) {
    location.href = '/static/dashboard.html';
  }
}

setup();
