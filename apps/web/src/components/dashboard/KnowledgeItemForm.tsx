"use client";

import { FormEvent, useState } from "react";

type KnowledgeItemFormProps = {
  apiBaseUrl: string;
  companyId: number;
};

export function KnowledgeItemForm(props: KnowledgeItemFormProps) {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedTitle = title.trim();
    const trimmedContent = content.trim();

    if (!trimmedTitle || !trimmedContent || isSubmitting) {
      return;
    }

    setIsSubmitting(true);
    setStatusMessage("");

    try {
      const response = await fetch(`${props.apiBaseUrl}/knowledge-items`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          company_id: props.companyId,
          title: trimmedTitle,
          content: trimmedContent,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to create knowledge item");
      }

      setTitle("");
      setContent("");
      setStatusMessage("Knowledge item added. Refresh the page to see it.");
    } catch {
      setStatusMessage("Could not add knowledge item. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="mt-4 space-y-3">
      <input
        value={title}
        onChange={(event) => setTitle(event.target.value)}
        placeholder="Title, e.g. Opening Hours"
        className="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-900"
      />

      <textarea
        value={content}
        onChange={(event) => setContent(event.target.value)}
        placeholder="Content the chatbot should know..."
        rows={5}
        className="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-900"
      />

      <button
        type="submit"
        disabled={isSubmitting}
        className="rounded-xl bg-gray-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
      >
        Add Knowledge
      </button>

      {statusMessage && <p className="text-sm text-gray-600">{statusMessage}</p>}
    </form>
  );
}