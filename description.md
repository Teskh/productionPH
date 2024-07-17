# Production Tracking App

## Project Overview

The Production Tracking App is a web-based application designed for monitoring and managing production activities across multiple lines and stations in a manufacturing setting. It's primarily used on tablets positioned at various stations along production lines, allowing workers to log their activities and track production data in real-time. The application is designed for a Spanish-speaking userbase, with all user-facing content presented in Spanish.

## Key Components and Their Relationships

### 1. Application Structure (app/__init__.py)

This file initializes the Flask application and sets up the background scheduler for automatic task pausing at the end of the day.
- `create_app()`: Creates and configures the Flask application, registers blueprints, and starts the background scheduler.

### 2. Configuration (config.py)

Defines the configuration for the application, including file paths and debug settings.

### 3. Data Management (data_manager.py)

Handles loading data from Excel files:
- `load_worker_data()`: Loads worker information, including supervisors, names, numbers, specialties, and gender.
- `load_project_data()`: Loads project details, including total houses and number of modules.
- `load_activity_data()`: Loads activities categorized by specialty.

These functions are used in routes.py to populate the necessary data for the application.

### 4. Utility Functions (app/utils.py)

Provides utility functions:
- `format_timestamp()`: Formats the current timestamp.
- `init_excel_file()`: Initializes or updates the Excel file structure for storing production data.

### 5. Models (app/models.py)

Defines the Task class with static methods for interacting with the Excel-based data store:
- `get_active_tasks()`: Retrieves active tasks for a worker.
- `get_all_active_tasks()`: Retrieves all active tasks.
- `add_task()`: Adds a new task to the Excel file.
- `update_task()`: Updates the status of a task.
- `get_user_tasks()`: Retrieves all tasks for a specific user.
- `get_related_active_tasks()`: Retrieves related active tasks for a specific project, house, module, and activity.
- `finish_related_tasks()`: Finishes all related tasks for a specific project, house, module, and activity.
- `get_task_by_id()`: Retrieves a specific task by its ID.
- `add_comment()`: Adds a comment to a specific task.
- `get_finished_task()`: Retrieves a finished task for a specific project, house, module, and activity.

These methods are used throughout routes.py to manage task data.

### 6. Routes (app/routes.py)

Defines the application's routes and business logic:
- `/`: Handles user login.
- `/dashboard`: Displays active and paused tasks for the logged-in user.
- `/start_new_task`: Allows users to start a new task.
- `/pause_task`, `/resume_task`, `/finish_task`: Manage task statuses.
- `/settings`: Allows users to configure line and station settings.
- `/add_comment`: Handles adding comments to tasks.
- `/get_project_details`: Retrieves project details for dynamic UI updates.

This file heavily interacts with the Task model and uses data loaded by data_manager.py.

### 7. Scheduled Tasks (app/scheduled_tasks.py)

Contains the `pause_active_tasks()` function, which is scheduled to run at the end of each day to automatically pause active tasks.

### 8. Templates

- `base.html`: The base template that other templates extend.
- `index.html`: The login page.
- `dashboard.html`: Displays active and paused tasks.
- `start_new_task.html`: Form for starting a new task.
- `settings.html`: Configuration page for line and station settings.

These templates are rendered by the corresponding routes in routes.py.

### 9. Static Files

CSS files for styling the application and JavaScript files for client-side functionality.

## Key Features and Their Implementation

1. Multi-Instance Setup: Each tablet represents a specific station and line, configured through the settings page and stored in the session.
2. User Authentication: Workers can log in using their worker number or by selecting their supervisor and name. Authentication is session-based.
3. Task Management: Workers can start, pause, resume, and finish tasks. The system enforces rules such as preventing the start of a new task if there are active tasks.
4. Production Data Tracking: Detailed information is captured for each task, including timestamps, worker details, project information, and task status.
5. Pause Functionality: Tasks can be paused with specific reasons, with up to two pauses per task allowed.
6. Dynamic UI Updates: The number of module buttons updates dynamically based on the selected project.
7. Frequent Tasks: The system tracks and displays the most frequent tasks for each user.
8. Fullscreen Mode: Added for better tablet and mobile experience.
9. Automatic Task Pausing: A scheduled task automatically pauses active tasks at the end of the day.
10. Comment System: Users can add comments to tasks, providing additional context or information.
11. Related Task Management: The system can finish all related tasks simultaneously, ensuring consistency across multiple workers working on the same task.
12. Unlisted Activities: Users can add and start tasks with activities not initially listed in their specialty.

## Data Flow

1. User logs in (routes.py -> index())
2. User data is loaded from Excel files (data_manager.py)
3. Dashboard is displayed with active and paused tasks (routes.py -> dashboard())
4. User starts a new task (routes.py -> start_new_task())
5. Task is added to the Excel file (models.py -> Task.add_task())
6. User pauses, resumes, or finishes a task (routes.py -> respective route functions)
7. Task status is updated in the Excel file (models.py -> Task.update_task())
8. Comments can be added to tasks (routes.py -> add_comment())
9. Related tasks are managed together (models.py -> finish_related_tasks())

This structure allows for a modular and maintainable application, with clear separation of concerns between data management, business logic, and presentation. The recent updates have enhanced the application's functionality, improving task management, user interaction, and data consistency across related tasks.
