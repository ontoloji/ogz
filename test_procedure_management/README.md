# Test Procedure Management System

Modern web-based test procedure management system for organizing, tracking, and reporting test procedures and results.

## Features

### Core Functionality
- ✅ **Test Procedure Management**: Create, edit, and organize test procedures (TP-001, TP-002, etc.)
- ✅ **Test Result Tracking**: Record and track test execution results
- ✅ **Search & Filtering**: Advanced search by level, category, keywords
- ✅ **Dashboard**: Real-time progress tracking and statistics
- ✅ **ECE Regulation References**: Link procedures to ECE regulations
- ✅ **PDF Export**: Generate professional PDF reports
- ✅ **Backup System**: Automated and manual database backups
- ✅ **Multilingual**: Full Turkish and English support

### Test Procedure Features
Each test procedure includes:
- Unique procedure code (TP-001, TP-002, etc.)
- Title, level (Basic/Advanced/Expert)
- Purpose and objectives
- Detailed step-by-step instructions
- Acceptance criteria
- Required equipment list
- ECE regulation references
- Estimated duration
- Prerequisites

### Test Result Features
Each test result includes:
- Test execution date and operator
- Pass/Fail/Partial status
- Step-by-step results
- Measurements and observations
- Environmental conditions (temperature, humidity)
- Actual duration
- Notes and attachments

## Technology Stack

- **Backend**: Flask 3.0 (Python)
- **Database**: SQLite (easily upgradeable to PostgreSQL/MySQL)
- **Frontend**: Bootstrap 5 + jQuery
- **PDF Generation**: ReportLab
- **Charts**: Chart.js

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. **Clone or navigate to the project directory:**
```bash
cd test_procedure_management
```

2. **Create a virtual environment (recommended):**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Initialize the database:**
The database will be automatically created on first run with sample data.

5. **Run the application:**
```bash
python app.py
```

6. **Open your browser:**
Navigate to `http://localhost:5000`

## Configuration

Edit `config.py` to customize:

- **Database**: Change `SQLALCHEMY_DATABASE_URI` for different database
- **Upload limits**: Adjust `MAX_CONTENT_LENGTH`
- **Backup settings**: Configure auto-backup interval
- **Languages**: Add more languages to `LANGUAGES` list

## Usage

### Creating a Test Procedure

1. Go to **Test Procedures** → **New Procedure**
2. Fill in:
   - Procedure code (e.g., TP-001)
   - Title in both Turkish and English
   - Level (Basic, Advanced, Expert)
   - Category
   - Purpose and objectives
   - Test steps with expected results
   - Acceptance criteria
   - Required equipment
   - ECE regulations (optional)
   - Estimated duration

3. Click **Save**

### Recording a Test Result

1. Go to **Test Results** → **New Test Result**
2. Select the test procedure
3. Fill in:
   - Test date and operator name
   - Overall status (Pass/Fail/Partial)
   - Step-by-step results
   - Environmental conditions
   - Measurements (JSON format)
   - Notes and observations

4. Click **Save**

### Searching and Filtering

**Test Procedures:**
- Search by code, title, or keywords
- Filter by level (Basic/Advanced/Expert)
- Filter by category
- Filter by status (Active/Inactive)

**Test Results:**
- Search by procedure code or operator
- Filter by status (Pass/Fail/Partial)
- Filter by operator
- Filter by date range
- Filter by procedure

### Exporting Data

**CSV Export:**
- Go to Test Results page
- Apply desired filters
- Click **Export CSV**

**PDF Export:**
- View any procedure or result
- Click **Export PDF**
- Choose download location

### Backup and Restore

**Creating a Backup:**
1. Go to **Backup** section
2. Click **Create Backup**
3. Enter optional notes
4. Backup file is saved to `backups/` folder

**Restoring from Backup:**
1. Go to **Backup** section
2. Find the backup you want to restore
3. Click **Restore**
4. Confirm the action (current database will be backed up first)

**Uploading a Backup:**
1. Go to **Backup** section
2. Click **Upload Backup**
3. Select `.db` file
4. File is added to backup list

## Project Structure

```
test_procedure_management/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── models.py                   # Database models
├── pdf_export.py               # PDF generation utilities
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── routes/                     # Route blueprints
│   ├── __init__.py
│   ├── dashboard.py           # Dashboard routes
│   ├── procedures.py          # Procedure CRUD routes
│   ├── results.py             # Results tracking routes
│   └── backup.py              # Backup/restore routes
│
├── templates/                  # HTML templates
│   ├── base.html              # Base layout
│   ├── dashboard/             # Dashboard pages
│   ├── procedures/            # Procedure pages
│   ├── results/               # Results pages
│   ├── backup/                # Backup pages
│   └── errors/                # Error pages (404, 500)
│
├── static/                     # Static files
│   ├── css/                   # Custom CSS
│   ├── js/                    # Custom JavaScript
│   └── img/                   # Images
│
├── instance/                   # Instance-specific files
│   └── test_procedures.db     # SQLite database
│
├── exports/                    # PDF exports
├── backups/                    # Database backups
└── uploads/                    # User uploads
```

## Database Schema

### TestProcedure
- Stores test procedure definitions
- Includes steps, criteria, equipment
- Supports bilingual content (TR/EN)

### TestResult
- Stores test execution results
- Links to TestProcedure
- Includes step-by-step results and measurements

### Category
- Organizes procedures by category
- Bilingual names and descriptions

### ECERegulation
- Reference database for ECE regulations
- Links to official documentation

### BackupLog
- Tracks all backup operations
- Stores backup metadata

## API Endpoints

### Procedures
- `GET /procedures/` - List procedures
- `GET /procedures/<id>` - View procedure
- `GET /procedures/create` - Create form
- `POST /procedures/create` - Create procedure
- `GET /procedures/<id>/edit` - Edit form
- `POST /procedures/<id>/edit` - Update procedure
- `POST /procedures/<id>/delete` - Delete procedure
- `GET /procedures/api/search` - Search API

### Results
- `GET /results/` - List results
- `GET /results/<id>` - View result
- `GET /results/create` - Create form
- `POST /results/create` - Create result
- `GET /results/<id>/edit` - Edit form
- `POST /results/<id>/edit` - Update result
- `POST /results/<id>/delete` - Delete result
- `GET /results/export` - Export CSV

### Dashboard
- `GET /dashboard/` - Main dashboard
- `GET /dashboard/statistics` - Detailed statistics

### Backup
- `GET /backup/` - List backups
- `POST /backup/create` - Create backup
- `GET /backup/download/<id>` - Download backup
- `POST /backup/restore/<id>` - Restore backup
- `POST /backup/delete/<id>` - Delete backup
- `POST /backup/upload` - Upload backup

## Customization

### Adding New Languages

1. Add language code to `config.py`:
```python
LANGUAGES = ['tr', 'en', 'de']  # Added German
```

2. Update database models to include new language fields
3. Update templates to display new language options

### Changing Color Theme

Edit the CSS variables in `templates/base.html`:
```css
:root {
    --primary-color: #your-color;
    --secondary-color: #your-color;
    ...
}
```

### Adding Custom Fields

1. Update `models.py` to add new database columns
2. Update forms in templates
3. Update route handlers to process new fields

## Troubleshooting

### Database Issues
- Delete `instance/test_procedures.db` to reset database
- Check file permissions for `instance/` folder

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Activate virtual environment

### Port Already in Use
- Change port in `app.py`: `app.run(port=5001)`
- Or kill process using port 5000

### PDF Generation Errors
- Ensure ReportLab is installed
- Check write permissions for `exports/` folder

## Production Deployment

### Security Checklist
- [ ] Change `SECRET_KEY` in production
- [ ] Use PostgreSQL/MySQL instead of SQLite
- [ ] Enable HTTPS
- [ ] Set `DEBUG = False`
- [ ] Configure proper backup automation
- [ ] Set up user authentication
- [ ] Configure firewall rules

### Recommended Setup
- **Web Server**: Gunicorn + Nginx
- **Database**: PostgreSQL
- **Process Manager**: systemd or supervisor
- **Backup**: Automated daily backups

## Contributing

This project is part of the SORT Test Automation System. For contributions or issues, please contact the development team.

## License

Proprietary - All rights reserved

## Support

For questions or support:
- Email: support@example.com
- Documentation: Internal wiki

## Version History

### v1.0.0 (2024-11-21)
- Initial release
- Complete CRUD operations for procedures and results
- Dashboard with statistics
- PDF export functionality
- Backup/restore system
- Turkish and English language support
- Sample data included

---

**Note**: This system integrates with the existing SORT Test Automation System and shares the same project repository.
