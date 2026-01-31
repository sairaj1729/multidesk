import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Mail, User, Calendar, Briefcase, Hash, CheckCircle, AlertCircle, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { jiraService } from "@/services/jira";
import { tasksService } from "@/services/tasks";

export default function AssigneeProfile() {
  const { accountId } = useParams();
  const navigate = useNavigate();
  const [assignee, setAssignee] = useState(null);
  const [assignedTasks, setAssignedTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tasksLoading, setTasksLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tasksError, setTasksError] = useState(null);

  useEffect(() => {
    if (accountId) {
      fetchAssigneeProfile();
      fetchAssignedTasks();
    }
  }, [accountId]);

  const fetchAssigneeProfile = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Try to get assignee from different sources
      const response = await jiraService.getAssignableUsers();
      
      if (response.success) {
        const foundAssignee = response.data.find(user => 
          user.accountId === accountId || user.account_id === accountId
        );
        
        if (foundAssignee) {
          setAssignee(foundAssignee);
        } else {
          // If not found, try from tasks
          const tasksResponse = await jiraService.getUniqueAssigneesFromTasks();
          if (tasksResponse.success) {
            const taskAssignee = tasksResponse.data.find(user => 
              user.account_id === accountId
            );
            if (taskAssignee) {
              setAssignee(taskAssignee);
            }
          }
        }
      }
    } catch (err) {
      setError("Failed to load assignee profile");
      console.error("Error fetching assignee profile:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchAssignedTasks = async () => {
    try {
      setTasksLoading(true);
      setTasksError(null);
      
      console.log("Fetching tasks for assignee profile, account ID:", accountId);
      console.log("Assignee data:", assignee);
      
      // Get tasks assigned to this user from database
      const response = await tasksService.getTasks();
      
      console.log("Tasks API response for profile:", response);
      
      if (response.success) {
        console.log("Total tasks in system:", response.data.tasks.length);
        
        const userTasks = response.data.tasks.filter(task => {
          const match1 = task.assignee_account_id === accountId;
          const match2 = task.assignee_email === assignee?.email;
          const match3 = task.assignee === assignee?.name;
          
          const isMatch = match1 || match2 || match3;
          
          if (isMatch) {
            console.log("Matching task found:", {
              key: task.key,
              summary: task.summary,
              assignee_account_id: task.assignee_account_id,
              accountId: accountId,
              assignee_email: task.assignee_email,
              assignee_name: task.assignee
            });
          }
          
          return isMatch;
        });
        
        console.log("Tasks assigned to this user:", userTasks.length);
        setAssignedTasks(userTasks);
      }
    } catch (err) {
      setTasksError("Failed to load assigned tasks");
      console.error("Error fetching assigned tasks:", err);
    } finally {
      setTasksLoading(false);
    }
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

  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" onClick={() => navigate(-1)}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <h1 className="text-2xl font-bold">Loading Assignee Profile...</h1>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  if (error || !assignee) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" onClick={() => navigate(-1)}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <h1 className="text-2xl font-bold">Assignee Profile</h1>
        </div>
        <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-6 text-center">
          <AlertCircle className="w-12 h-12 text-destructive mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-destructive">Profile Not Found</h2>
          <p className="mt-2 text-destructive/80">
            {error || "Could not find the assignee profile."}
          </p>
          <Button 
            onClick={() => navigate(-1)}
            className="mt-4"
          >
            Go Back
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <Button variant="ghost" onClick={() => navigate(-1)}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Assignees
        </Button>
        <h1 className="text-2xl font-bold">Assignee Profile</h1>
      </div>

      {/* Profile Header Card */}
      <Card>
        <CardHeader>
          <div className="flex items-start space-x-4">
            <Avatar className="w-16 h-16">
              <AvatarImage src={assignee.avatarUrls?.["48x48"] || assignee.avatar} />
              <AvatarFallback className="bg-dashboard-primary text-white text-xl">
                {assignee.name?.charAt(0) || assignee.displayName?.charAt(0) || "U"}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1">
              <CardTitle className="text-2xl">
                {assignee.name || assignee.displayName || "Unknown User"}
              </CardTitle>
              <CardDescription className="mt-1">
                {assignee.email || assignee.emailAddress || "No email provided"}
              </CardDescription>
              <div className="flex flex-wrap gap-2 mt-3">
                <Badge variant={assignee.active ? "default" : "secondary"}>
                  {assignee.active ? "Active" : "Inactive"}
                </Badge>
                {assignee.accountType && (
                  <Badge variant="outline">{assignee.accountType}</Badge>
                )}
                {assignee.task_count && (
                  <Badge className="bg-dashboard-info text-white">
                    {assignee.task_count} Assigned Tasks
                  </Badge>
                )}
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center space-x-2">
              <User className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">Account ID</span>
              <span className="text-sm font-medium">{assignee.accountId || assignee.account_id}</span>
            </div>
            {assignee.timezone && (
              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4 text-muted-foreground" />
                <span className="text-sm text-muted-foreground">Timezone</span>
                <span className="text-sm font-medium">{assignee.timezone}</span>
              </div>
            )}
            <div className="flex items-center space-x-2">
              <Calendar className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">Profile Source</span>
              <span className="text-sm font-medium">Jira Instance</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Assigned Tasks Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Assigned Tasks</h2>
          <Badge variant="outline">
            {assignedTasks.length} tasks
          </Badge>
        </div>

        {tasksLoading ? (
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
            <span className="ml-2">Loading tasks...</span>
          </div>
        ) : tasksError ? (
          <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4">
            <p className="text-destructive">{tasksError}</p>
            <Button 
              variant="outline" 
              size="sm" 
              className="mt-2"
              onClick={fetchAssignedTasks}
            >
              Retry
            </Button>
          </div>
        ) : assignedTasks.length === 0 ? (
          <Card>
            <CardContent className="py-8 text-center">
              <CheckCircle className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium text-muted-foreground">No Assigned Tasks</h3>
              <p className="text-muted-foreground mt-1">
                This assignee doesn't have any tasks assigned in the current project scope.
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {assignedTasks.map((task) => (
              <Card key={task.id || task.jira_id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg line-clamp-2">
                        {task.summary || task.title}
                      </CardTitle>
                      <CardDescription className="mt-1">
                        {task.project_name || task.project_key}
                      </CardDescription>
                    </div>
                    <div className="flex flex-col space-y-1 ml-2">
                      {getTaskStatusBadge(task.status)}
                      {getPriorityBadge(task.priority)}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Issue Type</span>
                      <Badge variant="outline">{task.issue_type || "Task"}</Badge>
                    </div>
                    {task.story_points && (
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Story Points</span>
                        <Badge variant="secondary">{task.story_points}</Badge>
                      </div>
                    )}
                    {task.duedate && (
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Due Date</span>
                        <span className={new Date(task.duedate) < new Date() ? "text-destructive" : "text-foreground"}>
                          {new Date(task.duedate).toLocaleDateString()}
                        </span>
                      </div>
                    )}
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Last Updated</span>
                      <span>{new Date(task.updated).toLocaleDateString()}</span>
                    </div>
                  </div>
                  
                  {task.sprint && (
                    <div className="mt-3 pt-3 border-t">
                      <div className="flex items-center space-x-2">
                        <Hash className="w-4 h-4 text-muted-foreground" />
                        <span className="text-sm text-muted-foreground">Sprint</span>
                        <Badge variant="outline">{task.sprint}</Badge>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}