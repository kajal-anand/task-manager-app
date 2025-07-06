# AI Innovation Feature

This Task Management API integrates three AI-powered features to enhance productivity and organization: AI Task Prioritizer, AI-Powered Task Tagging, and AI Sub-task Generator. Built with FastAPI, SQLAlchemy, and a responsive HTML/CSS/JavaScript frontend using Jinja2 templates, the application leverages Google's Gemini 1.5 Flash model for all AI operations, ensuring efficient and scalable task management.

## Setup

1. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Add your Gemini API key to .env as GEMINI_API_KEY
   uvicorn app.main:app --reload
   ```

2. **Access Frontend**
   - Open `http://localhost:8000` in your browser.
   - The frontend is served via FastAPI using Jinja2 templates with CSS for styling.

## Dependencies

- Python 3.8+
- FastAPI, Uvicorn, SQLAlchemy, python-dotenv, google-generativeai, Jinja2
- See `requirements.txt` for the full list:
  ```
  fastapi
  uvicorn
  sqlalchemy
  python-dotenv
  google-generativeai
  jinja2
  ```

## API Endpoints

- `POST /api/tasks/`: Create a new task with AI-assigned priority and tags.
- `GET /api/tasks/`: List top-level tasks with optional filtering (`?status=upcoming`, `?priority=high`, `?tag=work`, `?ordering=-priority`).
- `GET /api/tasks/{id}`: Retrieve a specific task, including its tags and sub-tasks.
- `PATCH /api/tasks/{id}`: Update a task (title, description, deadline, or completion status).
- `DELETE /api/tasks/{id}`: Delete a task.
- `POST /api/tasks/{id}/generate-subtasks/`: Generate sub-tasks for a given task.



### Option A: AI Task Prioritizer

**Why It's Valuable**:
- Automatically assigns priority levels (Low, Medium, High, Critical) to tasks based on their content, helping users focus on critical tasks without manual effort, thus improving productivity and decision-making.

**Technical Implementation**:
- **Model**: Uses Google's Gemini 1.5 Flash API for its high free-tier limits (15 requests per minute, 1,500 requests per day) and reliable performance.
- **Database**: Added `priority` field to the `Task` model as an Enum (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
- **Logic**: When a task is created via `POST /api/tasks/`, the backend calls the `AIService.prioritize_task` method, which sends a prompt to Gemini 1.5 Flash:  
  _"Analyze the following task and classify its priority as 'Low', 'Medium', 'High', or 'Critical'. Task Title: [title], Description: [description]. Return only the priority level."_
- **Response Handling**: The API response is parsed, validated against valid priority levels, and stored in the task’s `priority` field. Defaults to `LOW` on failure.
- **API Support**: The `GET /api/tasks/` endpoint supports filtering by priority (e.g., `?priority=high`) and sorting (e.g., `?ordering=-priority`).

**How to Use**:
- Create a task via `POST /api/tasks/` with a JSON body:
  ```json
  {
    "title": "Prepare project report",
    "description": "Compile data and draft report by Friday",
    "deadline": "2025-07-11T17:00:00"
  }
  ```
- The response includes the AI-assigned priority:
  ```json
  {
    "id": 1,
    "title": "Prepare project report",
    "description": "Compile data and draft report by Friday",
    "deadline": "2025-07-11T17:00:00",
    "status": "upcoming",
    "priority": "high",
    "completed": false,
    "created_at": "2025-07-06T14:27:00",
    "updated_at": "2025-07-06T14:27:00",
    "tags": [],
    "subtasks": []
  }
  ```
- Filter tasks by priority: `GET /api/tasks/?priority=high&ordering=-priority`.

### Option B: AI-Powered Task Tagging

**Why It's Valuable**:
- Automatically generates relevant tags (e.g., Work, Personal, Urgent) for tasks, enabling easy searching and organization, which streamlines task management and improves user efficiency.

**Technical Implementation**:
- **Model**: Uses Gemini 1.5 Flash for tag generation, ensuring quota-friendly operation.
- **Database**: Added a `Tag` model and a `task_tags` association table for a Many-to-Many relationship with `Task`.
- **Logic**: During task creation (`POST /api/tasks/`), the backend calls `AIService.generate_tags`, sending a prompt to Gemini 1.5 Flash:  
  _"Based on the following task, generate up to 3 relevant one-word tags from the following list: [Work, Personal, Health, Finance, Learning, Urgent, Shopping]. Return them as a JSON array of strings. Task Title: [title], Description: [description]."_
- **Response Handling**: The JSON response is parsed, validated against the allowed tag list, and limited to 3 tags. Tags are either reused (if existing) or created and associated with the task.
- **Sub-task Integration**: Sub-tasks inherit their parent’s tags for consistency.
- **API Support**: The `GET /api/tasks/` endpoint supports filtering by tag (e.g., `?tag=work`).

**How to Use**:
- Create a task via `POST /api/tasks/` as above. The response includes AI-generated tags:
  ```json
  {
    "id": 1,
    "title": "Prepare project report",
    "description": "Compile data and draft report by Friday",
    "deadline": "2025-07-11T17:00:00",
    "status": "upcoming",
    "priority": "high",
    "completed": false,
    "created_at": "2025-07-06T14:27:00",
    "updated_at": "2025-07-06T14:27:00",
    "tags": [{"id": 1, "name": "work"}, {"id": 2, "name": "urgent"}],
    "subtasks": []
  }
  ```
- Filter tasks by tag: `GET /api/tasks/?tag=work`.

### Option C: AI Sub-task Generator

**Why It's Valuable**:
- Breaks down complex tasks into smaller, actionable sub-tasks, simplifying project management and enabling users to tackle large tasks incrementally.

**Technical Implementation**:
- **Model**: Uses Gemini 1.5 Flash for generating sub-task titles.
- **Database**: Added a self-referencing `parent_id` ForeignKey to the `Task` model, with `parent` and `subtasks` relationships for hierarchical task structures.
- **Logic**: A dedicated endpoint `POST /api/tasks/{id}/generate-subtasks/` retrieves the parent task, calls `AIService.generate_subtasks` with the prompt:  
  _"You are a project manager. Break down the following task into a list of smaller, actionable sub-tasks. Return the result as a JSON array of simple task titles. Task Title: [title], Description: [description]."_
- **Response Handling**: The JSON response is parsed, limited to 5 sub-tasks, and new `Task` objects are created with the parent’s deadline and tags, linked via `parent_id`.
- **API Support**: The endpoint returns the created sub-tasks. Sub-tasks are included in the parent task’s `subtasks` field in `GET /api/tasks/` responses.

**How to Use**:
- Create a task (e.g., ID 1) via `POST /api/tasks/`.
- Generate sub-tasks: `POST /api/tasks/1/generate-subtasks/`.
- Response example:
  ```json
  [
    {
      "id": 2,
      "title": "Research mountain destinations",
      "description": null,
      "deadline": "2025-07-11T17:00:00",
      "parent_id": 1,
      "status": "upcoming",
      "priority": "low",
      "completed": false,
      "created_at": "2025-07-06T14:30:00",
      "updated_at": "2025-07-06T14:30:00",
      "tags": [{"id": 1, "name": "work"}, {"id": 2, "name": "urgent"}],
      "subtasks": []
    },
    {
      "id": 3,
      "title": "Book accommodations",
      "description": null,
      "deadline": "2025-07-11T17:00:00",
      "parent_id": 1,
      "status": "upcoming",
      "priority": "low",
      "completed": false,
      "created_at": "2025-07-06T14:30:00",
      "updated_at": "2025-07-06T14:30:00",
      "tags": [{"id": 1, "name": "work"}, {"id": 2, "name": "urgent"}],
      "subtasks": []
    }
  ]
  ```
- View sub-tasks in the parent task via `GET /api/tasks/1`.

## Features

- **AI Integration**: All features use Gemini 1.5 Flash for priority assignment, tag generation, and sub-task creation, with robust error handling and logging.
- **Task Hierarchy**: Sub-tasks are linked to parents via `parent_id` and only appear nested in API responses and UI, avoiding duplication.
- **Filtering and Sorting**: Filter tasks by status, priority, or tag; sort by any field (e.g., `-priority` for descending).
- **Responsive UI**: Frontend displays tasks with tags and sub-tasks, with indentation for sub-tasks and filter tabs for status and tags.
- **Time-Aware Status**: Automatically updates task status based on deadlines and completion.
- **Error Handling**: Comprehensive logging to `app.log` with rotation (max 1MB, 5 backups).

## Notes

- **Gemini API Quotas**: The free tier of Gemini 1.5 Flash allows 15 requests per minute and 1,500 requests per day. If you encounter 429 quota errors, enable billing in Google Cloud Console for higher limits (check https://ai.google.dev/pricing).
- **Environment Configuration**: Set `GEMINI_API_KEY` in `.env` with your Gemini API key. Other settings (e.g., `LOG_LEVEL`, `API_TIMEOUT`) are configurable in `.env`.
- **Database**: Uses SQLite (`tasks.db`) for simplicity, with SQLAlchemy for ORM.
- **Frontend**: Built with Jinja2 templates, Tailwind CSS, and vanilla JavaScript for real-time updates without page refresh.

## Example Workflow
1. Create a task: `POST /api/tasks/` with title "Plan a team trip" and description "Organize a 3-day trip to the mountains".
2. The task receives an AI-assigned priority (e.g., "high") and tags (e.g., ["work", "urgent"]).
3. Generate sub-tasks: `POST /api/tasks/1/generate-subtasks/` to create sub-tasks like "Research destinations", "Book accommodations", inheriting parent tags.
4. View tasks: `GET /api/tasks/?status=upcoming` to see top-level tasks with nested sub-tasks and tags.
5. Filter by tag: `GET /api/tasks/?tag=work` to list tasks with the "work" tag.



### Explanation
- **Scope**: The README covers all three AI features (Options A, B, and C) as implemented in the latest codebase
- **AI Model**: Specifies Gemini 1.5 Flash for all features, chosen for its higher free-tier limits and reliability.
- **Value and Implementation**: Each feature’s purpose, technical details (e.g., database changes, API prompts, response handling), and usage instructions are clearly documented.
- **API Usage**: Provides example API calls and responses for clarity, aligning with the endpoints in `main.py`.
- **Setup and Notes**: Includes comprehensive setup steps, dependency list, and guidance on handling Gemini API quotas.
