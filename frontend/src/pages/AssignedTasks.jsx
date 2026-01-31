import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Search, Filter, Calendar, AlertCircle, CheckCircle, Clock, Hash } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { tasksService } from "@/services/tasks";
import { apiService } from "@/services/api";
import { jiraService } from "@/services/jira";

export default function AssignedTasks() {
  const { accountId } = useParams();
  const navigate = useNavigate();
  const [tasks, setTasks] = useState([]);
  const [filteredTasks, setFilteredTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [priorityFilter, setPriorityFilter] = useState("all");
  const [assigneeName, setAssigneeName] = useState("");

  useEffect(() => {
    if (accountId) {
      fetchAssignedTasks();
    }
  }, [accountId]);

  useEffect(() => {
    filterTasks();
  }, [tasks, searchTerm, statusFilter, priorityFilter]);

  const fetchAssignedTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log("Fetching tasks for account ID:", accountId);
      
      // First, let's debug what assignees we have
      try {
        const debugResponse = await apiService.get('/api/tasks/debug/all');
        console.log("Debug data:", debugResponse);
      } catch (debugErr) {
        console.log("Debug endpoint failed:", debugErr);
      }
      
      const response = await tasksService.getTasks();
      
      console.log("Tasks API response:", response);
      
      if (response.success) {
        console.log("Total tasks received:", response.data.tasks.length);
        
        // Log all unique assignee account IDs in the tasks
        const allAccountIds = [...new Set(response.data.tasks.map(t => t.assignee_account_id))];
        console.log("All account IDs in tasks:", allAccountIds);
        console.log("Looking for account ID:", accountId);
        
        // Filter tasks assigned to this specific user
        const userTasks = response.data.tasks.filter(task => {
          const isMatch = task.assignee_account_id === accountId;
          if (isMatch) {
            console.log("Found matching task:", {
              key: task.key,
              summary: task.summary,
              assignee_account_id: task.assignee_account_id,
              accountId: accountId
            });
          }
          return isMatch;
        });
        
        console.log("Filtered tasks for this user:", userTasks.length);
        
        setTasks(userTasks);
        
        // Get assignee name from first task
        if (userTasks.length > 0) {
          setAssigneeName(userTasks[0].assignee || "Unknown User");
        } else {
          // Try to get assignee name from the assignee data
          setAssigneeName("User");
        }
      } else {
        setError(response.error);
      }
    } catch (err) {
      setError("Failed to load assigned tasks");
      console.error("Error fetching assigned tasks:", err);
    } finally {
      setLoading(false);
    }
  };

  const filterTasks = () => {
    let filtered = [...tasks];
    
    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(task => 
        task.summary?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        task.project_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        task.key?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    // Apply status filter
    if (statusFilter !== "all") {
      filtered = filtered.filter(task => task.status === statusFilter);
    }
    
    // Apply priority filter
    if (priorityFilter !== "all") {
      filtered = filtered.filter(task => task.priority === priorityFilter);
    }
    
    setFilteredTasks(filtered);
  };

  const getTaskStatusBadge = (status) => {
    const statusColors = {
      "To Do": "bg-gray-100 text-gray-800",
      "In Progress": "bg-blue-100 text-blue-800",
      "Done": "bg-green-100 text-green-800",
      "In Review": "bg-yellow-100 text-yellow-800",
      "Blocked": "bg-red-100 text-red-800"
    };
    
    const colorClass = statusColors[status] || "bg-muted text-muted-foreground";
    return <Badge className={colorClass}>{status}</Badge>;
  };

  const getPriorityBadge = (priority) => {
    const priorityColors = {
      "Highest": "bg-red-500 text-white",
      "High": "bg-orange-500 text-white", 
      "Medium": "bg-yellow-500 text-black",
      "Low": "bg-green-500 text-white",
      "Lowest": "bg-gray-500 text-white"
    };
    
    const colorClass = priorityColors[priority] || "bg-muted text-muted-foreground";
    return <Badge className={colorClass}>{priority}</Badge>;
  };

  const getStatusCounts = () => {
    const counts = {
      "To Do": 0,
      "In Progress": 0,
      "Done": 0,
      "In Review": 0,
      "Blocked": 0
    };
    
    tasks.forEach(task => {
      if (counts.hasOwnProperty(task.status)) {
        counts[task.status]++;
      }
    });
    
    return counts;
  };

  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" onClick={() => navigate(-1)}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <h1 className="text-2xl font-bold">Loading Assigned Tasks...</h1>
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
        <div className="flex items-center space-x-4">
          <Button variant="ghost" onClick={() => navigate(-1)}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <h1 className="text-2xl font-bold">Assigned Tasks</h1>
        </div>
        <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-6 text-center">
          <AlertCircle className="w-12 h-12 text-destructive mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-destructive">Error Loading Tasks</h2>
          <p className="mt-2 text-destructive/80">{error}</p>
          <Button 
            onClick={fetchAssignedTasks}
            className="mt-4"
          >
            Retry
          </Button>
        </div>
      </div>
    );
  }

  const statusCounts = getStatusCounts();

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <Button variant="ghost" onClick={() => navigate(-1)}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Profile
        </Button>
        <div>
          <h1 className="text-2xl font-bold">Assigned Tasks</h1>
          <p className="text-muted-foreground">Tasks assigned to {assigneeName}</p>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-dashboard-primary">{tasks.length}</div>
            <div className="text-sm text-muted-foreground">Total Tasks</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-blue-500">{statusCounts["In Progress"]}</div>
            <div className="text-sm text-muted-foreground">In Progress</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-green-500">{statusCounts["Done"]}</div>
            <div className="text-sm text-muted-foreground">Completed</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-yellow-500">{statusCounts["In Review"]}</div>
            <div className="text-sm text-muted-foreground">In Review</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-red-500">{statusCounts["Blocked"]}</div>
            <div className="text-sm text-muted-foreground">Blocked</div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Filter className="w-5 h-5" />
            <span>Filter Tasks</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
              <Input
                placeholder="Search tasks..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="To Do">To Do</SelectItem>
                <SelectItem value="In Progress">In Progress</SelectItem>
                <SelectItem value="Done">Done</SelectItem>
                <SelectItem value="In Review">In Review</SelectItem>
                <SelectItem value="Blocked">Blocked</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={priorityFilter} onValueChange={setPriorityFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Filter by priority" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Priorities</SelectItem>
                <SelectItem value="Highest">Highest</SelectItem>
                <SelectItem value="High">High</SelectItem>
                <SelectItem value="Medium">Medium</SelectItem>
                <SelectItem value="Low">Low</SelectItem>
                <SelectItem value="Lowest">Lowest</SelectItem>
              </SelectContent>
            </Select>
            
            <div className="flex items-center justify-between text-sm text-muted-foreground">
              <span>Showing:</span>
              <Badge variant="secondary">{filteredTasks.length} of {tasks.length}</Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tasks List */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold">
          Task List ({filteredTasks.length} tasks)
        </h2>
        
        {filteredTasks.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <CheckCircle className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium text-muted-foreground">No Tasks Found</h3>
              <p className="text-muted-foreground mt-1">
                {searchTerm || statusFilter !== "all" || priorityFilter !== "all" 
                  ? "Try adjusting your filters or search term."
                  : "This assignee doesn't have any tasks assigned in the current dataset."}
              </p>
              <div className="mt-4">
                <Button 
                  variant="outline" 
                  onClick={async () => {
                    // Try to sync Jira data
                    try {
                      const jiraResponse = await jiraService.syncJiraData();
                      console.log("Sync response:", jiraResponse);
                      if (jiraResponse.success) {
                        // Refresh tasks after sync
                        fetchAssignedTasks();
                      }
                    } catch (syncErr) {
                      console.error("Sync failed:", syncErr);
                    }
                  }}
                >
                  Sync Jira Data
                </Button>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {filteredTasks.map((task) => (
              <Card key={task.id || task.jira_id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg line-clamp-2">
                        {task.summary || task.title}
                      </CardTitle>
                      <CardDescription className="mt-1 flex items-center space-x-2">
                        <span>{task.key}</span>
                        <span>•</span>
                        <span>{task.project_name || task.project_key}</span>
                      </CardDescription>
                    </div>
                    <div className="flex flex-col space-y-1 ml-2">
                      {getTaskStatusBadge(task.status)}
                      {getPriorityBadge(task.priority)}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Issue Type:</span>
                        <div className="font-medium">{task.issue_type || "Task"}</div>
                      </div>
                      {task.story_points && (
                        <div>
                          <span className="text-muted-foreground">Story Points:</span>
                          <div className="font-medium">{task.story_points}</div>
                        </div>
                      )}
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      {task.duedate && (
                        <div>
                          <span className="text-muted-foreground">Due Date:</span>
                          <div className={new Date(task.duedate) < new Date() ? "font-medium text-destructive" : "font-medium"}>
                            {new Date(task.duedate).toLocaleDateString()}
                          </div>
                        </div>
                      )}
                      <div>
                        <span className="text-muted-foreground">Last Updated:</span>
                        <div className="font-medium">{new Date(task.updated).toLocaleDateString()}</div>
                      </div>
                    </div>
                    
                    {task.sprint && (
                      <div className="pt-2 border-t flex items-center space-x-2">
                        <Hash className="w-4 h-4 text-muted-foreground" />
                        <span className="text-sm text-muted-foreground">Sprint:</span>
                        <Badge variant="outline">{task.sprint}</Badge>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}