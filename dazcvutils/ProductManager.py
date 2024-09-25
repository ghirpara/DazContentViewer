import sys
import json
import requests
import argparse
import base64
import logging
from common import logger
from whoosh.fields import *

schema_def = {
    "objectName":TEXT(stored=True),
    "id":TEXT,
    "artists":KEYWORD(stored=True),
    "store":KEYWORD,
    "token":NUMERIC,
    "url":ID,
    "title":TEXT(stored=True),
    "description":TEXT(stored=True),
    "iconPath":ID,
    "dateLastUpdated":DATETIME(stored=True),
    "datePurchased":DATETIME(stored=True),
    "dateInstalled":DATETIME(stored=True),
    "dateReleased":DATETIME(stored=True)
}

class Product:

    def __init__(self):
        self.attributes = {}

    def merge_attributes(self, content):
        self.attributes.update(content)

    def str_to_image(self, imgstring):
        imgdata = base64.b64decode(imgstring)
        filename = 'test.jpg'
        with open(filename, 'wb') as f:
            f.write(imgdata)

class ProductManager:

    def __init__(self, args=None):
        if args is None:
            args={}
        base_host = args.get("base_host", "www.daz3d.com")
        api_root  = args.get("api_root", "/dazApi/slab/")
        self.root_url = f"https://{base_host}{api_root}"
        self.product_cache = {}

        logger.info (f"Initializing ProductManager: host=[{base_host}], api_root={api_root}, base_url={self.root_url}")

    def get_product(self, sku):
        if sku not in self.product_cache:
            self.add_product(sku)
        return self.product_cache[sku]


    def add_product_from_cache(self, cache_file):
        logger.info (f"Adding data from local cache file: {cache_file}")
        cache = json.load(open(cache_file, 'r'))
        for cname in cache:
            self.add_product(sku=cname, initial_attributes=cache[cname], load_remote=False)
    
    def x_add_product_from_metadata(self, metadata_file):
        logger.info (f"Adding data from metadata file: {metadata_file}")        
        metadata = json.load(open(metadata_file, 'r'))
        n=0
        for cname in metadata:
            for pname in metadata[cname]:
                print (f'Adding {pname}')
                product = metadata[cname][pname]
                product_object = self.add_product (sku=pname,
                                                    initial_attributes=product)
                n += 1
                if (n>10):
                    return
# 10 Handbags Collection|DAZ 3D| 59339| 146c7f5b-d1ee-4611-848a-b85fc7c6e62d| 146c7f5b-d1ee-4611-848a-b85fc7c6e62d

    def add_product_from_metadata(self, filename):
        logger.info (f"Adding data from metadata file: {filename}")        
        with open(filename, 'r') as f:
            n=0
            for line in f.readlines():
                parts=line.split("|")
                title, store, token, guid, lid = line.split('|')
                sku=token.strip()
                initial_attributes = {
                    "title": title.strip(), 
                    "sku": sku,
                    "guid": guid.strip()
                }
                self.add_product (guid=guid, initial_attributes=initial_attributes)
                n+=1
                if (n>5):
                    return

    def dump_product_cache(self):
        rv={}
        for sku in self.product_cache:
            product = self.product_cache[sku]
            rv[sku] = product.attributes
        return json.dumps(rv, indent=4)
    

    def add_product(self, guid, initial_attributes={}, load_remote=True):
        logger.info(f"Adding content for GUID {guid} (load_remote={load_remote})")
        if guid not in self.product_cache:
            self.product_cache[guid] = Product()

        product = self.product_cache[guid]

        if load_remote:
            sku=initial_attributes.get("sku")
            if len(sku) > 0:
                site_attributes = self.get_product_data(sku)
                product.merge_attributes(site_attributes)
            else:
                logger.warning(f"No valid SKU presented for requested product: {initial_attributes}")
        product.merge_attributes(initial_attributes)
        return product
        
    
 

if __name__ == '__main__':


    parser = argparse.ArgumentParser(
        prog=__name__[:-2],
        description='Manager class for processing product data and maintaining the local data cache.')

    parser.add_argument('filename')    
    parser.add_argument('-s', '--source', default="metadata", choices=["metadata", "cache"], action="store")
    parser.add_argument('-d', '--debug', default="store_true")
    parser.add_argument('-o', '--output', default=None)

    args = parser.parse_args()

    if (args.debug):
        logging.basicConfig(filename='copilot.log', level=logging.DEBUG)
    else:
        logging.basicConfig(filename='copilot.log', level=logging.INFO)

    source_file = args.filename
    source_type = args.source
    
    pm = ProductManager(args={})

    if source_type == "metadata":
        pm.add_product_from_metadata (source_file)
    else:
        pm.add_product_from_cache (source_file)

    if args.output is not None:
        with open(args.output, 'w') as f:
            f.write(pm.dump_product_cache())
    
    
    
    


