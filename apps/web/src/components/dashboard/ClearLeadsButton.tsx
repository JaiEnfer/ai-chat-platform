"use client";

type Props = {
  apiBaseUrl: string;
  companyId: number;
};

export function ClearLeadsButton({ apiBaseUrl, companyId }: Props) {
  async function handleClear() {
    const confirmed = window.confirm(
      "Delete all saved leads for this company?",
    );

    if (!confirmed) {
      return;
    }

    const response = await fetch(`${apiBaseUrl}/companies/${companyId}/leads`, {
      method: "DELETE",
    });

    if (!response.ok) {
      alert("Could not clear leads.");
      return;
    }

    window.location.reload();
  }

  return (
    <button
      type="button"
      onClick={handleClear}
      className="rounded-xl border border-red-200 px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-50"
    >
      Clear Leads
    </button>
  );
}
