"use client";

type Props = {
  apiBaseUrl: string;
  itemId: number;
};

export function DeleteKnowledgeButton({ apiBaseUrl, itemId }: Props) {
  async function handleDelete() {
    const confirmed = window.confirm("Delete this knowledge item?");

    if (!confirmed) {
      return;
    }

    const response = await fetch(`${apiBaseUrl}/knowledge-items/${itemId}`, {
      method: "DELETE",
    });

    if (!response.ok) {
      alert("Could not delete knowledge item.");
      return;
    }

    window.location.reload();
  }

  return (
    <button
      onClick={handleDelete}
      className="mt-3 rounded-lg border px-3 py-1 text-sm text-red-600"
    >
      Delete
    </button>
  );
}