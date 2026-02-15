import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

st.title("CPU Scheduling Visualizer")

# ---------------- Input ----------------

num = st.number_input("Enter number of processes", min_value=1, step=1)

processes = []

for i in range(int(num)):
    arrival = st.number_input(f"Arrival Time P{i+1}", min_value=0, step=1, key=f"a{i}")
    burst = st.number_input(f"Burst Time P{i+1}", min_value=1, step=1, key=f"b{i}")
    processes.append({"id": f"P{i+1}", "arrival": arrival, "burst": burst})

algo = st.selectbox("Select Algorithm", ["FCFS", "SJF", "SRTF", "Round Robin"])

if algo == "Round Robin":
    quantum = st.number_input("Enter Time Quantum", min_value=1, step=1)


# ---------------- FCFS ----------------

def fcfs(processes):
    processes = sorted(processes, key=lambda x: x['arrival'])
    time = 0
    schedule = []
    completion = {}

    for p in processes:
        if time < p['arrival']:
            time = p['arrival']
        start = time
        finish = start + p['burst']
        schedule.append((p['id'], start, finish))
        completion[p['id']] = finish
        time = finish

    return schedule, completion


# ---------------- SJF (Non-Preemptive) ----------------

def sjf(processes):
    processes = sorted(processes, key=lambda x: (x['arrival'], x['burst']))
    time = 0
    schedule = []
    completion = {}
    completed = []
    remaining = processes.copy()

    while remaining:
        available = [p for p in remaining if p['arrival'] <= time]

        if not available:
            time += 1
            continue

        p = min(available, key=lambda x: x['burst'])
        remaining.remove(p)

        start = time
        finish = start + p['burst']
        schedule.append((p['id'], start, finish))
        completion[p['id']] = finish
        time = finish

    return schedule, completion


# ---------------- SRTF (Preemptive) ----------------

def srtf(processes):
    time = 0
    schedule = []
    completion = {}
    remaining = {p['id']: p['burst'] for p in processes}
    arrived = []

    while remaining:
        for p in processes:
            if p['arrival'] == time:
                arrived.append(p)

        available = [p for p in arrived if p['id'] in remaining]

        if available:
            current = min(available, key=lambda x: remaining[x['id']])
            schedule.append((current['id'], time, time+1))
            remaining[current['id']] -= 1

            if remaining[current['id']] == 0:
                completion[current['id']] = time+1
                del remaining[current['id']]
        time += 1

    return schedule, completion


# ---------------- Round Robin ----------------

def round_robin(processes, quantum):
    time = 0
    schedule = []
    completion = {}
    queue = []
    remaining = {p['id']: p['burst'] for p in processes}

    processes = sorted(processes, key=lambda x: x['arrival'])
    i = 0

    while queue or i < len(processes):
        while i < len(processes) and processes[i]['arrival'] <= time:
            queue.append(processes[i])
            i += 1

        if queue:
            p = queue.pop(0)
            run_time = min(quantum, remaining[p['id']])
            start = time
            finish = time + run_time
            schedule.append((p['id'], start, finish))
            time = finish
            remaining[p['id']] -= run_time

            while i < len(processes) and processes[i]['arrival'] <= time:
                queue.append(processes[i])
                i += 1

            if remaining[p['id']] > 0:
                queue.append(p)
            else:
                completion[p['id']] = time
        else:
            time += 1

    return schedule, completion


# ---------------- Gantt Chart ----------------

def draw_gantt(schedule):
    fig, ax = plt.subplots()

    y = 10
    for pid, start, finish in schedule:
        ax.broken_barh([(start, finish-start)], (y, 9))
        ax.text(start + (finish-start)/2, y+4, pid, ha='center')

    ax.set_xlabel("Time")
    ax.set_yticks([])
    st.pyplot(fig)


# ---------------- RUN ----------------

if st.button("Run Scheduling"):

    if algo == "FCFS":
        schedule, completion = fcfs(processes)

    elif algo == "SJF":
        schedule, completion = sjf(processes)

    elif algo == "SRTF":
        schedule, completion = srtf(processes)

    elif algo == "Round Robin":
        schedule, completion = round_robin(processes, quantum)

    st.subheader("Gantt Chart")
    draw_gantt(schedule)

    # ----- Table -----
    data = []
    total_wt = 0
    total_tat = 0

    for p in processes:
        ct = completion[p['id']]
        tat = ct - p['arrival']
        wt = tat - p['burst']

        total_wt += wt
        total_tat += tat

        data.append([p['id'], p['arrival'], p['burst'], ct, tat, wt])

    df = pd.DataFrame(data, columns=["Process", "Arrival", "Burst", "Completion", "TAT", "WT"])

    st.subheader("Process Table")
    st.table(df)

    st.write("Average Waiting Time:", total_wt / len(processes))
    st.write("Average Turnaround Time:", total_tat / len(processes))

