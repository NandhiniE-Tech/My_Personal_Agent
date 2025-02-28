import csv
import json
import httpx
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from phi.model.groq import Groq
from phi.agent import Agent
from phi.tools.csv_tools import CsvTools

class PersonalPASystem:
    def __init__(self, data_dir: str = "pa_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize CSV files
        self.tasks_csv = self.data_dir / "tasks.csv"
        self.schedule_csv = self.data_dir / "schedule.csv"
        self.progress_csv = self.data_dir / "progress.csv"
        
        # Create CSV files if they don't exist
        self._initialize_csv_files()
        
        # Set up the agent with CSV tools
        self.csv_tools = CsvTools(
            csvs=[self.tasks_csv, self.schedule_csv, self.progress_csv],
            row_limit=None,
            read_csvs=True,
            list_csvs=True,
            query_csvs=True,
            read_column_names=True
        )
        
        self.agent = Agent(
            tools=[self.csv_tools],
            model=Groq(id="llama-3.3-70b-versatile"),
            markdown=True,
            show_tool_calls=True,
            instructions=[
                "You are a personal PA advisor that helps with task management and scheduling.",
                "Use the CSV tools to manage tasks, schedule, and track progress.",
                "Always provide actionable insights and recommendations.",
                "Focus on optimizing productivity and managing task migrations."
            ]
        )
    
    def _initialize_csv_files(self):
        # Initialize tasks.csv
        if not self.tasks_csv.exists():
            with open(self.tasks_csv, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    'task_id', 'title', 'description', 'category', 
                    'priority', 'status', 'created_date', 'due_date', 
                    'rollover_count', 'time_block'
                ])
        
        # Initialize schedule.csv
        if not self.schedule_csv.exists():
            with open(self.schedule_csv, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    'block_id', 'day', 'start_time', 'end_time', 
                    'block_name', 'block_type', 'task_ids'
                ])
                
                # Add your defined time blocks
                self._add_default_schedule(writer)
        
        # Initialize progress.csv
        if not self.progress_csv.exists():
            with open(self.progress_csv, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    'date', 'completed_tasks', 'pending_tasks', 
                    'rolled_over_tasks', 'productivity_score', 'notes'
                ])
    
    def _add_default_schedule(self, writer):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        block_id = 1
        
        for day in days:
            # Morning Routine & Mental Warm-Up
            writer.writerow([
                block_id, day, '06:00', '06:50', 
                'Morning Routine & Mental Warm-Up', 'routine', ''
            ])
            block_id += 1
            
            # Core Learning Sessions
            writer.writerow([
                block_id, day, '06:50', '10:00', 
                'Core Learning Sessions', 'learning', ''
            ])
            block_id += 1
            
            # Project & Skill Application
            writer.writerow([
                block_id, day, '10:30', '14:00', 
                'Project & Skill Application', 'project', ''
            ])
            block_id += 1
            
            # Job Search & Networking
            writer.writerow([
                block_id, day, '14:00', '15:00', 
                'Job Search & Networking', 'career', ''
            ])
            block_id += 1
            
            # Reflection & Planning
            writer.writerow([
                block_id, day, '20:30', '21:00', 
                'Reflection & Planning', 'planning', ''
            ])
            block_id += 1
    
    def add_task(self, title: str, description: str, category: str, 
                priority: int, due_date: str, time_block: str) -> None:
        """Add a new task to the system"""
        # Read existing tasks to get the next task_id
        with open(self.tasks_csv, 'r', newline='') as file:
            reader = csv.reader(file)
            rows = list(reader)
            
            # Skip header row and get max task_id
            if len(rows) > 1:
                task_ids = [int(row[0]) for row in rows[1:] if row[0].isdigit()]
                next_id = max(task_ids) + 1 if task_ids else 1
            else:
                next_id = 1
        
        # Append new task
        with open(self.tasks_csv, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                next_id, title, description, category, 
                priority, 'pending', datetime.now().strftime('%Y-%m-%d'),
                due_date, 0, time_block
            ])
        
        print(f"Task '{title}' added successfully with ID {next_id}")
    
    def update_task_status(self, task_id: int, new_status: str) -> None:
        """Update the status of a task"""
        # Read all tasks
        with open(self.tasks_csv, 'r', newline='') as file:
            reader = csv.reader(file)
            rows = list(reader)
        
        # Update the status of the specific task
        updated = False
        for row in rows[1:]:  # Skip header
            if row[0] == str(task_id):
                row[5] = new_status
                if new_status == 'completed':
                    # If marking as completed, update the rollover count
                    row[8] = '0'
                updated = True
                break
        
        if not updated:
            print(f"Task with ID {task_id} not found.")
            return
        
        # Write back all tasks
        with open(self.tasks_csv, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
        
        print(f"Task {task_id} status updated to '{new_status}'")
    
    def migrate_incomplete_tasks(self) -> None:
        """Migrate incomplete tasks to the next day"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Read all tasks
        with open(self.tasks_csv, 'r', newline='') as file:
            reader = csv.reader(file)
            rows = list(reader)
        
        # Identify and update incomplete tasks
        migrated_count = 0
        for row in rows[1:]:  # Skip header
            if row[5] == 'pending' and row[7] <= today:
                # Increment rollover count
                row[8] = str(int(row[8]) + 1)
                
                # Update due date to next day
                due_date = datetime.strptime(row[7], '%Y-%m-%d')
                new_due_date = due_date + timedelta(days=1)
                row[7] = new_due_date.strftime('%Y-%m-%d')
                
                migrated_count += 1
        
        # Write back all tasks
        with open(self.tasks_csv, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
        
        # Record migration in progress log
        self._update_progress_log(migrated_tasks=migrated_count)
        
        print(f"Migrated {migrated_count} incomplete tasks")
    
    def _update_progress_log(self, migrated_tasks: int = 0) -> None:
        """Update the progress log with today's stats"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Get task stats using SQL query via the CSV tools
        query = f"""
        SELECT 
            COUNT(*) FILTER (WHERE status = 'completed' AND due_date = '{today}') as completed,
            COUNT(*) FILTER (WHERE status = 'pending' AND due_date = '{today}') as pending
        FROM tasks
        """
        
        result = self.csv_tools.query_csv_file("tasks", query)
        lines = result.strip().split('\n')
        
        # Parse the query results
        if len(lines) >= 2:
            _, counts = lines
            completed, pending = map(int, counts.split(','))
            
            # Calculate productivity score (simple version)
            total = completed + pending
            productivity_score = round((completed / total * 100) if total > 0 else 0, 2)
            
            # Add to progress log
            with open(self.progress_csv, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    today, completed, pending, 
                    migrated_tasks, productivity_score, ''
                ])
    
    def get_today_schedule(self) -> List[Dict[str, Any]]:
        """Get today's schedule with assigned tasks"""
        today_name = datetime.now().strftime('%A')
        
        # Get schedule blocks for today
        query = f"""
        SELECT block_id, start_time, end_time, block_name, block_type, task_ids
        FROM schedule
        WHERE day = '{today_name}'
        ORDER BY start_time
        """
        
        schedule_result = self.csv_tools.query_csv_file("schedule", query)
        schedule_lines = schedule_result.strip().split('\n')
        
        schedule = []
        if len(schedule_lines) > 1:  # More than just the header
            headers = schedule_lines[0].split(',')
            
            for line in schedule_lines[1:]:
                values = line.split(',')
                block = dict(zip(headers, values))
                
                # Get tasks assigned to this block
                if block['task_ids']:
                    task_ids = block['task_ids'].split(';')
                    tasks_query = f"""
                    SELECT task_id, title, priority, status
                    FROM tasks
                    WHERE task_id IN ({','.join(task_ids)})
                    ORDER BY priority DESC
                    """
                    
                    tasks_result = self.csv_tools.query_csv_file("tasks", query)
                    tasks_lines = tasks_result.strip().split('\n')
                    
                    tasks = []
                    if len(tasks_lines) > 1:
                        task_headers = tasks_lines[0].split(',')
                        for task_line in tasks_lines[1:]:
                            task_values = task_line.split(',')
                            tasks.append(dict(zip(task_headers, task_values)))
                    
                    block['tasks'] = tasks
                else:
                    block['tasks'] = []
                
                schedule.append(block)
        
        return schedule
    
    def get_productivity_insights(self, days: int = 7) -> Dict[str, Any]:
        """Get productivity insights for the past days"""
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        query = f"""
        SELECT 
            date, completed_tasks, pending_tasks, 
            rolled_over_tasks, productivity_score
        FROM progress
        WHERE date BETWEEN '{start_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}'
        ORDER BY date
        """
        
        result = self.csv_tools.query_csv_file("progress", query)
        lines = result.strip().split('\n')
        
        # Process the results
        insights = {
            'period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            'data': [],
            'summary': {
                'avg_productivity': 0,
                'total_completed': 0,
                'total_rolled_over': 0,
                'completion_rate': 0
            }
        }
        
        if len(lines) > 1:
            headers = lines[0].split(',')
            total_productivity = 0
            total_completed = 0
            total_pending = 0
            total_rolled = 0
            
            for line in lines[1:]:
                values = line.split(',')
                data_point = dict(zip(headers, values))
                insights['data'].append(data_point)
                
                # Update summary counts
                total_productivity += float(data_point['productivity_score'])
                total_completed += int(data_point['completed_tasks'])
                total_pending += int(data_point['pending_tasks'])
                total_rolled += int(data_point['rolled_over_tasks'])
            
            # Calculate summary statistics
            days_count = len(insights['data'])
            if days_count > 0:
                insights['summary']['avg_productivity'] = round(total_productivity / days_count, 2)
                insights['summary']['total_completed'] = total_completed
                insights['summary']['total_rolled_over'] = total_rolled
                total_tasks = total_completed + total_pending
                insights['summary']['completion_rate'] = round((total_completed / total_tasks * 100) if total_tasks > 0 else 0, 2)
        
        return insights
    
    def run_cli(self):
        """Run the system in CLI mode"""
        self.agent.cli_app(stream=False)

def main():
    pa_system = PersonalPASystem()
    
    # Example: Add sample tasks
    pa_system.add_task(
        title="Complete 2 LeetCode problems", 
        description="Focus on dynamic programming problems", 
        category="DSA", 
        priority=1, 
        due_date=datetime.now().strftime('%Y-%m-%d'),
        time_block="Core Learning Sessions"
    )
    
    pa_system.add_task(
        title="Study ML supervised learning module", 
        description="Focus on Random Forests and Decision Trees", 
        category="ML", 
        priority=2, 
        due_date=datetime.now().strftime('%Y-%m-%d'),
        time_block="Core Learning Sessions"
    )
    
    pa_system.add_task(
        title="Apply to 3 job positions", 
        description="Focus on ML Engineer and Data Scientist roles", 
        category="Job Search", 
        priority=1, 
        due_date=datetime.now().strftime('%Y-%m-%d'),
        time_block="Job Search & Networking"
    )
    
    # Start CLI
    pa_system.run_cli()

if __name__ == "__main__":
    main()