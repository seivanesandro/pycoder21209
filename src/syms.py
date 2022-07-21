import argparse
from operator import truediv
import sys
import os
from pathlib import Path
import hashlib
import re

def compareContents(path):
    results = {}

    for (root, dirs, files) in os.walk(path, topdown=True):
        for file in files:
            fullName = os.path.join(root, file)
            hashData = hashlib.md5()
            with open(fullName, "rb") as fh:
                data = fh.read()
                hashData.update(data)
                
            hashData = hashData.hexdigest()

            if hashData in results:
                results[hashData].append(fullName)
            else:
                results[hashData] = [fullName]

    print("\n-- Content comparison --\n")
    foundResults = False
    
    for entry in results:
        numberResults = len(results[entry])

        if (numberResults > 1):
            if not foundResults:
                foundResults=True
                
            print(f'Files that are similar in content ({numberResults} files):')
            for f in results[entry]:
                print(f)
    
    if not foundResults:
        print("No results that meet the criteria were found.")
    

def compareName(path):
    results = {}
    
    for (root, dirs, files) in os.walk(path, topdown=True):
        for file in files:
            fullName = os.path.join(root, file)
            if file in results:
                results[file].append(fullName)
            else:
                results[file] = [fullName]
               
    print ("\n-- Name comparison --\n")
    foundResults = False
    
    for entry in results:
        numberResults = len(results[entry])
        
        if (numberResults>1):
            if not foundResults:
                foundResults = True
                
            print(f'File {entry} has {numberResults} files:')
            for f in results[entry]:
                print(f)
    
    if not foundResults:
        print("No results that meet the criteria were found.")
           
    

def compareExtensions(path):
    results = {}

    for (root, dirs, files) in os.walk(path, topdown=True):
        for file in files:
            fullName = os.path.join(root, file)
            _,ext = os.path.splitext(file)
            
            if ext in results:
                results[ext].append(fullName)
            else:
                results[ext] = [fullName]

    print("\n-- Extensions comparison --\n")
    foundResults = False
    
    for entry in results:
        numberResults = len(results[entry])

        if (numberResults >1):
            if not foundResults:
                foundResults=True
                
            print(f'\nExtension {entry} has {numberResults} files:')
            for f in results[entry]:
                print(f)
    
    if not foundResults:            
        print("No results that meet the criteria were found.")
            
         
def compareWithPattern(path, pattern):
    results = {}

    for (root, dirs, files) in os.walk(path, topdown=True):
        for file in files:
            fullName = os.path.join(root, file)
            if (re.search(pattern, file)):
                if pattern in results:
                    results[pattern].append(fullName)
                else:
                    results[pattern] = [fullName]

    print("\n-- Regex comparison --\n")
    foundResults = False
    
    for entry in results:
        numberResults = len(results[entry])

        if (numberResults > 1):
            if not foundResults:
                foundResults = True
                
            print(f'\nRegex pattern {entry} has {numberResults} files:')
            for f in results[entry]:
                print(f)
    
    if not foundResults:
        print("No results that meet the criteria were found.")
                
def main():
    #Declaração do argumentParser (parte do argparse). A descripção é um argumento que dá um resumo do que o programa faz.
    parser = argparse.ArgumentParser(
        description="SYMS - Search for similarities between files inside a directory")

    parser.add_argument('-c', '--contents', action='store_true', help = "detects files with the same binary content")
    parser.add_argument('-n', '--name', action='store_true', help="detects files with the same name (including extension)")
    parser.add_argument('-e', '--extension', action='store_true', help="detects files with the same extension")
    parser.add_argument('-r', '--regex', help = "detects files which name matches the regex expression PATTERN")
    
    parser.add_argument('caminho_dir', nargs="?", help="directory where to search the files", default=os.getcwd())
   
    #adiciona-se então todos os argumentos a variável args
    args = parser.parse_args()

    if args.contents:
        compareContents(args.caminho_dir)
    
    if args.extension:
        compareExtensions(args.caminho_dir)
    
    if args.regex:
        compareWithPattern(args.caminho_dir, args.regex)
   
    if args.name or (not args.regex and not args.content and not args.extension):
        compareName(args.caminho_dir)     
    

if __name__ == "__main__":
    try:
        main()
        sys.exit()
    except Exception as error:
        print(error)
        sys.exit()
