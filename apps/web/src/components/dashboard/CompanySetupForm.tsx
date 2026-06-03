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

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const response = await fetch(`${apiBaseUrl}/companies`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        owner_user_id: ownerUserId,
        name,
        website,
      }),
    });

    if (!response.ok) {
      setStatusMessage(await response.text());
      return;
    }

    window.location.reload();
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

      <button className="rounded-xl bg-gray-900 px-4 py-2 text-white">
        Create Company
      </button>

      {statusMessage && <p className="text-sm text-red-600">{statusMessage}</p>}
    </form>
  );
}