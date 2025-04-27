Get all projects:
```
from todoist_api_python.api import TodoistAPI

api = TodoistAPI("0123456789abcdef0123456789")

try:
projects = api.get_projects()
print(projects)
except Exception as error:
print(error)
```

Example response:

```
[
    Project(
        id: "220474322",
        name: "Inbox",
        comment_count: 10,
        order: 0,
        color: "grey",
        is_shared: False,
        is_favorite: False,
        is_inbox_project: True,
        is_team_inbox: False,
        view_style: "list",
        url: "https://todoist.com/showProject?id=220474322",
        parent_id: None,
    )
]
```

Get all sections:

```
from todoist_api_python.api import TodoistAPI

api = TodoistAPI("0123456789abcdef0123456789")

try:
    sections = api.get_sections(project_id="2203306141")
    print(sections)
except Exception as error:
    print(error)
```

```
[
    Section(
        id: "7025",
        project_id: "2203306141",
        order: 1,
        name: "Groceries"
    )
]
```

Get active tasks:

```
from todoist_api_python.api import TodoistAPI

api = TodoistAPI("0123456789abcdef0123456789")

try:
    tasks = api.get_tasks()
    print(tasks)
except Exception as error:
    print(error)
```

```
[
    Task(
        creator_id: "2671355",
        created_at: "2019-12-11T22:36:50.000000Z",
        assignee_id: "2671362",
        assigner_id: "2671355",
        comment_count: 10,
        is_completed: False,
        content: "Buy Milk",
        description: "",
        due: {
            date: "2016-09-01",
            is_recurring: false,
            datetime: "2016-09-01T12:00:00.000000Z",
            string: "tomorrow at 12",
            timezone: "Europe/Moscow"
        },
        deadline: {
            date: "2016-09-04"
        },
        duration: None,
        id: "2995104339",
        labels: ["Food", "Shopping"],
        order: 1,
        priority: 1,
        project_id: "2203306141",
        section_id: "7025",
        parent_id: "2995104589",
        url: "https://todoist.com/showTask?id=2995104339"
    )
]
```


Update a task:

```
from todoist_api_python.api import TodoistAPI

api = TodoistAPI("0123456789abcdef0123456789")

try:
    is_success = api.update_task(task_id="2995104339", content="Buy Coffee")
    print(is_success)
except Exception as error:
    print(error)
```

```
Task(
    creator_id: "2671355",
    created_at: "2019-12-11T22:36:50.000000Z",
    assignee_id: "2671362",
    assigner_id: "2671355",
    comment_count: 10,
    is_completed: False,
    content: "Buy Coffee",
    description: "",
    due: {
        date: "2016-09-01",
        is_recurring: false,
        datetime: "2016-09-01T12:00:00.000000Z",
        string: "tomorrow at 12",
        timezone: "Europe/Moscow"
    },
    deadline: {
        date: "2016-09-04"
    },
    duration: None,
    id: "2995104339",
    labels: ["Food", "Shopping"],
    order: 1,
    priority: 1,
    project_id: "2203306141",
    section_id: "7025",
    parent_id: "2995104589",
    url: "https://todoist.com/showTask?id=2995104339"
)
```