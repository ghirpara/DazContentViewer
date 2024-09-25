import json
from common import logger
from ProductManager import ProductManager



pm = ProductManager()

content = pm.get_product_data(sku="81555")

#print (json.dumps(content, indent=4))
print ("Retrieved content")
