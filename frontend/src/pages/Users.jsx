import { useState, useEffect } from "react";
import { Plus, Search, MoreVertical, Mail, Phone } from "lucide-react";
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
import { usersService } from "@/services/users";

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

export default function Users() {
  const [searchTerm, setSearchTerm] = useState("");
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [totalUsers, setTotalUsers] = useState(0);

  useEffect(() => {
    fetchUsers();
  }, [searchTerm]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const filters = {
        search: searchTerm || undefined
      };
      
      const response = await usersService.getUsers(filters, 1, 100);
      
      if (response.success) {
        setUsers(response.data.users);
        setTotalUsers(response.data.total);
      } else {
        setError(response.error);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading && users.length === 0) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold text-foreground">Users</h1>
            <p className="text-muted-foreground">Manage team members and their permissions</p>
          </div>
          <Button className="bg-dashboard-primary hover:bg-dashboard-primary/90">
            <Plus className="w-4 h-4 mr-2" />
            Add User
          </Button>
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
            <h1 className="text-2xl font-bold text-foreground">Users</h1>
            <p className="text-muted-foreground">Manage team members and their permissions</p>
          </div>
          <Button className="bg-dashboard-primary hover:bg-dashboard-primary/90">
            <Plus className="w-4 h-4 mr-2" />
            Add User
          </Button>
        </div>
        <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-6 text-center">
          <h2 className="text-xl font-semibold text-destructive">Error Loading Users</h2>
          <p className="mt-2 text-destructive/80">{error}</p>
          <button 
            onClick={fetchUsers}
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
          <h1 className="text-2xl font-bold text-foreground">Users</h1>
          <p className="text-muted-foreground">Manage team members and their permissions</p>
        </div>
        <Button className="bg-dashboard-primary hover:bg-dashboard-primary/90">
          <Plus className="w-4 h-4 mr-2" />
          Add User
        </Button>
      </div>

      {/* Search */}
      <div className="flex items-center space-x-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <Input
            placeholder="Search users..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <div className="text-sm text-muted-foreground">
          {users.length} of {totalUsers} users
        </div>
      </div>

      {/* Users Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {users.map((user) => (
          <div
            key={user.id}
            className="bg-card rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <Avatar className="w-12 h-12">
                  <AvatarImage src={user.avatar} />
                  <AvatarFallback className="bg-dashboard-primary text-white">
                    {user.first_name?.charAt(0)}{user.last_name?.charAt(0)}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <h3 className="font-semibold text-card-foreground">
                    {user.first_name} {user.last_name}
                  </h3>
                  <div className="mt-1">{getStatusBadge(user.is_verified)}</div>
                </div>
              </div>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="sm">
                    <MoreVertical className="w-4 h-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem>Edit User</DropdownMenuItem>
                  <DropdownMenuItem>View Details</DropdownMenuItem>
                  <DropdownMenuItem>Reset Password</DropdownMenuItem>
                  <DropdownMenuItem className="text-dashboard-danger">Remove User</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>

            <div className="space-y-3">
              {getRoleBadge(user.role)}

              <div className="space-y-2 text-sm">
                <div className="flex items-center space-x-2 text-muted-foreground">
                  <Mail className="w-4 h-4" />
                  <span>{user.email}</span>
                </div>
                {user.phone && (
                  <div className="flex items-center space-x-2 text-muted-foreground">
                    <Phone className="w-4 h-4" />
                    <span>{user.phone}</span>
                  </div>
                )}
              </div>

              <div className="pt-2 border-t text-xs text-muted-foreground">
                Joined {new Date(user.created_at).toLocaleDateString()}
              </div>
            </div>
          </div>
        ))}
      </div>

      {users.length === 0 && !loading && (
        <div className="text-center py-12">
          <div className="text-muted-foreground">No users found matching your search.</div>
        </div>
      )}
    </div>
  );
}