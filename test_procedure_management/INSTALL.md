# Test Procedure Management System - Installation Guide

## Quick Start

### Windows

1. **Open Command Prompt or PowerShell**

2. **Navigate to project directory:**
```cmd
cd path\to\test_procedure_management
```

3. **Create virtual environment:**
```cmd
python -m venv venv
venv\Scripts\activate
```

4. **Install dependencies:**
```cmd
pip install -r requirements.txt
```

5. **Run the application:**
```cmd
python run.py
```

6. **Open browser:**
Navigate to `http://localhost:5000`

### Linux/Mac

1. **Open Terminal**

2. **Navigate to project directory:**
```bash
cd /path/to/test_procedure_management
```

3. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
```

4. **Install dependencies:**
```bash
pip install -r requirements.txt
```

5. **Run the application:**
```bash
python run.py
```

6. **Open browser:**
Navigate to `http://localhost:5000`

## Detailed Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- 100MB free disk space

### Step-by-Step Installation

#### 1. Verify Python Installation

```bash
python --version
# or
python3 --version
```

Should output Python 3.8 or higher.

#### 2. Create Virtual Environment

**Why?** Virtual environments isolate project dependencies.

**Windows:**
```cmd
python -m venv venv
```

**Linux/Mac:**
```bash
python3 -m venv venv
```

#### 3. Activate Virtual Environment

**Windows:**
```cmd
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

You should see `(venv)` in your command prompt.

#### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Flask (web framework)
- Flask-SQLAlchemy (database ORM)
- ReportLab (PDF generation)
- Other utilities

#### 5. Run the Application

**Option A: Using run script (recommended)**
```bash
python run.py
```

**Option B: Using Flask directly**
```bash
export FLASK_APP=app.py  # Linux/Mac
set FLASK_APP=app.py     # Windows CMD
$env:FLASK_APP="app.py"  # Windows PowerShell

flask run
```

#### 6. Access the Application

Open your web browser and go to:
```
http://localhost:5000
```

## First Time Setup

### 1. Sample Data

The application automatically creates sample data on first run:
- 1 sample test procedure
- Categories
- ECE regulations

### 2. Language Selection

- Click the language selector (TR/EN) in the navigation bar
- Your preference is saved in the session

### 3. Create Your First Procedure

1. Go to **Test Procedures** → **New Procedure**
2. Fill in the required fields
3. Click **Save**

## Configuration

### Database Configuration

Default: SQLite database at `instance/test_procedures.db`

To change, edit `config.py`:
```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///path/to/your/database.db'
# or
SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/dbname'
```

### Upload Limits

Edit `config.py`:
```python
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
```

### Backup Settings

Edit `config.py`:
```python
AUTO_BACKUP_ENABLED = True
AUTO_BACKUP_INTERVAL_DAYS = 7
MAX_BACKUP_FILES = 10
```

## Troubleshooting

### Port Already in Use

If port 5000 is occupied, change it in `run.py`:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

### ModuleNotFoundError

Make sure virtual environment is activated and dependencies are installed:
```bash
pip install -r requirements.txt
```

### Database Errors

Delete the database and restart (WARNING: loses data):
```bash
rm instance/test_procedures.db
python run.py
```

### Permission Errors

**Windows:** Run Command Prompt as Administrator

**Linux/Mac:** Check folder permissions:
```bash
chmod -R 755 test_procedure_management
```

## Production Deployment

For production use, follow these additional steps:

### 1. Security

- Set strong `SECRET_KEY` in environment variables
- Use PostgreSQL or MySQL instead of SQLite
- Enable HTTPS
- Set `DEBUG = False`

### 2. WSGI Server

Use Gunicorn (Linux) or Waitress (Windows):

**Install:**
```bash
pip install gunicorn  # Linux
pip install waitress  # Windows
```

**Run:**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 'app:create_app()'
```

### 3. Reverse Proxy

Use Nginx or Apache as reverse proxy for static files and load balancing.

### 4. Process Manager

Use systemd (Linux) or Windows Service to keep app running.

### 5. Automated Backups

Set up cron job (Linux) or Task Scheduler (Windows) for regular backups.

## Updating

To update the application:

1. **Backup your database:**
```bash
cp instance/test_procedures.db instance/backup_$(date +%Y%m%d).db
```

2. **Pull latest changes** (if using git)

3. **Update dependencies:**
```bash
pip install -r requirements.txt --upgrade
```

4. **Restart application**

## Uninstallation

1. **Deactivate virtual environment:**
```bash
deactivate
```

2. **Delete project folder:**
```bash
rm -rf test_procedure_management  # Linux/Mac
rmdir /s test_procedure_management  # Windows
```

## Getting Help

- Check `README.md` for feature documentation
- Review `config.py` for configuration options
- Inspect browser console for JavaScript errors
- Check Flask logs for server errors

## System Requirements

### Minimum
- Python 3.8+
- 512MB RAM
- 100MB disk space
- Modern web browser

### Recommended
- Python 3.10+
- 1GB RAM
- 500MB disk space
- Chrome, Firefox, or Edge (latest version)

## Next Steps

After installation:

1. Read `README.md` for feature overview
2. Create your first test procedure
3. Record a test result
4. Explore the dashboard
5. Try PDF export
6. Create a database backup

Enjoy using the Test Procedure Management System!
