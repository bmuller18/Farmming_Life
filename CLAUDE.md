# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Project Instructions

## Database

- Supabase is the project's database.
- Never disable Row Level Security.
- Database access must go through backend/supabase_client.py.
- Do not create duplicate Supabase clients in other files.
- The player table contains: id, name, money, level.
- Use player.id to identify players.

## Python

- Use Python 3.12+.
- Keep database logic separated from application logic.
- Prefer reusable functions.
- Do not hardcode credentials.
- Credentials are stored in .env.

## Frontend

- The frontend is built with Flet for cross-platform GUI applications
- Frontend code is located in the frontend/ directory
- The frontend uses the same Supabase client backend for data access

## Important

- Before modifying the database structure, explain the proposed changes.
- Do not modify Supabase tables or RLS policies without explicit approval.

## Development Commands

### Backend Setup
```bash
# Create virtual environment (if not already created)
python -m venv env

# Activate virtual environment
source env/bin/activate  # On Windows: env\Scripts\activate

# Install backend dependencies
pip install -r requirements.txt
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Create/activate virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install frontend dependencies
pip install -r requirements.txt
```

### Running Applications

#### Backend Console Application
```bash
# From project root
python main.py

# Test Supabase connection
python test_connection.py
```

#### Frontend GUI Application
```bash
# From frontend directory
python main.py
```

### Environment Setup
Copy `.env.example` to `.env` (if it exists) and fill in your Supabase credentials:
```
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here
```

## Code Architecture

### Backend (`backend/`)
- `supabase_client.py`: Supabase connection and query functions
- `user_system.py`: Helper functions to get or create players and display player info
- Contains reusable functions for database access

### Frontend (`frontend/`)
- `main.py`: Flet GUI application for viewing player data
- Uses the backend Supabase client for data access
- Provides input for player ID and displays player information

### Shared
- `.env`: Environment variables for Supabase connection (gitignored)
- `requirements.txt`: Dependencies for each component