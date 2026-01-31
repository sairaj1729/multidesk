# Multi Desk Jira Dashboard - User Manual

## Table of Contents
- [Getting Started](#getting-started)
- [Registration and Login](#registration-and-login)
- [Dashboard Overview](#dashboard-overview)
- [Navigation Guide](#navigation-guide)
- [Feature-by-Feature Guide](#feature-by-feature-guide)
  - [Dashboard Analytics](#dashboard-analytics)
  - [Task Management](#task-management)
  - [User Management](#user-management)
  - [Data Management](#data-management)
  - [Reports](#reports)
  - [Risk Assessment](#risk-assessment)
  - [Integrations](#integrations)
  - [Settings](#settings)
- [Jira Integration](#jira-integration)
- [Troubleshooting](#troubleshooting)

## Getting Started

Welcome to the Multi Desk Jira Dashboard! This user manual will guide you through all features and functionalities of the platform.

### Prerequisites
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection
- Jira Cloud account (for integration features)

## Registration and Login

### Registering a New Account
1. Navigate to the homepage/login page
2. Click on "Create Account" or "Register" button
3. Fill in the registration form:
   - First Name
   - Last Name
   - Email Address
   - Password (minimum 6 characters)
   - Confirm Password
4. Click "Create Account"
5. If OTP verification is enabled:
   - Check your email for the verification code
   - Enter the OTP code when prompted
   - Or if bypassed, you'll be redirected to login immediately
6. After successful registration, you'll be logged in or redirected to login

### Logging In
1. Go to the login page
2. Enter your registered email address
3. Enter your password
4. Click "Sign In"
5. You'll be redirected to the dashboard

### Forgot Password
1. Click "Forgot Password" on the login page
2. Enter your email address
3. Check your email for the reset OTP
4. Enter the OTP and set a new password

## Dashboard Overview

The dashboard is your central hub for monitoring project status, analytics, and important metrics.

### Dashboard Components
- **Stat Cards**: Show key metrics like total users, tasks, projects, and risks
- **Analytics Charts**: Visual representations of project data and trends
- **Risk Alerts**: Display of any detected risks requiring attention
- **Recent Activity**: Shows recent system activity and updates

## Navigation Guide

### Sidebar Navigation
The left sidebar contains all main navigation options:

- **Dashboard**: Return to the main dashboard
- **Tasks**: Manage and prioritize tasks
- **Users**: User management and administration
- **Data Management**: File uploads and data handling
- **Reports**: View and generate reports
- **Risks**: Risk assessment and monitoring
- **Integrations**: Jira connection settings
- **Settings**: User preferences and account settings

### Top Navigation Bar
- **Logo**: Click to return to dashboard
- **User Profile**: Access profile settings and logout
- **Notifications**: View system notifications
- **Help**: Access help documentation

## Feature-by-Feature Guide

### Dashboard Analytics

#### Viewing Analytics
1. Land on the dashboard page
2. View stat cards showing:
   - Total Users
   - Active Projects
   - Pending Tasks
   - Identified Risks
3. Browse through various charts:
   - Task Distribution Chart
   - Project Status Chart
   - Team Productivity Chart
   - Risk Trend Chart

#### Interacting with Charts
- Hover over chart elements for detailed information
- Click on chart segments to drill down into specific data
- Use chart controls to adjust time ranges and filters

### Task Management

#### Viewing Tasks
1. Navigate to "Tasks" in the sidebar
2. View the list of all tasks
3. Tasks are organized by priority using the Eisenhower Matrix
4. Filter tasks by:
   - Priority (Urgent/Important, Not Urgent/Important, etc.)
   - Status (Pending, In Progress, Completed)
   - Project
   - Assignee

#### Creating a New Task
1. Click "Add Task" or "Create Task" button
2. Fill in task details:
   - Task Title
   - Description
   - Priority Level
   - Due Date
   - Assigned User
   - Project Association
3. Click "Save Task"

#### Updating a Task
1. Find the task in the list
2. Click the "Edit" button or task title
3. Modify the task details as needed
4. Click "Update Task"

#### Deleting a Task
1. Find the task in the list
2. Click the "Delete" button
3. Confirm deletion in the confirmation dialog

#### Task Prioritization (Eisenhower Matrix)
Tasks are automatically categorized using the Eisenhower Matrix:
- **Do First**: Urgent and Important
- **Schedule**: Not Urgent but Important  
- **Delegate**: Urgent but Not Important
- **Eliminate**: Not Urgent and Not Important

### User Management

#### Viewing Users
1. Navigate to "Users" in the sidebar
2. See the list of all registered users
3. View user details including:
   - Name
   - Email
   - Role
   - Status
   - Last Login

#### Managing User Roles
1. Go to the Users page
2. Find the user you want to modify
3. Click "Edit" or "Manage Role"
4. Select the appropriate role:
   - Admin: Full system access
   - Manager: Team and project management
   - User: Standard access
   - Viewer: Read-only access
5. Save changes

#### Adding a New User
1. Click "Add User" or "Create User" button
2. Enter user details:
   - First Name
   - Last Name
   - Email Address
   - Role Assignment
3. Click "Create User"
4. The user will receive an invitation email (if enabled)

#### Editing User Information
1. Find the user in the list
2. Click "Edit" button
3. Modify user details as needed
4. Click "Update User"

### Data Management

#### Uploading Files
1. Navigate to "Data Management" in the sidebar
2. Click "Upload File" or drag and drop a file into the upload zone
3. Select a CSV file containing your data
4. Wait for the file to upload
5. Review the data preview
6. Confirm and process the data
7. Check for success confirmation

#### Supported File Types
- **CSV Files**: For employee data, leave schedules, task information
- **Excel Files**: Converted to CSV format during upload

#### Data Formats
- **Employee Leave Data**: Columns for Name, Email, Leave Start Date, Leave End Date, Leave Type
- **Task Data**: Columns for Task Name, Project, Assignee, Due Date, Priority
- **User Data**: Columns for Name, Email, Department, Role

#### Downloading Data
1. Go to Data Management
2. Look for export/download buttons
3. Select the data you want to export
4. Choose format (usually CSV)
5. Click download

### Reports

#### Viewing Reports
1. Navigate to "Reports" in the sidebar
2. Browse available report types:
   - Project Analytics
   - Team Productivity
   - Risk Analysis
   - Task Progress
   - Resource Utilization

#### Generating Custom Reports
1. Go to the Reports section
2. Click "Create Report" or "Generate Report"
3. Select report type and parameters
4. Choose date ranges and filters
5. Click "Generate"

#### Exporting Reports
1. View the report you want to export
2. Click "Export" or "Download" button
3. Choose export format (PDF, Excel, CSV)
4. Download the file

### Risk Assessment

#### Viewing Risks
1. Navigate to "Risks" in the sidebar
2. See a list of all identified risks
3. Risks are categorized by severity:
   - Critical
   - High
   - Medium
   - Low

#### Risk Details
1. Click on a risk item to view details
2. See information about:
   - Risk Type
   - Affected Users/Projects
   - Impact Level
   - Detection Date
   - Status

#### Risk Monitoring
- The system automatically monitors for new risks
- Risk alerts appear on the dashboard
- Subscribe to risk notifications in settings

### Integrations

#### Jira Integration Setup
1. Navigate to "Integrations" in the sidebar
2. Click on "Jira Connection"
3. Enter your Jira credentials:
   - Jira Domain (e.g., company.atlassian.net)
   - Email Address
   - API Token
4. Click "Connect"
5. Test the connection
6. Save the configuration

#### Syncing Jira Data
1. Go to Integrations > Jira Connection
2. Click "Sync Now" for manual sync
3. Or wait for automatic scheduled syncs
4. Monitor sync status and results

#### Managing Connected Projects
1. View synced projects in the Jira section
2. See associated epics, stories, and tasks
3. Monitor sync status of each project

### Settings

#### Profile Settings
1. Click on your profile icon in the top right
2. Select "Settings" or "Profile Settings"
3. Update your information:
   - Name
   - Email
   - Password
   - Notification Preferences

#### Account Security
1. Go to Settings
2. Update your password
3. Manage connected integrations
4. Review security logs

#### Notification Preferences
1. In Settings, find "Notifications"
2. Choose which notifications to receive
3. Set notification frequency
4. Save preferences

## Jira Integration

### Setting Up Jira Connection

#### Obtaining Jira Credentials
1. Log into your Jira Cloud account
2. Go to Settings > Apps > APIs & Tokens
3. Create an API token
4. Note your Jira domain (e.g., company.atlassian.net)
5. Use your Jira email address

#### Connecting to Jira
1. Go to Integrations > Jira Connection
2. Enter your domain, email, and API token
3. Click "Test Connection" to verify
4. Click "Save" to establish the connection

#### Syncing Data
- **Manual Sync**: Click "Sync Now" to manually sync
- **Automatic Sync**: System syncs at scheduled intervals
- **Sync History**: View previous sync results and status

### Using Jira Data

#### Viewing Synced Projects
1. Once connected, projects appear in the dashboard
2. Browse projects, epics, stories, and tasks
3. View project status and progress

#### Managing Synced Tasks
- Tasks from Jira appear in the task management section
- Update tasks directly in the dashboard
- Changes sync back to Jira

## Troubleshooting

### Common Issues

#### Login Problems
- **Forgot Password**: Use the "Forgot Password" feature
- **Account Locked**: Contact your administrator
- **Invalid Credentials**: Double-check email and password

#### Jira Integration Issues
- **Connection Failed**: Verify domain, email, and API token
- **Sync Errors**: Check Jira permissions and network connectivity
- **Missing Data**: Ensure Jira projects have accessible data

#### File Upload Issues
- **Unsupported Format**: Ensure files are in CSV format
- **Upload Failed**: Check file size limits and internet connection
- **Data Validation**: Verify data matches required format

#### Performance Issues
- **Slow Loading**: Check internet connection and refresh page
- **Chart Not Loading**: Clear browser cache and try again
- **General Slowness**: Contact support if issues persist

### Getting Help

#### Built-in Help
- Look for help icons (?) throughout the application
- Hover over buttons for tooltips
- Check the Help section in the sidebar

#### Contact Support
- Use the "Contact Support" form in Settings
- Email support team directly
- Check online documentation

## Tips and Best Practices

### Maximizing Productivity
- Regularly review dashboard analytics for insights
- Keep task priorities updated using the Eisenhower Matrix
- Maintain current user information and roles
- Schedule regular data backups

### Data Management
- Organize data in proper CSV formats before upload
- Regularly clean and update user information
- Monitor file sizes to stay within limits
- Backup important data regularly

### Collaboration
- Use task assignments effectively
- Share relevant reports with team members
- Keep integration connections updated
- Communicate risks promptly

---

For additional support or questions, please contact your system administrator or our support team.