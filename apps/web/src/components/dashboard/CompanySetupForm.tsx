"use client";

import { FormEvent, useState } from "react";

type Props = {
  apiBaseUrl: string;
  ownerUserId: string;
};

export function CompanySetupForm({ apiBaseUrl, ownerUserId }: Props) {
  const [name, setName] = useState("");
  const [website, setWebsite] = useState("");
  const [statusMessage, setStatusMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedName = name.trim();
    let trimmedWebsite = website.trim();

    if (!trimmedName || !trimmedWebsite || isSubmitting) {
      setStatusMessage("Please enter company name and website.");
      return;
    }

    if (
      !trimmedWebsite.startsWith("http://") &&
      !trimmedWebsite.startsWith("https://")
    ) {
      trimmedWebsite = `https://${trimmedWebsite}`;
    }

    setIsSubmitting(true);
    setStatusMessage("");

    try {
      const response = await fetch(`${apiBaseUrl}/companies`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          owner_user_id: ownerUserId,
          name: trimmedName,
          website: trimmedWebsite,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        setStatusMessage(errorText);
        return;
      }

      window.location.reload();
    } catch (error) {
      setStatusMessage(
        error instanceof Error
          ? error.message
          : "Could not create company. Please try again.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="mt-4 space-y-3">
      <input
        value={name}
        onChange={(event) => setName(event.target.value)}
        placeholder="Company name"
        className="w-full rounded-xl border px-3 py-2"
      />

      <input
        value={website}
        onChange={(event) => setWebsite(event.target.value)}
        placeholder="https://example.com"
        className="w-full rounded-xl border px-3 py-2"
      />

      <button
        type="submit"
        disabled={isSubmitting}
        className="rounded-xl bg-gray-900 px-4 py-2 text-white disabled:opacity-50"
      >
        {isSubmitting ? "Creating..." : "Create Company"}
      </button>

      {statusMessage && <p className="text-sm text-red-600">{statusMessage}</p>}
    </form>
  );
}