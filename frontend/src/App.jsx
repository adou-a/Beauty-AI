
//把App.css的样式加载到当前前端应用里
import './App.css'
import Header from './components/Header'
import ChatInput from './components/ChatInput'
import MessageList from './components/MessageList'
import { useState } from 'react'


function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [sessionId, setSessionId] = useState("")


  return (
    <div>
      <Header />
      <MessageList />
      <ChatInput />

     
    </div>
  )
}
export default App
