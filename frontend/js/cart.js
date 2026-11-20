(() => {
  const MAX_ITEM_QUANTITY = 20;

  function findStoredToken(storage) {
    if (!storage) return "";

    const directKeys = [
      "uberate_session_id",
      "uberate_session",
      "uberate_token",
      "session_id",
      "sessionId",
      "session",
      "token",
      "access_token",
      "auth_token",
    ];

    for (const key of directKeys) {
      const val = storage.getItem(key);
      if (!val) continue;
      if (val.startsWith("{")) {
        try {
          const parsed = JSON.parse(val);
          const nested =
            parsed.session_id ||
            parsed.sessionId ||
            parsed.token ||
            parsed.access_token ||
            parsed.id;
          if (nested) return String(nested);
        } catch {
          // ignore non-JSON
        }
      } else {
        return val;
      }
    }

    for (let i = 0; i < storage.length; i++) {
      const key = storage.key(i);
      if (!key) continue;
      if (/session|token|auth/i.test(key)) {
        const val = storage.getItem(key);
        if (!val) continue;
        if (val.startsWith("{")) {
          try {
            const parsed = JSON.parse(val);
            const nested =
              parsed.session_id ||
              parsed.sessionId ||
              parsed.token ||
              parsed.access_token;
            if (nested) return String(nested);
          } catch {
            // ignore
          }
        } else {
          return val;
        }
      }
    }

    return "";
  }

  function getSessionToken() {
    if (typeof window.getSessionId === "function") {
      return window.getSessionId() || "";
    }
    return findStoredToken(window.localStorage) || findStoredToken(window.sessionStorage);
  }

  function formatMoney(amount) {
    const num = Number(amount || 0);
    return `$${num.toFixed(2)}`;
  }

  function ensureCartNavLink() {
    const nav = document.querySelector("nav");
    if (!nav) return;

    // Avoid duplicates if <a href="cart.html"> is already in the HTML
    if (nav.querySelector('a[href="cart.html"]')) return;

    const cartLink = document.createElement("a");
    cartLink.href = "cart.html";
    cartLink.innerHTML = 'Cart (<span id="nav-cart-count">0</span>)';

    // Place right before the Account link if account-nav.js already injected it
    const accountLink = nav.querySelector('a[href="account.html"]');
    if (accountLink) {
      nav.insertBefore(cartLink, accountLink);
    } else {
      nav.appendChild(cartLink);
    }
  }

  async function apiRequest(path, options = {}) {
    const token = getSessionToken();
    const headers = {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    };
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    const res = await fetch(path, {
      ...options,
      headers,
      credentials: "same-origin",
    });

    let data = null;
    try {
      data = await res.json();
    } catch {
      data = null;
    }

    if (!res.ok) {
      const detail =
        (data && (data.detail || data.message)) ||
        `Request failed (${res.status})`;
      const err = new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
      err.status = res.status;
      throw err;
    }
    return data;
  }

  function showAlert(message) {
    const el = document.getElementById("cart-alert");
    if (!el) return;
    if (!message) {
      el.textContent = "";
      el.classList.remove("visible");
      return;
    }
    el.textContent = message;
    el.classList.add("visible");
  }

  function updateNavCount(cart) {
    const badge = document.getElementById("nav-cart-count");
    if (!badge) return;
    const count = (cart?.items || []).reduce((sum, item) => sum + item.quantity, 0);
    badge.textContent = String(count);
  }

  function renderCart(cart) {
    updateNavCount(cart);

    const container = document.getElementById("cart-items-container");
    if (!container) return;

    const subtotalEl = document.getElementById("summary-subtotal");
    const deliveryEl = document.getElementById("summary-delivery");
    const totalEl = document.getElementById("summary-total");
    const clearBtn = document.getElementById("clear-cart-btn");
    const checkoutBtn = document.getElementById("checkout-btn");

    const items = cart?.items || [];

    subtotalEl.textContent = formatMoney(cart?.subtotal ?? 0);
    deliveryEl.textContent = formatMoney(cart?.delivery_fee ?? 0);
    totalEl.textContent = formatMoney(cart?.total ?? 0);

    if (items.length === 0) {
      clearBtn.hidden = true;
      checkoutBtn.disabled = true;
      container.innerHTML = `
        <div class="empty-state">
          <p><strong>Your cart is empty.</strong></p>
          <p>Browse restaurants and add dishes to start an order.</p>
          <a href="index.html">Browse Restaurants</a>
        </div>
      `;
      return;
    }

    clearBtn.hidden = false;
    checkoutBtn.disabled = false;
    container.innerHTML = "";

    for (const item of items) {
      const row = document.createElement("div");
      row.className = "cart-item";

      row.innerHTML = `
        <div>
          <p class="item-name"></p>
          <span class="item-unit">${formatMoney(item.unit_price)} each</span>
        </div>
        <div class="qty-controls">
          <button type="button" class="qty-dec" aria-label="Decrease quantity">−</button>
          <span class="qty-value">${item.quantity}</span>
          <button type="button" class="qty-inc" aria-label="Increase quantity" ${
            item.quantity >= MAX_ITEM_QUANTITY ? "disabled" : ""
          }>+</button>
        </div>
        <div class="line-total">${formatMoney(item.line_total)}</div>
        <button type="button" class="btn btn-ghost-danger remove-item">Remove</button>
      `;

      row.querySelector(".item-name").textContent = item.name;

      row.querySelector(".qty-dec").addEventListener("click", async () => {
        showAlert("");
        try {
          const updated =
            item.quantity <= 1
              ? await apiRequest(`/cart/items/${encodeURIComponent(item.menu_item_id)}`, {
                  method: "DELETE",
                })
              : await apiRequest(`/cart/items/${encodeURIComponent(item.menu_item_id)}`, {
                  method: "PATCH",
                  body: JSON.stringify({ quantity: item.quantity - 1 }),
                });
          renderCart(updated);
        } catch (err) {
          showAlert(err.message);
        }
      });

      row.querySelector(".qty-inc").addEventListener("click", async () => {
        if (item.quantity >= MAX_ITEM_QUANTITY) return;
        showAlert("");
        try {
          const updated = await apiRequest(
            `/cart/items/${encodeURIComponent(item.menu_item_id)}`,
            {
              method: "PATCH",
              body: JSON.stringify({ quantity: item.quantity + 1 }),
            }
          );
          renderCart(updated);
        } catch (err) {
          showAlert(err.message);
        }
      });

      row.querySelector(".remove-item").addEventListener("click", async () => {
        showAlert("");
        try {
          const updated = await apiRequest(
            `/cart/items/${encodeURIComponent(item.menu_item_id)}`,
            { method: "DELETE" }
          );
          renderCart(updated);
        } catch (err) {
          showAlert(err.message);
        }
      });

      container.appendChild(row);
    }
  }

  async function loadCart() {
    const isCartPage = Boolean(document.getElementById("cart-items-container"));
    if (isCartPage) showAlert("");

    // Skip API call if not signed in so non-cart pages stay clean
    if (!getSessionToken()) {
      if (isCartPage) {
        showAlert("Please sign in as a customer to view your cart.");
        renderCart({ items: [], subtotal: 0, delivery_fee: 0, total: 0 });
      } else {
        updateNavCount({ items: [] });
      }
      return;
    }

    try {
      const cart = await apiRequest("/cart", { method: "GET" });
      renderCart(cart);
    } catch (err) {
      if (isCartPage) {
        if (err.status === 401) {
          showAlert("Please sign in as a customer to view your cart.");
        } else {
          showAlert(err.message);
        }
        renderCart({ items: [], subtotal: 0, delivery_fee: 0, total: 0 });
      } else {
        updateNavCount({ items: [] });
      }
    }
  }

  async function addToCart(menuItemId, quantity = 1) {
    try {
      const updated = await apiRequest("/cart/items", {
        method: "POST",
        body: JSON.stringify({ menu_item_id: menuItemId, quantity }),
      });
      updateNavCount(updated);
      return updated;
    } catch (err) {
      if (err.status === 409) {
        const replace = window.confirm(
          "Your cart has items from another restaurant. Clear your current cart and add this item?"
        );
        if (!replace) return null;
        await apiRequest("/cart", { method: "DELETE" });
        const updated = await apiRequest("/cart/items", {
          method: "POST",
          body: JSON.stringify({ menu_item_id: menuItemId, quantity }),
        });
        updateNavCount(updated);
        return updated;
      }
      throw err;
    }
  }

  window.UberAteCart = { loadCart, addToCart, apiRequest };

  document.addEventListener("DOMContentLoaded", () => {
    ensureCartNavLink();

    const clearBtn = document.getElementById("clear-cart-btn");
    if (clearBtn) {
      clearBtn.addEventListener("click", async () => {
        showAlert("");
        try {
          const cleared = await apiRequest("/cart", { method: "DELETE" });
          renderCart(cleared);
        } catch (err) {
          showAlert(err.message);
        }
      });
    }

    loadCart();
  });
})();