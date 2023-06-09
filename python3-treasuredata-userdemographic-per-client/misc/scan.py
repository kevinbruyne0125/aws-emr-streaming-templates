import glob
import os
import json
import sys
import pickle
import gzip
import concurrent.futures
from datetime import datetime
def _map1(name):
  key_term_freq = {}
  print(name)
  for line in open(name):
    line = line.strip()
    #print(line)
    key, val = line.split('\t')
    val = json.loads(val)

    if key_term_freq.get(key) is None:
      key_term_freq[key] = {}
    for term, freq in val.items(): 
      if  key_term_freq[key].get(term) is None:
        key_term_freq[key][term] = 0 
      key_term_freq[key][term] += freq
    #print( term, key_term_freq[key][term] )
  save_name = 'shrink/{}.pkl.gz'.format(name.split('/').pop())
  #print( key_term_freq )
  open(save_name,'wb').write( gzip.compress(pickle.dumps(key_term_freq)) )

if '--map1' in sys.argv:
  names = [name for name in glob.glob('result-20171118/part-*')]
  _map1(names[0])
  with concurrent.futures.ProcessPoolExecutor(max_workers=16) as exe:
    exe.map(_map1, names)

if '--reduce1' in sys.argv:
  key_term_freq = {}
  files = glob.glob('shrink/*.pkl.gz')
  size = len(files)
  for index, name in enumerate( files ):
    print(name, index, '/', size)
    _key_term_freq = pickle.loads( gzip.decompress( open(name, 'rb').read() ) )
    for key, term_freq in _key_term_freq.items():
      #print(term_freq)
      if key_term_freq.get(key) is None:
        key_term_freq[key] = {}
      for term, freq in term_freq.items():
        if key_term_freq[key].get(term) is None:
          key_term_freq[key][term] = 0
        key_term_freq[key][term] += freq
        #print( term, freq, key_term_freq[key][term]  )
  now = datetime.now()
  year_month = '%04d_%02d'%(now.year, now.month)
  f = open('output_{}.txt'.format(year_month), 'w')
  for key, term_freq in key_term_freq.items():
    javari = key + '\t' + json.dumps(term_freq, ensure_ascii=False)
    f.write( javari + '\n' )
