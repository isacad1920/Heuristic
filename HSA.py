import matplotlib.pyplot as plt  # Import matplotlib for plotting graphs.
import random  # Import random for generating random values.
import copy 
from app import PROJECTS, calculate_penalty, print_schedule, schedule_projects  # Import specific functions and data from app2 module.

def initialize_harmony_memory(HMS, num_days, num_slots, num_rooms, projects):
    # Initialize harmony memory with sorted project schedules based on penalty.
    return sorted(
        [schedule_projects(num_days, num_slots, num_rooms, projects) for _ in range(HMS)],
        key=lambda x: x[1]
    )

def create_empty_schedule(num_days, num_slots, num_rooms):
    # Create a 3D list representing an empty schedule with None values.
    return [[[None for _ in range(num_rooms)] for _ in range(num_slots)] for _ in range(num_days)]

def find_valid_project(available_projects, assigned_projects, assigned_leaders, projects):
    # Find a valid project that is not yet assigned and whose leader is not already assigned.
    valid_projects = [p for p in available_projects if p not in assigned_projects and projects[p]['leader'] not in assigned_leaders]
    return random.choice(valid_projects) if valid_projects else None

def generate_random_schedule(num_days, num_slots, num_rooms, projects):
    # Generate a random project schedule and calculate its penalty.
    schedule = create_empty_schedule(num_days, num_slots, num_rooms)
    available_projects = list(projects.keys())
    assigned_projects = set()

    for day in range(num_days):
        for slot in range(num_slots):
            assigned_leaders = set()
            for room in range(num_rooms):
                project = find_valid_project(available_projects, assigned_projects, assigned_leaders, projects)
                if project:
                    leader = projects[project]['leader']
                    schedule[day][slot][room] = (project, leader, projects[project]['members'])
                    assigned_projects.add(project)
                    assigned_leaders.add(leader)

    fill_remaining_projects(schedule, projects, assigned_projects, num_days, num_slots, num_rooms)
    penalty = calculate_penalty(num_days, num_slots, num_rooms, schedule, projects, len(projects))
    return schedule, penalty

def fill_remaining_projects(schedule, projects, assigned_projects, num_days, num_slots, num_rooms):
    # Assign remaining projects that are not yet scheduled to available slots.
    remaining_projects = [p for p in projects if p not in assigned_projects]
    for project in remaining_projects:
        leader = projects[project]['leader']
        placed = False  # Flag to indicate whether the project is placed.

        for day in range(num_days):
            for slot in range(num_slots):
                for room in range(num_rooms):
                    # Check if room is available and leader constraint is satisfied.
                    if schedule[day][slot][room] is None and leader not in {entry[1] for entry in schedule[day][slot] if entry}:
                        schedule[day][slot][room] = (project, leader, projects[project]['members'])
                        assigned_projects.add(project)
                        placed = True
                        break
                if placed:
                    break
            if placed:
                break

        # Force assign the project if constraints cannot be satisfied.
        if not placed:
            for day in range(num_days):
                for slot in range(num_slots):
                    for room in range(num_rooms):
                        if schedule[day][slot][room] is None:
                            schedule[day][slot][room] = (project, leader, projects[project]['members'])
                            assigned_projects.add(project)
                            placed = True
                            break
                    if placed:
                        break
                if placed:
                    break

    # Ensure all projects are assigned.
    assert all(project in assigned_projects for project in projects), "Not all projects were scheduled!"

def adjust_schedule(solution, num_days, num_slots, num_rooms, projects):
    # Randomly adjust the schedule by replacing a project.
    new_solution = copy.deepcopy(solution)
    day, slot, room = random.randint(0, num_days-1), random.randint(0, num_slots-1), random.randint(0, num_rooms-1)
    assigned_projects = {p[0] for d in new_solution for s in d for p in s if p}

    available_projects = [p for p in projects if p not in assigned_projects or (new_solution[day][slot][room] and p == new_solution[day][slot][room][0])]
    if available_projects:
        project = random.choice(available_projects)
        new_solution[day][slot][room] = (project, projects[project]['leader'], projects[project]['members'])

    return new_solution, calculate_penalty(num_days, num_slots, num_rooms, new_solution, projects, len(projects))

def pitch_adjustment(solution, penalty, num_days, num_slots, num_rooms, projects, PAR):
    # Apply pitch adjustment based on probability threshold (PAR).
    return adjust_schedule(solution, num_days, num_slots, num_rooms, projects) if random.random() < PAR else (solution, penalty)

def update_harmony_memory(harmony_memory, new_solution, new_penalty, HMS):
    # Add new solution to harmony memory and keep the best HMS solutions.
    harmony_memory.append((new_solution, new_penalty))
    return sorted(harmony_memory, key=lambda x: x[1])[:HMS]

def harmony_search(NI, HMS, num_days, num_slots, num_rooms, projects, HMCR, PAR):
    # Perform the harmony search algorithm to optimize project scheduling.
    harmony_memory = initialize_harmony_memory(HMS, num_days, num_slots, num_rooms, projects)
    best_solution, best_penalty = harmony_memory[0]
    list_of_penalty = []
    for _ in range(NI):
        if random.random() < HMCR:
            new_solution, new_penalty = adjust_schedule(best_solution, num_days, num_slots, num_rooms, projects)
        else:
            new_solution, new_penalty = generate_random_schedule(num_days, num_slots, num_rooms, projects)

        new_solution, new_penalty = pitch_adjustment(new_solution, new_penalty, num_days, num_slots, num_rooms, projects, PAR)
        harmony_memory = update_harmony_memory(harmony_memory, new_solution, new_penalty, HMS)
        list_of_penalty.append(new_penalty)

        if new_penalty < best_penalty:
            best_solution, best_penalty = new_solution, new_penalty

    return best_solution, best_penalty, harmony_memory, list_of_penalty

# Parameter settings for harmony search.
NI, HMS, HMCR, PAR = 400, 3, 0.7, 0.3  # Number of iterations, harmony memory size, HMCR, and PAR.
num_days, num_slots, num_rooms, projects = 4, 1, 3, PROJECTS  # Dimensions and project data.

# Execute harmony search to find the best schedule.
best_schedule, best_penalty, final_harmony_memory, list_of_penalty = harmony_search(NI, HMS, num_days, num_slots, num_rooms, projects, HMCR, PAR)

# Output results.
print("Initial Harmony Memory:")
print(schedule_projects(num_days, num_slots, num_rooms, projects))
print("Best Schedule:")
print_schedule(best_schedule)
print("Best Penalty:", best_penalty)
print("Final Harmony Memory:", final_harmony_memory)

# Plot penalty values over iterations.
plt.plot(list_of_penalty)  # Plot penalty vs. iteration.
plt.title('Penalty vs Iterations')  # Set plot title.
plt.ylabel('Penalty')  # Label y-axis.
plt.xlabel('Iteration')  # Label x-axis.
plt.show()  # Display the plot.
