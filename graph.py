import matplotlib.pyplot as plt
import networkx as nx

from app import schedule_projects, PROJECTS
 
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

if __name__ == "__main__":
    num_days, num_slots, num_rooms = 5, 4, 3
    schedule, _ = schedule_projects(num_days, num_slots, num_rooms, PROJECTS)
    plot_schedule_graph(schedule, PROJECTS)