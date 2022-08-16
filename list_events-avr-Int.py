#!/usr/bin/env python3
# coding: utf8

"""

"""


import os
import sys
import argparse
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt

class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass


def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('-i','--i', type=str, help="Input a stream file")
    parser.add_argument('-f', '--f', type=str, help="Input a file with list of streams")
    parser.add_argument('-t','--t', type=float, help='Output stream file')
    return parser.parse_args()

def parsing_stream(input_stream, output_stream, treshold):
    out = open(output_stream, 'w')
    data = defaultdict(dict)
    with open(input_stream, 'r') as stream:
        
        in_list = 0

        for line in stream:
            line = line.strip()
            if line.startswith('Image filename:'):
                name_of_file = line.split()[-1]
                continue
            if line.startswith('Event:'):
                event = line.split('//')[-1]
                if "{} //{}".format(name_of_file, event) not in data:
                    data["{} //{}".format(name_of_file, event)] = {'Int':0, 'N':0}
                continue
            if line.find("Reflections measured after indexing") != -1:
                in_list = 1
                continue
            if line.find("End of reflections") != -1:
                in_list = 0
            if in_list == 1:
                in_list = 2
                continue
            elif in_list != 2:
                continue

            # From here, we are definitely handling a reflection line

            # Add reflection to list
            columns = line.split()
            
            try:
                data["{} //{}".format(name_of_file, event)]['Int'] += float(columns[3])
                data["{} //{}".format(name_of_file, event)]['N'] += 1
            except:
                print("Error with line: "+line.rstrip("\r\n"))
    
    d = []
    for key in data.keys():
        try:
            AvrInt = np.round(data[key]['Int'] / data[key]['N'], 2)
            if treshold is None:
                out.write(key+'\n')
            elif treshold and AvrInt > treshold:
                out.write(key+'\n')
            d.append(AvrInt)
        except:
            print(f'Not indexed {key}')
            pass
    out.close()
    plt.hist(d, bins=100, label="Avr Int")
    plt.show()


if __name__ == "__main__":
    args = parse_cmdline_args()
    
    if args.f is not None:
        with open(input_list_of_stream, 'r') as f:
            for input_stream in f:
                path = os.path.dirname(input_stream)            
                input_stream2 = os.path.basename(input_stream.strip())
                output_stream = os.path.join(path, input_stream2.split('.')[0]+"_all_events.lst")
                print(f'Output list is {output_stream}')
                parsing_stream(input_stream.strip(), output_stream, args.t)
    elif args.i is not None:
        input_stream = os.path.basename(args.i)
        path = os.path.dirname(args.i)
        output_stream = os.path.join(path, input_stream.split('.')[0]+"_all_events.lst")
        print(f'Output list is {output_stream}')
        parsing_stream(args.i, output_stream, args.t)
    else:
        print('Warning: you have to provide file with list of streams or a single stream!')