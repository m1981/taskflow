import os
from dotenv import load_dotenv
import streamlit as st
from todoist_api_python.api import TodoistAPI
import pandas as pd
# Load environment variables from .env file
load_dotenv()

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_all_data(_api):
    """Cached version of data fetching"""
    projects = _api.get_projects()
    all_tasks = _api.get_tasks()
    all_sections = _api.get_sections()  # Get ALL sections at once
    
    # Create task maps
    tasks_by_project = {}
    tasks_by_section = {}
    for task in all_tasks:
        # Map by project
        project_id = task.project_id
        if project_id not in tasks_by_project:
            tasks_by_project[project_id] = []
        tasks_by_project[project_id].append(task)
        
        # Map by section
        section_id = task.section_id
        if section_id:
            if section_id not in tasks_by_section:
                tasks_by_section[section_id] = []
            tasks_by_section[section_id].append(task)
    
    # Map sections by project
    sections_by_project = {}
    for section in all_sections:
        project_id = section.project_id
        if project_id not in sections_by_project:
            sections_by_project[project_id] = []
        sections_by_project[project_id].append(section)
    
    # Get descriptions from tasks
    project_descriptions = {}
    for project in projects:
        project_tasks = tasks_by_project.get(project.id, [])
        description = next(
            (task.description for task in project_tasks 
             if task.content == "Description" and task.description),
            "-----------------"
        )
        project_descriptions[project.id] = description
    
    return projects, tasks_by_project, project_descriptions, sections_by_project

def organize_projects_and_sections(projects):
    organized_items = []
    project_map = {project.id: project for project in projects}

    def add_items(parent_id, depth):
        parent_projects = [p for p in projects if p.parent_id == parent_id]
        # Sort projects by order
        for project in sorted(parent_projects, key=lambda x: (x.order or 0, x.name)):
            project.depth = depth
            organized_items.append(project)
            add_items(project.id, depth + 2)

    add_items(None, 0)
    return organized_items

def format_task_line(task, project_name, section_name=""):
    due_date = task.due.date if task.due else ''
    labels = ", ".join(task.labels) if task.labels else ""
    section_name = section_name.ljust(20)
    return f"{project_name.ljust(20)} {section_name} {task.content.ljust(50)} {labels.ljust(20)} {due_date}"

def escape_markdown(text):
    """Escape special characters that could break markdown table formatting"""
    if not isinstance(text, str):
        return text
    # Escape pipes, which are table separators in markdown
    text = text.replace("|", "\\|")
    # Replace tabs and multiple spaces with a single space
    text = " ".join(text.split())
    # Escape other special markdown characters if needed
    special_chars = ['*', '_', '[', ']', '(', ')', '#', '+', '-', '.', '!']
    for char in special_chars:
        text = text.replace(char, f"\\{char}")
    return text

def truncate_text(text, max_length=50):
    """Truncate text to max_length characters, adding ellipsis if needed"""
    if not isinstance(text, str):
        return text
    return (text[:max_length - 3] + '...') if len(text) > max_length else text

def format_project_name(project_name, depth):
    """Format project name with proper indentation"""
    indent = "  " * depth  # Two spaces per depth level
    return f"{indent}{project_name}"

def format_tree_line(indent_level, is_last, text):
    """Format a line in tree-style ASCII art"""
    if indent_level == 0:
        return text
    
    indent = "│   " * (indent_level - 1)
    prefix = "└── " if is_last else "├── "
    return f"{indent}{prefix}{text}"

def main():
    st.title("📋 TaskFlow")
    
    with st.sidebar:
        api_key = st.text_input(
            "Todoist API Key",
            value=os.getenv('TODOIST_API_KEY', ''),
            type="password"
        )

    if not api_key:
        st.warning("Please enter your Todoist API key in the sidebar")
        return

    try:
        api = TodoistAPI(api_key)
        
        with st.spinner("Loading Todoist data..."):
            projects, tasks_by_project, project_descriptions, sections_by_project = get_all_data(api)
            organized_items = organize_projects_and_sections(projects)

        # Build the ASCII tree
        tree_lines = []

        for project_idx, project in enumerate(organized_items):
            is_last_project = project_idx == len(organized_items) - 1
            project_line = format_tree_line(project.depth, is_last_project, project.name)
            tree_lines.append(project_line)
            
            project_tasks = tasks_by_project.get(project.id, [])
            
            # Global tasks (no section)
            global_tasks = [t for t in project_tasks if not t.section_id and t.content != "Description"]
            sorted_global_tasks = sorted(global_tasks, key=lambda x: (x.order or 0, x.content))
            
            sections = sections_by_project.get(project.id, [])
            has_sections = bool(sections)
            
            # Process global tasks
            for task_idx, task in enumerate(sorted_global_tasks):
                is_last_task = (task_idx == len(sorted_global_tasks) - 1) and not has_sections
                due_str = task.due.date if task.due else ''
                labels_str = ", ".join(task.labels) if task.labels else ''
                task_info = f"{task.content} [{labels_str}] {due_str}"
                task_line = format_tree_line(project.depth + 1, is_last_task, task_info)
                tree_lines.append(task_line)
            
            # Process sections and their tasks
            sorted_sections = sorted(sections, key=lambda x: (x.order or 0, x.name))
            for section_idx, section in enumerate(sorted_sections):
                is_last_section = section_idx == len(sorted_sections) - 1
                section_line = format_tree_line(project.depth + 1, is_last_section, f"[{section.name}]")
                tree_lines.append(section_line)
                
                section_tasks = [t for t in project_tasks if t.section_id == section.id]
                sorted_section_tasks = sorted(section_tasks, key=lambda x: (x.order or 0, x.content))
                
                for task_idx, task in enumerate(sorted_section_tasks):
                    is_last_task = task_idx == len(sorted_section_tasks) - 1
                    due_str = task.due.date if task.due else ''
                    labels_str = ", ".join(task.labels) if task.labels else ''
                    task_info = f"{task.content} [{labels_str}] {due_str}"
                    task_line = format_tree_line(project.depth + 2, is_last_task, task_info)
                    tree_lines.append(task_line)

        # Display as preformatted text
        st.text("\n".join(tree_lines))

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    main()