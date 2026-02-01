import {
  Bar,
  BarChart,
  Line,
  LineChart,
  Pie,
  PieChart,
  Cell,
  ResponsiveContainer,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";

// Default data for fallback with improved colors
const defaultTasksByStatusData = [
  { name: "To Do", value: 30, fill: "#3b82f6" },    // Blue for TODO
  { name: "In Progress", value: 45, fill: "#f59e0b" }, // Amber for In Progress
  { name: "Done", value: 60, fill: "#10b981" },    // Emerald for Done
  { name: "Blocked", value: 15, fill: "#ef4444" },  // Red for Blocked
];

const defaultTaskVelocityData = [
  { month: "Aug", tasks: 30, completed: 25 },
  { month: "Sep", tasks: 35, completed: 28 },
  { month: "Oct", tasks: 40, completed: 32 },
  { month: "Nov", tasks: 45, completed: 38 },
  { month: "Dec", tasks: 38, completed: 30 },
  { month: "Jan", tasks: 32, completed: 28 },
];

const defaultIssueTypeData = [
  { name: "Task", value: 35, fill: "#6366f1" },     // Indigo for Task
  { name: "Story", value: 40, fill: "#8b5cf6" },   // Violet for Story
  { name: "Epic", value: 15, fill: "#ec4899" },    // Pink for Epic
  { name: "Bug", value: 10, fill: "#f97316" },     // Orange for Bug
];

export function AnalyticsCharts({ data }) {
  // Color mapping for common status values
  const getStatusColor = (status) => {
    const colorMap = {
      "To Do": "#3b82f6",      // Blue
      "Todo": "#3b82f6",       // Blue
      "TO DO": "#3b82f6",      // Blue
      "In Progress": "#f59e0b", // Amber
      "In Review": "#f59e0b",  // Amber
      "In Development": "#f59e0b", // Amber
      "Done": "#10b981",       // Emerald
      "Closed": "#10b981",     // Emerald
      "Resolved": "#10b981",   // Emerald
      "Blocked": "#ef4444",    // Red
      "Open": "#8b5cf6",       // Violet
      "Backlog": "#6366f1",    // Indigo
      "Ready": "#10ac84",      // Green
      "Cancelled": "#6b7280",  // Gray
      "Deferred": "#9ca3af",   // Gray
      default: "#94a3b8"       // Slate
    };
    return colorMap[status] || colorMap.default;
  };

  // Color mapping for issue types
  const getIssueTypeColor = (type) => {
    const colorMap = {
      "Task": "#6366f1",       // Indigo
      "Story": "#8b5cf6",      // Violet
      "Epic": "#ec4899",       // Pink
      "Bug": "#f97316",        // Orange
      "Sub-task": "#0ea5e9",   // Sky
      "Subtask": "#0ea5e9",    // Sky
      "Feature": "#10b981",    // Emerald
      "Improvement": "#84cc16", // Lime
      default: "#94a3b8"       // Slate
    };
    return colorMap[type] || colorMap.default;
  };

  // Use real data if provided, otherwise use defaults
  const tasksByStatusData = data?.tasks_by_status?.length > 0 
    ? data.tasks_by_status.map(item => ({
        name: item.name,
        value: item.value,
        fill: getStatusColor(item.name)
      }))
    : defaultTasksByStatusData;

  const taskVelocityData = data?.task_velocity?.length > 0
    ? data.task_velocity.map(item => ({
        month: item.month,
        tasks: item.tasks,
        completed: item.completed
      }))
    : defaultTaskVelocityData;

  const issueTypeData = data?.issue_type_distribution?.length > 0
    ? data.issue_type_distribution.map(item => ({
        name: item.name,
        value: item.value,
        fill: getIssueTypeColor(item.name)
      }))
    : defaultIssueTypeData;

  return (
    <div className="bg-card rounded-lg p-6 shadow-lg hover:shadow-xl transition-all duration-200 border border-border">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-foreground">
          Jira & Employee Analytics
        </h2>
        <p className="text-sm text-muted-foreground">
          Visualizing operational and human resources data trends.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Tasks by Status */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-foreground">
            Tasks by Status
          </h3>
          <p className="text-xs text-muted-foreground">
            Jira Task Distribution
          </p>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={tasksByStatusData}>
                <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} axisLine={false} />
                <YAxis tick={{ fontSize: 12 }} axisLine={false} />
                <Tooltip />
                <Bar dataKey="value" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Task Velocity */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-foreground">Task Velocity</h3>
          <p className="text-xs text-muted-foreground">
            Monthly completion rate
          </p>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={taskVelocityData}>
                <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} axisLine={false} />
                <YAxis tick={{ fontSize: 12 }} axisLine={false} />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="tasks"
                  name="Tasks"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={{ fill: "#3b82f6", strokeWidth: 2, r: 4 }}
                />
                <Line
                  type="monotone"
                  dataKey="completed"
                  name="Completed"
                  stroke="#10b981"
                  strokeWidth={2}
                  dot={{ fill: "#10b981", strokeWidth: 2, r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Issue Type Distribution */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-foreground">
            Issue Type Distribution
          </h3>
          <p className="text-xs text-muted-foreground">Jira issue breakdown</p>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={issueTypeData}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="value"
                  nameKey="name"
                >
                  {issueTypeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AnalyticsCharts;