# Personal Assistance AGENTS to track & review our task priority.

A conversational task management and scheduling system built with Phi Framework.

## Overview

Personal PA System is an intelligent assistant designed to help you manage your daily tasks, optimize your schedule, and track your productivity over time. The system uses natural language processing to understand your needs and two specialized agents to handle different aspects of task management.

## Features

- **Conversational Task Creation**: Add tasks by simply mentioning them in conversation
- **Automatic Scheduling**: Tasks are automatically assigned to appropriate time blocks
- **Progress Tracking**: Daily productivity metrics are calculated and stored
- **Task Migration**: Incomplete tasks are rescheduled intelligently
- **Daily Reporting**: Get insights on your productivity patterns
- **Smart Categorization**: Tasks are categorized based on their description

## System Components

The system consists of two specialized agents:

1. **Personal Assistant Agent**: Handles day-to-day task management
   - Records new tasks
   - Updates task status
   - Shows schedule information
   - Provides real-time assistance

2. **Progress Reviewer Agent**: Handles end-of-day review and planning
   - Generates daily reports
   - Calculates productivity metrics
   - Identifies incomplete tasks
   - Provides productivity insights

## Installation

### Prerequisites

- Python 3.10+
- Phi Framework
- Groq API key (for the LLM). if you have openai use 

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/personal-pa-system.git
   cd personal-pa-system
