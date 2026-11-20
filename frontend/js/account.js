const profileForm = document.querySelector("#profile-form");
const accountDetails = document.querySelector("#account-details");
const accountStatus = document.querySelector("#account-status");
const accountError = document.querySelector("#account-error");
const signinLink = document.querySelector("#account-signin");
const signoutButton = document.querySelector("#signout");
const closeButton = document.querySelector("#close-account");
const editableFields = ["name", "phone", "delivery_address"];
let profile;

function showSignedOut(message) {
  accountDetails.hidden = true;
  signinLink.hidden = false;
  accountStatus.textContent = message;
}

function showAccount(user) {
  accountDetails.hidden = false;
  signinLink.hidden = true;

  const isCustomer = user.role === "customer";
  profileForm.hidden = !isCustomer;
  closeButton.hidden = !isCustomer;

  const identity = document.querySelector("#account-identity");
  identity.hidden = isCustomer;
  identity.textContent = `${user.name} (${user.email})`;

  if (isCustomer) {
    profile = user;
    for (const field of [...editableFields, "email"]) {
      profileForm.elements.namedItem(field).value = user[field] ?? "";
    }
  }
}

async function loadAccount() {
  if (!sessionStorage.getItem(SESSION_KEY)) {
    showSignedOut("You’re signed out.");
    return;
  }

  try {
    const user = await apiGet("/auth/me");
    const details = user.role === "customer"
      ? await apiGet("/customers/me")
      : user;

    showAccount(details);
    accountStatus.textContent = "";
  } catch (err) {
    if (err.status === 403) setSession(null);
    showSignedOut("Could not load your account.");
    accountError.textContent = err.message;
  }
}

async function runAccountAction(action) {
  accountError.textContent = "";
  accountStatus.textContent = "";

  const buttons = accountDetails.querySelectorAll("button");
  buttons.forEach((button) => { button.disabled = true; });

  try {
    await action();
  } catch (err) {
    accountError.textContent = err.message;
  } finally {
    buttons.forEach((button) => { button.disabled = false; });
  }
}

profileForm.addEventListener("submit", (event) => {
  event.preventDefault();

  runAccountAction(async () => {
    const changes = {};

    for (const field of editableFields) {
      const value = profileForm.elements.namedItem(field).value.trim();
      if (value !== (profile[field] ?? "")) changes[field] = value;
    }

    if (!Object.keys(changes).length) {
      accountStatus.textContent = "No changes to save.";
      return;
    }

    if (changes.delivery_address === "") {
      accountError.textContent = "Enter a delivery address to replace your current one.";
      return;
    }

    const saved = await apiPatch("/customers/me", changes);
    showAccount(saved);
    showAccountNav(saved);
    accountStatus.textContent = "Profile saved.";
  });
});

signoutButton.addEventListener("click", () => {
  runAccountAction(async () => {
    await apiPost("/auth/logout");
    setSession(null);
    showSignedOut("You’re signed out.");
  });
});

closeButton.addEventListener("click", () => {
  if (!window.confirm("Deactivate your account? You won’t be able to sign in again.")) {
    return;
  }

  runAccountAction(async () => {
    await apiDelete("/customers/me");
    setSession(null);
    showSignedOut("Your account was deactivated.");
  });
});

document.addEventListener("sessionchange", () => {
  if (!sessionStorage.getItem(SESSION_KEY)) showSignedOut("You’re signed out.");
});

loadAccount();