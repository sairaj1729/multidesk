# Multi Desk - Complete Codebase Analysis

## 📋 Overview

Multi Desk is a comprehensive project management and risk analysis application that integrates with Jira to provide unified insights across projects, tasks, and employee leave data. The system uses a modern stack with React frontend and FastAPI backend.

## 🏗️ Architecture

### Backend (Python/FastAPI)
- **Framework**: FastAPI with ASGI
- **Database**: MongoDB (MongoDB Atlas)
- **Authentication**: JWT with email verification
- **External Integrations**: Jira API
- **Email Service**: Resend API
- **File Processing**: Pandas for Excel/CSV processing

### Frontend (React/Vite)
- **Framework**: React 18 with Vite
- **UI Library**: shadcn/ui components
- **State Management**: React Query for server state
- **Routing**: React Router DOM
- **Styling**: Tailwind CSS

## 🔐 Authentication System

### Backend Components
- **Location**: `backend/services/auth_service.py`
- **Key Features**:
  - User registration with email verification
  - JWT token-based authentication
  - Password hashing with bcrypt/sha256
  - Email verification via OTP
  - Password reset functionality
  - OTP bypass configuration for development

### Frontend Components
- **Location**: `frontend/src/services/auth.js`
- **Key Components**:
  - `ProtectedRoute` component for route protection
  - Authentication service with local storage
  - Token management and user session handling

## 📊 Data Storage & Management

### MongoDB Collections
1. **users** - User accounts and profiles
2. **jira_credentials** - Encrypted Jira API credentials
3. **jira_tasks** - Synced Jira tasks and issues
4. **leaves** - Employee leave records from uploaded files
5. **files** - Uploaded file metadata
6. **risk_alerts** - Generated risk analysis results
7. **reports** - Generated reports metadata

### Data Flow Process
```
1. User uploads leave data file (Excel/CSV)
2. File is processed by leave_processor.py
3. Leave records are stored in 'leaves' collection
4. Risk analysis service checks for conflicts
5. Risk alerts are generated and stored in 'risk_alerts'
6. Dashboard displays unified insights
```

## 🎯 Core Features

### 1. Jira Integration
**Backend**: `backend/services/jira_service.py`
- Connects to Jira instances using API tokens
- Encrypts credentials using Fernet encryption
- Fetches tasks, projects, users, and issue types
- Synchronizes data to local MongoDB
- Supports custom fields (Story Points, Start Date, Sprint)

**Frontend**: `frontend/src/pages/JiraConnection.jsx`
- User-friendly connection form
- Real-time validation and feedback
- Automatic redirection after successful connection

### 2. Risk Analysis System
**Backend**: `backend/services/risk_service.py`
- Analyzes task conflicts with employee leaves
- Calculates risk scores based on:
  - Leave overlap with due dates
  - Task priority and status
  - Story points and complexity
  - Unassigned tasks
  - Start date delays
- Risk levels: CRITICAL, HIGH, MEDIUM, LOW
- Automatic analysis triggers after data sync

**Frontend**: `frontend/src/pages/Risks.jsx`
- Visual risk dashboard with color-coded alerts
- Detailed risk information display
- Manual risk analysis trigger
- Real-time risk count indicator

### 3. Data Management
**Backend**: 
- `backend/services/files_service.py` - File upload/download management
- `backend/services/leave_processor.py` - Excel/CSV processing

**Frontend**: `frontend/src/pages/DataManagement.jsx`
- Drag-and-drop file upload
- Supported formats: Excel (.xlsx, .xls), CSV
- File preview and management
- Processing status tracking

### 4. Dashboard & Analytics
**Backend**: `backend/services/dashboard_service.py`
- Aggregates task statistics
- Eisenhower Matrix implementation
- Task velocity tracking
- Issue type distribution

**Frontend**: `frontend/src/pages/Dashboard.jsx`
- Stat cards for key metrics
- Interactive charts and visualizations
- One-click data synchronization
- Real-time updates

### 5. Task Management
**Backend**: `backend/services/tasks_service.py`
- Task filtering and search
- Pagination support
- Status-based filtering
- Priority and assignee filtering

**Frontend**: `frontend/src/pages/Tasks.jsx`
- Task listing with filters
- Detailed task information
- Assignee management

## 🔄 Data Flow Architecture

### Authentication Flow
```
1. User registers → Email verification sent
2. User verifies email → Account activated
3. User logs in → JWT token generated
4. Token stored in localStorage
5. Protected routes check token validity
6. API requests include Authorization header
```

### Jira Integration Flow
```
1. User connects Jira → Credentials stored encrypted
2. Initial sync fetches projects/tasks
3. Tasks stored in jira_tasks collection
4. Risk analysis triggered automatically
5. Dashboard updated with new data
```

### File Processing Flow
```
1. User uploads leave file
2. File stored in uploads directory
3. Background task processes file
4. Leave records inserted into database
5. Risk analysis triggered
6. Results displayed in risk dashboard
```

## 🔌 API Integration Points

### Core Endpoints

**Authentication**: `/api/auth/`
- `POST /register` - User registration
- `POST /login` - User login
- `POST /verify-email` - Email verification
- `POST /forgot-password` - Password reset
- `GET /me` - Current user info

**Jira Integration**: `/api/jira/`
- `POST /connect` - Connect Jira account
- `POST /sync` - Sync Jira data
- `GET /connection-status` - Check connection
- Various endpoints for issues, projects, users

**Tasks**: `/api/tasks/`
- `GET /` - List tasks with filtering
- `GET /{id}` - Get specific task
- `GET /debug/all` - Debug task data

**Files**: `/api/files/`
- `POST /upload` - Upload files
- `GET /` - List files
- `GET /{id}/download` - Download file
- `DELETE /{id}` - Delete file

**Risks**: `/api/risks/`
- `GET /check` - Trigger risk analysis
- `GET /` - Get risk alerts

## 🛠️ Key Technical Components

### Security Features
- **Password Encryption**: bcrypt/sha256 with salt
- **Token Security**: JWT with expiration
- **Credential Encryption**: Fernet encryption for Jira tokens
- **CORS Protection**: Configured allowed origins
- **Input Validation**: Pydantic models for data validation

### Performance Optimizations
- **Background Processing**: File processing in background tasks
- **Database Indexing**: Optimized queries with indexes
- **Pagination**: Server-side pagination for large datasets
- **Caching**: React Query for client-side caching

### Error Handling
- **Backend**: Comprehensive exception handling with logging
- **Frontend**: User-friendly error messages and toast notifications
- **Validation**: Form validation and API error responses

## 📈 Future Enhancement Opportunities

### Backend Improvements
1. **Caching Layer**: Redis for frequently accessed data
2. **Real-time Updates**: WebSocket integration for live updates
3. **Advanced Analytics**: Machine learning for risk prediction
4. **API Rate Limiting**: Better Jira API rate limiting
5. **Audit Logging**: Comprehensive audit trail

### Frontend Enhancements
1. **Dark Mode**: Complete dark theme support
2. **Mobile Responsiveness**: Enhanced mobile experience
3. **Offline Support**: PWA capabilities
4. **Advanced Filtering**: More sophisticated search capabilities
5. **Custom Dashboards**: User-configurable widgets

### Feature Additions
1. **Notifications**: Email/push notifications for critical risks
2. **Team Collaboration**: Shared project views and commenting
3. **Resource Planning**: Capacity and resource allocation tools
4. **Reporting**: Advanced report generation and scheduling
5. **Integrations**: Slack, Microsoft Teams, Google Calendar

## 🎯 Key Strengths

1. **Comprehensive Integration**: Seamless Jira integration with local data storage
2. **Risk Intelligence**: Proactive risk detection and analysis
3. **User Experience**: Clean, intuitive interface with good UX patterns
4. **Data Security**: Strong encryption and security practices
5. **Scalable Architecture**: Well-structured codebase for future growth
6. **Real-time Updates**: Immediate feedback and data synchronization

## 📊 Data Model Relationships

```
User (1) → (n) Jira Credentials
User (1) → (n) Jira Tasks
User (1) → (n) Files
User (1) → (n) Risk Alerts
User (1) → (n) Leave Records
File (1) → (n) Leave Records
Task (1) → (1) Assignee (User)
Risk Alert (1) → (1) Task
Risk Alert (1) → (1) Leave Record
```

## 🚀 Deployment Architecture

- **Frontend**: Vercel deployment (static assets)
- **Backend**: Render deployment (FastAPI application)
- **Database**: MongoDB Atlas (cloud database)
- **Email Service**: Resend API
- **Environment Variables**: Secure configuration management

## 📝 Configuration & Environment

Key environment variables:
- `SECRET_KEY` - JWT secret key
- `FERNET_KEY` - Encryption key for sensitive data
- `MONGODB_URL` - MongoDB connection string
- `RESEND_API_KEY` - Email service API key
- `BYPASS_OTP_VERIFICATION` - Development convenience flag

## 🎨 UI/UX Highlights

- **Consistent Design System**: shadcn/ui components with Tailwind CSS
- **Responsive Layout**: Mobile-first design approach
- **Accessibility**: Proper ARIA labels and keyboard navigation
- **Visual Feedback**: Loading states, success/error indicators
- **Intuitive Navigation**: Clear sidebar navigation and breadcrumbs