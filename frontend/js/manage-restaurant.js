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