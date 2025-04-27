import os
from dotenv import load_dotenv
import streamlit as st
from todoist_api_python.api import TodoistAPI

# Load environment variables from .env file
load_dotenv()

def get_project_descriptions(api, projects):
    project_descriptions = {}
    for project in projects:
        tasks = api.get_tasks(project_id=project.id)

        description_found = False
        for task in tasks:
            if task.content == "Description":
                if task.description:
                    project_descriptions[project.id] = task.description
                    description_found = True
                    break

        if not description_found:
            project_descriptions[project.id] = "-----------------"

    return project_descriptions

def get_project_tasks(api, project_id):
    return api.get_tasks(project_id=project_id)

def get_project_sections(api, project_id):
    return api.get_sections(project_id=project_id)

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

        with st.spinner("Loading projects..."):
            projects = api.get_projects()
            project_descriptions = get_project_descriptions(api, projects)
            organized_items = organize_projects_and_sections(projects)

        with st.expander("All Projects", expanded=True):
            for item in organized_items:
                indent = "    " * item.depth
                
                col1, col2 = st.columns([2, 3])
                with col1:
                    st.markdown(f"**{item.name}**")
                with col2:
                    st.markdown(project_descriptions[item.id])
                
                # Add this section to show tasks and sections
                sections = get_project_sections(api, item.id)
                tasks = get_project_tasks(api, item.id)
                
                # Show tasks without sections
                unsectioned_tasks = [t for t in tasks if not t.section_id]
                for task in unsectioned_tasks:
                    st.markdown(f"{indent}  • {task.content}")
                
                # Show sections and their tasks
                for section in sections:
                    st.markdown(f"{indent}  📑 **{section.name}**")
                    section_tasks = [t for t in tasks if t.section_id == section.id]
                    for task in section_tasks:
                        st.markdown(f"{indent}    • {task.content}")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("Please check your API key and try again")

if __name__ == '__main__':
    main()