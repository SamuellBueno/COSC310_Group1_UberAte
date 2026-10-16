def test_restaurant_details_page_is_served(client):
    response = client.get("/ui/restaurant.html")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_restaurant_details_script_is_served(client):
    response = client.get("/ui/js/restaurant.js")

    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"]