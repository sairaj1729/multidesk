import { NavLink, useLocation } from "react-router-dom";
import { 
  LayoutDashboard, 
  CheckSquare, 
  FileText, 
  Users, 
  Settings, 
  HelpCircle,
  Plug,
  Database,
  AlertTriangle
} from "lucide-react";
import { cn } from "@/lib/utils";

const sidebarItems = [
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    title: "Tasks",
    href: "/tasks",
    icon: CheckSquare,
  },
  {
    title: "Data Management",
    href: "/data-management",
    icon: Database,
  },
  {
    title: "Risk Alerts",
    href: "/risks",
    icon: AlertTriangle,
  },
  {
    title: "Reports",
    href: "/reports",
    icon: FileText,
  },
  {
    title: "Users",
    href: "/users",
    icon: Users,
  },
  {
    title: "Integrations",
    href: "/integrations",
    icon: Plug,
  },
  {
    title: "Settings",
    href: "/settings",
    icon: Settings,
  },
  {
    title: "Help & Support",
    href: "/help",
    icon: HelpCircle,
  },
];

export default function Sidebar() {
  const location = useLocation();

  return (
    <div className="flex h-screen w-64 flex-col bg-sidebar border-r border-sidebar-border shadow-lg">
      {/* Logo/Brand */}
      <div className="flex h-16 items-center px-6 border-b border-sidebar-border bg-card">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-dashboard-primary rounded-lg flex items-center justify-center shadow-md">
            <LayoutDashboard className="w-4 h-4 text-dashboard-primary-foreground" />
          </div>
          <span className="text-xl font-bold text-sidebar-foreground">Multi Desk</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 bg-sidebar">
        {sidebarItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.href;

          return (
            <NavLink
              key={item.href}
              to={item.href}
              className={cn(
                "flex items-center space-x-3 px-4 py-3 rounded-lg text-sm font-semibold transition-all duration-200",
                isActive
                  ? "bg-dashboard-primary text-dashboard-primary-foreground shadow-md"
                  : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
              )}
            >
              <Icon className="w-5 h-5" />
              <span>{item.title}</span>
            </NavLink>
          );
        })}
      </nav>
    </div>
  );
}