# import urllib.request
import requests
import sys
import os
import time
import curses
from queue import Queue
from contextlib import contextmanager
from threading import *
import glob
from bs4 import BeautifulSoup
import shutil


class Worker(Thread):
    """ Thread executing tasks from a given tasks queue """

    def __init__(self, tasks, tid):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.tid = tid
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except Exception as e:
                print(e)
            finally:
                self.tasks.task_done()


class ThreadPool:
    """ Pool of threads consuming tasks from a queue """

    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for n in range(num_threads):
            Worker(self.tasks, n)

    def add_task(self, func, *args, **kargs):
        """ Add a task to the queue """
        self.tasks.put((func, args, kargs))

    def map(self, func, args_list):
        """ Add a list of tasks to the queue """
        for args in args_list:
            self.add_task(func, args)

    def wait_completion(self):
        """ Wait for completion of all the tasks in the queue """
        self.tasks.join()


BUFFER = ''
TOPR = []
LOCK = Lock()
CV = Condition()
FILESIZE = 0
N_CONN = 8
PBAR = None
stdscr = curses.initscr()
POOL = ThreadPool(N_CONN)
parentFolder = 'Brooklyn 99'


def makeDirs(fileName):
    if not os.path.exists(parentFolder):
        os.makedirs(parentFolder)

    if not os.path.exists(parentFolder + '/' + fileName):
        os.makedirs(parentFolder + '/' + fileName)


@contextmanager
def non_blocking_lock(lock):
    locked = lock.acquire(False)
    try:
        yield locked
    finally:
        if locked:
            lock.release()


def progressPrinter(tDown):
    with non_blocking_lock(LOCK) as l:
        if l:
            per = (sum(tDown)/FILESIZE)*100
            PBAR.setProperty("value", per)
            stdscr.addstr(0, 0, BUFFER.format(*tuple(TOPR)))
            stdscr.refresh()


def downloadFile(url, r, part, tDown):

    ranges = "bytes={}-{}".format(r[0], r[1])
    headers = {"Range": ranges}
    response = requests.get(url, headers=headers, stream=True)
    
    with CV:
        while response.headers['Content-Type'] == 'text/html':
            CV.wait()
            response = requests.get(url, headers=headers, stream=True)
        # return

    chunkSize = 1024
    fileSize = int(response.headers['Content-Length'])
    downloaded = 0
    barLength = 50
    filePath = parentFolder + '/temp/' + str(r[0])

    with open(filePath, 'wb') as f:
        for data in response.iter_content(chunk_size=chunkSize):
            downloaded += len(data)
            f.write(data)
            tDown[part-1] = downloaded 
            done = int(barLength * downloaded / fileSize)
            printer = "[{}{}] {:1.2f}MB of {:1.2f}MB ({:1.2f} percent) of {} done".format('=' * done, ' ' * (barLength-done), (float(downloaded) / (
                1024 * 1024)), (fileSize / (1024 * 1024)), (100 * downloaded / fileSize), part)
            TOPR[part-1] = printer
            progressPrinter(tDown)
    print('\n')

    with CV:
        CV.notifyAll()


def makeRanges(n, ranges):
    r = int(n/ranges)
    toret = []
    s = 0

    for _ in range(1, ranges):
        toret.append((s, s+r))
        s = s+r+1
    toret.append((s, n))

    return toret


def numericalSort(value):
    spl = value.split('/')
    return spl[-1]


def downloadHelp(filename, url, pbar = None):
    global BUFFER, PBAR, FILESIZE

    PBAR = pbar
    response = requests.head(url)
    FILESIZE = int(response.headers['Content-Length'])
    print('downloading ' + filename + ' from ' + url)

    response.close()
    ranges = makeRanges(FILESIZE, N_CONN)
    makeDirs("temp")

    totalDown = []

    for n in range(N_CONN):
        BUFFER += '{}\n'
        totalDown.append(0)
        TOPR.append(
            "[{}] 0MB of 0MB (0 percent) of {} done".format(' ' * 50, n+1))
        POOL.add_task(downloadFile, url, ranges[n], n+1, totalDown)

    POOL.wait_completion()

    filePath = parentFolder + '/' + filename
    files = glob.glob(parentFolder + '/temp/*')
    with open(filePath, 'wb') as f:
        for file in sorted(files, key=numericalSort):
            fl = open(file, 'rb')
            f.write(fl.read())
            fl.close()

    shutil.rmtree(parentFolder + '/temp')


# if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         print("Usage: downloader.py [filename] [url]")
#         exit()

#     stdscr = curses.initscr()
#     curses.noecho()
#     curses.cbreak()

#     try:
#         downloadHelp(
#             sys.argv[1], sys.argv[2]
#         )
#     finally:
#         pass
#         curses.echo()
#         curses.nocbreak()
#         curses.endwin()
