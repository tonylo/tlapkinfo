#!/usr/bin/python3

# TL: Had to use python3 because zipfile in Python 2.7
#     on my Ubuntu 14 cannot handle idiosyncrasies of APK
#     zips
#
# Compression type information
# https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT
# Section 4.4.5
#

import getopt, sys
import zipfile
from collections import namedtuple

imagelist = [".png", ".jpg", ".jpeg", ".bmp", ".gif"]

ApkData = namedtuple("ApkData", "storedsize uctotalsize assetsize metainfsize xmlsize miscsize cassetsize ucassetsize")

def usage():
    print("Go away")

# 0 - The file is stored (no compression)
# 1 - The file is Shrunk
# 2 - The file is Reduced with compression factor 1
# 3 - The file is Reduced with compression factor 2
# 4 - The file is Reduced with compression factor 3
# 5 - The file is Reduced with compression factor 4
# 6 - The file is Imploded
# 7 - Reserved for Tokenizing compression algorithm
# 8 - The file is Deflated
# 9 - Enhanced Deflating using Deflate64(tm)
# 10 - PKWARE Data Compression Library Imploding (old IBM TERSE)
# 11 - Reserved by PKWARE
# 12 - File is compressed using BZIP2 algorithm
# 13 - Reserved by PKWARE
# 14 - LZMA (EFS)
# 15 - Reserved by PKWARE
# 16 - Reserved by PKWARE
# 17 - Reserved by PKWARE
# 18 - File is compressed using IBM TERSE (new)
# 19 - IBM LZ77 z Architecture (PFS)
# 97 - WavPack compressed data
# 98 - PPMd version I, Rev 1
#def compression_type():
    
compression_types = (
(0, 'stored'),
(8, 'deflated'),
)

compression_types_dict = dict(compression_types)

def isasset(f):
    for ext in imagelist:
        if f.endswith(ext):
            return True;
    return False

def getzipinfo(afilename):
    with zipfile.ZipFile(afilename, 'r') as z:
        return z.infolist()

def getapkdata(afilename, totalonly=False):
    storedsize = 0
    uctotalsize = 0
    assetsize = 0
    metainfsize = 0
    xmlsize = 0
    miscsize = 0
    ucassetsize = 0
    cassetsize = 0
    for i in getzipinfo(afilename):
        matched = False
        if i.compress_type != zipfile.ZIP_DEFLATED:
            storedsize += i.file_size
        else:
            storedsize += i.compress_size

        uctotalsize += i.file_size

        if i.filename.startswith("META-INF/"):
            matched = True
            metainfsize += i.file_size

        if isasset(i.filename):
            matched = True
            if i.compress_type != zipfile.ZIP_DEFLATED:
                assetsize += i.file_size
                ucassetsize += i.file_size
            else:
                assetsize += i.compress_size
                cassetsize += i.compress_size

        if i.filename.endswith(".xml"):
            matched = True
            xmlsize += i.file_size

        if not matched:
            miscsize += i.file_size

        if not totalonly:
            print(i.filename, compression_types_dict[i.compress_type],
                  i.compress_size, i.file_size)

    return ApkData(
            storedsize, uctotalsize, assetsize, metainfsize, xmlsize,
            miscsize, cassetsize, ucassetsize)

def parseapk(afilename, totalonly=False):
    d = getapkdata(afilename, totalonly)
    if totalonly:
        print("apk:", afilename)
        print("stored content: ", d.storedsize)
        print("uncompressed content: ", d.uctotalsize)
        print("asset content: ", d.assetsize)
        print("meta content: ", d.metainfsize)
        print("xml content: ", d.xmlsize)
        print("misc content: ", d.miscsize)
        print("matched content total:",
                d.assetsize + d.metainfsize + d.xmlsize + d.miscsize)
        print("compressed asset size:", d.cassetsize)
        print("uncompressed asset size:", d.ucassetsize)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                        "hatf:v", ["help", "all", "total", "file="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err)) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    if len(sys.argv) <= 1:
        usage();
        sys.exit(2)

    verbose = False
    showtotal = False
    allfiles = False
    filearg = False
    filename = sys.argv[1]
    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o in ("-a", "--all"):
            allfiles = True
        elif o in ("-t", "--total"):
            showtotal = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-f", "--file"):
            filename = a
            filearg = True
        else:
            assert False, "unhandled option"

    if filearg:
        parseapk(filename, showtotal)

if __name__ == "__main__":
    main()
