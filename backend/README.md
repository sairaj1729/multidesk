# MultiDesk JIRA Dashboard - Backend Documentation

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Data Flow](#data-flow)
- [Technical Details](#technical-details)
- [Troubleshooting](#troubleshooting)

## Overview

MultiDesk is a comprehensive JIRA dashboard solution that integrates with JIRA Cloud instances to provide enhanced project management capabilities. The system focuses on risk detection by identifying potential delivery delays caused by employee leave periods overlapping with task due dates.

### Key Capabilities:
- JIRA project and task synchronization
- Employee leave management via CSV upload
- Automated risk detection and alerting
- Real-time dashboard visualization
- Cross-team collaboration insights

## Features

### 1. JIRA Integration
- **Project Synchronization**: Automatically fetches and updates JIRA projects
- **Task Management**: Syncs all tasks, stories, epics, and bugs from JIRA
- **Admin Access**: Supports admin-level access to view all tasks in projects (not just assigned tasks)
- **Multiple Issue Types**: Handles Tasks, Stories, Epics, and Bugs
- **Real-time Updates**: Keeps local database synchronized with JIRA changes

### 2. Leave Management
- **CSV Upload**: Support for employee leave data via CSV file upload
- **Flexible Date Formats**: Handles various date formats (YYYY-MM-DD, MM/DD/YYYY, etc.)
- **Email Matching**: Matches employee emails to JIRA assignee emails
- **Bulk Processing**: Processes multiple leave entries simultaneously
- **Validation**: Validates date ranges and email formats

### 3. Risk Detection
- **Automated Analysis**: Runs risk analysis automatically after leave upload
- **Date Overlap Detection**: Identifies when task due dates fall within employee leave periods
- **Risk Scoring**: Provides HIGH/LOW/MEDIUM risk levels based on impact
- **Real-time Alerts**: Immediate risk alert generation upon data changes
- **Cross-team Impact**: Identifies risks affecting multiple team members

### 4. Data Management
- **MongoDB Integration**: Robust NoSQL database for scalable data storage
- **Data Persistence**: All data stored permanently for historical analysis
- **Real-time Sync**: Live synchronization between JIRA and local database
- **Data Validation**: Comprehensive validation for data integrity

### 5. API Services
- **RESTful Architecture**: Clean, intuitive API endpoints
- **Authentication**: Secure token-based authentication
- **File Handling**: Robust file upload and processing capabilities
- **Background Processing**: Asynchronous task processing for improved performance

## Architecture

### Tech Stack
- **Backend**: Python 3.13 with FastAPI
- **Database**: MongoDB with Motor async driver
- **Authentication**: JWT tokens
- **Data Processing**: Pandas for CSV processing
- **HTTP Client**: HTTPX for API calls
- **Frontend**: React/Vite (separate repository)

### Core Components
```
├── routers/          # API route handlers
│   ├── jira.py      # JIRA integration endpoints
│   ├── files.py     # File upload endpoints  
│   ├── risks.py     # Risk detection endpoints
│   └── ...
├── services/        # Business logic
│   ├── jira_service.py      # JIRA sync logic
│   ├── leave_processor.py   # Leave data processing
│   ├── risk_service.py      # Risk detection algorithms
│   └── ...
├── models/          # Data models
├── db/              # Database connections
└── utils/           # Utility functions
```

### Database Collections
- **jira_tasks**: Stores synchronized JIRA tasks
- **jira_projects**: Stores project information
- **jira_credentials**: Securely stores JIRA API credentials
- **leaves**: Stores employee leave data from CSV uploads
- **risk_alerts**: Stores detected risk information
- **files**: Tracks uploaded files and processing status
- **users**: User account information

## Installation

### Prerequisites
- Python 3.13+
- MongoDB Community Server
- JIRA Cloud account with API access

### Setup Steps

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd industy/backend
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On Linux/Mac
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start the Server**
   ```bash
   uvicorn main:app --reload
   ```

## Configuration

### Environment Variables
```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=multidesk

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Configuration (for notifications)
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USER=your-email@gmail.com
MAIL_PASS=your-app-password
MAIL_FROM=your-email@gmail.com
```

### JIRA API Setup
1. Create API token in JIRA: Profile → Account settings → Security → API tokens
2. Ensure your account has appropriate permissions
3. Use the format: `your-email@domain.com` and the generated API token

## API Endpoints

### JIRA Integration
```
POST /api/jira/connect
  - Connect JIRA account with credentials
  - Body: {email, api_token, domain}

GET /api/jira/tasks
  - Get all synchronized tasks
  - Returns paginated task list

POST /api/jira/sync
  - Force manual sync of JIRA data
  - Triggers full data refresh

GET /api/jira/projects
  - Get all synchronized projects
```

### File Management
```
POST /api/files/upload
  - Upload leave data CSV file
  - Auto-processes and triggers risk analysis
  - Returns file processing status

GET /api/files/
  - Get list of uploaded files
  - Includes processing status and record counts

GET /api/files/{file_id}
  - Get details of specific uploaded file
```

### Risk Detection
```
GET /api/risks
  - Get all current risk alerts
  - Returns risk level, affected tasks, and timelines

GET /api/risks/{risk_id}
  - Get specific risk details

POST /api/risks/analyze
  - Manual trigger for risk analysis
  - Runs analysis on current data
```

### Authentication
```
POST /api/auth/login
  - User login and token generation

POST /api/auth/register
  - New user registration

GET /api/auth/me
  - Get current user profile
```

## Data Flow

### 1. JIRA Data Sync Flow
```
1. User connects JIRA account
2. System validates credentials
3. Fetches all projects from JIRA
4. Fetches all tasks using optimized JQL queries:
   - First tries: "project = {specific_project}" (admin access)
   - Falls back to: "project in projectsWhereUserHasPermission()"
   - Alternative: "assignee = currentUser() OR reporter = currentUser()"
5. Processes and converts data to internal format
6. Stores in MongoDB collections (jira_tasks, jira_projects)
7. Updates dashboard with fresh data
```

### 2. Leave Data Upload Flow
```
1. User uploads CSV file via UI
2. Backend receives file and creates record in files collection
3. Background task processes CSV:
   - Validates required columns (employee_email, leave_start, leave_end)
   - Converts dates to proper datetime format for MongoDB
   - Normalizes email addresses
4. Stores leave records in leaves collection
5. Updates file status to "processed"
6. Automatically triggers risk analysis
```

### 3. Risk Detection Flow
```
1. Risk analysis triggered (manual or automatic)
2. Clears existing risk alerts
3. Iterates through all JIRA tasks:
   - Checks for valid assignee email and due date
   - Compares task due date with employee leave periods
   - Uses date range overlap algorithm
4. Creates risk alerts for overlapping periods:
   - Task details (key, summary, assignee)
   - Due date and leave period
   - Risk level (HIGH for critical overlaps)
5. Stores risk alerts in risk_alerts collection
6. Updates UI with new risk information
```

## Technical Details

### JQL Queries Used
The system uses multiple JQL strategies to ensure comprehensive data access:

1. **Primary**: `project = {specific_project}` - For admin access to all project tasks
2. **Fallback**: `project in projectsWhereUserHasPermission()` - Standard permission-based access
3. **Alternative**: `assignee = currentUser() OR reporter = currentUser()` - Personal assignments

### Date Handling
- All dates stored as `datetime` objects in MongoDB (never `date` objects)
- Proper timezone handling with UTC storage
- Flexible date format parsing for CSV uploads
- Consistent date comparison algorithms

### Security Measures
- API tokens encrypted in database
- JWT token-based authentication
- Input validation for all endpoints
- SQL injection prevention (using MongoDB queries properly)
- Rate limiting protection

### Performance Optimizations
- Background task processing for file uploads
- Efficient MongoDB indexing
- Connection pooling for database operations
- Caching for frequently accessed data

## Troubleshooting

### Common Issues

#### JIRA Connection Issues
- **Problem**: "Invalid JIRA connection"
- **Solution**: Verify API token and email match exactly
- **Check**: Ensure JIRA domain is correct format (https://company.atlassian.net)

#### File Upload Issues
- **Problem**: Upload completes but no records processed
- **Solution**: Check CSV format - ensure headers are: employee_email, leave_start, leave_end
- **Check**: Verify date format is YYYY-MM-DD

#### Risk Detection Not Working
- **Problem**: No risks detected despite overlapping dates
- **Solution**: Verify email addresses match between JIRA and leave data
- **Check**: Ensure task due dates and leave dates actually overlap

#### Database Connection Issues
- **Problem**: Cannot connect to MongoDB
- **Solution**: Verify MONGODB_URL in .env file
- **Check**: Ensure MongoDB service is running

### Debugging Endpoints
```
GET /api/mongo/connection-test
  - Test MongoDB connectivity

GET /api/mongo/test-task-storage
  - Test task storage functionality

GET /api/mongo/test-jira-fetch
  - Test JIRA data fetch with credentials
```

### Logging
- All operations logged with appropriate severity levels
- Risk detection events logged with detailed information
- File processing steps logged for troubleshooting
- JIRA API calls logged for debugging connectivity issues

## Deployment

### Production Setup
1. Use environment-specific configuration
2. Set up proper SSL certificates
3. Configure production database
4. Set up monitoring and alerting
5. Implement backup strategies

### Environment Variables for Production
```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=multidesk_prod
SECRET_KEY=production-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours
DEBUG=False
```

## Support & Maintenance

### Monitoring
- Database connectivity
- API response times
- File processing success rates
- Risk detection accuracy
- JIRA sync frequency

### Backup Strategy
- Regular MongoDB backups
- API credential encryption key rotation
- Configuration version control

---

## Contact & Support

For technical support or questions about implementation:
- Check the API documentation
- Review the logs for error details
- Contact the development team for complex issues

**Version**: 1.0.0
**Last Updated**: January 2026