
import time
import bisect

class TodoJob():
    ''' Something to happen later '''

    def __init__(self, up, when, what):
        self.when = when
        self.what = what
        self.up = up

    def __lt__(self, other):
        return self.when < other.when

    def dt(self):
        return self.when - time.time()

    def doit(self):
        self.what()

class ToDo():

    ''' Get things done '''

    def __init__(self):
        self.todo_list = []

    def schedule(self, when, what):
        if when < 10000:
            when += time.time()
        j = TodoJob(self, when, what)
        bisect.insort(self.todo_list, j)
        return j

    def cancel(self, j):
        try:
            self.todo_list.remove(j)
        except ValueError:
            pass

    def next_timeout(self):
        while self.todo_list:
            j = self.todo_list[0]
            dt = j.dt()
            if dt > 0:
                return dt
            self.todo_list.pop(0)
            j.doit()
        return 3
