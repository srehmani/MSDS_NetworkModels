# import required packages
import matplotlib.pyplot as plt
import pulp

# Setup tasks
tasks = ['A', 'B', 'C', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'E', 'F', 'G', 'H']

# Setup task durations by scenario
durations = {
    'best': {
        'A': 10, 'B': 12, 'C': 8, 'D': 195, 'D1': 20, 'D2': 30, 'D3': 40, 'D4': 45,
        'D5': 20, 'D6': 15, 'D7': 15, 'D8': 10, 'E': 10, 'F': 8, 'G': 5, 'H': 3
    },
    'expected': {
        'A': 15, 'B': 18, 'C': 12, 'D': 245, 'D1': 25, 'D2': 40, 'D3': 50, 'D4': 55,
        'D5': 25, 'D6': 20, 'D7': 18, 'D8': 12, 'E': 16, 'F': 10, 'G': 7, 'H': 5
    },
    'worst': {
        'A': 20, 'B': 24, 'C': 16, 'D': 335, 'D1': 35, 'D2': 50, 'D3': 70, 'D4': 75,
        'D5': 35, 'D6': 30, 'D7': 25, 'D8': 15, 'E': 20, 'F': 16, 'G': 10, 'H': 7
    }
}

# Task precedence (based on directed graph)
precedences = {
    'C': ['A'], 'D1': ['A'], 'D2': ['D1'], 'D3': ['D1'], 'D4': ['D2', 'D3'],
    'D5': ['D4'], 'D6': ['D4'], 'D7': ['D6'], 'D8': ['D5', 'D7'],
    'E': ['B', 'C'], 'F': ['D8', 'E'], 'G': ['A', 'D8'], 'H': ['F', 'G']
}

# Create solver function
def solve_project_plan(scenario):
    
    # Create a linear programming problem
    model = pulp.LpProblem("Project_Min_Time", pulp.LpMinimize)

    # Decision variables
    start_times = pulp.LpVariable.dicts("Start", tasks, lowBound=0, cat='Continuous')

    # Project completion time should be the same as Task H completion time
    project_completion = pulp.LpVariable("Completion", lowBound=0, cat='Continuous')

    # Objective function
    model += project_completion, "Minimize_Total_Project_Time"

    # Constraints:    
    
    # Task dependencies (precedences)
    for task, preds in precedences.items():
        for pred in preds:
            # predecessors dependency
            model += start_times[task] >= start_times[pred] + durations[scenario][pred], f"Precedence_{pred}_to_{task}"

    # Project completion time must be after Task H completes
    model += project_completion >= start_times['H'] + durations[scenario]['H'], "Project_Completion_After_Task_H"

    # Solve
    model.solve()

    # Output
    start_times_solution = {task: pulp.value(start_times[task]) for task in tasks}
    total_project_time = pulp.value(model.objective)

    print(f"Project plan for the '{scenario}' scenario.")
    print(f"Status: {pulp.LpStatus[model.status]}")
    for task in tasks:
        print(f"{start_times[task].name} = {start_times_solution[task]}")
    print(f"Total Project Time = {total_project_time}")

    # Return dataset for plotting
    return start_times_solution, total_project_time

# Gantt chart
def plot_gchart(start_times, durations, scenario):
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    task_labels = tasks
    task_colors = plt.cm.tab20c(range(len(tasks)))

    for i, task in enumerate(tasks):
        start_time = start_times[task]
        duration = durations[scenario][task]
        
        ax.barh(i, duration, left=start_time, color=task_colors[i])
        
        ax.text(start_time + duration / 2, i, f'{task} ({duration}h)', 
                va='center', ha='left', color='black')

    ax.set_yticks(range(len(tasks)))
    ax.set_yticklabels(task_labels)
    ax.set_xlabel('Time')
    ax.set_title(f'Gantt Chart {scenario.capitalize()} Scenario')
    plt.grid(True)
    plt.show()

################################################################################################################################
# select scenario
chosen_scenario = 'expected'

# solve
start_times_solution, total_project_time = solve_project_plan(chosen_scenario)

# generate plot
plot_gchart(start_times_solution, durations, chosen_scenario)
