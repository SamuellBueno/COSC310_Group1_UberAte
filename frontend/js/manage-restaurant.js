document.getElementById("create-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const result = document.getElementById("result");
  const error = document.getElementById("error");
  result.textContent = "";
  error.textContent = "";

  const body = {
    name: document.getElementById("name").value.trim(),
    cuisine: document.getElementById("cuisine").value.trim(),
    address: document.getElementById("address").value.trim(),
    is_open: document.getElementById("is_open").checked,
  };

  try {
    const restaurant = await apiPost("/restaurants", body);
    result.textContent = `Created ${restaurant.name} with id ${restaurant.id}`;
    event.target.reset();
  } catch (err) {
    error.textContent = err.message;
  }
});

document.getElementById("edit-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const result = document.getElementById("edit-result");
  const error = document.getElementById("edit-error");
  result.textContent = "";
  error.textContent = "";

  const id = document.getElementById("edit-id").value.trim();
  const body = {};
  const name = document.getElementById("edit-name").value.trim();
  const cuisine = document.getElementById("edit-cuisine").value.trim();
  const address = document.getElementById("edit-address").value.trim();
  const isOpen = document.getElementById("edit-is_open").value;

  if (name) body.name = name;
  if (cuisine) body.cuisine = cuisine;
  if (address) body.address = address;
  if (isOpen) body.is_open = isOpen === "true";

  try {
    const restaurant = await apiPatch(`/restaurants/${id}`, body);
    result.textContent = `Updated ${restaurant.name} (${restaurant.id})`;
  } catch (err) {
    error.textContent = err.message;
  }
});