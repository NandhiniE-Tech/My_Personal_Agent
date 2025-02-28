from phi.agent import Agent
from phi.model.groq import Groq
from phi.storage.agent.sqlite import SqlAgentStorage
from phi.tools.file import FileTools
from phi.tools.calendar import GoogleCalendarTools
from phi.tools.date_time import DateTimeTools
from phi.playground import Playground, serve_playground_app
import pandas as pd
import os
from datetime import datetime, timedelta

# Define custom tool for task management
class TaskManagerTools:
    def __init__(self, task_file="tasks.csv"):
        self.task_file = task_file
        if not os.path.exists(task_file):
            # Create empty tasks file with columns
            df = pd.DataFrame(columns=[
                'task_id', 'name', 'category', 'priority', 'scheduled_date', 
                'scheduled_time', 'duration_mins', 'status', 'completion_date', 
                'notes', 'rollover_count'
            ])
            df.to_csv(task_file, index=False)

    def list_all_tasks(self):
        """List all tasks in the system"""
        df = pd.read_csv(self.task_file)
        return df.to_dict(orient='records')
    
    def list_tasks_by_date(self, date_str):
        """List all tasks scheduled for a specific date"""
        df = pd.read_csv(self.task_file)
        filtered = df[df['scheduled_date'] == date_str]
        return filtered.to_dict(orient='records')
    
    def list_pending_tasks(self):
        """List all tasks with status 'pending' or 'in_progress'"""
        df = pd.read_csv(self.task_file)
        filtered = df[df['status'].isin(['pending', 'in_progress'])]
        return filtered.to_dict(orient='records')
    
    def add_task(self, name, category, priority, scheduled_date, scheduled_time, 
                 duration_mins, status="pending", notes=""):
        """Add a new task to the system"""
        df = pd.read_csv(self.task_file)
        
        # Generate new task ID
        task_id = 1
        if not df.empty:
            task_id = df['task_id'].max() + 1
            
        new_task = {
            'task_id': task_id,
            'name': name,
            'category': category,
            'priority': priority,
            'scheduled_date': scheduled_date,
            'scheduled_time': scheduled_time,
            'duration_mins': duration_mins,
            'status': status,
            'completion_date': '',
            'notes': notes,
            'rollover_count': 0
        }
        
        df = pd.concat([df, pd.DataFrame([new_task])], ignore_index=True)
        df.to_csv(self.task_file, index=False)
        return f"Task added successfully with ID: {task_id}"
    
    def update_task_status(self, task_id, status, notes=""):
        """Update the status of a task"""
        df = pd.read_csv(self.task_file)
        
        if task_id not in df['task_id'].values:
            return f"Error: Task with ID {task_id} not found"
            
        idx = df.index[df['task_id'] == task_id][0]
        df.at[idx, 'status'] = status
        
        if status == "completed":
            df.at[idx, 'completion_date'] = datetime.now().strftime('%Y-%m-%d')
            
        if notes:
            df.at[idx, 'notes'] = notes
            
        df.to_csv(self.task_file, index=False)
        return f"Task {task_id} updated to status: {status}"
    
    def rollover_incomplete_tasks(self, from_date, to_date):
        """Move incomplete tasks from one date to another"""
        df = pd.read_csv(self.task_file)
        
        # Find incomplete tasks for the specified date
        incomplete = df[(df['scheduled_date'] == from_date) & 
                        (df['status'].isin(['pending', 'in_progress']))]
        
        rollover_count = 0
        for idx in incomplete.index:
            # Increment rollover count
            df.at[idx, 'rollover_count'] = df.at[idx, 'rollover_count'] + 1
            df.at[idx, 'scheduled_date'] = to_date
            df.at[idx, 'notes'] = df.at[idx, 'notes'] + f" | Rolled over from {from_date}"
            rollover_count += 1
            
        df.to_csv(self.task_file, index=False)
        return f"Rolled over {rollover_count} tasks from {from_date} to {to_date}"
    
    def generate_daily_report(self, date_str):
        """Generate a summary report for a specific day"""
        df = pd.read_csv(self.task_file)
        day_tasks = df[df['scheduled_date'] == date_str]
        
        total_tasks = len(day_tasks)
        completed = len(day_tasks[day_tasks['status'] == 'completed'])
        incomplete = total_tasks - completed
        
        completion_rate = 0
        if total_tasks > 0:
            completion_rate = (completed / total_tasks) * 100
            
        # Tasks by category
        category_counts = day_tasks['category'].value_counts().to_dict()
        
        # Tasks by priority
        priority_counts = day_tasks['priority'].value_counts().to_dict()
        
        # Calculate scheduled study/work hours
        total_scheduled_mins = day_tasks['duration_mins'].sum()
        
        report = {
            "date": date_str,
            "total_tasks": total_tasks,
            "completed_tasks": completed,
            "incomplete_tasks": incomplete,
            "completion_rate": f"{completion_rate:.1f}%",
            "total_scheduled_hours": f"{total_scheduled_mins/60:.1f}",
            "categories": category_counts,
            "priorities": priority_counts,
            "incomplete_task_details": day_tasks[day_tasks['status'] != 'completed'].to_dict(orient='records')
        }
        
        return report

# Create Task Scheduler Agent
task_scheduler_agent = Agent(
    name="Task Scheduler PA",
    model=Groq(id="llama-3.3-70b-versatile"),
    tools=[
        TaskManagerTools(),
        DateTimeTools(),
        FileTools()
    ],
    instructions=[
        "You are a personal assistant specializing in task management and scheduling.",
        "Help the user maintain their schedule based on their predefined time blocks.",
        "Assist with adding, updating, and tracking tasks.",
        "At the end of each day, identify incomplete tasks and suggest when to roll them over.",
        "Provide daily and weekly summaries of task completion rates.",
        "Format task information in easy-to-read tables when possible.",
        "Always suggest improvements to the user's schedule based on their completion patterns."
    ],
    storage=SqlAgentStorage(table_name="task_scheduler_agent", db_file="agents.db"),
    add_history_to_messages=True,
    markdown=True,
)

# Create Progress Analytics Agent
progress_analytics_agent = Agent(
    name="Progress Analytics PA",
    model=Groq(id="llama-3.3-70b-versatile"),
    tools=[
        TaskManagerTools(),
        FileTools()
    ],
    instructions=[
        "You analyze the user's task completion patterns and provide insights.",
        "Generate weekly and monthly reports on productivity and learning progress.",
        "Identify patterns in task completion rates across different categories.",
        "Suggest schedule optimizations based on historical performance.",
        "Help the user track their progress toward long-term goals.",
        "Use data visualization descriptions to make the analysis more understandable.",
        "Always focus on constructive insights rather than criticism."
    ],
    storage=SqlAgentStorage(table_name="progress_analytics_agent", db_file="agents.db"),
    add_history_to_messages=True,
    markdown=True,
)

# Add Google Calendar integration (optional)
# This would require setting up OAuth credentials
calendar_agent = Agent(
    name="Calendar Integration PA",
    model=Groq(id="llama-3.3-70b-versatile"),
    tools=[
        GoogleCalendarTools(), 
        TaskManagerTools(),
        DateTimeTools()
    ],
    instructions=[
        "You help sync tasks between the task management system and Google Calendar.",
        "Create calendar events for scheduled tasks.",
        "Update task statuses based on calendar completion.",
        "Send reminders for upcoming deadlines and scheduled activities.",
        "Suggest schedule adjustments when calendar conflicts arise."
    ],
    storage=SqlAgentStorage(table_name="calendar_agent", db_file="agents.db"),
    add_history_to_messages=True,
    markdown=True,
)

# Create the playground with all agents
app = Playground(agents=[
    task_scheduler_agent, 
    progress_analytics_agent,
    calendar_agent
]).get_app()

if __name__ == "__main__":
    serve_playground_app("playground:app", reload=True)