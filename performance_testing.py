import shutil
import os
import time
import commentController
import checkAPI
import restrictor
import isolator
import cProfile
import re
import pstats
n = 5
def generate():
    # set the source file name and path
    source_file = 'C:\\Users\\Rund\\Desktop\\Yad\\testfiles\\testPlanClass.cpp'

    # loop through 500 times to create copies of the file
    for i in range(n):
        # set the destination file name and path
        dest_file = f'C:\\Users\\Rund\\Desktop\\Yad\\per\\test{i+1}.cpp'
        # copy the source file to the destination
        shutil.copyfile(source_file, dest_file)
        print(f'File copy {i+1} created.')
        


def test():
    for i in range(1, n):
        # construct the filename
        filename = "C:\\Users\\Rund\\Desktop\\Yad\\per\\test{}.cpp".format(i)
        rest = "C:\\Users\\Rund\\Desktop\\Yad\\restrict.yaml"
        destination = "C:\\Users\\Rund\\Desktop\\Yad\\testfiles\\destination.cpp"
    
        # commentController.deleteComments(filename, "")
        restrictor.restrict(filename, rest, "n")
        isolator.isolateClass(filename, destination, "class C1class", "true")
        isolator.isolateClass(filename, destination, "class Fclass", "false")
        isolator.isolateFunction(filename, destination, "Fclass::Fclass()")
        checkAPI.main(filename, destination, "at_least")
    
if __name__ == "__main__":
    generate()
    test()
    cProfile.run('test()', "output.txt")
    with open("output_time.txt", "w") as f:
        p = pstats.Stats("output.dat", stream=f)
        p.sort_stats("time").print_stats()