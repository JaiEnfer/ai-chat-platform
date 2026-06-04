"use client";

import { useRouter } from "next/navigation";

type Props = {
  apiBaseUrl: string;
  companyId: number;
};

export function DeleteAccountButton({ apiBaseUrl, companyId }: Props) {
  const router = useRouter();

  async function handleDelete() {
    const confirmed = window.confirm(
      "Delete this company account and all stored leads, conversations, and knowledge?",
    );

    if (!confirmed) {
      return;
    }

    const doubleConfirmed = window.confirm(
      "This cannot be undone. Do you want to permanently delete all company data?",
    );

    if (!doubleConfirmed) {
      return;
    }

    const response = await fetch(`${apiBaseUrl}/companies/${companyId}`, {
      method: "DELETE",
    });

    if (!response.ok) {
      alert("Could not delete account.");
      return;
    }

    router.replace("/dashboard");
    router.refresh();
  }

  return (
    <button
      type="button"
      onClick={handleDelete}
      className="rounded-xl bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700"
    >
      Delete Account
    </button>
  );
}
