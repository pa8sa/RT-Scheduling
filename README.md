# RT-Scheduling

## Overview

RT-Scheduling is a real-time task scheduling simulation project. The project simulates the scheduling of tasks across multiple subsystems, each with its own set of resources and cores. The tasks have various attributes such as duration, resource usage, entering time, and other parameters specific to each subsystem.

## Project Structure

The project consists of the following files:

- `main.py`: The main entry point of the project. It initializes the resources and tasks, and starts the scheduling simulation.
- `task.py`: Defines the `Task` class, which represents a task with various attributes.
- `resource_.py`: Defines the `Resource_` class, which represents a resource with a count and a name.
- `core.py`: Defines the `Core` class, which represents a core that can execute tasks and calculate various metrics such as average waiting time, turnaround time, and response time.
- `globals.py`: Contains global variables and synchronization primitives used across the project.
- `subSystem1.py`, `subSystem2.py`, `subSystem3.py`, `subSystem4.py`: Implement the scheduling logic for each subsystem.

## Running the Simulation

To run the simulation, execute the `main.py` script:

```sh
python main.py
```
main.py is the main system of the project that creates 4 threads for each subsystem .
this file gets inputs from in.txt , creates threads for each subsystem , waits until subsystems finishes and print the waiting time , turnaround time and response time for each core of each subsystem

### Sub System 1  
- **Cores**: 3 cores, each with a dedicated ready queue.
- **Features**:  
  - **Scheduling Algorithm**: Weighted Round Robin (WRR) with dynamic quantum based on task weights.
  - **Load Balancing**: Push/pull migration between cores to balance queue lengths.
  - **Starvation Avoidance**: Aging mechanism in the waiting queue (older tasks gain priority).
  - **Resource Management**: Tasks temporarily release resources during execution pauses.

### Sub System 2  
- **Cores**: 2 cores sharing a single ready queue.
- **Features**:  
  - **Scheduling Algorithm**: Shortest Remaining Time First (SRTF) for minimal latency.
  - **Deadlock Avoidance**: Atomic resource allocation (tasks acquire all resources upfront).
  - **Queue Sorting**: Ready queue dynamically sorted by task durations.

### Sub System 3  
- **Cores**: 1 core with a priority-based ready queue.
- **Features**:  
  - **Scheduling Algorithm**: Rate Monotonic Scheduling (RMS) for periodic tasks.
  - **Resource Borrowing**: Borrows resources from other subsystems if local resources are insufficient.
  - **Periodic Tasks**: Supports recursion and re-entrant tasks with defined periods (e.g., sensor polling).
  - **Preemption**: Higher-priority tasks preempt lower-priority ones.

### Sub System 4  
- **Cores**: 2 cores sharing a ready queue and a waiting queue.
- **Features**:  
  - **Scheduling Algorithm**: First-Come-First-Served (FCFS) with aging in the waiting queue.
  - **Fault Handling**: 30% probability of task failure, with retry logic.
  - **Prerequisites**: Tasks can specify dependencies (e.g., "TaskB must run after TaskA").
  - **Deterministic Sorting**: Ready queue sorted by entering time and duration.

---