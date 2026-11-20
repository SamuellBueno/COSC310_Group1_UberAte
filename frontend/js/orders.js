// orders page: orders.html shows my orders, orders.html?order_id=O2 shows one order

document.addEventListener("DOMContentLoaded", () => {
  const statusMessage = document.getElementById("status-message");
  const errorEl = document.getElementById("error");
  const container = document.getElementById("orders");
  const title = document.getElementById("title");
  const lede = document.getElementById("lede");

  function showError(message) {
    statusMessage.style.display = "none";
    errorEl.textContent = message;
    errorEl.style.display = "block";
  }

  // the stored order may call its timestamp created_at or placed_at
  function placedAt(order) {
    const value = order.created_at ?? order.placed_at;
    return value ? new Date(value).toLocaleString() : "";
  }

  function statusBadge(order) {
    const badge = document.createElement("span");
    badge.className = "item-status available";
    badge.textContent = order.status.charAt(0).toUpperCase() + order.status.slice(1);
    return badge;
  }

  // a short card for the list, click opens the full order
  function renderSummary(order) {
    const card = document.createElement("section");
    card.style.cursor = "pointer";
    card.addEventListener("click", () => {
      window.location.href = `orders.html?order_id=${encodeURIComponent(order.id)}`;
    });

    const header = document.createElement("div");
    header.style.cssText = "display:flex;justify-content:space-between;align-items:center;";
    const name = document.createElement("h3");
    name.textContent = `${order.restaurant_name} (order ${order.id})`;
    header.append(name, statusBadge(order));

    const meta = document.createElement("p");
    meta.textContent = `${order.items.length} item(s), placed ${placedAt(order)}`;

    card.append(header, meta, makeRow("Total", formatMoney(order.total), true));
    return card;
  }

  // the full order, every line is the snapshot taken at checkout
  function renderDetail(order) {
    title.textContent = `Order ${order.id}.`;
    lede.textContent = `${order.restaurant_name}, placed ${placedAt(order)}`;

    const card = document.createElement("section");
    card.append(statusBadge(order));
    if (order.delivery_address) {
      const address = document.createElement("p");
      address.textContent = `Delivering to: ${order.delivery_address}`;
      card.append(address);
    }
    for (const item of order.items) {
      const lineTotal = item.unit_price * item.quantity;
      card.append(makeRow(`${item.name} x${item.quantity} @ ${formatMoney(item.unit_price)}`, formatMoney(lineTotal)));
    }
    card.append(document.createElement("hr"));
    if (order.subtotal !== undefined) card.append(makeRow("Subtotal", formatMoney(order.subtotal)));
    if (order.delivery_fee !== undefined) card.append(makeRow("Delivery", formatMoney(order.delivery_fee)));
    card.append(makeRow("Total", formatMoney(order.total), true));

    const back = document.createElement("a");
    back.href = "orders.html";
    back.textContent = "Back to all orders";
    card.append(back);
    return card;
  }

  async function load() {
    const orderId = new URLSearchParams(window.location.search).get("order_id");
    try {
      if (orderId) {
        const order = await apiGet(`/orders/${encodeURIComponent(orderId)}`);
        statusMessage.style.display = "none";
        container.replaceChildren(renderDetail(order));
        return;
      }
      const orders = await apiGet("/orders");
      if (orders.length === 0) {
        statusMessage.textContent = "No orders yet.";
        return;
      }
      statusMessage.style.display = "none";
      container.replaceChildren(...orders.map(renderSummary));
    } catch (err) {
      // 401 not signed in, 403 not your order, 404 unknown order
      showError(err.message);
    }
  }

  load();
});