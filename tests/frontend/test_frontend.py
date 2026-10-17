def test_restaurant_details_page_is_served(client):
    response = client.get("/ui/restaurant.html")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_restaurant_details_script_is_served(client):
    response = client.get("/ui/js/restaurant.js")

    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"]


def test_manage_page_and_menu_management_script_are_served(client):
    page_response = client.get("/ui/manage.html")
    script_response = client.get("/ui/js/manage-menu.js")

    assert page_response.status_code == 200
    assert "menu-create-form" in page_response.text
    assert script_response.status_code == 200
    assert "javascript" in script_response.headers["content-type"]