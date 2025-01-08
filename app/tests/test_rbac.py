import pytest

from .constants import BASE_API_PREFIX

API_PREFIX = f"{BASE_API_PREFIX}/auth"


@pytest.fixture(scope="module")
async def role_id(client, postfix):
    role_name = f"test_role_{postfix}"
    response = await client.post(f"{API_PREFIX}/roles", json={"name": role_name, "is_preset": False})
    role_data = response.json().get('data')
    role_id = role_data.get('id')
    yield role_id
    await client.delete(f"{API_PREFIX}/roles/{role_id}")


@pytest.mark.anyio
async def test_get_my_role(client):
    response = await client.get(f"{API_PREFIX}/my_role")
    assert response.status_code == 200
    response_data = response.json()
    print('response_data:', response_data)
    assert response_data['code'] == 0
    expected_role = {
        "id": 1,
        "name": "superAdmin",
        "description": None,
        "is_preset": True
    }
    assert response_data['data'] == expected_role


@pytest.mark.anyio
async def test_get_my_menus(client):
    response = await client.get(f"{API_PREFIX}/my_menus")
    assert response.status_code == 200
    response_data = response.json()
    print('response_data:', response_data)
    assert response_data['code'] == 0
    data = response_data['data']
    assert isinstance(data, list)
    assert "id" in data[0]
    assert "name" in data[0]
    assert "path" in data[0]
    assert "parent_id" in data[0]
    assert "action" in data[0]


class TestRole:
    @pytest.mark.anyio
    @pytest.mark.run(order=11)
    async def test_create_role(self, client, role_id):
        """
        Test create role API
        """
        assert isinstance(role_id, int)

    @pytest.mark.anyio
    @pytest.mark.run(order=12)
    async def test_create_duplicated_role(self, client, postfix):
        test_role_name = f"test_role_{postfix}"
        response = await client.post(f"{API_PREFIX}/roles", json={
            "name": test_role_name
        })
        assert response.status_code == 200
        response_data = response.json()
        print('response_data:', response_data)
        assert response_data['code'] == 1

    @pytest.mark.anyio
    @pytest.mark.run(order=13)
    async def test_get_roles(self, client):
        response = await client.get(f"{API_PREFIX}/roles")
        assert response.status_code == 200
        response_data = response.json()
        print('response_data:', response_data)
        assert response_data['code'] == 0
        data = response_data['data']['items']
        assert isinstance(data, list)
        assert "id" in data[0]
        assert "name" in data[0]
        assert "description" in data[0]
        assert "is_preset" in data[0]

    @pytest.mark.anyio
    @pytest.mark.run(order=14)
    async def test_get_role(self, client, postfix, role_id):
        response = await client.get(f"{API_PREFIX}/roles/{role_id}")
        assert response.status_code == 200
        response_data = response.json()
        print('response_data:', response_data)
        assert response_data['code'] == 0
        expected_role = {
            "id": role_id,
            "name": f"test_role_{postfix}",
            "description": None,
            "is_preset": False
        }
        assert response_data['data'] == expected_role

    @pytest.mark.anyio
    @pytest.mark.run(order=15)
    async def test_update_role(self, client, role_id):
        # update role without description
        response = await client.put(f"{API_PREFIX}/roles/{role_id}", json={
            "name": "updated_role"
        })
        assert response.status_code == 200
        response_data = response.json()
        print('response_data:', response_data)
        assert response_data['code'] == 0
        expected_role = {
            "id": role_id,
            "name": "updated_role",
            "description": None,
            "is_preset": False
        }
        assert response_data['data'] == expected_role

        # update role with description
        response = await client.put(f"{API_PREFIX}/roles/{role_id}", json={
            "name": "updated_role",
            "description": "updated_role description"
        })
        assert response.status_code == 200
        response_data = response.json()
        print('response_data:', response_data)
        assert response_data['code'] == 0
        expected_role = {
            "id": role_id,
            "name": "updated_role",
            "description": "updated_role description",
            "is_preset": False
        }
        assert response_data['data'] == expected_role

    @pytest.mark.anyio
    @pytest.mark.run(order=16)
    async def test_read_role_menus(self, client, role_id, config):
        response = await client.get(f"{API_PREFIX}/roles/{role_id}/menus")
        assert response.status_code == 200
        response_data = response.json()
        print('response_data:', response_data)
        assert response_data['code'] == 0
        data = response_data['data']
        assert isinstance(data, list)
        assert len(data) > 0
        assert "id" in data[0]
        assert "name" in data[0]
        assert "path" in data[0]
        assert "parent_id" in data[0]
        assert "action" in data[0]
        config["menu_list"] = data

    @pytest.mark.anyio
    @pytest.mark.run(order=17)
    async def test_assign_role_menus(self, client, role_id, config):
        # change menu actions to edit in _menus_list
        for menu in config["menu_list"]:
            menu['action'] = "edit"
        response = await client.put(f"{API_PREFIX}/roles/{role_id}/menus", json=config["menu_list"])
        assert response.status_code == 200
        response_data = response.json()
        print('response_data:', response_data)
        assert response_data['code'] == 0
        data = response_data['data']
        assert isinstance(data, list)
        assert "id" in data[0]
        assert "name" in data[0]
        assert "path" in data[0]
        assert "parent_id" in data[0]
        assert "action" in data[0]
        assert data[0]['action'] == "edit"

    @pytest.mark.anyio
    @pytest.mark.run(order=99)
    async def test_delete_role(self, client, role_id):
        print(f"Delete role: {role_id}")
        response = await client.delete(f"{API_PREFIX}/roles/{role_id}")
        assert response.status_code == 200
        response_data = response.json()
        print('response_data:', response_data)
        assert response_data['code'] == 0


@pytest.fixture(scope="module")
async def test_menu(client, postfix):
    menu_name = f"test_menu_{postfix}"
    response = await client.post(f"{API_PREFIX}/menus", json={
        "name": menu_name,
        "path": "/test",
        "parent_id": None,
        "actions": ["view"]
    })
    menu_data = response.json().get('data')
    return menu_data


class TestMenu:
    """
    Test Menu APIs
    Test Sequence:
    1. create parent menu
    2. create 2 sub menu
    3. get menus
    4. update menu
    5. delete 1 sub menu
    6. delete parent menu with another sub menu
    """
    _menu_id = None
    _menu_name = None
    _sub_menu_id = None

    @pytest.mark.anyio
    @pytest.mark.run(order=21)
    async def test_create_menu(self, client, test_menu):
        """
        Test create menu API
        """
        assert 'id' in test_menu and isinstance(test_menu['id'], int), "Menu ID should be present and of type int"
        TestMenu._menu_id = test_menu['id']
        TestMenu._menu_name = test_menu['name']

    @pytest.mark.anyio
    @pytest.mark.run(order=22)
    async def test_create_sub_menu(self, client):
        """
        Test create sub menu API
        """
        response = await client.post(f"{API_PREFIX}/menus", json={
            "name": "sub_menu_1",
            "path": "/test/sub_menu_1",
            "parent_id": TestMenu._menu_id,
            "actions": ["view"]
        })
        assert response.status_code == 200
        response_data = response.json()
        print('response_data:', response_data)
        assert response_data['code'] == 0
        TestMenu._sub_menu_id = response_data['data']['id']

        # create another sub menu
        response = await client.post(f"{API_PREFIX}/menus", json={
            "name": "sub_menu_2",
            "path": "/test/sub_menu_2",
            "parent_id": TestMenu._menu_id,
            "actions": ["view"]
        })
        assert response.status_code == 200
        response_data = response.json()
        print('response_data:', response_data)
        assert response_data['code'] == 0

    @pytest.mark.anyio
    @pytest.mark.run(order=23)
    async def test_get_menus(self, client):
        response = await client.get(f"{API_PREFIX}/menus")
        assert response.status_code == 200
        response_data = response.json()
        print('response_data:', response_data)
        assert response_data['code'] == 0
        data = response_data['data']
        assert isinstance(data, list)
        # search the menus and check the TestMenu._menu_id is present, and check the fields in the menu
        assert any(menu['id'] == TestMenu._menu_id for menu in data)
        assert "id" in data[0]
        assert "name" in data[0]
        assert "path" in data[0]
        assert "parent_id" in data[0]

    @pytest.mark.anyio
    @pytest.mark.run(order=24)
    async def test_update_menu(self, client):
        response = await client.put(f"{API_PREFIX}/menus/{TestMenu._menu_id}", json={
            "name": f"{TestMenu._menu_name}_updated",
            "path": "/test" + "_updated",
            "parent_id": None,
            "super_only": False
        })
        assert response.status_code == 200
        response_data = response.json()
        print('response_data:', response_data)
        assert response_data['code'] == 0
        expected_menu = {
            "id": TestMenu._menu_id,
            "name": f"{TestMenu._menu_name}_updated",
            "path": "/test_updated",
            "parent_id": None,
            "super_only": False
        }
        assert response_data['data'] == expected_menu

    @pytest.mark.anyio
    @pytest.mark.run(order=26)
    async def test_delete_sub_menu(self, client):
        response = await client.delete(f"{API_PREFIX}/menus/{TestMenu._sub_menu_id}")
        assert response.status_code == 200
        response_data = response.json()
        print('response_data:', response_data)
        assert response_data['code'] == 0

    @pytest.mark.anyio
    @pytest.mark.run(order=98)
    async def test_delete_menu(self, client):
        response = await client.delete(f"{API_PREFIX}/menus/{TestMenu._menu_id}")
        assert response.status_code == 200
        response_data = response.json()
        print('response_data:', response_data)
        assert response_data['code'] == 0


@pytest.fixture(scope="module")
async def test_user(client, postfix):
    user_name = f"test_user_{postfix}"
    response = await client.post(f"{API_PREFIX}/users", json={
        "name": user_name,
        "email": f"{user_name}@gmail.com"
    })
    user_data = response.json().get('data')
    return user_data


class TestUser:
    _user_id = None

    @pytest.mark.anyio
    @pytest.mark.run(order=1)
    async def test_create_user(self, client, test_user):
        """
        Test create user API
        """
        assert 'id' in test_user and isinstance(test_user['id'], int), "User ID should be present and of type int"
        TestUser._user_id = test_user['id']

    @pytest.mark.anyio
    @pytest.mark.run(order=2)
    async def test_get_users(self, client):
        response = await client.get(f"{API_PREFIX}/users")
        assert response.status_code == 200
        response_data = response.json()
        print('response_data:', response_data)
        assert response_data['code'] == 0
        data = response_data['data']['items']
        assert isinstance(data, list)
        assert "id" in data[0]
        assert "name" in data[0]
        assert "email" in data[0]
        assert "role" in data[0]

    @pytest.mark.anyio
    @pytest.mark.run(order=3)
    async def test_assign_user_role(self, client, role_id):
        print(f'Test role_id: {role_id}')
        assert isinstance(role_id, int)
        assert role_id > 0
        response = await client.put(f"{API_PREFIX}/users/{TestUser._user_id}/role?role_id={role_id}")
        assert response.status_code == 200
        response_data = response.json()
        print('response_data:', response_data)
        assert response_data['code'] == 0

    @pytest.mark.anyio
    @pytest.mark.run(order=4)
    async def test_delete_user(self, client):
        response = await client.delete(f"{API_PREFIX}/users/{TestUser._user_id}")
        assert response.status_code == 200
        response_data = response.json()
        print('response_data:', response_data)
        assert response_data['code'] == 0
