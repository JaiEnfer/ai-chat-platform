"use client";

import { useState } from "react";

type Props = {
  apiBaseUrl: string;
  leadId: number;
};

export function LeadActionsMenu({ apiBaseUrl, leadId }: Props) {
  const [selectedAction, setSelectedAction] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);

  async function handleActionChange(action: string) {
    setSelectedAction(action);

    if (action !== "delete") {
      return;
    }

    const confirmed = window.confirm("Delete this lead?");

    if (!confirmed) {
      setSelectedAction("");
      return;
    }

    setIsDeleting(true);

    const response = await fetch(`${apiBaseUrl}/leads/${leadId}`, {
      method: "DELETE",
    });

    setIsDeleting(false);
    setSelectedAction("");

    if (!response.ok) {
      alert("Could not delete lead.");
      return;
    }

    window.location.reload();
  }

  return (
    <select
      value={selectedAction}
      onChange={(event) => void handleActionChange(event.target.value)}
      disabled={isDeleting}
      className="rounded-lg border border-gray-300 px-2 py-1 text-sm text-gray-700"
    >
      <option value="">{isDeleting ? "Deleting..." : "Actions"}</option>
      <option value="delete">Delete lead</option>
    </select>
  );
}
