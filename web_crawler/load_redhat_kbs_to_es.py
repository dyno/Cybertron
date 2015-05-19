from datetime import datetime
from elasticsearch import Elasticsearch
from webpage import RedHatKBPage
from os import listdir
from os.path import isfile, join

class RHKB_to_ES_Loader:

##############################################################################
# RedHat Database structure:
#    KBid, URL, Issue, Environment, Resolution 
###############################################
#    KBid, URL, Issue, Environment, Resolution, Rootcause, Diagnostic, Title
#    search fields name in es: 
#       issue, env, resolution, rootcause, diagnostic, title
##############################################################################

    def __init__(self, dir):
        self.es = Elasticsearch()
        self.index = 'redhat_kb'
        self.doc_type = 'kb'
        self.kb_dir = dir 
        self.create_index()      
    
    def create_index(self): 
        # Create an index with settings and mapping, a line is a term
        #    1. add a new tokenizer which divide by /n
        #    2. add mappings to doc_type and field
        doc = {
            'settings':{
                'analysis':{
                    'analyzer':{
                        'line_tokenizer':{
                            'type':'pattern',
                            'pattern':'\n'
                        }
                    }
                }
            },
            'mappings':{
                self.doc_type:{
                   'properties':{
                        'issue':{
                            'type':'string',
                            'analyzer':'line_tokenizer'
                        },                                         
                        'env':{
                            'type':'string',
                            'analyzer':'line_tokenizer'
                        },                                       
                        'resolution':{
                            'type':'string',
                            'analyzer':'line_tokenizer'
                        },                                       
                        'rootcause':{
                            'type':'string',
                            'analyzer':'line_tokenizer'
                        },                                       
                        'diagnostic':{
                            'type':'string',
                            'analyzer':'line_tokenizer'
                        },                                       
                        'title':{
                            'type':'string',
                            'analyzer':'line_tokenizer'
                        }                                       
                    } 
                } 
            }
        }
        res = self.es.indices.create(index = self.index, body = doc)
        return res    

    def index_item(self, page):
        if page.is_en_page() == False:
            print "INFO: It is not an en page"
            return False
        doc = {
            'url': page.get_url(),
            'issue': page.get_issue(),
            'env': page.get_env(),
            'resolution': page.get_resolution(),
            'rootcause': page.get_rootcause(),
            'diagnostic': page.get_diagnostic(),
            'title': page.get_title()
        }
        res = self.es.index(index = self.index, doc_type = self.doc_type, id = page.get_id(), body = doc)
        return res['created']

    def index_all(self):
        # iter all kbs
        for f in listdir(self.kb_dir):
            print "DEBUG: %s" %(f)
            file = join(self.kb_dir, f)
            if isfile(file):
                self.index_item(RedHatKBPage(file))

if __name__ == "__main__":
    import sys
    print len(sys.argv)
    if len(sys.argv) < 2:
        print "Please provide KB dirname"
        exit(0)
    
    loader = RHKB_to_ES_Loader(sys.argv[1])
 
    print loader.index_all()
