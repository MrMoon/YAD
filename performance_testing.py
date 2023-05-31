import shutil
import time
import os
import time
import commentController
import checkAPI
import restrictor
import isolator
import cProfile
import re
import pstats

from argparse import ArgumentParser

n = 100
dir_name = os.path.dirname(__file__)

def generate():
    # set the source file name and path
    source_file = os.path.join(dir_name, 'testfiles','testPlanClass.cpp')

    # loop through 500 times to create copies of the file
    for i in range(n):
        # set the destination file name and path
        dest_file = os.path.join(dir_name, 'per', f'test{i+1}.cpp')
        # copy the source file to the destination
        shutil.copyfile(source_file, dest_file)
        print(f'File copy {i+1} created.')
        


def test():
    for i in range(n):
        # construct the filename
        file_name = os.path.join(dir_name, 'per', f'test{i+1}.cpp')
        dest_file = os.path.join(dir_name, 'testfiles', 'destination.cpp')
    
        # commentController.deleteComments(filename, "")
        restrictor.restrict(file_name, os.path.join(dir_name, 'restrict.yaml', 'n'))
        isolator.isolateClass(file_name, dest_file, 'class C1class', 'true')
        isolator.isolateClass(file_name, dest_file, 'class Fclass', 'false')
        isolator.isolateFunction(file_name, dest_file, 'Fclass::Fclass()')
        checkAPI.main(file_name, dest_file, 'at_least')
    
if __name__ == "__main__":
    start = time.time()

    generate()
    print('Generation Done')
    
    test()
    print('Testing Done')
    
    cProfile.run('test()', "output.dat")
    print('cProfile run DONE')
    time_output = os.path.join(dir_name, 'output_time.txt')
    with open(time_output, 'w') as f:
        print('File Opened')
        p = pstats.Stats('output.dat', stream=f)
        p.sort_stats("time").print_stats()
        print('File Written')
        print('File Closed')
    print('Process finished in %s seconds' % (time.time() - start_time))
