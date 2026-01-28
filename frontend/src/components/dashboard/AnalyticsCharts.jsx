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

// Default data for fallback
const defaultTasksByStatusData = [
  { name: "Pending", value: 25, fill: "hsl(var(--chart-4))" },
  { name: "In Progress", value: 45, fill: "hsl(var(--chart-3))" },
  { name: "Done", value: 85, fill: "hsl(var(--chart-2))" },
  { name: "Verified", value: 15, fill: "hsl(var(--chart-1))" },
];

const defaultTaskVelocityData = [
  { month: "Jan", tasks: 40, completed: 35 },
  { month: "Feb", tasks: 45, completed: 40 },
  { month: "Mar", tasks: 38, completed: 42 },
  { month: "Apr", tasks: 55, completed: 48 },
  { month: "May", tasks: 52, completed: 55 },
  { month: "Jun", tasks: 48, completed: 50 },
];

const defaultIssueTypeData = [
  { name: "Story", value: 45, fill: "hsl(var(--chart-1))" },
  { name: "Bug", value: 25, fill: "hsl(var(--chart-4))" },
  { name: "Task", value: 20, fill: "hsl(var(--chart-2))" },
  { name: "Epic", value: 10, fill: "hsl(var(--chart-3))" },
];

export function AnalyticsCharts({ data }) {
  // Use real data if provided, otherwise use defaults
  const tasksByStatusData = data?.tasks_by_status?.length > 0 
    ? data.tasks_by_status.map((item, index) => ({
        name: item.name,
        value: item.value,
        fill: `hsl(var(--chart-${(index % 4) + 1}))`
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
    ? data.issue_type_distribution.map((item, index) => ({
        name: item.name,
        value: item.value,
        fill: `hsl(var(--chart-${(index % 4) + 1}))`
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
                  stroke="hsl(var(--chart-1))"
                  strokeWidth={2}
                  dot={{ fill: "hsl(var(--chart-1))", strokeWidth: 2, r: 4 }}
                />
                <Line
                  type="monotone"
                  dataKey="completed"
                  name="Completed"
                  stroke="hsl(var(--chart-2))"
                  strokeWidth={2}
                  dot={{ fill: "hsl(var(--chart-2))", strokeWidth: 2, r: 4 }}
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