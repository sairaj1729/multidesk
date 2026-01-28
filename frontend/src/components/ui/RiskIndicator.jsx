import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { AlertTriangle } from 'lucide-react';
import { riskService } from '@/services/risks';
import { useNavigate } from 'react-router-dom';

const RiskIndicator = () => {
  const [riskCount, setRiskCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchRiskCount();
    // Set up polling to check for new risks
    const interval = setInterval(fetchRiskCount, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchRiskCount = async () => {
    try {
      const risks = await riskService.getAllRisks();
      setRiskCount(risks.length);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch risk count:', error);
      setLoading(false);
    }
  };

  const handleClick = () => {
    navigate('/risks');
  };

  // Don't show the indicator if there are no risks or still loading
  if (loading || riskCount === 0) {
    return null;
  }

  return (
    <Button
      onClick={handleClick}
      className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-lg bg-red-600 hover:bg-red-700 text-white z-50 animate-pulse"
      aria-label={`View ${riskCount} risk alerts`}
    >
      <div className="relative">
        <AlertTriangle className="h-6 w-6" />
        <span className="absolute -top-2 -right-2 bg-white text-red-600 text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center">
          {riskCount}
        </span>
      </div>
    </Button>
  );
};

export default RiskIndicator;