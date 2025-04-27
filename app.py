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
        for project in sorted(projects, key=lambda x: x.name):
            if project.parent_id == parent_id:
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

        # Build the markdown table
        table_lines = []
        # Add table header
        table_lines.append("| Project | Section | Task | Labels | Due Date |")
        table_lines.append("|---------|----------|------|--------|----------|")

        for project in organized_items:
            project_tasks = tasks_by_project.get(project.id, [])
            
            # Global tasks (no section)
            for task in project_tasks:
                if not task.section_id and task.content != "Description":
                    due_str = task.due.date if task.due else ''
                    labels_str = ", ".join(task.labels) if task.labels else ''
                    # Escape special characters in all fields
                    project_name = escape_markdown(project.name)
                    task_content = escape_markdown(task.content)
                    labels_str = escape_markdown(labels_str)
                    line = f"| {project_name} | - | {task_content} | {labels_str} | {due_str} |"
                    table_lines.append(line)
            
            # Section tasks
            for section in sections_by_project.get(project.id, []):
                section_tasks = [t for t in project_tasks if t.section_id == section.id]
                for task in section_tasks:
                    due_str = task.due.date if task.due else ''
                    labels_str = ", ".join(task.labels) if task.labels else ''
                    # Escape special characters in all fields
                    project_name = escape_markdown(project.name)
                    section_name = escape_markdown(section.name)
                    task_content = escape_markdown(task.content)
                    labels_str = escape_markdown(labels_str)
                    line = f"| {project_name} | {section_name} | {task_content} | {labels_str} | {due_str} |"
                    table_lines.append(line)

        # Display the markdown table
        st.markdown("\n".join(table_lines))

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    main()