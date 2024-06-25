from stix2 import Filter, CompositeDataSource, FileSystemSource, TAXIICollectionSource
from stix2.v20 import AttackPattern
from taxii2client import Collection
 
# to allow for the retrieval of unknown custom STIX2 content,
# just create *Stores/*Sources with the 'allow_custom' flag

# create FileSystemStore
fs = FileSystemSource("/path/to/stix2_data/", allow_custom=True)

# create TAXIICollectionSource
colxn = Collection('http://taxii_url')
ts = TAXIICollectionSource(colxn, allow_custom=True)