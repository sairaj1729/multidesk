import { Search, Bell, Settings, User, LogOut } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { authService } from "@/services/auth";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";

export default function Header() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const user = authService.getUser();

  const handleLogout = () => {
    authService.logout();
    toast({
      title: "Logged Out",
      description: "You have been successfully logged out.",
    });
    navigate("/");
  };

  const getInitials = () => {
    if (user?.first_name && user?.last_name) {
      return `${user.first_name.charAt(0)}${user.last_name.charAt(0)}`.toUpperCase();
    }
    return user?.email?.charAt(0).toUpperCase() || "U";
  };

  const getDisplayName = () => {
    if (user?.first_name && user?.last_name) {
      return `${user.first_name} ${user.last_name}`;
    }
    return user?.email || "User";
  };

  return (
    <header className="h-16 bg-card border-b border-border px-6 flex items-center justify-between shadow-sm">
      {/* Left side - could add breadcrumbs or other navigation here */}
      <div className="flex items-center space-x-4">
        {/* Placeholder for breadcrumbs */}
      </div>

      {/* Right side - Search, Notifications, Settings, Profile */}
      <div className="flex items-center space-x-4">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <Input
            placeholder="Search tasks, issues..."
            className="pl-10 w-64 bg-muted/50 border-border focus:bg-card focus:border-ring"
          />
        </div>

        {/* Notifications */}
        <Button variant="ghost" size="sm" className="relative">
          <Bell className="w-5 h-5 text-muted-foreground" />
          {/* Show notification badge if user is not verified */}
          {!user?.is_verified && (
            <span className="absolute -top-1 -right-1 h-3 w-3 bg-dashboard-danger rounded-full text-xs"></span>
          )}
        </Button>

        {/* Settings */}
        <Button variant="ghost" size="sm" onClick={() => navigate("/settings")}>
          <Settings className="w-5 h-5 text-muted-foreground" />
        </Button>

        {/* Profile Dropdown */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm" className="flex items-center space-x-2">
              <Avatar className="w-8 h-8">
                <AvatarImage src="" />
                <AvatarFallback className="bg-dashboard-primary text-dashboard-primary-foreground text-sm font-semibold">
                  {getInitials()}
                </AvatarFallback>
              </Avatar>
              <span className="hidden md:block text-sm font-medium">{getDisplayName()}</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            <DropdownMenuItem onClick={() => navigate("/settings")}>
              <User className="w-4 h-4 mr-2" />
              Profile
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => navigate("/settings")}>
              <Settings className="w-4 h-4 mr-2" />
              Settings
            </DropdownMenuItem>
            {!user?.is_verified && (
              <DropdownMenuItem onClick={() => navigate("/verify-email", { state: { email: user?.email } })}>
                <Bell className="w-4 h-4 mr-2" />
                Verify Email
              </DropdownMenuItem>
            )}
            <DropdownMenuItem 
              onClick={handleLogout}
              className="text-dashboard-danger focus:text-dashboard-danger-foreground focus:bg-dashboard-danger"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Sign Out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
