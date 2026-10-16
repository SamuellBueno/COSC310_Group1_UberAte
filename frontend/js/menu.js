document.addEventListener("DOMContentLoaded", () => {
  const restaurantSelect = document.getElementById("restaurant-select");
  const menuContainer = document.getElementById("menu-items");
  const statusMessage = document.getElementById("status-message");

  // Load all restaurants to populate the dropdown
  async function loadRestaurants() {
    try {
      const response = await fetch("/restaurants");
      if (!response.ok) {
        throw new Error("Failed to load restaurants");
      }
      const restaurants = await response.json();

      restaurants.forEach((restaurant) => {
        const option = document.createElement("option");
        option.value = restaurant.id;
        option.textContent = restaurant.name;
        restaurantSelect.appendChild(option);
      });
      const restaurantId = new URLSearchParams(window.location.search).get("id");

      if (restaurantId) {
        restaurantSelect.value = restaurantId;
        await loadMenu(restaurantId);
      }
    } catch (err) {
      statusMessage.textContent = "Error loading restaurants. Please try again later.";
      statusMessage.style.display = "block";
    }
  }

  // Load and render menu items for the chosen restaurant
  async function loadMenu(restaurantId) {
    if (!restaurantId) {
      menuContainer.innerHTML = "";
      statusMessage.textContent = "Please select a restaurant to view its menu.";
      statusMessage.style.display = "block";
      return;
    }

    try {
      const response = await fetch(`/restaurants/${restaurantId}/menu-items`);
      if (!response.ok) {
        throw new Error("Failed to load menu items");
      }
      const items = await response.json();

      menuContainer.innerHTML = "";

      if (items.length === 0) {
        statusMessage.textContent = "No menu items available for this restaurant.";
        statusMessage.style.display = "block";
        return;
      }

      statusMessage.style.display = "none";

      // Group items by category
      const grouped = items.reduce((acc, item) => {
        acc[item.category] = acc[item.category] || [];
        acc[item.category].push(item);
        return acc;
      }, {});

      // Render each category section
      Object.entries(grouped).forEach(([category, categoryItems]) => {
        const section = document.createElement("section");
        section.className = "category-section";

        const title = document.createElement("h2");
        title.className = "category-title";
        title.textContent = category;
        section.appendChild(title);

        categoryItems.forEach((item) => {
          const card = document.createElement("div");
          card.className = "item-card";

          const header = document.createElement("div");
          header.className = "item-header";

          const name = document.createElement("h3");
          name.className = "item-name";
          name.textContent = item.name;

          const price = document.createElement("span");
          price.className = "item-price";
          price.textContent = `$${item.price.toFixed(2)}`;

          header.appendChild(name);
          header.appendChild(price);
          card.appendChild(header);

          if (item.description) {
            const desc = document.createElement("p");
            desc.className = "item-desc";
            desc.textContent = item.description;
            card.appendChild(desc);
          }

          const status = document.createElement("span");
          status.className = `item-status ${item.available ? "available" : "unavailable"}`;
          status.textContent = item.available ? "Available" : "Unavailable";
          card.appendChild(status);

          section.appendChild(card);
        });

        menuContainer.appendChild(section);
      });
    } catch (err) {
      menuContainer.innerHTML = "";
      statusMessage.textContent = "Error loading menu items.";
      statusMessage.style.display = "block";
    }
  }

  restaurantSelect.addEventListener("change", (e) => {
    loadMenu(e.target.value);
  });

  loadRestaurants();
});