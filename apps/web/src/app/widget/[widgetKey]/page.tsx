import { ChatWidget } from "@/components/chat-widget/ChatWidget";

type Props = {
  params: Promise<{
    widgetKey: string;
  }>;
};

export default async function WidgetPage({ params }: Props) {
  const { widgetKey } = await params;

  return (
    <main className="min-h-screen bg-gray-100">
      <ChatWidget widgetKey={widgetKey} />
    </main>
  );
}