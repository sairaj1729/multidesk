import { useState, useEffect } from "react";
import { Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { tasksService } from "@/services/tasks";

const statusStyles = {
  "Done": "bg-emerald-100 text-emerald-800 border-emerald-200",
  "In Progress": "bg-amber-100 text-amber-800 border-amber-200",
  "To Do": "bg-slate-100 text-slate-700 border-slate-200",
};

const priorityStyles = {
  "High": "bg-red-100 text-red-800 border-red-200",
  "Medium": "bg-amber-100 text-amber-800 border-amber-200",
  "Low": "bg-blue-100 text-blue-800 border-blue-200",
};



const Pill = ({ value, styles }) => (
  <Badge className={`border ${styles} font-medium`}>
    {value}
  </Badge>
);



export default function Tasks() {
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [priorityFilter, setPriorityFilter] = useState("all");
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [totalTasks, setTotalTasks] = useState(0);

  useEffect(() => {
    fetchTasks();
  }, [searchTerm, statusFilter, priorityFilter]);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const filters = {
        search: searchTerm || undefined,
        status: statusFilter !== "all" ? statusFilter : undefined,
        priority: priorityFilter !== "all" ? priorityFilter : undefined
      };
      
      const response = await tasksService.getTasks(filters, 1, 100);
      
      if (response.success) {
        console.log("FIRST TASK RAW FROM API 👉", response.data.tasks[0]);

        setTasks(response.data.tasks);
        setTotalTasks(response.data.total);
      } else {
        setError(response.error);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading && tasks.length === 0) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold text-foreground">Jira Tasks</h1>
            <p className="text-muted-foreground">Manage and track your project tasks</p>
          </div>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold text-foreground">Jira Tasks</h1>
            <p className="text-muted-foreground">Manage and track your project tasks</p>
          </div>
        </div>
        <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-6 text-center">
          <h2 className="text-xl font-semibold text-destructive">Error Loading Tasks</h2>
          <p className="mt-2 text-destructive/80">{error}</p>
          <button 
            onClick={fetchTasks}
            className="mt-4 px-4 py-2 bg-destructive text-destructive-foreground rounded-md hover:opacity-90"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Jira Tasks</h1>
          <p className="text-muted-foreground">Manage and track your project tasks</p>
        </div>
        {/* <Button className="bg-dashboard-primary hover:bg-dashboard-primary/90">
          Create Task
        </Button> */}
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <Input
            placeholder="Search tasks..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>

        <div className="flex gap-2">
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="To Do">To Do</SelectItem>
              <SelectItem value="In Progress">In Progress</SelectItem>
              <SelectItem value="Done">Done</SelectItem>
            </SelectContent>
          </Select>

          <Select value={priorityFilter} onValueChange={setPriorityFilter}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Priority" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Priority</SelectItem>
              <SelectItem value="High">High</SelectItem>
              <SelectItem value="Medium">Medium</SelectItem>
              <SelectItem value="Low">Low</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Tasks Table */}
      <div className="bg-card rounded-xl border shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full table-fixed">
            <thead className="bg-muted/40 border-b">
              <tr>
                  <th className="w-[30%] px-6 py-4 text-xs uppercase tracking-wide">Task</th>
                  <th className="w-[12%] px-6 py-4 text-xs uppercase tracking-wide">Status</th>
                  <th className="w-[12%] px-6 py-4 text-xs uppercase tracking-wide">Priority</th>
                  <th className="w-[14%] px-6 py-4 text-xs uppercase tracking-wide">Assignee</th>
                  <th className="w-[10%] px-6 py-4 text-xs uppercase tracking-wide">Start</th>
                  <th className="w-[10%] px-6 py-4 text-xs uppercase tracking-wide">Due</th>
                  <th className="w-[12%] px-6 py-4 text-xs uppercase tracking-wide">Type</th>

              </tr>
            </thead>

            <tbody>
              {tasks.map((task) => (
               <tr
                key={task.id}
                className="border-b last:border-none hover:bg-muted/30 transition-colors"
              >
                {/* TASK */}
                <td className="px-6 py-4">
                  <div className="space-y-1">
                    <p
                      title={task.summary}
                      className="font-medium text-sm text-foreground line-clamp-2 leading-snug"
                    >
                      {task.summary}
                    </p>

                    <p className="text-xs font-mono text-muted-foreground truncate">
                      {task.key}
                    </p>
                  </div>
                </td>

                {/* STATUS */}
                <td className="px-6 py-4">
                  <Pill
                    value={task.status}
                    styles={statusStyles[task.status] || "bg-muted"}
                  />
                </td>

                {/* PRIORITY */}
                <td className="px-6 py-4">
                  <Pill
                    value={task.priority}
                    styles={priorityStyles[task.priority] || "bg-muted"}
                  />
                </td>

                {/* ASSIGNEE */}
                <td className="px-6 py-4 text-sm">
                  {task.assignee || "Unassigned"}
                </td>

                {/* START DATE */}
                <td className="px-6 py-4 text-sm text-muted-foreground">
                  {task.start_date
                    ? new Date(task.start_date || task.startDate).toLocaleDateString()
                    : "—"}
                </td>

                {/* DUE DATE */}
                <td className="px-6 py-4 text-sm">
                  {task.duedate
                    ? new Date(task.duedate).toLocaleDateString()
                    : "—"}
                </td>

                {/* TYPE */}
                <td className="px-6 py-4">
                  <Badge variant="outline" className="text-xs">
                    {task.issue_type}
                  </Badge>
                </td>
              </tr>

              ))}
            </tbody>
          </table>
        </div>

        {tasks.length === 0 && !loading && (
          <div className="p-8 text-center text-muted-foreground">
            No tasks found matching your criteria.
          </div>
        )}
      </div>
      
      {totalTasks > 0 && (
        <div className="text-sm text-muted-foreground text-center">
          Showing {tasks.length} of {totalTasks} tasks
        </div>
      )}
    </div>
  );
}