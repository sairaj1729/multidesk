import React, { useEffect, useState } from "react";
import { StatCard } from "@/components/dashboard/StatCard";
import { EisenhowerMatrix } from "@/components/dashboard/EisenhowerMatrix";
import { AnalyticsCharts } from "@/components/dashboard/AnalyticsCharts";
import { dashboardService } from "@/services/dashboard";
import { jiraService } from "@/services/jira";
import { useToast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";

export default function Dashboard() {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isSyncing, setIsSyncing] = useState(false);
  
  const { toast } = useToast();

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await dashboardService.getDashboardData();
      
      if (response.success) {
        setDashboardData(response.data);
      } else {
        setError(response.error);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const syncJiraData = async () => {
    try {
      setIsSyncing(true);
      const response = await jiraService.syncJiraData();
      
      if (response.success) {
        toast({
          title: "Sync Successful",
          description: "Jira data has been updated successfully.",
        });
        // Refresh dashboard data after sync
        fetchDashboardData();
      } else {
        toast({
          title: "Sync Failed",
          description: response.error || "Failed to sync Jira data.",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Sync Failed",
        description: "An unexpected error occurred during sync.",
        variant: "destructive",
      });
    } finally {
      setIsSyncing(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="p-8 bg-background min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 bg-background min-h-screen">
        <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-6 text-center">
          <h2 className="text-xl font-semibold text-destructive">Error Loading Dashboard</h2>
          <p className="mt-2 text-destructive/80">{error}</p>
          <div className="mt-4 flex justify-center gap-2">
            <button 
              onClick={fetchDashboardData}
              className="px-4 py-2 bg-destructive text-destructive-foreground rounded-md hover:opacity-90"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  const stats = dashboardData?.stats || {};
  const eisenhower = dashboardData?.eisenhower || {};
  const analytics = dashboardData?.analytics || {};

  return (
    <div className="p-8 space-y-8 bg-background min-h-screen">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Jira Dashboard Overview</h1>
          <p className="text-muted-foreground">Unified insights across your Jira projects.</p>
        </div>
        <Button 
          onClick={syncJiraData} 
          disabled={isSyncing}
          variant="outline"
          className="flex items-center gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${isSyncing ? 'animate-spin' : ''}`} />
          {isSyncing ? 'Syncing...' : 'Sync Data'}
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Jira Tasks"
          value={stats.total_tasks || 0}
          subtitle="All active tasks"
          trend={stats.total_tasks_trend ? `↑ +${stats.total_tasks_trend}%` : ""}
          variant="primary"
        />
        <StatCard
          title="Tasks In Progress"
          value={stats.in_progress_tasks || 0}
          subtitle="Activity being worked on"
          trend={stats.in_progress_tasks_trend ? `↑ +${stats.in_progress_tasks_trend}%` : ""}
          variant="warning"
        />
        <StatCard
          title="Completed Tasks"
          value={stats.completed_tasks || 0}
          subtitle="This month"
          trend={stats.completed_tasks_trend ? `↑ +${stats.completed_tasks_trend}%` : ""}
          variant="success"
        />
        <StatCard
          title="Overdue Tasks"
          value={stats.overdue_tasks || 0}
          subtitle="Requiring immediate attention"
          trend={stats.overdue_tasks_trend ? `↑ +${stats.overdue_tasks_trend}%` : ""}
          variant="danger"
        />
      </div>

      {/* Eisenhower Matrix */}
      <EisenhowerMatrix data={eisenhower} />

      {/* Analytics Charts */}
      <AnalyticsCharts data={analytics} />
    </div>
  );
}