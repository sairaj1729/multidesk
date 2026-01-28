import { AlertTriangle, Clock, Calendar, Archive } from "lucide-react";
import { useState } from "react";

const quadrants = [
  {
    title: "Urgent & Important",
    subtitle: "Do these immediately",
    icon: AlertTriangle,
    variant: "danger",
    key: "urgent_important"
  },
  {
    title: "Urgent & Not Important",
    subtitle: "Delegate these tasks",
    icon: Clock,
    variant: "warning",
    key: "urgent_not_important"
  },
  {
    title: "Not Urgent & Important",
    subtitle: "Schedule for later",
    icon: Calendar,
    variant: "primary",
    key: "not_urgent_important"
  },
  {
    title: "Not Urgent & Not Important",
    subtitle: "Eliminate or postpone",
    icon: Archive,
    variant: "muted",
    key: "not_urgent_not_important"
  },
];

export function EisenhowerMatrix({ data }) {
  const [hoveredQuadrant, setHoveredQuadrant] = useState(null);

  const getQuadrantStyles = (variant) => {
    switch (variant) {
      case "danger":
        return "bg-dashboard-danger/10 border border-dashboard-danger/20 hover:bg-dashboard-danger/20 transition-all duration-200";
      case "warning":
        return "bg-dashboard-warning/10 border border-dashboard-warning/20 hover:bg-dashboard-warning/20 transition-all duration-200";
      case "primary":
        return "bg-dashboard-primary/10 border border-dashboard-primary/20 hover:bg-dashboard-primary/20 transition-all duration-200";
      case "muted":
        return "bg-muted/50 border border-muted-foreground/20 hover:bg-muted transition-all duration-200";
      default:
        return "bg-card border border-border";
    }
  };

  const getIconAndTextStyles = (variant) => {
    switch (variant) {
      case "danger":
        return "text-dashboard-danger";
      case "warning":
        return "text-dashboard-warning";
      case "primary":
        return "text-dashboard-primary";
      case "muted":
        return "text-muted-foreground";
      default:
        return "text-card-foreground";
    }
  };

  const getPriorityStyles = (priority) => {
    switch (priority) {
      case 'Highest':
      case 'High':
        return "bg-dashboard-danger/15 text-dashboard-danger border border-dashboard-danger/30";
      case 'Medium':
        return "bg-dashboard-warning/15 text-dashboard-warning border border-dashboard-warning/30";
      case 'Low':
      case 'Lowest':
        return "bg-dashboard-primary/15 text-dashboard-primary border border-dashboard-primary/30";
      default:
        return "bg-muted text-muted-foreground border border-border";
    }
  };

  // Use real data if provided, otherwise use defaults
  const quadrantValues = data ? [
    data.urgent_important || 0,
    data.urgent_not_important || 0,
    data.not_urgent_important || 0,
    data.not_urgent_not_important || 0
  ] : [12, 25, 40, 110];

  // Get task data for each quadrant
  const quadrantTasks = data ? [
    data.urgent_important_tasks || [],
    data.urgent_not_important_tasks || [],
    data.not_urgent_important_tasks || [],
    data.not_urgent_not_important_tasks || []
  ] : [[], [], [], []];

  return (
    <div className="bg-card rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-border relative">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-foreground">
          Jira Task Prioritization
        </h2>
        <p className="text-sm text-muted-foreground mt-1">
          Organize tasks by urgency and importance
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {quadrants.map((quadrant, index) => {
          const Icon = quadrant.icon;
          const iconTextStyles = getIconAndTextStyles(quadrant.variant);
          const value = quadrantValues[index];
          const tasks = quadrantTasks[index];
          
          return (
            <div
              key={index}
              className={`p-5 rounded-xl cursor-pointer ${getQuadrantStyles(
                quadrant.variant
              )} relative group transition-all duration-200`}
              onMouseEnter={() => setHoveredQuadrant(index)}
              onMouseLeave={() => setHoveredQuadrant(null)}
            >
              <div className="flex items-center justify-between mb-3">
                <Icon className={`w-5 h-5 ${iconTextStyles}`} />
                <span className={`text-3xl font-bold ${iconTextStyles}`}>
                  {value}
                </span>
              </div>
              <h3 className={`font-semibold text-sm ${iconTextStyles}`}>
                {quadrant.title}
              </h3>
              <p className={`text-xs opacity-80 mt-1 ${iconTextStyles}`}>
                {quadrant.subtitle}
              </p>

              {/* Enhanced tooltip with task details */}
              {hoveredQuadrant === index && tasks.length > 0 && (
                <div className="absolute z-20 left-1/2 transform -translate-x-1/2 bottom-full mb-3 w-80 bg-popover border border-border rounded-xl shadow-xl p-4 transition-all duration-200 ease-out">
                  <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-1 w-3 h-3 bg-popover border-r border-b border-border rotate-45"></div>
                  <div className="relative">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className={`font-bold text-sm ${iconTextStyles}`}>
                        {quadrant.title}
                      </h4>
                      <span className="text-xs text-muted-foreground">
                          Showing top {Math.min(5, tasks.length)} of {tasks.length}
                      </span>

                    </div>
                    <div className="max-h-72 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-muted scrollbar-track-transparent scrollbar-thumb-rounded-full">
                        {tasks
                          .slice() // clone array
                          .sort((a, b) => {
                            // 1️⃣ Earlier due date first
                            if (a.duedate && b.duedate) {
                              return new Date(a.duedate) - new Date(b.duedate);
                            }
                            if (a.duedate) return -1;
                            if (b.duedate) return 1;

                            // 2️⃣ Higher priority next
                            const priorityOrder = {
                              Highest: 4,
                              High: 3,
                              Medium: 2,
                              Low: 1,
                              Lowest: 0
                            };

                            return (priorityOrder[b.priority] || 0) - (priorityOrder[a.priority] || 0);
                          })
                          .slice(0, 5)
                          .map((task, taskIndex) => (
                        <div key={taskIndex} className="mb-3 last:mb-0 pb-3 border-b border-border/50 last:border-b-0">
                          <div className="flex justify-between items-start gap-2">
                            <div className="flex-1 min-w-0">
                              <p className="font-medium text-sm text-foreground truncate">
                                {task.summary}
                              </p>
                              <div className="flex items-center gap-2 mt-1">
                                <span className="text-xs text-muted-foreground bg-muted px-1.5 py-0.5 rounded">
                                  {task.key}
                                </span>
                                <span className="text-xs text-muted-foreground truncate">
                                  {task.project_name}
                                </span>
                              </div>
                            </div>
                            <span className={`text-xs px-2 py-1 rounded-full whitespace-nowrap ${getPriorityStyles(task.priority)}`}>
                              {task.priority}
                            </span>
                          </div>
                          <div className="flex justify-between items-center mt-2">
                            <span className="text-xs text-muted-foreground bg-muted/50 px-1.5 py-0.5 rounded">
                              {task.status}
                            </span>
                            {task.duedate && (
                              <span className="text-xs text-muted-foreground">
                                Due: {new Date(task.duedate).toLocaleDateString()}
                              </span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                        {tasks.length > 5 && (
                  <div className="flex justify-between items-center mt-2 pt-2 border-t border-border/50">
                    <span className="text-xs text-muted-foreground">
                      +{tasks.length - 5} more tasks
                    </span>

                    <button
                      className="text-xs font-medium text-dashboard-primary hover:underline"
                      onClick={(e) => {
                        e.stopPropagation();
                        window.location.href = `/dashboard/eisenhower/view-all?quadrant=${quadrant.key}`;
                      }}
                    >
                      View all →
                    </button>
                  </div>
                )}

                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default EisenhowerMatrix;