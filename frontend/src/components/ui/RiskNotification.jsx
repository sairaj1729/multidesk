import React, { useState, useEffect } from 'react';
import { AlertTriangle, X } from 'lucide-react';
import { riskService } from '@/services/risks';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';

const RiskNotification = () => {
  const [showNotification, setShowNotification] = useState(false);
  const [riskCount, setRiskCount] = useState(0);
  const [previousRiskCount, setPreviousRiskCount] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    checkForNewRisks();
    // Set up polling to check for new risks
    const interval = setInterval(checkForNewRisks, 60000); // Check every minute
    return () => clearInterval(interval);
  }, []);

  const checkForNewRisks = async () => {
    try {
      const risks = await riskService.getAllRisks();
      const currentRiskCount = risks.length;
      
      setRiskCount(currentRiskCount);
      
      // Check if new risks appeared
      if (currentRiskCount > previousRiskCount && previousRiskCount !== 0) {
        setShowNotification(true);
      }
      
      setPreviousRiskCount(currentRiskCount);
    } catch (error) {
      console.error('Failed to check for new risks:', error);
    }
  };

  const handleViewRisks = () => {
    setShowNotification(false);
    navigate('/risks');
  };

  const handleClose = () => {
    setShowNotification(false);
  };

  if (!showNotification || riskCount === 0) {
    return null;
  }

  return (
    <div className="fixed top-4 right-4 z-50 animate-in slide-in-from-right duration-300">
      <div className="bg-red-50 border border-red-200 rounded-lg shadow-lg p-4 max-w-md">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <AlertTriangle className="h-5 w-5 text-red-500" />
          </div>
          <div className="ml-3 flex-1">
            <p className="text-sm font-medium text-red-800">
              ⚠️ New Risk Alert
            </p>
            <p className="mt-1 text-sm text-red-700">
              {riskCount} task{riskCount !== 1 ? 's' : ''} may be delayed due to upcoming leaves
            </p>
            <div className="mt-3 flex space-x-2">
              <Button
                size="sm"
                variant="outline"
                className="h-8 px-2 text-xs border-red-300 text-red-700 hover:bg-red-100"
                onClick={handleViewRisks}
              >
                View Details
              </Button>
            </div>
          </div>
          <div className="ml-4 flex-shrink-0">
            <button
              className="inline-flex text-red-500 hover:text-red-700"
              onClick={handleClose}
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RiskNotification;