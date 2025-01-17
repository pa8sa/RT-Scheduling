import threading

time_unit = -1

subsystems_ready_cycle = 0
subsystems_finish_cycle = 0
subsystems_ready_cycle_lock = threading.Lock()
subsystems_finish_cycle_lock = threading.Lock()

sys1_ready_threads = 0
sys1_finish_threads = 0
sys1_ready_threads_lock = threading.Lock()
sys1_finish_threads_lock = threading.Lock()

sys2_ready_threads = 0
sys2_finish_threads = 0
sys2_ready_threads_lock = threading.Lock()
sys2_finish_threads_lock = threading.Lock()

def wait_for_subsystems_start_together():
  while True:
    if subsystems_ready_cycle == 2:
      break

def wait_for_subsystems_finish_together():
  while True:
    if subsystems_finish_cycle == 2:
      break