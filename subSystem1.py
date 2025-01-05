import threading

def core():
    ready_queue = []
    pass

def subSystem1(Rs, tasks):
    for r in Rs:
        print(r.name)
    for task in tasks:
        print(task.name)
    print(f'{__name__} says hello!')
    waiting_queue = []
    cores = []
    for i in range(3):
        t = threading.Thread(target=core)
        cores.append(t)
        t.start()
    
    for t in cores:
        t.join()
