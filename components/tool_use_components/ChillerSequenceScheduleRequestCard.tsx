"use client";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { format } from "date-fns";
import { useState } from "react";

interface ScheduleArgs {
  chiller_id: string;
  profile_type: string;
  old_schedule: Array<{
    start: string | null;
    stop: string | null;
  }>;
  new_schedule: Array<{
    start: string | null;
    stop: string | null;
  }>;
}

interface ChillerSequenceScheduleRequestCardProps {
  result: {
    success: boolean;
    message: string;
    data: ScheduleArgs;
  };
}

type ScheduleStatus = 'pending' | 'submitting' | 'success' | 'error' | 'cancelled';

export function ChillerSequenceScheduleRequestCard({
  result
}: ChillerSequenceScheduleRequestCardProps) {
  // If data is undefined or doesn't have required properties, don't render
  if (!result?.data?.chiller_id || !result?.data?.old_schedule || !result?.data?.new_schedule) {
    return null;
  }

  const { chiller_id, profile_type = '', old_schedule, new_schedule } = result.data;
  const [status, setStatus] = useState<ScheduleStatus>('pending');
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const formatTime = (timeStr: string | null) => {
    return timeStr || '--:--';
  };

  const isNextDay = (start: string | null, stop: string | null) => {
    if (!start || !stop) return false;
    const [startHour] = start.split(':').map(Number);
    const [stopHour] = stop.split(':').map(Number);
    return stopHour < startHour;
  };

  const handleConfirm = async () => {
    try {
      setStatus('submitting');
      setError(null);
      setMessage(null);

      const response = await fetch('/api/chiller_plant/chiller_sequence_schedule_change', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          chiller_id,
          profile_type,
          old_schedule,
          new_schedule
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Failed to update schedule');
      }

      setStatus('success');
      setMessage(data.message || 'Successfully updated schedule');

      // Notify the parent component through window.postMessage
      window.postMessage({ 
        type: 'CONFIRM_SCHEDULE', 
        chillerId: chiller_id,
        success: true 
      }, '*');

    } catch (err) {
      setStatus('error');
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      console.error('Failed to update schedule:', err);
    }
  };

  const handleCancel = () => {
    setStatus('cancelled');
    setMessage('Schedule change request cancelled');
    setError(null);
    
    // Notify the parent component through window.postMessage
    window.postMessage({ 
      type: 'CANCEL_SCHEDULE', 
      chillerId: chiller_id,
      success: true 
    }, '*');
  };

  const getStatusBadge = () => {
    switch (status) {
      case 'submitting':
        return (
          <div className="px-2 py-0.5 bg-blue-950/50 rounded text-xs text-blue-400 font-medium border border-blue-900/50 animate-pulse">
            Submitting...
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
            Pending
          </div>
        );
    }
  };

  const renderTimeSlots = (schedule: Array<{ start: string | null; stop: string | null }>) => {
    return schedule
      .filter(slot => slot.start !== null || slot.stop !== null) // Skip slots where both are null
      .map((slot, index) => (
        <div key={index} className="flex justify-between items-center py-2 px-3 bg-zinc-950/50 rounded-md">
          <span className="text-xs text-zinc-500">Period {index + 1}</span>
          <div className="flex items-center gap-2">
            <span className="text-sm text-zinc-300 font-medium">
              {slot.start === null && slot.stop 
                ? `Stop at ${slot.stop}`
                : slot.stop === null && slot.start
                ? `Start at ${slot.start}`
                : `${slot.start} - ${slot.stop}`}
            </span>
            {isNextDay(slot.start, slot.stop) && (
              <span className="text-xs text-amber-400">(next day)</span>
            )}
          </div>
        </div>
      ));
  };

  return (
    <div className="flex flex-col gap-4 rounded-2xl p-6 bg-zinc-900/50 backdrop-blur-sm max-w-[500px] border border-zinc-800 shadow-xl">
      {/* Title Section */}
      <div className="flex flex-row justify-between items-center">
        <h2 className="text-xl font-medium text-zinc-100">Schedule Change Request</h2>
        <div className="text-sm font-medium text-emerald-400 bg-emerald-950/50 px-3 py-1 rounded-full border border-emerald-800/50">
          {chiller_id ? chiller_id.replace("chiller_", "CH-") : 'N/A'}
        </div>
      </div>

      {/* Current Schedule Section */}
      <div className="bg-zinc-900/70 rounded-lg p-4 border border-zinc-800/50">
        <div className="flex items-center gap-2 mb-2">
          <h3 className="text-sm font-medium text-zinc-400">Current Schedule</h3>
          <div className="text-xs font-medium text-zinc-400 bg-zinc-950/50 px-3 py-1 rounded-full border border-zinc-800/50">
            Profile: {profile_type}
          </div>
        </div>
        <div className="space-y-2">
          {renderTimeSlots(old_schedule)}
        </div>
      </div>

      {/* New Schedule Section */}
      <div className="bg-zinc-900/70 rounded-lg p-4 border border-zinc-800/50">
        <div className="flex items-center gap-2 mb-2">
          <h3 className="text-sm font-medium text-zinc-400">New Schedule</h3>
          <div className="text-xs font-medium text-zinc-400 bg-zinc-950/50 px-3 py-1 rounded-full border border-zinc-800/50">
            Profile: {profile_type}
          </div>
          {getStatusBadge()}
        </div>
        <div className="space-y-2">
          {renderTimeSlots(new_schedule.map((slot, index) => ({
            ...slot,
            start: formatTime(slot.start),
            stop: formatTime(slot.stop)
          })))}
        </div>
      </div>

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
          {status === 'submitting' ? 'Confirming...' : 
           status === 'success' ? 'Confirmed' : 
           status === 'error' ? 'Try Again' : 
           status === 'cancelled' ? 'Cancelled' :
           'Confirm Change'}
        </Button>
      </div>
    </div>
  );
}
