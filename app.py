import os
from dotenv import load_dotenv
import streamlit as st
from todoist_api_python.api import TodoistAPI

# Load environment variables from .env file
load_dotenv()

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_all_data(_api):
    """Cached version of data fetching"""
    projects = _api.get_projects()
    all_tasks = _api.get_tasks()  # Gets ALL tasks at once
    
    # Create task maps
    tasks_by_project = {}
    for task in all_tasks:
        project_id = task.project_id
        if project_id not in tasks_by_project:
            tasks_by_project[project_id] = []
        tasks_by_project[project_id].append(task)
    
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
    
    return projects, tasks_by_project, project_descriptions

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

def main():
    st.title("📋 TaskFlow")

    st.markdown("""
        <style>
        .project-item {
            padding: 5px;
            border-radius: 5px;
            margin: 2px 0;
        }
        .project-description {
            color: #666;
            font-style: italic;
        }
        </style>
    """, unsafe_allow_html=True)
    st.markdown("*Intelligent task scheduling and time blocking*")

    with st.sidebar:
        st.header("Configuration")
        api_key = st.text_input(
            "Todoist API Key",
            value=os.getenv('TODOIST_API_KEY', ''),  # Changed from TODOIST_KEY to TODOIST_API_KEY
            type="password"
        )
        st.markdown("*Get your API key from [Todoist Settings](https://todoist.com/app/settings/integrations)*")

    if not api_key:
        st.warning("Please enter your Todoist API key in the sidebar")
        return

    try:
        api = TodoistAPI(api_key)

        with st.spinner("Loading Todoist data..."):
            progress_bar = st.progress(0)
            
            # Fetch data
            progress_bar.progress(20)
            projects, tasks_by_project, project_descriptions = get_all_data(api)
            
            progress_bar.progress(60)
            organized_items = organize_projects_and_sections(projects)
            
            progress_bar.progress(100)
            progress_bar.empty()

        with st.expander("All Projects", expanded=True):
            for item in organized_items:
                indent = "    " * item.depth
                
                col1, col2 = st.columns([2, 3])
                with col1:
                    st.markdown(f"**{item.name}**")
                with col2:
                    st.markdown(project_descriptions[item.id])
                
                # Use pre-fetched tasks
                project_tasks = tasks_by_project.get(item.id, [])
                
                # Group tasks by section
                tasks_by_section = {}
                unsectioned_tasks = []
                for task in project_tasks:
                    if task.section_id:
                        if task.section_id not in tasks_by_section:
                            tasks_by_section[task.section_id] = []
                        tasks_by_section[task.section_id].append(task)
                    else:
                        unsectioned_tasks.append(task)
                
                # Show unsectioned tasks
                for task in unsectioned_tasks:
                    if task.content != "Description":  # Skip description tasks
                        st.markdown(f"{indent}  • {task.content}")
                
                # Show sections and their tasks
                sections = api.get_sections(project_id=item.id)
                for section in sections:
                    st.markdown(f"{indent}  📑 **{section.name}**")
                    section_tasks = tasks_by_section.get(section.id, [])
                    for task in section_tasks:
                        st.markdown(f"{indent}    • {task.content}")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("Please check your API key and try again")

if __name__ == '__main__':
    main()