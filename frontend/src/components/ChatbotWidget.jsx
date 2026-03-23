import { useMemo, useState } from "react";
import api, { getApiErrorMessage } from "../api";

const ChatbotWidget = () => {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: "bot",
      text: "Hello. I am EMS Support Bot. Ask me about attendance, payroll, leave, login, and timesheets.",
    },
  ]);

  const quickQuestions = useMemo(
    () => [
      "How do I apply leave?",
      "My attendance is missing",
      "How can I reset my password?",
      "Where can I see payroll history?",
    ],
    [],
  );

  const askQuestion = async (inputText) => {
    const text = (inputText || "").trim();
    if (!text || loading) {
      return;
    }

    setMessages((prev) => [...prev, { role: "user", text }]);
    setQuery("");
    setLoading(true);

    try {
      const { data } = await api.post("/chatbot/support", { query: text });
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: data?.answer || "No answer found." },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text: getApiErrorMessage(
            error,
            "Support bot is unavailable. Please try again.",
          ),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    await askQuestion(query);
  };

  return (
    <div className="chatbot-widget">
      {open && (
        <section className="chatbot-panel" aria-label="EMS support chatbot">
          <header className="chatbot-header">
            <div>
              <strong>EMS Support</strong>
              <small>Employee help desk</small>
            </div>
            <button
              type="button"
              className="chatbot-close"
              onClick={() => setOpen(false)}
              aria-label="Close chatbot"
            >
              x
            </button>
          </header>

          <div className="chatbot-messages">
            {messages.map((message, index) => (
              <div
                key={`${message.role}-${index}`}
                className={`chatbot-msg ${message.role}`}
              >
                {message.text}
              </div>
            ))}
            {loading && <div className="chatbot-msg bot">Typing...</div>}
          </div>

          <div className="chatbot-quick-questions">
            {quickQuestions.map((item) => (
              <button
                type="button"
                key={item}
                onClick={() => askQuestion(item)}
                disabled={loading}
              >
                {item}
              </button>
            ))}
          </div>

          <form className="chatbot-form" onSubmit={handleSubmit}>
            <input
              type="text"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Type your question"
              maxLength={400}
              disabled={loading}
            />
            <button type="submit" disabled={loading || !query.trim()}>
              Send
            </button>
          </form>
        </section>
      )}

      <button
        type="button"
        className="chatbot-fab"
        onClick={() => setOpen((prev) => !prev)}
        aria-label={open ? "Hide chatbot" : "Open chatbot"}
      >
        <span className="chatbot-fab-dot" />
        <span>Chat</span>
      </button>
    </div>
  );
};

export default ChatbotWidget;
