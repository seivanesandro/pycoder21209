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
    out_file = file + '.rle'
    rle.encode_rle(type, file, out_file)
    
def decodeRLE(file):
    p = Path(file)
    rle.decode_rle(file, p.with_suffix(''))
    
def encodePWD(file, pwd, type):
    encrypt.encrypt_file(type, file, pwd)
    
def decodePWD(file, pwd, type):
    encrypt.decrypt_file(type,file, pwd)

def main():
    args = docopt(__doc__)
    type = rle.RLEMethod.B
    
    if (args['--type'] == '1'):
        type = rle.RLEMethod.A
    
    if (args['--encode']):
        if (args['--password']):      
            type = encrypt.CryptMethod.FERNET_SMALL
            encodePWD(args['FILE'], args['--password'], type)
            
        else:
            encodeRLE(type, args['FILE'])
    elif (args['--decode']):
        if (args['--password']):
            type = encrypt.CryptMethod.FERNET_SMALL
            decodePWD(args['FILE'], args['--password'], type)
            
        else:
            decodeRLE(args['FILE'])

if __name__=='__main__':
   main()
    

