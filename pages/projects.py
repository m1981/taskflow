import streamlit as st
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from todoist_api_python.api import TodoistAPI

# Load environment variables
load_dotenv()

# Cache configuration
CACHE_DURATION_HOURS = 24
CACHE_FILE = "projects_cache.json"

def load_cache():
    """Load projects from local cache file"""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
                cache_time = datetime.fromisoformat(cache_data['timestamp'])
                
                # Check if cache is still valid
                if datetime.now() - cache_time < timedelta(hours=CACHE_DURATION_HOURS):
                    return cache_data['projects']
    except Exception as e:
        st.error(f"Error loading cache: {e}")
    return None

def save_cache(projects):
    """Save projects to local cache file"""
    try:
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'projects': projects
        }
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache_data, f, indent=2)
    except Exception as e:
        st.error(f"Error saving cache: {e}")

def fetch_projects(api):
    """Fetch projects from Todoist API"""
    try:
        projects_raw = api.get_projects()
        projects = []
        
        # Convert paginator to list and flatten if needed
        all_projects = list(projects_raw)
        
        # Flatten nested lists
        flattened_projects = []
        for item in all_projects:
            if isinstance(item, list):
                flattened_projects.extend(item)
            else:
                flattened_projects.append(item)
        
        for project in flattened_projects:
            projects.append({
                'id': project.id,
                'name': project.name,
                'color': project.color,
                'is_favorite': project.is_favorite,
                'is_inbox_project': getattr(project, 'inbox_project', project.is_inbox_project if hasattr(project, 'is_inbox_project') else False),
                'parent_id': project.parent_id,
                'order': getattr(project, 'child_order', project.order if hasattr(project, 'order') else 0) or 0,
                'comment_count': getattr(project, 'comment_count', 0)
            })
        
        return projects
    except Exception as e:
        st.error(f"Error fetching projects: {e}")
        return []

def organize_projects_hierarchy(projects):
    """Organize projects in hierarchical structure with tree indicators"""
    project_map = {p['id']: p for p in projects}
    organized = []
    
    def add_project_with_children(project, depth=0, is_last=True, parent_prefix=""):
        # Add tree structure indicators
        if depth == 0:
            prefix = ""
            next_prefix = ""
        else:
            prefix = parent_prefix + ("└── " if is_last else "├── ")
            next_prefix = parent_prefix + ("    " if is_last else "│   ")
        
        project['depth'] = depth
        project['tree_prefix'] = prefix
        organized.append(project)
        
        # Add children
        children = [p for p in projects if p['parent_id'] == project['id']]
        children.sort(key=lambda x: (x['order'], x['name']))
        
        for i, child in enumerate(children):
            is_last_child = (i == len(children) - 1)
            add_project_with_children(child, depth + 1, is_last_child, next_prefix)
    
    # Start with root projects (no parent)
    root_projects = [p for p in projects if not p['parent_id']]
    root_projects.sort(key=lambda x: (x['order'], x['name']))
    
    for i, project in enumerate(root_projects):
        is_last_root = (i == len(root_projects) - 1)
        add_project_with_children(project, 0, is_last_root)
    
    return organized

def main():
    st.set_page_config(
        page_title="Projects - TaskFlow",
        page_icon="📁",
        layout="wide"
    )
    
    st.title("📁 Projects Overview")
    
    # Sidebar for API key and controls
    with st.sidebar:
        api_key = st.text_input(
            "Todoist API Key",
            value=os.getenv('TODOIST_API_KEY', ''),
            type="password"
        )
        
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            refresh_clicked = st.button("🔄 Refresh", use_container_width=True)
        with col2:
            clear_cache = st.button("🗑️ Clear Cache", use_container_width=True)
    
    if not api_key:
        st.warning("Please enter your Todoist API key in the sidebar")
        return
    
    # Clear cache if requested
    if clear_cache:
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
            st.success("Cache cleared!")
            st.rerun()
    
    # Load projects (from cache or API)
    projects = None
    cache_used = False
    
    if not refresh_clicked:
        projects = load_cache()
        if projects:
            cache_used = True
    
    if projects is None:
        try:
            api = TodoistAPI(api_key)
            with st.spinner("Fetching projects from Todoist..."):
                projects = fetch_projects(api)
                if projects:
                    save_cache(projects)
        except Exception as e:
            st.error(f"Failed to connect to Todoist API: {e}")
            return
    
    if not projects:
        st.warning("No projects found")
        return
    
    # Display cache status
    if cache_used:
        st.info("📦 Data loaded from cache")
    else:
        st.success("🔄 Data refreshed from Todoist")
    
    # Organize projects hierarchically
    organized_projects = organize_projects_hierarchy(projects)
    
    # Display projects
    st.subheader(f"Total Projects: {len(projects)}")
    
    # Create columns for better layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        for project in organized_projects:
            # Create indentation based on hierarchy depth
            indent = "　" * project['depth']  # Using full-width space for better alignment
            
            # Add tree structure indicators
            if project['depth'] > 0:
                tree_indicator = "└── " if project['depth'] == 1 else "　　└── "
            else:
                tree_indicator = ""
            
            # Project icon based on type
            if project['is_inbox_project']:
                icon = "📥"
            elif project['is_favorite']:
                icon = "⭐"
            else:
                icon = "📁"
            
            # Color indicator
            color_indicator = f"🟢" if project['color'] == 'green' else \
                             f"🔵" if project['color'] == 'blue' else \
                             f"🔴" if project['color'] == 'red' else \
                             f"🟡" if project['color'] == 'yellow' else \
                             f"🟣" if project['color'] == 'purple' else \
                             f"🟠" if project['color'] == 'orange' else "⚪"
            
            # Display project with tree structure
            st.markdown(f"{indent}{tree_indicator}{icon} **{project['name']}** {color_indicator}")
    
    with col2:
        st.subheader("Legend")
        st.markdown("📥 Inbox Project")
        st.markdown("⭐ Favorite")
        st.markdown("📁 Regular Project")
        st.markdown("🟢🔵🔴🟡🟣🟠⚪ Colors")

if __name__ == "__main__":
    main()