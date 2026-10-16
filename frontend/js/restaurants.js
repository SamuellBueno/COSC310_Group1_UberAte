async function loadRestaurants() {
    const params = new URLSearchParams();

    const search = document.getElementById("search").value.trim();
    const cuisine = document.getElementById("cuisine").value.trim();
    const openOnly = document.getElementById("open-only").checked;

    if (search) params.set("search", search);
    if (cuisine) params.set("cuisine", cuisine);
    if (openOnly) params.set("open", "true");

    const list = document.getElementById("restaurant-list");
    const error = document.getElementById("error");

    list.replaceChildren();
    error.textContent = "";

    try {
    const restaurants = await apiGet(`/restaurants?${params}`);

    if (restaurants.length === 0) {
        list.textContent = "No restaurants match.";
    }

    for (const restaurant of restaurants) {
        const item = document.createElement("li");
        const link = document.createElement("a");

        link.textContent =
        `${restaurant.name} (${restaurant.cuisine})` +
        (restaurant.is_open ? " - Open" : " - Closed");

        link.href =
        `restaurant.html?id=${encodeURIComponent(restaurant.id)}`;

        item.append(link);
        list.append(item);
    }
    } catch (err) {
    error.textContent = err.message;
    }
}

document.getElementById("filters").addEventListener("submit", (event) => {
    event.preventDefault();
    loadRestaurants();
});

loadRestaurants();