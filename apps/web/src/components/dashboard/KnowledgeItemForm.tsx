"use client";

import { ChangeEvent, FormEvent, useState } from "react";

type KnowledgeItemFormProps = {
  apiBaseUrl: string;
  companyId: number;
};

type KnowledgeMode = "manual" | "html" | "file";

const knowledgeModes: Array<{
  id: KnowledgeMode;
  label: string;
  description: string;
}> = [
  {
    id: "manual",
    label: "Manual",
    description: "Add a short answer, FAQ, or policy directly.",
  },
  {
    id: "html",
    label: "HTML",
    description: "Paste cleaned markup from a support page or article.",
  },
  {
    id: "file",
    label: "Document",
    description: "Upload files like PDF, DOCX, CSV, or HTML.",
  },
];

export function KnowledgeItemForm(props: KnowledgeItemFormProps) {
  const [activeMode, setActiveMode] = useState<KnowledgeMode>("manual");
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [htmlTitle, setHtmlTitle] = useState("");
  const [htmlContent, setHtmlContent] = useState("");
  const [fileTitle, setFileTitle] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isSubmittingManual, setIsSubmittingManual] = useState(false);
  const [isSubmittingHtml, setIsSubmittingHtml] = useState(false);
  const [isSubmittingFile, setIsSubmittingFile] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");

  async function handleManualSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedTitle = title.trim();
    const trimmedContent = content.trim();

    if (!trimmedTitle || !trimmedContent || isSubmittingManual) {
      return;
    }

    setIsSubmittingManual(true);
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
        const errorText = await response.text();
        throw new Error(errorText || "Failed to create knowledge item");
      }

      setTitle("");
      setContent("");
      setStatusMessage("Manual knowledge added. Refresh the page to see it.");
    } catch (error) {
      setStatusMessage(
        error instanceof Error
          ? `Could not add manual knowledge: ${error.message}`
          : "Could not add manual knowledge. Please try again.",
      );
    } finally {
      setIsSubmittingManual(false);
    }
  }

  async function handleHtmlSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedTitle = htmlTitle.trim();
    const trimmedHtmlContent = htmlContent.trim();

    if (!trimmedTitle || !trimmedHtmlContent || isSubmittingHtml) {
      return;
    }

    setIsSubmittingHtml(true);
    setStatusMessage("");

    try {
      const response = await fetch(
        `${props.apiBaseUrl}/companies/${props.companyId}/knowledge-html`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            title: trimmedTitle,
            html_content: trimmedHtmlContent,
            source_label: `html:${trimmedTitle}`,
          }),
        },
      );

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || "Failed to import HTML knowledge");
      }

      const data = (await response.json()) as { chunks_created: number };

      setHtmlTitle("");
      setHtmlContent("");
      setStatusMessage(
        `HTML imported successfully. Created ${data.chunks_created} knowledge chunks.`,
      );
    } catch (error) {
      setStatusMessage(
        error instanceof Error
          ? `Could not import HTML knowledge: ${error.message}`
          : "Could not import HTML knowledge. Please try again.",
      );
    } finally {
      setIsSubmittingHtml(false);
    }
  }

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const nextFile = event.target.files?.[0] ?? null;
    setSelectedFile(nextFile);

    if (nextFile && !fileTitle.trim()) {
      const fileNameWithoutExtension =
        nextFile.name.replace(/\.[^/.]+$/, "") || nextFile.name;
      setFileTitle(fileNameWithoutExtension);
    }
  }

  async function handleFileSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!selectedFile || isSubmittingFile) {
      return;
    }

    setIsSubmittingFile(true);
    setStatusMessage("");

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      if (fileTitle.trim()) {
        formData.append("title", fileTitle.trim());
      }

      const response = await fetch(
        `${props.apiBaseUrl}/companies/${props.companyId}/knowledge-files`,
        {
          method: "POST",
          body: formData,
        },
      );

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || "Failed to upload knowledge file");
      }

      const data = (await response.json()) as {
        chunks_created: number;
        source: string;
      };

      setSelectedFile(null);
      setFileTitle("");
      setStatusMessage(
        `File imported successfully from ${data.source}. Created ${data.chunks_created} knowledge chunks.`,
      );
    } catch (error) {
      setStatusMessage(
        error instanceof Error
          ? `Could not upload knowledge file: ${error.message}`
          : "Could not upload knowledge file. Please try again.",
      );
    } finally {
      setIsSubmittingFile(false);
    }
  }

  return (
    <div className="mt-4 space-y-6">
      <div className="grid gap-3 md:grid-cols-3">
        {knowledgeModes.map((mode) => {
          const isActive = activeMode === mode.id;

          return (
            <button
              key={mode.id}
              type="button"
              onClick={() => setActiveMode(mode.id)}
              className={`rounded-2xl border p-4 text-left transition ${
                isActive
                  ? "border-gray-900 bg-gray-900 text-white"
                  : "border-gray-200 bg-white text-gray-900 hover:border-gray-400"
              }`}
            >
              <p className="text-sm font-semibold">{mode.label}</p>
              <p
                className={`mt-1 text-sm ${
                  isActive ? "text-gray-200" : "text-gray-500"
                }`}
              >
                {mode.description}
              </p>
            </button>
          );
        })}
      </div>

      {activeMode === "manual" && (
        <form
          onSubmit={handleManualSubmit}
          className="space-y-3 rounded-2xl border p-4"
        >
          <div>
            <h3 className="text-sm font-semibold text-gray-900">Manual Entry</h3>
            <p className="mt-1 text-sm text-gray-500">
              Add a short answer, policy, FAQ, or support note directly.
            </p>
          </div>

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
            disabled={isSubmittingManual}
            className="rounded-xl bg-gray-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
          >
            {isSubmittingManual ? "Saving..." : "Add Manual Knowledge"}
          </button>
        </form>
      )}

      {activeMode === "html" && (
        <form
          onSubmit={handleHtmlSubmit}
          className="space-y-3 rounded-2xl border p-4"
        >
          <div>
            <h3 className="text-sm font-semibold text-gray-900">Paste HTML</h3>
            <p className="mt-1 text-sm text-gray-500">
              Paste cleaned HTML snippets, support page markup, or exported article
              content.
            </p>
          </div>

          <input
            value={htmlTitle}
            onChange={(event) => setHtmlTitle(event.target.value)}
            placeholder="HTML source title"
            className="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-900"
          />

          <textarea
            value={htmlContent}
            onChange={(event) => setHtmlContent(event.target.value)}
            placeholder="<section><h2>Support Policy</h2>..."
            rows={7}
            className="w-full rounded-xl border border-gray-300 px-3 py-2 font-mono text-sm outline-none focus:border-gray-900"
          />

          <button
            type="submit"
            disabled={isSubmittingHtml}
            className="rounded-xl bg-gray-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
          >
            {isSubmittingHtml ? "Importing..." : "Import HTML"}
          </button>
        </form>
      )}

      {activeMode === "file" && (
        <form
          onSubmit={handleFileSubmit}
          className="space-y-3 rounded-2xl border p-4"
        >
          <div>
            <h3 className="text-sm font-semibold text-gray-900">Upload File</h3>
            <p className="mt-1 text-sm text-gray-500">
              Upload txt, md, html, csv, json, pdf, or docx files for ingestion.
            </p>
          </div>

          <input
            value={fileTitle}
            onChange={(event) => setFileTitle(event.target.value)}
            placeholder="Optional display title"
            className="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-900"
          />

          <input
            type="file"
            onChange={handleFileChange}
            accept=".txt,.md,.rst,.html,.htm,.csv,.json,.pdf,.docx"
            className="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm outline-none file:mr-4 file:rounded-lg file:border-0 file:bg-gray-900 file:px-3 file:py-2 file:text-sm file:font-medium file:text-white"
          />

          <button
            type="submit"
            disabled={!selectedFile || isSubmittingFile}
            className="rounded-xl bg-gray-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
          >
            {isSubmittingFile ? "Uploading..." : "Upload Knowledge File"}
          </button>
        </form>
      )}

      {statusMessage && <p className="text-sm text-gray-600">{statusMessage}</p>}
    </div>
  );
}
