"use client";

import { FormEvent, useState } from "react";

type WebsiteScrapeFormProps = {
  apiBaseUrl: string;
  companyId: number;
};

export function WebsiteScrapeForm({
  apiBaseUrl,
  companyId,
}: WebsiteScrapeFormProps) {
  const [url, setUrl] = useState("");
  const [statusMessage, setStatusMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedUrl = url.trim();

    if (!trimmedUrl || isSubmitting) {
      return;
    }

    setIsSubmitting(true);
    setStatusMessage("");

    try {
      const response = await fetch(
        `${apiBaseUrl}/companies/${companyId}/scrape-website`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            url: trimmedUrl,
          }),
        },
      );

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || "Website scraping failed");
      }

      const data = (await response.json()) as {
        chunks_created: number;
      };

      setUrl("");
      setStatusMessage(
        `Website imported successfully. Created ${data.chunks_created} knowledge chunks. Refresh the page to see them.`,
      );
    } catch (error) {
      setStatusMessage(
        error instanceof Error
          ? `Could not import website: ${error.message}`
          : "Could not import website. Please try again.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="mt-4 space-y-3">
      <input
        value={url}
        onChange={(event) => setUrl(event.target.value)}
        placeholder="https://example.com"
        className="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-900"
      />

      <button
        type="submit"
        disabled={isSubmitting}
        className="rounded-xl bg-gray-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
      >
        {isSubmitting ? "Importing..." : "Import Website"}
      </button>

      {statusMessage && <p className="text-sm text-gray-600">{statusMessage}</p>}
    </form>
  );
}