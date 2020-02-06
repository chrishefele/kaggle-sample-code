from contextlib import contextmanager
import multiprocessing
import sys
from time import time

@contextmanager
def timer(label):
    # timer(), as suggested by Sang Han 
    output = '{label}: {time:03.3f} sec'
    start = time()
    try:
        yield
    finally:
        end = time()
    print(output.format(label=label, time=end-start))
    sys.stdout.flush()

def worker(n):
    with timer("string creation time"):
        b = b'*' * n
    return b

def main():

    n_processes = 4
    file_name = "outfile.txt"

    mil = 1000*1000 
    str_len = 30*mil
    
    args = [str_len]*n_processes
    processes = multiprocessing.Pool(n_processes)
    
    t0 = time()
    results = processes.map(worker, args)
    print("time to map:",  time()-t0)
    
    with timer("time to write all strings sequentially"):
        fout = open(file_name, "wb")
        for result in results:
            fout.write(result)
        fout.close()

if __name__ == '__main__':
    main()

