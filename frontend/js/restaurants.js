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
        list.innerHTML = '<li class="empty-message">No restaurants match those filters.</li>';
    }

    for (const restaurant of restaurants) {
        const item = document.createElement("li");
        item.className = "restaurant-card";
        const link = document.createElement("a");

        link.href =
        `restaurant.html?id=${encodeURIComponent(restaurant.id)}`;

        const name = document.createElement("span");
        name.className = "restaurant-name";
        name.textContent = restaurant.name;

        const meta = document.createElement("span");
        meta.className = "restaurant-meta";
        meta.textContent = restaurant.cuisine;

        const status = document.createElement("span");
        status.className = `status ${restaurant.is_open ? "open" : "closed"}`;
        status.textContent = restaurant.is_open ? "Open now" : "Currently closed";

        link.append(name, meta, status);
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