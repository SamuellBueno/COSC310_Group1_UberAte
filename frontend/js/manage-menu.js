const createMenuForm = document.getElementById("menu-create-form");
const editMenuForm = document.getElementById("menu-edit-form");
const createRestaurantSelect = document.getElementById("menu-restaurant");
const editRestaurantSelect = document.getElementById("menu-edit-restaurant");
const editItemSelect = document.getElementById("menu-edit-item");
const editFields = [
  document.getElementById("menu-edit-name"),
  document.getElementById("menu-edit-description"),
  document.getElementById("menu-edit-category"),
  document.getElementById("menu-edit-price"),
  document.getElementById("menu-edit-available"),
];
let menuItems = [];

function setMessage(id, message) {
  document.getElementById(id).textContent = message;
}

function addRestaurantOptions(restaurants) {
  [createRestaurantSelect, editRestaurantSelect].forEach((select) => {
    select.innerHTML = '<option value="">-- Choose a Restaurant --</option>';
    restaurants.forEach((restaurant) => {
      const option = document.createElement("option");
      option.value = restaurant.id;
      option.textContent = restaurant.name;
      select.appendChild(option);
    });
  });
}

async function loadRestaurantsForMenuForms() {
  try {
    const restaurants = await apiGet("/restaurants");
    addRestaurantOptions(restaurants);
  } catch (err) {
    setMessage("menu-create-error", `Unable to load restaurants: ${err.message}`);
    setMessage("menu-edit-error", `Unable to load restaurants: ${err.message}`);
  }
}

function setEditFieldsEnabled(enabled) {
  editFields.forEach((field) => {
    field.disabled = !enabled;
  });
  document.getElementById("menu-edit-submit").disabled = !enabled;
}

function showSelectedItem() {
  const item = menuItems.find((candidate) => candidate.id === editItemSelect.value);
  setEditFieldsEnabled(Boolean(item));
  if (!item) {
    return;
  }

  document.getElementById("menu-edit-name").value = item.name;
  document.getElementById("menu-edit-description").value = item.description || "";
  document.getElementById("menu-edit-category").value = item.category;
  document.getElementById("menu-edit-price").value = item.price;
  document.getElementById("menu-edit-available").checked = item.available;
}

async function loadMenuItems(restaurantId) {
  editItemSelect.innerHTML = '<option value="">-- Choose a menu item --</option>';
  menuItems = [];
  setEditFieldsEnabled(false);
  if (!restaurantId) {
    return;
  }

  try {
    menuItems = await apiGet(`/restaurants/${encodeURIComponent(restaurantId)}/menu-items`);
    menuItems.forEach((item) => {
      const option = document.createElement("option");
      option.value = item.id;
      option.textContent = item.name;
      editItemSelect.appendChild(option);
    });
    editItemSelect.disabled = false;
    if (menuItems.length === 0) {
      setMessage("menu-edit-error", "This restaurant has no menu items to edit.");
    } else {
      setMessage("menu-edit-error", "");
    }
  } catch (err) {
    setMessage("menu-edit-error", `Unable to load menu items: ${err.message}`);
  }
}

createMenuForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setMessage("menu-create-result", "");
  setMessage("menu-create-error", "");

  const restaurantId = createRestaurantSelect.value;
  const body = {
    name: document.getElementById("menu-name").value.trim(),
    description: document.getElementById("menu-description").value.trim(),
    category: document.getElementById("menu-category").value.trim(),
    price: Number(document.getElementById("menu-price").value),
    available: document.getElementById("menu-available").checked,
  };

  try {
    const item = await apiPost(`/restaurants/${encodeURIComponent(restaurantId)}/menu-items`, body);
    setMessage("menu-create-result", `Created ${item.name}.`);
    createMenuForm.reset();
    document.getElementById("menu-available").checked = true;
  } catch (err) {
    setMessage("menu-create-error", err.message);
  }
});

editRestaurantSelect.addEventListener("change", () => {
  setMessage("menu-edit-result", "");
  setMessage("menu-edit-error", "");
  loadMenuItems(editRestaurantSelect.value);
});

editItemSelect.addEventListener("change", () => {
  setMessage("menu-edit-result", "");
  setMessage("menu-edit-error", "");
  showSelectedItem();
});

editMenuForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setMessage("menu-edit-result", "");
  setMessage("menu-edit-error", "");

  const body = {
    name: document.getElementById("menu-edit-name").value.trim(),
    description: document.getElementById("menu-edit-description").value.trim(),
    category: document.getElementById("menu-edit-category").value.trim(),
    price: Number(document.getElementById("menu-edit-price").value),
    available: document.getElementById("menu-edit-available").checked,
  };

  try {
    const item = await apiPatch(`/menu-items/${encodeURIComponent(editItemSelect.value)}`, body);
    setMessage("menu-edit-result", `Updated ${item.name}.`);
    await loadMenuItems(editRestaurantSelect.value);
    editItemSelect.value = item.id;
    showSelectedItem();
  } catch (err) {
    setMessage("menu-edit-error", err.message);
  }
});

loadRestaurantsForMenuForms();
