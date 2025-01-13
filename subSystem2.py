import globals
import threading
from typing import List
from queue import Queue
from task import Task
from resource_ import Resource_

ready_queue = Queue()

def core(index, resources: List[Resource_]):
    pass

def subSystem2(resources: List[Resource_], tasks: List[Task]):
    global ready_queue
    
    for task in tasks:
        ready_queue.put(task)    
            
    task_list = list(ready_queue.queue)
    task_list.sort(key=lambda task: task.duration)
    ready_queue = Queue()
    for task in task_list:
        ready_queue.put(task)

    cores = []
    for i in range(2):
        t = threading.Thread(target=core, args=(i, resources))
        cores.append(t)
        t.start()
        
    for t in cores:
        t.join()
