# Multi Desk Jira Dashboard

A comprehensive dashboard and task management system that integrates with Jira Cloud to provide advanced analytics, risk assessment, and employee management features.

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Frontend Features](#frontend-features)
- [Backend Features](#backend-features)
- [Jira Integration](#jira-integration)
- [Data Management](#data-management)
- [Risk Assessment](#risk-assessment)
- [User Management](#user-management)
- [Reports](#reports)
- [Deployment](#deployment)

## Features

### Core Features
- **Jira Cloud Integration**: Sync projects, epics, stories, and tasks from Jira
- **Risk Assessment**: Automated risk detection based on employee leave patterns and task deadlines
- **Eisenhower Matrix**: Priority-based task organization and visualization
- **Analytics Dashboard**: Comprehensive charts and metrics for project tracking
- **User Management**: Role-based access control and user administration
- **Data Import/Export**: CSV upload and download capabilities
- **Email Verification**: User registration and OTP-based verification
- **File Management**: Document and report management system

### Advanced Features
- **Leave Pattern Analysis**: Identifies potential risks based on employee leave schedules
- **Task Prioritization**: Smart categorization using Eisenhower Matrix methodology
- **Real-time Sync**: Automatic synchronization with Jira Cloud
- **Custom Reporting**: Detailed analytics and project insights
- **Risk Alerts**: Proactive notifications for potential project risks

## Tech Stack

### Backend
- **Python 3.13+**
- **FastAPI** - High-performance web framework
- **MongoDB** - NoSQL database with Motor driver
- **Pandas** - Data processing and analysis
- **Resend** - Email delivery service
- **Jira REST API** - Cloud integration

### Frontend
- **React 18** - Component-based UI framework
- **Vite** - Build tool and development server
- **Tailwind CSS** - Utility-first styling
- **Shadcn/ui** - Pre-built UI components
- **Lucide React** - Icon library

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.13+
- MongoDB
- Jira Cloud account with API access

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd industry
```

2. **Setup Backend**
```bash
cd backend
pip install -r requirements.txt
```

3. **Setup Frontend**
```bash
cd frontend
npm install
```

4. **Configure Environment Variables**
   - Copy `.env.example` to `.env` in both backend and frontend
   - Update with your specific configuration

5. **Start the Application**
```bash
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

## Environment Variables

### Backend (.env)
```env
# FastAPI Configuration
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=304
FERNET_KEY=your-fernet-key

# MongoDB Configuration
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=multidesk-db

# Resend Configuration
RESEND_API_KEY=your-resend-api-key
RESEND_SENDER_EMAIL=onboarding@resend.dev
BYPASS_OTP_VERIFICATION=true

# Jira Configuration
JIRA_DOMAIN=your-domain.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your-jira-api-token

# OTP Configuration
OTP_EXPIRE_MINUTES=10
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

## Frontend Features

### Dashboard Components
- **Analytics Charts**: Visual representations of project metrics
- **Stat Cards**: Key performance indicators and counts
- **Eisenhower Matrix**: Task prioritization matrix
- **Risk Alerts**: Display of detected risks and warnings
- **Employee Data Management**: User and leave data overview

### Navigation
- **Dashboard**: Main analytics and overview
- **Tasks**: Task management and prioritization
- **Users**: User management and administration
- **Data Management**: File upload and data handling
- **Reports**: Detailed analytics and insights
- **Risks**: Risk assessment and alerts
- **Integrations**: Jira connection settings
- **Settings**: User preferences and configurations

### Data Management
- **File Upload Zone**: Drag-and-drop CSV file uploads
- **Data Preview Dialog**: Preview of uploaded data before processing
- **CSV Export**: Download reports and analytics as CSV

## Backend Features

### API Endpoints

#### Authentication (`/api/auth`)
- `/register` - User registration with email verification
- `/login` - User authentication
- `/verify-email` - OTP verification
- `/resend-verification` - Resend verification OTP
- `/forgot-password` - Password reset request
- `/reset-password` - Password reset with OTP
- `/me` - Get current user info

#### Jira Integration (`/api/jira`)
- `/connect` - Connect to Jira Cloud
- `/sync` - Sync projects and tasks
- `/projects` - Get Jira projects
- `/epics` - Get Jira epics
- `/stories` - Get Jira stories
- `/tasks` - Get Jira tasks

#### User Management (`/api/users`)
- `/all` - Get all users
- `/create` - Create user
- `/update/{user_id}` - Update user
- `/delete/{user_id}` - Delete user
- `/assign-role` - Assign user roles

#### Task Management (`/api/tasks`)
- `/all` - Get all tasks
- `/create` - Create task
- `/update/{task_id}` - Update task
- `/delete/{task_id}` - Delete task
- `/prioritize` - Task prioritization

#### File Management (`/api/files`)
- `/upload` - Upload files
- `/download/{filename}` - Download files
- `/list` - List available files
- `/preview` - Preview file data

#### Reports (`/api/reports`)
- `/analytics` - Get analytics data
- `/generate` - Generate reports
- `/export` - Export reports as CSV
- `/summary` - Get report summaries

#### Risk Assessment (`/api/risks`)
- `/analyze` - Analyze risks
- `/alerts` - Get risk alerts
- `/patterns` - Get risk patterns
- `/monitor` - Monitor ongoing risks

#### Dashboard (`/api/dashboard`)
- `/stats` - Get dashboard statistics
- `/charts` - Get chart data
- `/analytics` - Get analytics data
- `/recent-activity` - Get recent activity

### Data Models
- **User**: User authentication and profile information
- **Task**: Task details and status
- **Project**: Jira project information
- **Epic**: Jira epic information
- **Story**: Jira story information
- **Risk Alert**: Risk detection and alerting
- **Report**: Analytics and reporting data
- **OTP**: One-time password storage

## Jira Integration

### Setup Process
1. **Obtain Jira Credentials**:
   - Domain: Your Jira instance URL (e.g., `company.atlassian.net`)
   - Email: Your Jira account email
   - API Token: Generate from Jira settings > Security

2. **Connect to Jira**:
   - Navigate to Integrations page
   - Enter Jira credentials
   - Test connection
   - Save configuration

3. **Sync Projects**:
   - Trigger manual sync or wait for scheduled sync
   - View synced projects, epics, stories, and tasks

### Synchronization Features
- **Automatic Sync**: Scheduled synchronization with Jira
- **Manual Sync**: On-demand synchronization
- **Incremental Updates**: Only sync changes since last sync
- **Conflict Resolution**: Handle overlapping data gracefully

## Data Management

### File Upload Process
1. **Prepare CSV File**: Ensure proper format with required columns
2. **Upload File**: Use drag-and-drop or file selection
3. **Preview Data**: Review data before processing
4. **Process Data**: Confirm and process the uploaded data
5. **Verify Results**: Check for successful processing

### Supported Data Types
- **Employee Leave Data**: Leave patterns and schedules
- **Task Information**: Project tasks and deadlines
- **User Data**: Employee profiles and information
- **Risk Data**: Historical risk patterns and alerts

### Data Processing
- **Validation**: Check data integrity and format
- **Transformation**: Convert to internal data structures
- **Storage**: Save to MongoDB collections
- **Indexing**: Optimize for search and retrieval

## Risk Assessment

### Risk Detection Mechanisms
- **Leave Pattern Analysis**: Identify overlaps between leaves and critical tasks
- **Deadline Monitoring**: Track approaching task deadlines
- **Resource Availability**: Monitor team capacity and availability
- **Historical Patterns**: Learn from past risk incidents

### Risk Categories
- **High Priority**: Immediate attention required
- **Medium Priority**: Monitor and plan response
- **Low Priority**: Track for future reference

### Risk Mitigation
- **Alert Notifications**: Proactive risk alerts
- **Suggestion Engine**: Recommended mitigation strategies
- **Impact Assessment**: Evaluate potential consequences
- **Resolution Tracking**: Monitor risk resolution progress

## User Management

### Roles and Permissions
- **Admin**: Full system access and management
- **Manager**: Team and project management
- **User**: Standard task and data access
- **Viewer**: Read-only access to reports and analytics

### User Operations
- **Registration**: Self-service user registration
- **Verification**: Email-based account verification
- **Profile Management**: Update personal information
- **Role Assignment**: Administrative role management

### Security Features
- **JWT Authentication**: Secure token-based authentication
- **Password Policies**: Enforce strong passwords
- **Session Management**: Secure session handling
- **Access Logging**: Track user activities

## Reports

### Report Types
- **Project Analytics**: Project performance and metrics
- **Team Productivity**: Team efficiency and output
- **Risk Analysis**: Risk exposure and trends
- **Task Progress**: Task completion and timelines
- **Resource Utilization**: Resource allocation and usage

### Report Generation
- **Scheduled Reports**: Automated report generation
- **Ad-hoc Reports**: On-demand report creation
- **Export Options**: Multiple export formats
- **Visualization**: Charts and graphs for insights

### Analytics Features
- **Interactive Charts**: Drill-down and filtering
- **Comparative Analysis**: Compare different time periods
- **Trend Identification**: Spot patterns and trends
- **Predictive Insights**: Forecast future performance

## Deployment

### Local Development
```bash
# Backend
cd backend
python main.py

# Frontend
cd frontend
npm run dev
```

### Production Deployment

#### Backend (Render)
1. Create Render account and new Web Service
2. Connect to your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host=0.0.0.0 --port=$PORT`
5. Add environment variables in Render dashboard

#### Frontend (Vercel/Netlify)
1. Create account on Vercel or Netlify
2. Import your repository
3. Set build settings:
   - Build command: `npm run build`
   - Output directory: `dist`
4. Add environment variables

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build
```

## Configuration

### OTP Bypass (Development)
For development without email service:
```env
BYPASS_OTP_VERIFICATION=true
```

### Production Settings
```env
BYPASS_OTP_VERIFICATION=false
SECRET_KEY=production-secret-key
```

## Troubleshooting

### Common Issues
- **Jira Connection**: Verify API token permissions and domain
- **Database Connection**: Check MongoDB URL and credentials
- **Email Delivery**: Validate Resend configuration and sender email
- **Frontend API Calls**: Confirm API URL configuration

### Debugging
- Check backend logs for error details
- Verify environment variable configuration
- Test API endpoints individually
- Review network connectivity and CORS settings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test thoroughly
4. Submit a pull request

## License

This project is licensed under the MIT License.

---

For support or questions, please contact the development team.