import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertTriangle, Calendar, User, FileText, PlayCircle } from 'lucide-react';
import { riskService } from '@/services/risks';


const riskStyles = {
  CRITICAL: {
    border: "border-red-600",
    badge: "bg-red-600 text-white",
    glow: "hover:shadow-red-500/20",
  },
  HIGH: {
    border: "border-amber-500",
    badge: "bg-amber-500 text-white",
    glow: "hover:shadow-amber-500/20",
  },
  MEDIUM: {
    border: "border-blue-500",
    badge: "bg-blue-500 text-white",
    glow: "hover:shadow-blue-500/20",
  },
  LOW: {
    border: "border-emerald-500",
    badge: "bg-emerald-500 text-white",
    glow: "hover:shadow-emerald-500/20",
  },
};

const Info = ({ label, value, icon: Icon }) => (
  <div className="flex items-center gap-2">
    <Icon className="w-4 h-4 text-muted-foreground" />
    <div>
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="font-medium">{value}</p>
    </div>
  </div>
);



const Risks = () => {
  const [risks, setRisks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchRisks();
  }, []);

  const fetchRisks = async () => {
    try {
      setLoading(true);
      console.log('Fetching risks...');
      const data = await riskService.getAllRisks();
      console.log('Received risks data:', data);
      console.log('Number of risks:', data.length);
      setRisks(data);
    } catch (err) {
      setError('Failed to fetch risks');
      console.error('Error fetching risks:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  const getRiskLevelColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="flex-1 space-y-4 p-8 pt-6">
        <div className="flex items-center justify-between">
          <h2 className="text-3xl font-bold tracking-tight">Risk Alerts</h2>
        </div>
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-1 space-y-4 p-8 pt-6">
        <div className="flex items-center justify-between">
          <h2 className="text-3xl font-bold tracking-tight">Risk Alerts</h2>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      </div>
    );
  }

  const refreshRisks = async () => {
    try {
      setLoading(true);
      console.log('Refreshing risks...');
      const data = await riskService.getAllRisks();
      console.log('Received refreshed risks data:', data);
      console.log('Number of refreshed risks:', data.length);
      setRisks(data);
    } catch (err) {
      setError('Failed to fetch risks');
      console.error('Error fetching risks:', err);
    } finally {
      setLoading(false);
    }
  };

  const runRiskAnalysis = async () => {
    try {
      setLoading(true);
      console.log('Running risk analysis...');
      const result = await riskService.checkRisks();
      console.log('Risk analysis result:', result);
      // Refresh the risks after analysis
      await refreshRisks();
    } catch (err) {
      setError('Failed to run risk analysis');
      console.error('Error running risk analysis:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold tracking-tight">Risk Alerts</h2>
        <div className="flex items-center gap-2">
          <button
            onClick={runRiskAnalysis}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
          >
            <AlertTriangle className="w-4 h-4" />
            {loading ? 'Analyzing...' : 'Run Risk Analysis'}
          </button>
          <Badge variant="secondary" className="text-lg py-1 px-3">
            <AlertTriangle className="mr-2 h-4 w-4" />
            {risks.length} Active Risks
          </Badge>
        </div>
      </div>

      <p className="text-muted-foreground">
        These tasks pose potential risks based on due dates, priorities, status, and employee leaves. Review and take appropriate action.
      </p>

      {risks.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <AlertTriangle className="h-12 w-12 text-green-500 mb-4" />
            <h3 className="text-xl font-semibold mb-2">No Active Risks</h3>
            <p className="text-muted-foreground text-center">
              All tasks are on track. No conflicts with employee leaves or deadline risks detected.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-1 lg:grid-cols-1">
          {risks.map((risk) => (
            <Card
  key={risk._id}
  className={`border-l-4 ${riskStyles[risk.risk_level]?.border}
    bg-card shadow-sm hover:shadow-lg ${riskStyles[risk.risk_level]?.glow}
    transition-all duration-200`}
>
  {/* HEADER */}
  <CardHeader className="pb-3">
    <div className="flex items-start justify-between gap-4">
      <CardTitle className="text-base font-semibold flex items-center gap-2">
        <FileText className="w-4 h-4 text-muted-foreground" />
        <span className="font-mono text-sm text-muted-foreground">
          {risk.task_key}
        </span>
        <span className="truncate break-words whitespace-normal">{risk.task_title}</span>
      </CardTitle>

      <Badge className={riskStyles[risk.risk_level]?.badge}>
        {risk.risk_level}
      </Badge>
    </div>
  </CardHeader>

  {/* BODY */}
  <CardContent className="space-y-4">
    <div className="grid grid-cols-1 md:grid-cols-5 gap-4 text-sm">
      <Info label="Assignee" value={risk.assignee || "Unassigned"} icon={User} />
      <Info label="Start Date" value={formatDate(risk.start_date)} icon={PlayCircle} />
      <Info label="Due Date" value={formatDate(risk.due_date)} icon={Calendar} />
      <Info label="Leave Start" value={formatDate(risk.leave_start)} icon={Calendar} />
      <Info label="Leave End" value={formatDate(risk.leave_end)} icon={Calendar} />
    </div>

    {/* REASONS */}
    {risk.reasons?.length > 0 && (
      <div className="pt-3 border-t">
        <p className="text-xs font-medium text-muted-foreground mb-2">
          Risk Factors
        </p>
        <div className="flex flex-wrap gap-2">
          {risk.reasons.map((reason, idx) => (
            <span
              key={idx}
              className="px-2 py-1 rounded-md text-xs
                bg-muted/60 text-muted-foreground
                border border-border"
            >
              {reason}
            </span>
          ))}
        </div>
      </div>
    )}
  </CardContent>
</Card>

          ))}
        </div>
      )}
    </div>
  );
};

export default Risks;