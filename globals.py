import threading

time_unit = -1

breaking_point = 25

def increment_time_unit():
  global time_unit
  time_unit += 1

global_start_barrier = threading.Barrier(8, action=increment_time_unit)
global_finish_barrier = threading.Barrier(8)

print_turn = 1
print_turn_lock = threading.Lock()
