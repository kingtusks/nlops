import { useState, useRef, useEffect } from "react"
import ReactMarkdown from "react-markdown"
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome"
import { faPaperPlane } from "@fortawesome/free-solid-svg-icons"
import "./App.css"

const Spinner = () => <div className="spinner" />

export default function App() {
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Hi, I'm nlops. Tell me what you need. I can manage your containers and servers." }
  ])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, loading])

  const send = async () => {
    const msg = input.trim()
    if (!msg || loading) return
    setInput("")
    setMessages(prev => [...prev, { role: "user", content: msg }])
    setLoading(true)

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg }),
      })
      const data = await res.json()
      setMessages(prev => [...prev, { role: "assistant", content: data.response }])
    } catch {
      setMessages(prev => [...prev, { role: "assistant", content: "Couldn't reach the backend." }])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  return (
    <div className="app">
      <header className="header">
        <span className="logo">nlops</span>
        <span className="status">
          {loading ? <Spinner /> : <><div className="dot" /> ready</>}
        </span>
      </header>

      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <span className="label">{msg.role === "assistant" ? "nlops" : "You"}</span>
            <div className={`bubble ${msg.role}`}>
              {msg.role === "assistant"
                ? <ReactMarkdown>{msg.content}</ReactMarkdown>
                : msg.content
              }
            </div>
          </div>
        ))}

        {loading && (
          <div className="typing">
            <div className="typing-bubble">
              <span /><span /><span />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className="input-area">
        <div className="input-row">
          <input
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && send()}
            placeholder="restart nginx, check disk usage, list containers..."
            disabled={loading}
            autoFocus
          />
          <button className="send-btn" onClick={send} disabled={loading || !input.trim()}>
              <FontAwesomeIcon icon={faPaperPlane} style={{ width: 14, height: 14 }} />
            </button>
        </div>
      </div>
    </div>
  )
}