const restaurantId = new URLSearchParams(window.location.search).get("id");

async function loadRestaurant() {
    const name = document.getElementById("name");
    const info = document.getElementById("info");
    const error = document.getElementById("error");
    const menuLink = document.getElementById("menu-link");

    if (!restaurantId) {
    error.textContent = "No restaurant ID was provided.";
    return;
    }

    try {
    const restaurant = await apiGet(
        `/restaurants/${encodeURIComponent(restaurantId)}`
    );

    name.textContent = restaurant.name;

    info.textContent =
        `${restaurant.cuisine} · ${restaurant.address} · ` +
        `Rating: ${restaurant.rating ?? "Not rated yet"} · ` +
        (restaurant.is_open ? "Open" : "Closed");
    info.className = "detail-info";

    menuLink.href =
        `menu.html?id=${encodeURIComponent(restaurantId)}`;
    menuLink.className = "button";
    menuLink.hidden = false;
    } catch (err) {
    error.textContent = err.message;
    }
}

loadRestaurant();