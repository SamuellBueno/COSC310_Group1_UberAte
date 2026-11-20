const signinForm = document.querySelector("#signin-form");
const registerForm = document.querySelector("#register-form");

signinForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const error = document.querySelector("#signin-error");
  const button = signinForm.querySelector("button");
  error.textContent = "";
  button.disabled = true;

  try {
    const credentials = Object.fromEntries(new FormData(signinForm));
    const login = await apiPost("/auth/login", credentials);
    setSession(login.session_id);
    location.assign("account.html");
  } catch (err) {
    error.textContent = err.message;
  } finally {
    button.disabled = false;
  }
});

registerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const error = document.querySelector("#register-error");
  const status = document.querySelector("#register-status");
  const button = registerForm.querySelector("button");
  error.textContent = "";
  status.textContent = "";
  button.disabled = true;

  try {
    const details = Object.fromEntries(new FormData(registerForm));
    if (!details.phone.trim()) delete details.phone;
    if (!details.delivery_address.trim()) delete details.delivery_address;

    const user = await apiPost("/auth/register", details);
    registerForm.reset();
    signinForm.elements.email.value = user.email;
    signinForm.elements.password.value = "";
    status.textContent = "Account created. You can sign in now.";
    signinForm.elements.password.focus();
  } catch (err) {
    error.textContent = err.message;
  } finally {
    button.disabled = false;
  }
});