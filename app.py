import streamlit as st
# Must be the first Streamlit command
st.set_page_config(
    page_title="TaskFlow",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="auto"
)

import os
from dotenv import load_dotenv
from todoist_api_python.api import TodoistAPI
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.grid_options_builder import GridOptionsBuilder

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

        # Convert your data to a pandas DataFrame
        rows = []
        for project in organized_items:
            project_tasks = tasks_by_project.get(project.id, [])
            
            # Define global tasks first
            global_tasks = [t for t in project_tasks if not t.section_id and t.content != "Description"]
            
            # Add global tasks
            for task in sorted(global_tasks, key=lambda x: (x.order or 0, x.content)):
                rows.append({
                    'Project': project.name,
                    'Task ID': task.id,
                    'Project ID': task.project_id,
                    'Section ID': task.section_id or '-',
                    'Parent ID': task.parent_id or '-',
                    'Order': task.order or 0,
                    'Section': '-',
                    'Task': task.content,
                    'Labels': ", ".join(task.labels) if task.labels else '',
                    'Due Date': task.due.date if task.due else ''
                })
                
            # Add section tasks
            sections = sections_by_project.get(project.id, [])
            for section in sorted(sections, key=lambda x: (x.order or 0, x.name)):
                section_tasks = [t for t in project_tasks if t.section_id == section.id]
                for task in sorted(section_tasks, key=lambda x: (x.order or 0, x.content)):
                    rows.append({
                        'Project': project.name,
                        'Task ID': task.id,
                        'Project ID': task.project_id,
                        'Section ID': task.section_id,
                        'Parent ID': task.parent_id or '-',
                        'Order': task.order or 0,
                        'Section': section.name,
                        'Task': task.content,
                        'Labels': ", ".join(task.labels) if task.labels else '',
                        'Due Date': task.due.date if task.due else ''
                    })
        
        df = pd.DataFrame(rows)
        
        # Configure grid options with wider columns and 200 rows per page
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(resizable=True, filterable=True, sorteable=True)
        gb.configure_pagination(enabled=True, 
                              paginationAutoPageSize=False, 
                              paginationPageSize=200)  # Set to 200 results per page
        
        # Configure column widths
        gb.configure_column('Project', minWidth=150)
        gb.configure_column('Task ID', minWidth=100)
        gb.configure_column('Project ID', minWidth=100)
        gb.configure_column('Section ID', minWidth=100)
        gb.configure_column('Parent ID', minWidth=100)
        gb.configure_column('Order', minWidth=80)
        gb.configure_column('Section', minWidth=150)
        gb.configure_column('Task', minWidth=300)  # Make task column wider
        gb.configure_column('Labels', minWidth=200)
        gb.configure_column('Due Date', minWidth=120)
        
        grid_options = gb.build()
        
        # Display the grid with custom height
        AgGrid(df, 
               gridOptions=grid_options,
               allow_unsafe_jscode=True,
               theme='streamlit',
               height=800,  # Set a fixed height for the grid
               fit_columns_on_grid_load=True)  # Make columns fit the screen width

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    main()