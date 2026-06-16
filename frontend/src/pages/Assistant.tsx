import { useEffect, useRef, useState } from 'react';
import { Bot, Send, User } from 'lucide-react';
import { datasetService } from '../services/datasetService';
import type { Dataset } from '../types';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export function Assistant() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    datasetService.list().then((res) => {
      setDatasets(res.data.datasets);
      if (res.data.datasets[0]) setSelectedId(res.data.datasets[0].id);
    });
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (text: string) => {
    if (!selectedId || !text.trim()) return;
    const userMsg: Message = { role: 'user', content: text };
    setMessages((m) => [...m, userMsg]);
    setInput('');
    setLoading(true);
    try {
      const { data } = await datasetService.chat(
        selectedId,
        text,
        messages.map((m) => ({ role: m.role, content: m.content }))
      );
      setMessages((m) => [...m, { role: 'assistant', content: data.reply }]);
      setSuggestions(data.suggestions);
    } catch {
      setMessages((m) => [...m, { role: 'assistant', content: 'Sorry, I could not process that request.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">AI Data Assistant</h1>
        <select
          value={selectedId ?? ''}
          onChange={(e) => { setSelectedId(Number(e.target.value)); setMessages([]); }}
          className="rounded-lg border px-3 py-2 dark:border-gray-600 dark:bg-gray-700"
        >
          {datasets.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
        </select>
      </div>

      <Card className="flex flex-1 flex-col !p-0 overflow-hidden">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-500 py-12">
              <Bot className="mx-auto h-12 w-12 text-primary-600 mb-4" />
              <p>Ask me anything about your dataset!</p>
              <div className="mt-4 flex flex-wrap justify-center gap-2">
                {['Summarize this dataset', 'Find anomalies', 'Show revenue trends', 'Which category performs best?'].map((s) => (
                  <button
                    key={s}
                    onClick={() => sendMessage(s)}
                    className="rounded-full border px-3 py-1 text-sm hover:bg-primary-50 dark:hover:bg-primary-900/20"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : ''}`}>
              {msg.role === 'assistant' && <Bot className="h-8 w-8 shrink-0 text-primary-600" />}
              <div
                className={`max-w-[80%] rounded-xl px-4 py-3 text-sm whitespace-pre-wrap ${
                  msg.role === 'user'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                }`}
              >
                {msg.content}
              </div>
              {msg.role === 'user' && <User className="h-8 w-8 shrink-0 text-gray-400" />}
            </div>
          ))}
          {loading && <p className="text-sm text-gray-500 animate-pulse">Analyzing...</p>}
          <div ref={bottomRef} />
        </div>

        {suggestions.length > 0 && (
          <div className="flex flex-wrap gap-2 border-t px-4 py-2 dark:border-gray-700">
            {suggestions.slice(0, 4).map((s) => (
              <button key={s} onClick={() => sendMessage(s)} className="text-xs text-primary-600 hover:underline">
                {s}
              </button>
            ))}
          </div>
        )}

        <form
          onSubmit={(e) => { e.preventDefault(); sendMessage(input); }}
          className="flex gap-2 border-t p-4 dark:border-gray-700"
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your data..."
            className="flex-1 rounded-lg border px-4 py-2 dark:border-gray-600 dark:bg-gray-700"
          />
          <Button type="submit" disabled={loading || !selectedId}>
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </Card>
    </div>
  );
}
