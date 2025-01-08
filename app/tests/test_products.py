import random
import string

import pytest

from .constants import BASE_API_PREFIX
from ..log import logger

API_PREFIX = f"{BASE_API_PREFIX}/admin/vision_one"
PRODUCT_API_PREFIX = f"{API_PREFIX}/products"


def generate_random_code(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


@pytest.fixture(scope="module")
async def product_code(client):
    product_code = generate_random_code()
    yield product_code


@pytest.fixture(scope="module")
async def product_id(client, product_code):
    response = await client.post(f"{PRODUCT_API_PREFIX}", json={
        "code": product_code,
        "name": f"Test Product {product_code}"
    })
    product_data = response.json().get('data')
    product_id = product_data.get('id')
    yield product_id
    await client.delete(f"{PRODUCT_API_PREFIX}/{product_id}")


class TestProduct:
    @pytest.mark.anyio
    @pytest.mark.run(order=211)
    async def test_create_product(self, client, product_id):
        """
        Test create product API
        """
        assert isinstance(product_id, int)

    @pytest.mark.anyio
    @pytest.mark.run(order=212)
    async def test_create_duplicated_product(self, client, product_code):
        test_product_code = product_code
        response = await client.post(f"{PRODUCT_API_PREFIX}", json={
            "code": test_product_code,
            "name": f"Test Product {product_code}"
        })
        assert response.status_code == 200
        response_data = response.json()
        print('response_data:', response_data)
        assert response_data['code'] == 1

    @pytest.mark.anyio
    @pytest.mark.run(order=213)
    async def test_get_products(self, client):
        response = await client.get(f"{PRODUCT_API_PREFIX}")
        assert response.status_code == 200
        response_data = response.json()
        print('response_data:', response_data)
        assert response_data['code'] == 0
        assert "data" in response_data
        paged_products = response_data['data']
        assert "items" in paged_products
        assert "total" in paged_products and paged_products['total'] > 0
        items = paged_products['items']
        assert "id" in items[0]
        assert "code" in items[0]
        assert "name" in items[0]

    @pytest.mark.anyio
    @pytest.mark.run(order=214)
    async def test_get_product(self, client, product_code, product_id):
        response = await client.get(f"{PRODUCT_API_PREFIX}/{product_id}")
        assert response.status_code == 200
        response_data = response.json()
        print('response_data:', response_data)
        assert response_data['code'] == 0
        expected_product = {
            "id": product_id,
            "code": product_code,
            "name": f"Test Product {product_code}"
        }
        assert response_data['data'] == expected_product

    @pytest.mark.anyio
    @pytest.mark.run(order=215)
    async def test_update_product(self, client,product_code, product_id):
        # update product without description
        logger.debug(f"Update product: {product_id}")
        response = await client.put(f"{PRODUCT_API_PREFIX}/{product_id}", json={
            "code": product_code,
            "name": f"Updated Product {product_code}"
        })
        assert response.status_code == 200
        response_data = response.json()
        print('response_data:', response_data)
        assert response_data['code'] == 0
        expected_product = {
            "id": product_id,
            "code": product_code,
            "name": f"Updated Product {product_code}"
        }
        assert response_data['data'] == expected_product

    @pytest.mark.anyio
    @pytest.mark.run(order=299)
    async def test_delete_product(self, client, product_id):
        print(f"Delete product: {product_id}")
        response = await client.delete(f"{PRODUCT_API_PREFIX}/{product_id}")
        assert response.status_code == 200
        response_data = response.json()
        print('response_data:', response_data)
        assert response_data['code'] == 0
