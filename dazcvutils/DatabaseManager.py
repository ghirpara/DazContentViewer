import os
import sys
import logging
import json
import argparse
import tempfile
from common import get_daz_product_data, cleanify, logger
from datetime import datetime, timedelta
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser
from whoosh.qparser.dateparse import DateParserPlugin
from whoosh.fields import *
from StudioBridge import StudioBridge
from ProductManager import Product, schema_def

class DatabaseManager:
    def __init__(self):
        self.schema = Schema(**schema_def)
        if not os.path.exists("_indexdir"):
            os.mkdir("_indexdir")
            self.index = create_in("_indexdir", self.schema)
        else:
            self.index = open_dir("_indexdir")
            

    def __mkdate__(self, ds):
        dt = datetime.datetime.strptime(ds, "%Y-%m-%dT%H:%M:%S.%fZ")        
        return dt
    
    def index_metadata_collection(self, input_file:str):
        logging.info(f"Indexing metadata collection from input file {input_file}")
        n=0
        content = json.load(open(input_file, 'r'))
        for cname in content:
            for pname in content[cname]:
                product = content[cname][pname]
                self.index_document(document=product)
                n += 1

        logging.info(f"Indexed {n} products.")

    def index_product(self, product:Product):
        kwargs={}
        token = product.get_attr('token', None)

        keys = Product.schema_def.keys()
        if token is not None and token.isdigit():
            for key in keys:
                value = product.get_attr(key, None)
                if value is not None:
                    if key.startswith('date'):
                        value=self.__mkdate__(value)
                    kwargs[key]=value
            
            try:
                self.writer = self.index.writer()                
                self.writer.add_document(**kwargs)
                self.writer.commit()
                logging.info (f"Wrote product {token}")            
            except Exception as e:
                logging.error (f'Failed to write content for {token}: {e}')
        
    def search(self, querystring, default_field, limit=100):
        parser = QueryParser (default_field, self.index.schema)
        parser.add_plugin(DateParserPlugin())
        query = parser.parse (querystring)

        with self.index.searcher() as searcher:
            results = searcher.search(query, limit=limit)
            print (f"""Received {len(results)} results.""")
            print (f"""Scored length {results.scored_length()}""")
            for result in results:
                print (f"""Result {result['title']}""")


    def validate(self, args):

        outputfile = args['script_args']['output_file']
        
        with open(outputfile, 'r') as f:
            for line in f.readlines():
                line=line.strip()
                parts=line.split("|")
                parts=[x.strip() for x in parts]
                title,store,token,guid,uid=parts
                if token.isnumeric() is False:
                    print (f"Non-numeric token {token}: {line}")
    
    # 2. For each item in the returned list, query the DAZ Store to get the remainder of the metadata 
    # 3. Write full cache of data to disk as a file that the "index" command can use to update the index
    def preload(self, args):

        total=0
        count=0
        cache={}
        cache_file='cache.json'

        # 1. Download initial set of metadata using the DB_List_Products.dsa script 
        bridge = StudioBridge(args)
        bridge.execute()


    def load(self, args):

        # TODO: Add option to not specify an output_file on the command line and 
        # instead use the default value that is the same as in the DB_List_Products.dsa
        # script, which is $PWD/sample.out
        outputfile = args['script_args']['output_file']

        cache_file='cache.json'

        if os.path.exists(cache_file):
            cache=json.load(open(cache_file, 'r'))
        else:
            cache={}
        
        with open(outputfile, 'r') as f:
            total=sum(1 for _ in f)

        logger.info(f"Processing {total} product files.")

        with open(outputfile, 'r') as f:
            for line in f.readlines():
                title,store,token,guid,uuid=line.split('|')
                token = token.strip()
                gurl = f"https://www.daz3d.com/dazApi/slab/{token}"
                content = get_daz_product_data(token, gurl)
                cache[token] = content
                count +=1
                logger.info(f"Processing product {token}.")
                if (count % 100 == 0):
                    logger.info (f'Read {count} of {total} product files.')
        
        logger.info(f'Wrote {len(cache.keys())} to cache file {cache_file}')
        f=open(cache_file, 'w')
        f.write(json.dumps(cache))
        f.close()
        

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog=__name__[:-2],
        description='Manager class for processing product data and maintaining the local data cache.')

    parser.add_argument('command')    
    parser.add_argument('-q', '--query', default=None)
    parser.add_argument('-i', '--input-file', default=None)
    parser.add_argument('-f', '--query-field', default="description")
    parser.add_argument('-x', '--extended-script-args', default=[])
    parser.add_argument('-d', '--daz-path', default="C:/Program Files/DAZ 3D/DAZStudio4/DAZStudio.exe",
                        help="Path to the DAZStudio.exe file")
    parser.add_argument('-c', '--cli-args', 
                        metavar="KEY=VALUE", 
                        action="append",
                        default=[],
                        help="""
                        Command line arguments to DAZ CLI interface. 
                        See http://docs.daz3d.com/doku.php/public/software/dazstudio/4/referenceguide/tech_articles/command_line_options/start for a list of values.
                        """
                        )
    parser.add_argument('-s', '--script-args', 
                        action="append",
                        default=[],
                        help="scriptArgs to pass to the script. Each argument corresponds to an element in the App.scriptArg array")
    parser.add_argument('-n', '--no-command',
                        action="store_true",
                        help="If specified print out the command line to be executed, but don't actually run it.")
    
    args = parser.parse_args()

    dm = DatabaseManager()

    if args.command == "preload":

        dm.preload(cleanify(vars(args), ["script_args", "cli_args"]))

    elif args.command == "validate":

        dm.validate(cleanify(vars(args), ["script_args", "cli_args"]))
        
    elif args.command == "index" and args.input_file is not None:
        
        dm.index_metadata_collection(cleanify(vars(args), ["script_args", "cli_args"]))

    elif args.command == "load":
        
        dm.load(cleanify(vars(args), ["script_args", "cli_args"]))

    elif args.command == "query" and args.query is not None:

        querystring = args.query
        default_field = args.query_field
        results = dm.search (querystring, default_field)

        










    
