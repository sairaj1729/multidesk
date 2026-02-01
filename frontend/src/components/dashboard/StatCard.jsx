export function StatCard({ title, value, subtitle, trend, variant = "default" }) {
  const getVariantStyles = () => {
    switch (variant) {
      case "primary":
        return "border-l-4 border-l-dashboard-primary";
      case "success":
        return "border-l-4 border-l-dashboard-success";
      case "warning":
        return "border-l-4 border-l-dashboard-warning";
      case "danger":
        return "border-l-4 border-l-dashboard-danger";
      case "info":
        return "border-l-4 border-l-blue-500";
      default:
        return "border-l-4 border-l-muted-foreground/30";
    }
  };

  const getTrendColor = () => {
    if (trend?.includes("↑")) return "text-dashboard-success";
    if (trend?.includes("↓")) return "text-dashboard-danger";
    return "text-dashboard-info";
  };

  return (
    <div
      className={`bg-card rounded-lg p-6 shadow-lg hover:shadow-xl transition-all duration-200 border border-border ${getVariantStyles()}`}
    >
      <div className="space-y-3">
        <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
          {title}
        </h3>
        <div className="flex items-center space-x-2">
          <span className="text-3xl font-bold text-foreground">{value}</span>
        </div>
        <p className="text-sm text-muted-foreground">{subtitle}</p>
        {trend && (
          <p className={`text-xs font-semibold ${getTrendColor()}`}>{trend}</p>
        )}
      </div>
    </div>
  );
}

export default StatCard;