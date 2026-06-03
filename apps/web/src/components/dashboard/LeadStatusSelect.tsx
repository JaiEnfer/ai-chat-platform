"use client";

import { useState } from "react";

type Props = {
  apiBaseUrl: string;
  leadId: number;
  currentStatus: string;
};

const STATUSES = ["new", "contacted", "converted", "closed"];

export function LeadStatusSelect({
  apiBaseUrl,
  leadId,
  currentStatus,
}: Props) {
  const [status, setStatus] = useState(currentStatus);
  const [isUpdating, setIsUpdating] = useState(false);

  async function handleChange(newStatus: string) {
    setStatus(newStatus);
    setIsUpdating(true);

    const response = await fetch(`${apiBaseUrl}/leads/${leadId}/status`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        status: newStatus,
      }),
    });

    setIsUpdating(false);

    if (!response.ok) {
      alert("Could not update lead status.");
      setStatus(currentStatus);
    }
  }

  return (
    <div className="flex items-center gap-2">
      <select
        value={status}
        onChange={(event) => handleChange(event.target.value)}
        disabled={isUpdating}
        className="rounded-lg border border-gray-300 px-2 py-1 text-sm"
      >
        {STATUSES.map((statusOption) => (
          <option key={statusOption} value={statusOption}>
            {statusOption}
          </option>
        ))}
      </select>

      {isUpdating && <span className="text-xs text-gray-500">Saving...</span>}
    </div>
  );
}