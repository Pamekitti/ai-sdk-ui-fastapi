"use client";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { format } from "date-fns";
import { WrenchIcon } from "lucide-react";

interface MaintenanceArgs {
  device_id: string | string[];
  maintenance_flag: boolean;
  reporter_name: string;
  technician_name: string;
  time: string;
  reason?: string;
}

interface MaintenanceRequestCardProps {
  result: {
    success: boolean;
    message: string;
    data: MaintenanceArgs;
  };
}

type MaintenanceStatus = 'pending' | 'submitting' | 'success' | 'error' | 'cancelled';

export function MaintenanceRequestCard({
  result
}: MaintenanceRequestCardProps) {
  // If data is undefined or doesn't have required properties, don't render
  if (!result?.data?.device_id || result?.data?.maintenance_flag === undefined) {
    return null;
  }

  const { device_id, maintenance_flag, reporter_name, technician_name, time, reason = '' } = result.data;
  const deviceIds = Array.isArray(device_id) ? device_id : [device_id];
  const [status, setStatus] = useState<MaintenanceStatus>('pending');
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const formatDateTime = (timeStr: string) => {
    try {
      const date = new Date(timeStr);
      // Check if date is valid
      if (isNaN(date.getTime())) {
        return timeStr;
      }
      return format(date, "MMM d, yyyy 'at' h:mm a");
    } catch {
      return timeStr;
    }
  };

  const handleConfirm = async () => {
    try {
      setStatus('submitting');
      setError(null);
      setMessage(null);

      const response = await fetch('/api/chiller_plant/device_maintenance_flag', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          device_id,
          maintenance_flag,
          reporter_name,
          technician_name,
          time,
          reason
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Failed to update maintenance flag');
      }

      setStatus('success');
      setMessage(data.message || 'Successfully updated maintenance flag');

      window.postMessage({ 
        type: 'CONFIRM_MAINTENANCE', 
        deviceId: device_id,
        success: true 
      }, '*');

    } catch (err) {
      setStatus('error');
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      console.error('Failed to update maintenance flag:', err);
    }
  };

  const handleCancel = () => {
    setStatus('cancelled');
    setMessage('Maintenance request cancelled');
    setError(null);
    
    window.postMessage({ 
      type: 'CANCEL_MAINTENANCE', 
      deviceId: device_id,
      success: true 
    }, '*');
  };

  const getStatusBadge = () => {
    switch (status) {
      case 'submitting':
        return (
          <div className="px-2 py-0.5 bg-blue-950/50 rounded text-xs text-blue-400 font-medium border border-blue-900/50 animate-pulse">
            Processing...
          </div>
        );
      case 'success':
        return (
          <div className="px-2 py-0.5 bg-emerald-950/50 rounded text-xs text-emerald-400 font-medium border border-emerald-900/50">
            Confirmed
          </div>
        );
      case 'error':
        return (
          <div className="px-2 py-0.5 bg-red-950/50 rounded text-xs text-red-400 font-medium border border-red-900/50">
            Failed
          </div>
        );
      case 'cancelled':
        return (
          <div className="px-2 py-0.5 bg-zinc-950/50 rounded text-xs text-zinc-400 font-medium border border-zinc-800/50">
            Cancelled
          </div>
        );
      default:
        return (
          <div className="px-2 py-0.5 bg-amber-950/50 rounded text-xs text-amber-400 font-medium border border-amber-900/50">
            Pending Approval
          </div>
        );
    }
  };

  return (
    <div className="flex flex-col gap-4 rounded-2xl p-6 bg-zinc-900/50 backdrop-blur-sm max-w-[500px] border border-zinc-800 shadow-xl">
      {/* Title Section */}
      <div className="flex flex-row justify-between items-center">
        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <WrenchIcon className="size-5 text-zinc-400 fill-zinc-400" />
            <h2 className="text-xl font-medium text-zinc-100">Maintenance Request</h2>
          </div>
          <p className="text-sm text-zinc-400 mt-1">
            {formatDateTime(time)}
          </p>
        </div>
        {getStatusBadge()}
      </div>

      {/* Device Info */}
      <div className="bg-zinc-900/70 rounded-lg p-4 border border-zinc-800/50">
        <div className="flex flex-col gap-3">
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium text-zinc-400">Device IDs</span>
            <div className="flex flex-wrap gap-2 justify-end">
              {deviceIds.map((id, index) => (
                <span 
                  key={index}
                  className="text-sm font-medium text-emerald-400 bg-emerald-950/50 px-3 py-1 rounded-full border border-emerald-800/50"
                >
                  {id.replace("chiller_", "CH-")}
                </span>
              ))}
            </div>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium text-zinc-400">Action</span>
            <span className="text-sm font-medium text-zinc-300">
              {maintenance_flag ? 'Set to Maintenance Mode' : 'Remove from Maintenance'}
            </span>
          </div>
        </div>
      </div>

      {/* Personnel Info */}
      <div className="bg-zinc-900/70 rounded-lg p-4 border border-zinc-800/50">
        <div className="flex flex-col gap-3">
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium text-zinc-400">Reporter</span>
            <span className="text-sm font-medium text-zinc-300">{reporter_name}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium text-zinc-400">Technician</span>
            <span className="text-sm font-medium text-zinc-300">{technician_name}</span>
          </div>
        </div>
      </div>

      {/* Reason Section */}
      {reason && (
        <div className="bg-zinc-900/70 rounded-lg p-4 border border-zinc-800/50">
          <span className="text-sm font-medium text-zinc-400">Reason</span>
          <div className={cn(
            "mt-2 p-3 bg-zinc-950/50 rounded-md border-l-4",
            {
              "border-emerald-500": status === 'success',
              "border-red-500": status === 'error',
              "border-blue-500": status === 'submitting',
              "border-zinc-500": status === 'cancelled',
              "border-amber-500": status === 'pending'
            }
          )}>
            <p className="text-sm text-zinc-300">{reason}</p>
          </div>
        </div>
      )}

      {/* Status Messages */}
      {message && (
        <div className={cn(
          "px-3 py-2 rounded-lg",
          {
            "bg-emerald-950/50 border border-emerald-900/50": status === 'success' || status === 'pending' || status === 'submitting',
            "bg-zinc-950/50 border border-zinc-800/50": status === 'cancelled'
          }
        )}>
          <p className={cn(
            "text-sm",
            {
              "text-emerald-400": status === 'success' || status === 'pending' || status === 'submitting',
              "text-zinc-400": status === 'cancelled'
            }
          )}>{message}</p>
        </div>
      )}
      {error && (
        <div className="px-3 py-2 bg-red-950/50 border border-red-900/50 rounded-lg">
          <p className="text-sm text-red-400">{error}</p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex flex-row gap-3 mt-2">
        <Button
          variant="outline"
          className={cn(
            "flex-1 border-zinc-700 text-zinc-300 hover:bg-zinc-800 hover:text-zinc-100 transition-all duration-200",
            {
              "opacity-50 cursor-not-allowed": status === 'submitting' || status === 'success' || status === 'cancelled'
            }
          )}
          onClick={handleCancel}
          disabled={status === 'submitting' || status === 'success' || status === 'cancelled'}
        >
          {status === 'cancelled' ? 'Cancelled' : 'Cancel'}
        </Button>
        <Button
          variant="default"
          className={cn(
            "flex-1 transition-all duration-200",
            {
              "bg-emerald-600 hover:bg-emerald-500": status === 'pending',
              "bg-emerald-700 hover:bg-emerald-600 animate-pulse": status === 'submitting',
              "bg-emerald-800 cursor-not-allowed": status === 'success',
              "bg-red-600 hover:bg-red-500": status === 'error',
              "bg-zinc-700 cursor-not-allowed": status === 'cancelled'
            }
          )}
          onClick={handleConfirm}
          disabled={status === 'submitting' || status === 'success' || status === 'cancelled'}
        >
          {status === 'submitting' ? 'Processing...' : 
           status === 'success' ? 'Confirmed' : 
           status === 'error' ? 'Try Again' : 
           status === 'cancelled' ? 'Cancelled' :
           'Confirm Request'}
        </Button>
      </div>
    </div>
  );
}
