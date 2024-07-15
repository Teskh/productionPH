# Production Tracking App

## Description
The Production Tracking App is a web-based application designed to monitor and manage production activities across multiple lines and stations in a manufacturing setting. It's primarily used on tablets positioned at various stations along production lines, allowing workers to log their activities and track production data in real-time. The application is designed for a Spanish-speaking userbase, with all user-facing content presented in Spanish.

## Key Features

### Multi-Instance Setup
- Runs on multiple devices (tablets) on a production line
- Each instance represents a specific station and line
- Line and station settings are remembered for each instance

### User Authentication
- Workers can log in using their worker number or by selecting their supervisor and name from dropdown menus
- Authentication is session-based

### Instance-based Settings
- Each tablet is configured with specific line and station settings
- Settings can be changed through a dedicated settings page

### Task Management
- Workers can start new tasks, pause ongoing tasks, resume paused tasks, and finish tasks
- The system enforces a rule that workers cannot start a new task if they have active tasks
- All paused tasks for a worker are displayed and can be managed

### Production Data Tracking
- Detailed information is captured for each task, including timestamps, worker details, project information, and task status

### Project and Activity Management
- Projects are loaded from a separate data source
- Activities are assigned based on worker specialties
- Projects include information about the number of modules, which dynamically updates the UI

### Pause Functionality
- Tasks can be paused with specific reasons (end of day, lunch break, lack of materials, other)
- The system allows for up to two pauses per task, recording timestamps and detailed reasons for each
- A modal dialog is used for selecting pause reasons, improving the user experience

### Gender-based Welcome Messages
- The app displays "Bienvenido" or "Bienvenida" based on the worker's gender

### Responsive UI Design
- Consistent layout across different pages
- Optimized table layouts for efficient space use
- Improved mobile responsiveness with fullscreen capability

### Error Handling and Validation
- Input validation for worker numbers and task-related inputs
- Flash messages with automatic fadeout for user feedback

### Persistent Task Information
- The app remembers the last project, house number, and module selected when starting a new task

### Dynamic UI Updates
- The number of module buttons updates dynamically based on the selected project

## Technical Implementation

### Backend
- Framework: Flask (Python)
- Database: Excel files (using openpyxl library)
- Session Management: Flask session for user authentication and instance-based settings
- Concurrency Handling: FileLock for managing concurrent access to Excel files

### Frontend
- HTML/CSS: Bootstrap for responsive design
- JavaScript: jQuery for dynamic content and user interactions
- AJAX: For asynchronous data loading (e.g., worker lists, project details)
- SVG Icons: Integrated SVG icons for improved visual design

### Data Management
Four main Excel files are used for data storage:
- worker_data.xlsx: Stores worker information (name, number, specialty, supervisor, gender)
- project_data.xlsx: Contains project details (total houses, number of modules)
- activity_data.xlsx: Lists activities categorized by specialty
- production_data.xlsx: Records all task-related information

## Additional Features

### Frequent Tasks
- The system now tracks and displays the most frequent tasks for each user, allowing for quicker task initiation

### Enhanced Pause System
- Improved pause functionality with more detailed reason tracking and UI enhancements

### Dynamic Module Selection
- The number of available modules is now dynamically updated based on the selected project

### Improved Dashboard Layout
- Enhanced dashboard design with better organization of active and paused tasks

### Fullscreen Mode
- Added fullscreen capability for better tablet and mobile experience

### Automatic Task Pausing
- Implemented a scheduled task to automatically pause active tasks at the end of the day


