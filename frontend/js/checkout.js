// checkout page: show the backend's cart total and send it back as expected_total,
// so a price change between "view cart" and "place order" is caught by the backend (409)

document.addEventListener("DOMContentLoaded", () => {
  const statusMessage = document.getElementById("status-message");
  const errorEl = document.getElementById("error");
  const content = document.getElementById("checkout-content");
  const restaurantName = document.getElementById("restaurant-name");
  const itemsList = document.getElementById("items-list");
  const totals = document.getElementById("totals");
  const placeOrderBtn = document.getElementById("place-order-btn");

  // the total the customer is looking at right now
  let seenTotal = null;

  function showError(message) {
    errorEl.textContent = message;
    errorEl.style.display = "block";
  }

  function clearError() {
    errorEl.textContent = "";
    errorEl.style.display = "none";
  }

  function renderCart(cart) {
    restaurantName.textContent = cart.restaurant_name ?? `Restaurant ${cart.restaurant_id}`;

    itemsList.replaceChildren();
    for (const item of cart.items) {
      const label = `${item.name} x${item.quantity}`;
      // lines the backend flags as not orderable are shown but marked
      const suffix = item.orderable === false ? " (no longer available)" : "";
      itemsList.append(makeRow(label + suffix, formatMoney(item.line_total)));
    }

    totals.replaceChildren(
      makeRow("Subtotal", formatMoney(cart.subtotal)),
      makeRow("Delivery", formatMoney(cart.delivery_fee)),
      makeRow("Total", formatMoney(cart.total), true),
    );
    seenTotal = cart.total;
  }

  async function loadCart() {
    try {
      const cart = await apiGet("/cart");
      if (!cart.items || cart.items.length === 0) {
        content.style.display = "none";
        statusMessage.textContent = "Your cart is empty. Add something from a menu first.";
        statusMessage.style.display = "block";
        return;
      }
      renderCart(cart);
      statusMessage.style.display = "none";
      content.style.display = "block";
    } catch (err) {
      content.style.display = "none";
      statusMessage.style.display = "none";
      // 404 = no active cart, 401 = not signed in, 403 = not a customer or deactivated
      showError(err.message);
    }
  }

  placeOrderBtn.addEventListener("click", async () => {
    clearError();
    placeOrderBtn.disabled = true;
    placeOrderBtn.textContent = "Placing order...";
    try {
      const order = await apiPost("/checkout", { expected_total: seenTotal });
      window.location.href = `orders.html?order_id=${encodeURIComponent(order.id)}`;
    } catch (err) {
      showError(err.message);
      placeOrderBtn.disabled = false;
      placeOrderBtn.textContent = "Place order";
      // 409: price or availability changed, reload so the customer sees the new total
      // (loadCart doesn't clear the error, so the message stays visible above the new numbers)
      if (err.status === 409) loadCart();
    }
  });

  loadCart();
});