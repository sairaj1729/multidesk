# Risk Detection UI Implementation

## Overview
Implemented a high-visibility risk detection system for the MultiDesk dashboard that alerts managers when tasks may be delayed due to employee leaves.

## Components Created

### 1. Risk Service (`services/risks.js`)
- Handles API calls to `/api/risks`
- Provides methods to fetch all risks and manually check for risks

### 2. Risks Page (`pages/Risks.jsx`)
- Dedicated page to view all risk alerts
- Displays risks in a clean, manager-friendly format
- Shows task details, assignee, dates, and risk level
- Color-coded risk levels (HIGH = red, MEDIUM = yellow, LOW = green)

### 3. Risk Indicator (`components/ui/RiskIndicator.jsx`)
- Floating button that appears in bottom-right corner
- Only visible when risks exist
- Shows dynamic count of active risks
- Animated pulse effect to draw attention
- Clicking navigates to /risks page

### 4. Risk Notification (`components/ui/RiskNotification.jsx`)
- Transient notification that appears when new risks are detected
- Compares current risk count with previous count
- Shows message: "⚠️ X tasks may be delayed due to upcoming leaves"
- Includes "View Details" button that navigates to /risks

## Features Implemented

### Persistent Risk Indicator
- Fixed position (bottom-right)
- Visible on all pages
- Only appears when risk count > 0
- Red color with warning icon
- Dynamic count badge
- Click navigates to /risks

### Risk Notifications
- Appears when new risks are detected
- Top-right positioning
- Clear warning message
- "View Details" button
- Auto-dismiss after interaction

### Risk Dashboard Page (/risks)
- Clean, readable table/list of risks
- Columns: Task ID, Task Title, Assignee, Due Date, Leave Period, Risk Level
- Color-coded risk levels
- Responsive design
- Empty state when no risks exist

## Integration Points

### Routing
- Added `/risks` route in `App.jsx`
- Integrated with existing protected route structure

### Layout
- Added `RiskIndicator` and `RiskNotification` to `AppLayout`
- Appears on all protected pages

### Sidebar
- Added "Risk Alerts" link with AlertTriangle icon
- Positioned logically in navigation flow

## Technical Details

### Data Structure
Each risk object contains:
- `task_key`: Task identifier (e.g., "SCRUM-123")
- `task_title`: Task description
- `assignee`: Employee email
- `due_date`: Task deadline
- `leave_start`: Start of employee leave
- `leave_end`: End of employee leave
- `risk_level`: HIGH/MEDIUM/LOW severity

### Polling
- RiskIndicator: Checks every 30 seconds
- RiskNotification: Checks every 60 seconds

### UX Behavior
- No risks = no red button/notification
- Risks present = persistent indicator
- New risks = transient notification
- Non-blocking workflow
- Clear navigation to details

## Files Modified/Added

1. `src/services/risks.js` - New service
2. `src/pages/Risks.jsx` - New page component
3. `src/components/ui/RiskIndicator.jsx` - New UI component
4. `src/components/ui/RiskNotification.jsx` - New UI component
5. `src/App.jsx` - Added route
6. `src/components/layout/AppLayout.jsx` - Integrated components
7. `src/components/layout/Sidebar.jsx` - Added navigation link

## Usage

1. Upload employee leave CSV file via Data Management
2. System automatically detects task/leave conflicts
3. Risk alerts appear in:
   - Floating indicator (bottom-right)
   - Transient notification (top-right)
   - Risk Alerts page (/risks)
4. Managers can review and take action

## Styling

- Uses existing UI component library (shadcn/ui)
- Consistent with current design system
- Responsive for all screen sizes
- Accessible with proper ARIA labels
- Animations for attention without annoyance

## Future Enhancements

- Add risk filtering/sorting on Risks page
- Implement risk acknowledgment/dismissal
- Add email notifications
- Include risk history/timeline
- Add mitigation suggestions