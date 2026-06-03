"use client";

import { FormEvent, useState } from "react";

type CompanyOnboardingFormProps = {
  apiBaseUrl: string;
  ownerUserId: string;
};

export function CompanyOnboardingForm(props: CompanyOnboardingFormProps) {
  const [name, setName] = useState("");
  const [website, setWebsite] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedName = name.trim();
    const trimmedWebsite = website.trim();

    if (!trimmedName || !trimmedWebsite || isSubmitting) {
      return;
    }

    setIsSubmitting(true);
    setStatusMessage("");

    try {
      const response = await fetch(`${props.apiBaseUrl}/companies`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          owner_user_id: props.ownerUserId,
          name: trimmedName,
          website: trimmedWebsite,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || "Failed to create company");
      }

      setStatusMessage("Company created. Refreshing dashboard...");
      window.location.reload();
    } catch (error) {
      setStatusMessage(
        error instanceof Error
          ? `Could not create company: ${error.message}`
          : "Could not create company. Please try again.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="mt-6 space-y-3">
      <input
        value={name}
        onChange={(event) => setName(event.target.value)}
        placeholder="Company name"
        className="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-900"
      />

      <input
        value={website}
        onChange={(event) => setWebsite(event.target.value)}
        placeholder="https://example.com"
        className="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-900"
      />

      <button
        type="submit"
        disabled={isSubmitting}
        className="rounded-xl bg-gray-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
      >
        {isSubmitting ? "Creating..." : "Create Company"}
      </button>

      {statusMessage && <p className="text-sm text-gray-600">{statusMessage}</p>}
    </form>
  );
}
