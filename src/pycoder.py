"""
Usage:
    pycoder.py (-c [-t TYPE] | -d) [-p PASSWD] FILE
    
Arguments:
    FILE                            File to be transformed   

Options:
    -c --encode                     Encode FILE optionally with PASSWD
    -t TYPE --type=TYPE             RLE method [default: 2]
    -d --decode                     Decode FILE optionally with PASSWD
    -p PASSWD --password=PASSWD     Encode/Decode using password PASSWD
    
    -h --help                       Show this screen
"""


from docopt import docopt
from pathlib import Path
import rle
import encrypt

def encodeRLE (type, file):
    p = Path(file);
    rle.encode_rle(type, file, p.with_suffix('.rle'))
    
def decodeRLE(file):
    p = Path(file)
    rle.decode_rle(file, p.with_suffix(''))
    
def encodePWD(file, pwd):
    encrypt.encrypt_file(1, file, pwd)
    
def decodePWD(file, pwd):
    encrypt.decrypt(1,file, file, pwd)

def main():
    args = docopt(__doc__)
    
    if (args['--encode']):
        if (args['--password']):
            encodePWD(args['FILE'], args['--password'])
        else:
            encodeRLE(args['--type'], args['FILE'])
    elif (args['--decode']):
        if (args['--password']):
            decodePWD(args['FILE'], args['--password'])
        else:
            decodeRLE(args['FILE'])
        

if __name__=='__main__':
   main()
    

