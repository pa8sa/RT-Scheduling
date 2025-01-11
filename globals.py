import threading

time_unit = 0
sys1_ready_threads = 0
sys1_finish_threads = 0
sys1_ready_threads_lock = threading.Lock()
sys1_finish_threads_lock = threading.Lock()