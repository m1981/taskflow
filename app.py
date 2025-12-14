import streamlit as st
# Must be the first Streamlit command
st.set_page_config(
    page_title="TaskFlow",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="auto"
)

import os
import time
from dotenv import load_dotenv
from todoist_api_python.api import TodoistAPI
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
import streamlit.components.v1 as components

# Load environment variables from .env file
load_dotenv()

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_all_data(_api):
    """Cached version of data fetching"""
    print("DEBUG: Starting get_all_data")
    
    print("DEBUG: Fetching projects...")
    projects = list(_api.get_projects())
    print(f"DEBUG: Got {len(projects)} projects, type: {type(projects)}")
    
    print("DEBUG: Fetching tasks...")
    all_tasks_raw = list(_api.get_tasks())
    print(f"DEBUG: Got tasks_raw, type: {type(all_tasks_raw)}, length: {len(all_tasks_raw)}")
    
    print("DEBUG: Fetching sections...")
    all_sections = list(_api.get_sections())
    print(f"DEBUG: Got sections, type: {type(all_sections)}, length: {len(all_sections)}")
    
    # Flatten tasks if they're nested in lists
    print("DEBUG: Flattening tasks...")
    all_tasks = []
    for i, item in enumerate(all_tasks_raw):
        print(f"DEBUG: Item {i} type: {type(item)}")
        if isinstance(item, list):
            print(f"DEBUG: Item {i} is a list with {len(item)} elements")
            all_tasks.extend(item)
        else:
            print(f"DEBUG: Item {i} is not a list, appending directly")
            all_tasks.append(item)
    
    print(f"DEBUG: After flattening, all_tasks length: {len(all_tasks)}")
    if all_tasks:
        print(f"DEBUG: First task type: {type(all_tasks[0])}")
    
    # Create task maps
    print("DEBUG: Creating task maps...")
    tasks_by_project = {}
    tasks_by_section = {}
    for i, task in enumerate(all_tasks):
        print(f"DEBUG: Processing task {i}, type: {type(task)}")
        try:
            # Map by project
            project_id = task.project_id
            print(f"DEBUG: Task {i} project_id: {project_id}")
        except AttributeError as e:
            print(f"DEBUG: ERROR on task {i}: {e}")
            print(f"DEBUG: Task content: {task}")
            raise
        
        # Map by section
        section_id = task.section_id
        if section_id:
            if section_id not in tasks_by_section:
                tasks_by_section[section_id] = []
            tasks_by_section[section_id].append(task)
    
    print("DEBUG: Mapping sections by project...")
    # Map sections by project
    sections_by_project = {}
    for i, section in enumerate(all_sections):
        print(f"DEBUG: Section {i} type: {type(section)}")
        if isinstance(section, list):
            print(f"DEBUG: Section {i} is a list with {len(section)} elements")
            print(f"DEBUG: First element type: {type(section[0]) if section else 'empty'}")
        else:
            print(f"DEBUG: Section {i} is not a list, processing directly")
        
        project_id = section.project_id
        if project_id not in sections_by_project:
            sections_by_project[project_id] = []
        sections_by_project[project_id].append(section)
    
    print("DEBUG: Getting project descriptions...")
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
    
    print("DEBUG: get_all_data completed successfully")
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
    
    # Add navigation
    tab1, tab2 = st.tabs(["Tasks View", "Projects View"])
    
    with tab2:
        # Import and run projects page
        import pages.projects as projects_page
        projects_page.main()
        return
    
    with tab1:
        # Your existing task view code
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
                print("DEBUG: Data fetched, organizing projects...")
                organized_items = organize_projects_and_sections(projects)
                print(f"DEBUG: Organized {len(organized_items)} items")

            # Filter for only "Test" project
            print("DEBUG: Filtering for Test project...")
            test_projects = [p for p in organized_items if p.name == "Test"]
            print(f"DEBUG: Found {len(test_projects)} Test projects")

            # Debug: Check what we actually have
            st.write(f"Debug - organized_items type: {type(organized_items)}")
            if organized_items:
                st.write(f"Debug - first item type: {type(organized_items[0])}")
                st.write(f"Debug - first item: {organized_items[0]}")

            # Convert your data to a pandas DataFrame
            rows = []
            for project in test_projects:
                st.write(f"Debug - project type: {type(project)}")
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
        
            if not rows:
                st.warning("No project named 'Test' found or no tasks in the Test project")
                return
            
            df = pd.DataFrame(rows)
            
            # Configure grid options
            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_default_column(resizable=True, filterable=True, sorteable=True)
            gb.configure_pagination(enabled=True, 
                                  paginationAutoPageSize=False, 
                                  paginationPageSize=200)
            
            # Add checkbox selection
            gb.configure_selection(selection_mode='multiple', use_checkbox=True)
            
            # Configure column widths
            gb.configure_column('Project', minWidth=150)
            gb.configure_column('Task ID', minWidth=100)
            gb.configure_column('Project ID', minWidth=100)
            gb.configure_column('Section ID', minWidth=100)
            gb.configure_column('Parent ID', minWidth=100)
            gb.configure_column('Order', minWidth=80)
            gb.configure_column('Section', minWidth=150)
            gb.configure_column('Task', minWidth=300)
            gb.configure_column('Labels', minWidth=200)
            gb.configure_column('Due Date', minWidth=120)
            
            grid_options = gb.build()
            
            # Display the grid and get the response FIRST
            grid_response = AgGrid(df, 
                                 gridOptions=grid_options,
                                 allow_unsafe_jscode=True,
                                 theme='streamlit',
                                 height=800,
                                 fit_columns_on_grid_load=True)

            # Now add action buttons AFTER grid is displayed
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Close Selected Tasks"):
                    selected_rows = grid_response['selected_rows']
                    if selected_rows:
                        with st.spinner("Closing selected tasks..."):
                            for row in selected_rows:
                                try:
                                    api.close_task(task_id=row['Task ID'])
                                    st.success(f"Closed task: {row['Task']}")
                                except Exception as e:
                                    st.error(f"Failed to close task {row['Task']}: {str(e)}")
                            time.sleep(1)  # Small delay to ensure UI updates
                            st.rerun()
                    else:
                        st.warning("No tasks selected")

            with col2:
                if st.button("Delete Selected Tasks"):
                    selected_rows = grid_response['selected_rows']
                    if selected_rows:
                        with st.spinner("Deleting selected tasks..."):
                            for row in selected_rows:
                                try:
                                    api.delete_task(task_id=row['Task ID'])
                                    st.success(f"Deleted task: {row['Task']}")
                                except Exception as e:
                                    st.error(f"Failed to delete task {row['Task']}: {str(e)}")
                            time.sleep(1)  # Small delay to ensure UI updates
                            st.rerun()
                    else:
                        st.warning("No tasks selected")

            with col3:
                if st.button("Add Label to Selected"):
                    selected_rows = grid_response['selected_rows']
                    if selected_rows:
                        label = st.text_input("Enter label name:")
                        if label and st.button("Apply Label"):
                            with st.spinner("Applying label..."):
                                for row in selected_rows:
                                    try:
                                        current_labels = row['Labels'].split(", ") if row['Labels'] else []
                                        current_labels.append(label)
                                        api.update_task(
                                            task_id=row['Task ID'],
                                            labels=list(set(current_labels))
                                        )
                                        st.success(f"Added label to task: {row['Task']}")
                                    except Exception as e:
                                        st.error(f"Failed to add label to task {row['Task']}: {str(e)}")
                                time.sleep(1)  # Small delay to ensure UI updates
                                st.rerun()
                    else:
                        st.warning("No tasks selected")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    main()