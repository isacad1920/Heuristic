# ---------------------- Helper Functions ----------------------

def check_same_leader(leader, projects):
    """Check if the same leader is assigned to multiple projects."""
    for project in projects:
        if project in PROJECTS and leader == PROJECTS[project]['leader']:
            return True
    return False


def collect_all_members(selected_projects):
  
    # Create an empty set to hold all the members (so no duplicates)
    all_members = set()
    # Loop through each selected project
    for project in selected_projects:
        # Add each project’s members to the set
        all_members.update(PROJECTS[project]['members'])
        # Add the leader to the set too
        all_members.add(PROJECTS[project]['leader'])
    # Return the set of all members
    return all_members


def count_conflicts(all_members, current_project):
  
    # Create a set of the current project’s members, including its leader
    current_members = set(PROJECTS[current_project]['members'])
    current_members.add(PROJECTS[current_project]['leader'])
    # Return how many members from the current project overlap with the already selected members
    return len(all_members & current_members)


def select_project_with_least_conflict(available_projects, selected_projects):
  
    # Start with an infinite number for least conflict
    least_conflict = float('inf')
    # Set selected_project to None to start
    selected_project = None
    
    # Collect all members from the already selected projects
    all_members = collect_all_members(selected_projects)

    # Loop through all available projects to find the one with the least conflict
    for project in available_projects:
        # If the project is already selected, skip it
        if project in selected_projects:
            continue
        
        # If the project’s leader is already scheduled, skip it
        if check_same_leader(PROJECTS[project]['leader'], selected_projects):
            continue
        
        # Count conflicts with the already selected members
        conflicts = count_conflicts(all_members, project)
        
        # If this project has fewer conflicts, choose it
        if conflicts < least_conflict:
            least_conflict = conflicts
            selected_project = project

    # Return the selected project
    return selected_project


def is_last_project_scheduled(all_selected_projects, total_projects):
    """
    Check if the last project (based on the order) is assigned.
    """
    # If the number of selected projects equals the total number of projects, return True
    return len(all_selected_projects) == total_projects


# ---------------------- Penalty Calculation Functions ----------------------

def calculate_unoccupied_room_penalty(num_days, num_slots, num_rooms, schedule, all_selected_projects, total_projects):
  
    # Start with no penalty
    penalty = 0
    # If the last project hasn't been scheduled, check for unoccupied rooms
    if not is_last_project_scheduled(all_selected_projects, total_projects):
        # Loop through all days and slots to check for empty rooms
        for day in range(num_days):
            for slot in range(num_slots):
                # Count how many rooms are occupied in this slot
                occupied_rooms = sum(1 for room in range(num_rooms) if schedule[day][slot][room] is not None)
                # If any rooms are empty, penalize
                if occupied_rooms > 0:
                    penalty += (num_rooms - occupied_rooms) * 3
    # Return the total penalty
    return penalty


def calculate_member_conflicts_penalty(num_days, num_slots, num_rooms, schedule):

    penalty = 0
    # Loop through all days and slots
    for day in range(num_days):
        for slot in range(num_slots):
            # Create a list of researchers in this slot
            researchers_in_slot = []
            for room in range(num_rooms):
                # If the room is not empty
                if schedule[day][slot][room] is not None:
                    # Get the leader and members of the project in this room
                    _, leader, members = schedule[day][slot][room]
                    # Add the leader and members to the list
                    researchers_in_slot.append(leader)
                    researchers_in_slot.extend(members)
            # Penalize if there are duplicate members (conflicts)
            penalty += len(researchers_in_slot) - len(set(researchers_in_slot))
    # Return the penalty for conflicts
    return penalty


def calculate_idle_time_penalty(num_days, num_slots, num_rooms, schedule):
    
    # Start with no penalty
    penalty = 0
    # Dictionary to keep track of when each researcher is scheduled
    researcher_schedules = {}

    # Loop through all days and slots to collect meeting times
    for day in range(num_days):
        for slot in range(num_slots):
            for room in range(num_rooms):
                # If the room is not empty
                if schedule[day][slot][room] is not None:
                    # Get the leader and members for this room’s project
                    _, leader, members = schedule[day][slot][room]
                    # Add the researcher’s day and slot to their schedule
                    attendees = [leader] + members
                    for researcher in attendees:
                        if researcher not in researcher_schedules:
                            researcher_schedules[researcher] = []
                        researcher_schedules[researcher].append((day, slot))

    # Loop through each researcher’s schedule to check for idle time
    for researcher, meetings in researcher_schedules.items():
        meetings.sort()  # Sort meetings by day and slot
        for i in range(len(meetings) - 1):
            # If two meetings are on the same day
            if meetings[i][0] == meetings[i + 1][0]:
                gap = meetings[i + 1][1] - meetings[i][1]
                # If there’s a gap of more than 1 slot, penalize for idle time
                if gap > 1:
                    penalty += gap - 1

    # Return the idle time penalty
    return penalty


def calculate_penalty(num_days, num_slots, num_rooms, schedule, all_selected_projects, total_projects):
    
    # Start with no penalty
    penalty = 0
    # Add penalties for unoccupied rooms, member conflicts, and idle time
    penalty += calculate_unoccupied_room_penalty(num_days, num_slots, num_rooms, schedule, all_selected_projects, total_projects)
    penalty += calculate_member_conflicts_penalty(num_days, num_slots, num_rooms, schedule)
    penalty += calculate_idle_time_penalty(num_days, num_slots, num_rooms, schedule)
    # Return the total penalty
    return penalty


# ---------------------- Main Scheduling Function ----------------------

def schedule_projects(num_days, num_slots, num_rooms, projects):
    
    # Initialize a 3D list to hold the schedule for all days, slots, and rooms
    schedule = [[[None for _ in range(num_rooms)] for _ in range(num_slots)] for _ in range(num_days)]
    # Keep track of which projects have been selected
    all_selected_projects = []
    # Get the total number of projects
    total_projects = len(projects)

    # Loop through all days and slots to assign projects to rooms
    for day in range(num_days):
        for slot in range(num_slots):
            # Get a list of available projects that haven’t been selected yet
            available_projects = [p for p in projects if p not in all_selected_projects]
            selected_projects_for_slot = []

            for room in range(num_rooms):
                # Select the project with the least conflict
                selected_project = select_project_with_least_conflict(available_projects, selected_projects_for_slot)

                # If a project is selected, assign it to this room
                if selected_project:
                    schedule[day][slot][room] = (selected_project, PROJECTS[selected_project]['leader'], PROJECTS[selected_project]['members'])
                    selected_projects_for_slot.append(selected_project)
                    all_selected_projects.append(selected_project)

    # After scheduling, calculate the total penalty
    penalty = calculate_penalty(num_days, num_slots, num_rooms, schedule, all_selected_projects, total_projects)
    
    return schedule, penalty


# ---------------------- Output Functions ----------------------

def print_schedule(schedule):
    
    # Loop through all days, slots, and rooms in the schedule
    for day, slots in enumerate(schedule):
        for slot, rooms in enumerate(slots):
            for room, meeting in enumerate(rooms):
                # If the room has a scheduled project, print it
                if meeting is not None:
                    project_id, leader, _ = meeting
                    print(f"Day={day + 1}, Slot={slot + 1}, Room={room + 1} -> Project {project_id} (Leader: {leader}) (Members: {', '.join(PROJECTS[project_id]['members'])})")

# ---------------------- Main Program ----------------------

PROJECTS = {
    "P1": {"leader": "A", "members": ["B", "C", "D", "E"]},
    "P2": {"leader": "B", "members": ["A", "E", "F", "G"]},
    "P3": {"leader": "C", "members": ["B", "D", "E", "G"]},
    "P4": {"leader": "D", "members": ["A", "B", "F", "G"]},
    "P5": {"leader": "A", "members": ["C", "D", "G", "H"]},
    "P6": {"leader": "B", "members": ["A", "E", "G", "H"]},
    "P7": {"leader": "C", "members": ["B", "E", "G", "H"]},
    "P8": {"leader": "A", "members": ["B", "D", "F", "G"]},
    "P9": {"leader": "B", "members": ["A", "C", "D", "E"]},
    "P10": {"leader": "E", "members": ["A", "B", "C", "D"]},
}

if __name__ == "__main__":
    num_days = 4
    num_slots = 1
    num_rooms = 3

    # Schedule projects
    schedule, penalty = schedule_projects(num_days, num_slots, num_rooms, PROJECTS)

    print("Schedule:")
    print_schedule(schedule)
    print(schedule)

    # Print the total penalty
    print(f"\nTotal Penalty: {penalty}")


# ---------------------- Helper Functions ----------------------
import matplotlib.pyplot as plt
import networkx as nx
 
def draw_graph():

    def plot_schedule_graph(schedule, projects):
        # Collect unique projects from the schedule
        unique_projects = {room[0] for day in schedule for slot in day for room in slot if room}

        # Create a graph
        G = nx.Graph()

        # Assign unique colors to projects
        color_map = plt.cm.tab10(range(len(unique_projects)))
        project_colors = {project: color_map[idx % len(color_map)] for idx, project in enumerate(unique_projects)}

        # Add nodes for each project
        for project in unique_projects:
            G.add_node(project, label=project, color=project_colors[project])

        # Add edges based on shared members
        for project in unique_projects:
            members = set(projects[project]['members'])
            leader = projects[project]['leader']
            for other_project in unique_projects:
                if project != other_project:
                    other_members = set(projects[other_project]['members'])
                    other_leader = projects[other_project]['leader']
                    if leader in other_members or other_leader in members or members & other_members:
                        G.add_edge(project, other_project, color='black')  # Conflict edges are red

        # Extract node and edge colors
        node_colors = [data['color'] for _, data in G.nodes(data=True)]
        edge_colors = [data['color'] for _, _, data in G.edges(data=True)]

        # Draw the graph
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_size=3000, node_color=node_colors, font_size=10, font_weight="bold")
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors)
        labels = nx.get_node_attributes(G, 'label')
        nx.draw_networkx_labels(G, pos, labels)
        plt.title("Project Schedule and Conflicts")
        plt.show()

