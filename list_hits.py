#!/usr/bin/env python3
# coding: utf8

"""

"""


import os
import sys
import h5py as h5
import subprocess
import re
import argparse
from collections import defaultdict
import pandas as pd


class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('-i','--i', type=str, help="Input stream file")
    parser.add_argument('-f','--f', type=str, help="Input file with list of streams file")
    return parser.parse_args()


def parsing_stream(input_stream, list_with_hits):
    out = open(list_with_hits, 'w')
    
    total_filenames = 0
    total_hits = 0

    with open(input_stream, 'r') as stream:
        
        found_pattern = False
        hit = -10

        for line in stream:
            
            if line.startswith('Image filename:'):
                name_of_file = line.split()[-1]
                total_filenames += 1
                found_pattern = True

            elif line.startswith('Event:'):
                event = line.split('//')[-1]
                
            elif line.startswith('hit ='):
                hit = int(line.split(' = ')[-1])

            elif found_pattern and hit == 1:
                total_hits += hit
                new_line = "{} //{}".format(name_of_file, event)
                out.write(new_line)
                found_pattern = False
                hit = -10

            else:
                pass
    print("Total hits = {}, total records = {} for {}".format(total_hits, total_filenames, input_stream))
    out.close()

    if total_hits == 0:
        print("Number of hits is zero. Delete {}".format(list_with_hits))
        os.remove(list_with_hits)


if __name__ == "__main__":
    args = parse_cmdline_args()
    input_list_of_stream = args.f
    
    if input_list_of_stream is not None:
        path = os.path.dirname(input_list_of_stream)
        with open(input_list_of_stream, 'r') as f:
            for input_stream in f:
                if len(input_stream.strip()) != 0:
                    input_stream2 = os.path.basename(input_stream.strip())
                    list_with_hits = os.path.join(path, input_stream2.split('.')[0]+"_hits.lst")
                    print("Work with {}, output list with hits is {}\n".format(input_stream2, list_with_hits))
                    parsing_stream(input_stream.strip(), list_with_hits)
                else:
                    continue
    elif args.i is not None:
        parsing_stream(args.i, args.i.split('.')[0]+"_hits.lst")
    else:
        print('Warning: you have to provide file with list of streams or a single stream!')