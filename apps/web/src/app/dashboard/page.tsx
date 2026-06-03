import { KnowledgeItemForm } from "@/components/dashboard/KnowledgeItemForm";
import { currentUser } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";
import { CompanySetupForm } from "@/components/dashboard/CompanySetupForm";
export const dynamic = "force-dynamic";
export const revalidate = 0;

type Analytics = {
  company_id: number;
  total_leads: number;
  total_conversation_messages: number;
  total_lead_requests: number;
  total_knowledge_items: number;
};

type Lead = {
  id: number;
  company_id: number;
  name: string;
  email: string;
  phone: string | null;
  message: string | null;
  created_at: string;
};

type ConversationMessage = {
  id: number;
  company_id: number;
  visitor_id: string;
  user_message: string;
  bot_answer: string;
  should_collect_lead: boolean;
  created_at: string;
};

type KnowledgeItem = {
  id: number;
  company_id: number;
  title: string;
  content: string;
  created_at: string;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;
const CONFIGURED_WIDGET_KEY = process.env.NEXT_PUBLIC_WIDGET_KEY;

async function getJson<T>(path: string): Promise<T> {
  if (!API_BASE_URL) {
    throw new Error("Missing NEXT_PUBLIC_API_BASE_URL");
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${path}`);
  }

  return response.json() as Promise<T>;
}

export default async function DashboardPage() {
  const user = await currentUser();

  if (!user) {
    redirect("/");
  }

  let company: {
    id: number;
    owner_user_id: string;
    name: string;
    website: string;
    widget_key: string;
  } | null = null;

  let companyLoadError = "";

  try {
    company = await getJson<{
      id: number;
      owner_user_id: string;
      name: string;
      website: string;
      widget_key: string;
    }>(`/users/${user.id}/company`);
  } catch (error) {
    companyLoadError =
      error instanceof Error ? error.message : "Unknown company loading error";

    company = null;
  }

  if (!company) {
    return (
      <main className="min-h-screen bg-gray-100 p-8 text-gray-900">
        <div className="mx-auto max-w-3xl rounded-2xl bg-white p-6 shadow-sm">
          <h1 className="text-2xl font-bold">Set up your company</h1>
          <p className="mt-2 text-gray-600">
            Your account is signed in, but no company is connected yet.
          </p>
          {companyLoadError && (
            <p className="mt-2 text-red-500">{companyLoadError}</p>
          )}

          {API_BASE_URL && (
            <CompanySetupForm apiBaseUrl={API_BASE_URL} ownerUserId={user.id} />
          )}
        </div>
      </main>
    );
  }

  const companyId = company.id;
  const hasWidgetKeyMismatch =
    Boolean(CONFIGURED_WIDGET_KEY) &&
    CONFIGURED_WIDGET_KEY !== company.widget_key;

  const [analytics, leads, conversationMessages, knowledgeItems] =
    await Promise.all([
      getJson<Analytics>(`/companies/${companyId}/analytics`),
      getJson<Lead[]>(`/companies/${companyId}/leads`),
      getJson<ConversationMessage[]>(
        `/companies/${companyId}/conversation-messages`,
      ),
      getJson<KnowledgeItem[]>(`/companies/${companyId}/knowledge-items`),
    ]);

  return (
    <main className="min-h-screen bg-gray-100 p-8 text-gray-900">
      <div className="mx-auto max-w-6xl space-y-8">
        <div>
          <h1 className="text-3xl font-bold">Business Dashboard</h1>
          <p className="mt-1 text-sm text-gray-500">
            Company: {company.name}
          </p>
          <p className="mt-1 text-sm text-gray-500">Company ID: {company.id}</p>
          <p className="mt-1 text-sm text-gray-500">
            Widget key: {company.widget_key}
          </p>
          <p className="mt-2 text-gray-600">
            Leads, chatbot activity, and basic analytics.
          </p>
        </div>

        {hasWidgetKeyMismatch && (
          <section className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
            Vercel is using widget key <strong>{CONFIGURED_WIDGET_KEY}</strong>,
            but this signed-in company owns <strong>{company.widget_key}</strong>.
            Update `NEXT_PUBLIC_WIDGET_KEY` in Vercel to match this company if
            you want widget leads to appear here.
          </section>
        )}

        <section className="grid gap-4 md:grid-cols-4">
          <MetricCard title="Leads" value={analytics.total_leads} />
          <MetricCard
            title="Messages"
            value={analytics.total_conversation_messages}
          />
          <MetricCard
            title="Lead Requests"
            value={analytics.total_lead_requests}
          />
          <MetricCard
            title="Knowledge Items"
            value={analytics.total_knowledge_items}
          />
        </section>

        <section className="rounded-2xl bg-white p-5 shadow-sm">
          <h2 className="text-xl font-semibold">Recent Leads</h2>

          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b text-gray-500">
                  <th className="py-2">Name</th>
                  <th className="py-2">Email</th>
                  <th className="py-2">Phone</th>
                  <th className="py-2">Message</th>
                </tr>
              </thead>

              <tbody>
                {leads.map((lead) => (
                  <tr key={lead.id} className="border-b last:border-0">
                    <td className="py-3">{lead.name}</td>
                    <td className="py-3">{lead.email}</td>
                    <td className="py-3">{lead.phone ?? "-"}</td>
                    <td className="py-3">{lead.message ?? "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            {leads.length === 0 && (
              <p className="py-6 text-sm text-gray-500">No leads yet.</p>
            )}
          </div>
        </section>

        <section className="rounded-2xl bg-white p-5 shadow-sm">
          <h2 className="text-xl font-semibold">Chatbot Knowledge</h2>
          <p className="mt-1 text-sm text-gray-500">
            Add facts the chatbot should use when answering visitors.
          </p>

          {API_BASE_URL && (
            <KnowledgeItemForm apiBaseUrl={API_BASE_URL} companyId={companyId} />
          )}

          <div className="mt-6 space-y-3">
            {knowledgeItems.map((item) => (
              <div key={item.id} className="rounded-xl border p-4">
                <p className="font-medium">{item.title}</p>
                <p className="mt-1 text-sm text-gray-600">{item.content}</p>
              </div>
            ))}

            {knowledgeItems.length === 0 && (
              <p className="text-sm text-gray-500">No knowledge items yet.</p>
            )}
          </div>
        </section>

        <section className="rounded-2xl bg-white p-5 shadow-sm">
          <h2 className="text-xl font-semibold">Recent Conversations</h2>

          <div className="mt-4 space-y-4">
            {conversationMessages.slice(0, 10).map((message) => (
              <div key={message.id} className="rounded-xl border p-4">
                <p className="text-xs text-gray-500">
                  Visitor: {message.visitor_id}
                </p>

                <p className="mt-2 text-sm">
                  <span className="font-semibold">Visitor:</span>{" "}
                  {message.user_message}
                </p>

                <p className="mt-2 text-sm">
                  <span className="font-semibold">Bot:</span>{" "}
                  {message.bot_answer}
                </p>

                {message.should_collect_lead && (
                  <p className="mt-2 text-xs font-medium text-orange-700">
                    Lead collection requested
                  </p>
                )}
              </div>
            ))}

            {conversationMessages.length === 0 && (
              <p className="text-sm text-gray-500">No conversations yet.</p>
            )}
          </div>
        </section>
      </div>
    </main>
  );
}

function MetricCard(props: { title: string; value: number }) {
  return (
    <div className="rounded-2xl bg-white p-5 shadow-sm">
      <p className="text-sm text-gray-500">{props.title}</p>
      <p className="mt-2 text-3xl font-bold">{props.value}</p>
    </div>
  );
}
