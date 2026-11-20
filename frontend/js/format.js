// small display helpers shared by checkout.js and orders.js, load after api.js

// money comes from the backend as a float, only formatting happens here
function formatMoney(value) {
  return `$${Number(value).toFixed(2)}`;
}

// one label/value row, used for lines and totals (textContent only, never innerHTML)
function makeRow(label, value, bold) {
  const row = document.createElement("div");
  row.style.cssText = "display:flex;justify-content:space-between;gap:1rem;padding:0.35rem 0;";
  if (bold) row.style.fontWeight = "800";
  const left = document.createElement("span");
  left.textContent = label;
  const right = document.createElement("span");
  right.textContent = value;
  row.append(left, right);
  return row;
}