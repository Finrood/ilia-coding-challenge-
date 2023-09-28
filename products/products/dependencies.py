from typing import Dict, Union

from nameko import config
from nameko.extensions import DependencyProvider
import redis
import logging

from products.exceptions import NotFound, IllegalArgumentException


REDIS_URI_KEY = 'REDIS_URI'

logger = logging.getLogger(__name__)

class StorageWrapper:
    """
    Product storage

    A very simple example of a custom Nameko dependency. Simplified
    implementation of products database based on Redis key value store.
    Handling the product ID increments or keeping sorted sets of product
    names for ordering the products is out of the scope of this example.

    """

    NotFound = NotFound
    IllegalArgumentException = IllegalArgumentException

    def __init__(self, client):
        self.client = client

    def _format_key(self, product_id: str) -> str:
        return f'products:{product_id}'

    def _from_hash(self, document: Dict[bytes, bytes]) -> Dict[str, Union[str, int]]:
        return {
            'id': document[b'id'].decode('utf-8'),
            'title': document[b'title'].decode('utf-8'),
            'passenger_capacity': int(document[b'passenger_capacity']),
            'maximum_speed': int(document[b'maximum_speed']),
            'in_stock': int(document[b'in_stock'])
        }

    def get(self, product_id):
        product = self.client.hgetall(self._format_key(product_id))
        if not product:
            raise NotFound(f'Product ID {product_id} does not exist')
        else:
            return self._from_hash(product)

    def list(self):
        product_keys = self.client.keys(self._format_key('*'))
        for key in product_keys:
            yield self._from_hash(self.client.hgetall(key))

    def create(self, product):
        product_key = self._format_key(product['id'])
        if self.client.exists(product_key):
            raise IllegalArgumentException(f'Product key {product_key} already exist')
        else:
            self.client.hmset(product_key, product)

    def delete(self, product_id):
        product_key = self._format_key(product_id)
        self.client.delete(product_key)

    def decrement_stock(self, product_id, amount):
        product_key = self._format_key(product_id)
        if not self.client.exists(product_key):
            raise NotFound(f'Product ID {product_id} does not exist')

        return self.client.hincrby(product_key, 'in_stock', -amount)


class Storage(DependencyProvider):

    def setup(self):
        try:
            self.client = redis.StrictRedis.from_url(config.get(REDIS_URI_KEY))
            logger.info("Connected to Redis")
        except Exception as e:
            logger.error(f"Error connecting to Redis: {e}")
            raise

    def get_dependency(self, worker_ctx):
        return StorageWrapper(self.client)
