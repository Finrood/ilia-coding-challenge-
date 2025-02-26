import logging

from nameko.events import event_handler
from nameko.rpc import rpc

from products import dependencies, schemas


logger = logging.getLogger(__name__)


class ProductsService:

    name = 'products'

    storage = dependencies.Storage()

    @rpc
    def get_product(self, product_id):
        product = self.storage.get_product(product_id)
        return schemas.Product().dump(product).data

    @rpc
    def list_products(self):
        products = self.storage.list_products()
        return schemas.Product(many=True).dump(products).data

    @rpc
    def create_product(self, product):
        product = schemas.Product(strict=True).load(product).data
        self.storage.create_product(product)

    @rpc
    def delete_product(self, product_id):
        self.storage.delete_product(product_id)

    @event_handler('orders', 'order_created')
    def handle_order_created(self, payload):
        for product in payload['order']['order_details']:
            self.storage.decrement_stock(
                product['product_id'], product['quantity'])
