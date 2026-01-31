import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Plus, Search, MoreVertical, Mail, Briefcase, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { jiraService } from "@/services/jira";

const getStatusBadge = (status) => {
  const isActive = status === true || status === "Active";
  return isActive ? (
    <Badge className="bg-dashboard-success text-white">Active</Badge>
  ) : (
    <Badge variant="outline">Inactive</Badge>
  );
};

const getRoleBadge = (role) => {
  const colors = {
    "admin": "bg-dashboard-danger text-white",
    "project_manager": "bg-dashboard-primary text-white",
    "developer": "bg-dashboard-info text-white",
    "user": "bg-dashboard-accent text-white",
  };

  // Convert role to display name
  const roleDisplayNames = {
    "admin": "Administrator",
    "project_manager": "Project Manager",
    "developer": "Developer",
    "user": "User",
  };

  const displayName = roleDisplayNames[role] || role;
  const colorClass = colors[role] || "bg-muted text-muted-foreground";

  return (
    <Badge className={colorClass}>{displayName}</Badge>
  );
};

const getAssigneeTypeBadge = (assigneeType) => {
  const colors = {
    "assignable": "bg-dashboard-primary text-white",
    "from_tasks": "bg-dashboard-info text-white",
    "jira_user": "bg-dashboard-success text-white",
  };

  const typeDisplayNames = {
    "assignable": "Assignable",
    "from_tasks": "From Tasks",
    "jira_user": "Jira User",
  };

  const displayName = typeDisplayNames[assigneeType] || assigneeType;
  const colorClass = colors[assigneeType] || "bg-muted text-muted-foreground";

  return (
    <Badge className={colorClass}>{displayName}</Badge>
  );
};

export default function Users() {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState("");
  const [assignees, setAssignees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [totalAssignees, setTotalAssignees] = useState(0);
  const [sourceType, setSourceType] = useState("from_tasks"); // from_tasks, assignable, jira_users

  useEffect(() => {
    fetchAssignees();
  }, [searchTerm, sourceType]);

  const fetchAssignees = async () => {
    try {
      setLoading(true);
      setError(null);
      
      let response;
      
      switch (sourceType) {
        case "from_tasks":
          response = await jiraService.getUniqueAssigneesFromTasks();
          break;
        case "assignable":
          response = await jiraService.getAssignableUsers();
          break;
        case "jira_users":
          response = await jiraService.getJiraUsers();
          break;
        default:
          response = await jiraService.getUniqueAssigneesFromTasks();
      }
      
      if (response.success) {
        // Filter by search term if provided
        let filteredAssignees = response.data;
        if (searchTerm) {
          filteredAssignees = response.data.filter(assignee => 
            assignee.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            assignee.email?.toLowerCase().includes(searchTerm.toLowerCase())
          );
        }
        
        setAssignees(filteredAssignees);
        setTotalAssignees(filteredAssignees.length);
      } else {
        setError(response.error);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleViewProfile = (assignee) => {
    const accountId = assignee.account_id || assignee.accountId;
    console.log("Navigating to profile with assignee:", assignee);
    console.log("Using account ID:", accountId);
    if (accountId) {
      navigate(`/assignee/${accountId}`);
    }
  };

  const handleViewTasks = (assignee) => {
    const accountId = assignee.account_id || assignee.accountId;
    console.log("Navigating to tasks with assignee:", assignee);
    console.log("Using account ID:", accountId);
    if (accountId) {
      navigate(`/assignee/${accountId}/tasks`);
    }
  };

  if (loading && assignees.length === 0) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold text-foreground">Jira Assignees</h1>
            <p className="text-muted-foreground">View team members from your Jira instance</p>
          </div>
          <div className="flex space-x-2">
            <select 
              value={sourceType}
              onChange={(e) => setSourceType(e.target.value)}
              className="px-3 py-2 border rounded-md bg-background text-foreground"
            >
              <option value="from_tasks">From Tasks</option>
              <option value="assignable">Assignable Users</option>
              <option value="jira_users">All Jira Users</option>
            </select>
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
            <h1 className="text-2xl font-bold text-foreground">Jira Assignees</h1>
            <p className="text-muted-foreground">View team members from your Jira instance</p>
          </div>
          <div className="flex space-x-2">
            <select 
              value={sourceType}
              onChange={(e) => setSourceType(e.target.value)}
              className="px-3 py-2 border rounded-md bg-background text-foreground"
            >
              <option value="from_tasks">From Tasks</option>
              <option value="assignable">Assignable Users</option>
              <option value="jira_users">All Jira Users</option>
            </select>
          </div>
        </div>
        <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-6 text-center">
          <h2 className="text-xl font-semibold text-destructive">Error Loading Assignees</h2>
          <p className="mt-2 text-destructive/80">{error}</p>
          <button 
            onClick={fetchAssignees}
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
          <h1 className="text-2xl font-bold text-foreground">Jira Assignees</h1>
          <p className="text-muted-foreground">View team members from your Jira instance</p>
        </div>
        <div className="flex space-x-2">
          <select 
            value={sourceType}
            onChange={(e) => setSourceType(e.target.value)}
            className="px-3 py-2 border rounded-md bg-background text-foreground"
          >
            <option value="from_tasks">From Tasks</option>
            <option value="assignable">Assignable Users</option>
            <option value="jira_users">All Jira Users</option>
          </select>
        </div>
      </div>

      {/* Search */}
      <div className="flex items-center space-x-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <Input
            placeholder="Search assignees..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <div className="text-sm text-muted-foreground">
          {assignees.length} assignees
        </div>
        {getAssigneeTypeBadge(sourceType)}
      </div>

      {/* Assignees Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {assignees.map((assignee, index) => (
          <div
            key={assignee.account_id || assignee.email || index}
            className="bg-card rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <Avatar className="w-12 h-12">
                  <AvatarImage src={assignee.avatarUrls?.["48x48"] || assignee.avatar} />
                  <AvatarFallback className="bg-dashboard-primary text-white">
                    {assignee.name?.charAt(0) || assignee.displayName?.charAt(0) || "U"}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <h3 className="font-semibold text-card-foreground">
                    {assignee.name || assignee.displayName || "Unknown User"}
                  </h3>
                  <div className="mt-1">
                    {assignee.task_count ? (
                      <Badge variant="outline">{assignee.task_count} tasks</Badge>
                    ) : (
                      <Badge variant="outline">Jira User</Badge>
                    )}
                  </div>
                </div>
              </div>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="sm">
                    <MoreVertical className="w-4 h-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={() => handleViewProfile(assignee)}>
                    View Profile
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => handleViewTasks(assignee)}>
                    View Assigned Tasks
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    View Workload
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>

            <div className="space-y-3">
              {getAssigneeTypeBadge(sourceType)}

              <div className="space-y-2 text-sm">
                <div className="flex items-center space-x-2 text-muted-foreground">
                  <Mail className="w-4 h-4" />
                  <span>{assignee.email || assignee.emailAddress || "No email"}</span>
                </div>
                {assignee.accountType && (
                  <div className="flex items-center space-x-2 text-muted-foreground">
                    <User className="w-4 h-4" />
                    <span>{assignee.accountType}</span>
                  </div>
                )}
                {assignee.active !== undefined && (
                  <div className="flex items-center space-x-2 text-muted-foreground">
                    <Briefcase className="w-4 h-4" />
                    <span>{assignee.active ? "Active" : "Inactive"}</span>
                  </div>
                )}
              </div>

              {assignee.accountId && (
                <div className="pt-2 border-t text-xs text-muted-foreground">
                  Account ID: {assignee.accountId}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {assignees.length === 0 && !loading && (
        <div className="text-center py-12">
          <div className="text-muted-foreground">No assignees found matching your search.</div>
          <div className="text-sm text-muted-foreground mt-2">
            Try changing the source type or search term
          </div>
        </div>
      )}
    </div>
  );
}