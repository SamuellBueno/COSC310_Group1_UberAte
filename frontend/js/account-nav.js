const accountNavLink = document.createElement("a");
document.querySelector("nav").append(accountNavLink);

function showAccountNav(user) {
    accountNavLink.href = user ? "account.html" : "signin.html";
    accountNavLink.textContent = user ? `Account (${user.name})` : "Sign in";
}

async function refreshAccountNav() {
    const sessionId = sessionStorage.getItem(SESSION_KEY);
    if (!sessionId) {
        showAccountNav(null);
        return;
    }

    try {
        const user = await apiGet("/auth/me");
        if (sessionStorage.getItem(SESSION_KEY) === sessionId) showAccountNav(user);
    } catch {
        if (sessionStorage.getItem(SESSION_KEY) === sessionId) showAccountNav(null);
}
}

document.addEventListener("sessionchange", refreshAccountNav);
showAccountNav(null);
refreshAccountNav();