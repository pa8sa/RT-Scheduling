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

this system has 1 waiting queue and 3 core that each of them has 1 ready queue .

this system has some features like load balancing including pull migration and push migration , starvation avoiding using aging in waiting queue , running tasks based on WRR algorithm and ...

### Sub System 2

this system has 1 ready queue and 2 core that use this ready queue shared .

this system has some features like running tasks based on SRTF algorithm , hold and wait for resources , deadlock avoidance and ...

### Sub System 3



### Sub System 4

this system has 1 waiting queue and 2 cores that using 1 ready queue shared .

this system has some features like running tasks based on FCFS algorithm , starvation avoiding using aging in waiting queue , handles failing tasks with 30% probability , handles that prerequisite for a task has to be executed before it and ...