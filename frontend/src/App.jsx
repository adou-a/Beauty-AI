
//把App.css的样式加载到当前前端应用里
import './App.css'
import Header from './components/Header'
import ChatInput from './components/ChatInput'
import MessageList from './components/MessageList'
import { useState, useEffect ,useRef} from 'react'
// Restore the real API after testing by changing this import to './api/chat'.
import { sendMessage } from './api/chat'

function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [sessionId,setSessionId] = useState(()=>{
    const storedSessionId =localStorage.getItem("beauty_ai_session_id") 
    if (storedSessionId !== null && storedSessionId.trim() !== ""){
      return storedSessionId 
    }else {
      return crypto.randomUUID()
    }
  })
  const requestRef = useRef(false)


  useEffect(() => {

  localStorage.setItem("beauty_ai_session_id",sessionId)
  
},[sessionId])




function handleInputChange(newValue) {
    setInput(newValue)
  }

 async function handleSubmit(){

  const submittedMessage = input.trim()
   if (submittedMessage === "") {
     return
   }
   if (sessionId.trim() === ""){return

   }

   if (requestRef.current){
     return
    }
    requestRef.current = true
try{
  setError("")
  const newMessage = {
  id: crypto.randomUUID(),
  role: "user",
  content: submittedMessage
  }


  setMessages(prevMessages => [...prevMessages,newMessage])
  setInput("")
  setLoading(true)

  const answer = await sendMessage(sessionId,submittedMessage)

  const assistantMessage = {
    id: crypto.randomUUID(),
    role: "assistant",
    content: answer
  }
  setMessages(prevMessages => [...prevMessages,assistantMessage])
}catch(err){
  if (err.code === "invalid_request") { setError("输入内容存在问题，请检查后重新提交。")}
  else if (err.code === "service_unavailable") { setError("AI 服务暂时不可用，请稍后再试。")}
  else if (err.code === "internal_error") { setError("系统处理时出现异常，请重新尝试。")}
  else if (err.code === "network_error") { setError("网络连接失败，请检查网络或稍后重试。")}
  else if (err.code === "invalid_response") { setError("服务返回异常，请稍后重试。")}
  else { setError("请求失败，请稍后重试。")}
  setInput(prevInput => {if (prevInput === ""){
    return submittedMessage}else{ return prevInput}})
}
finally{
setLoading(false)
requestRef.current = false
}
 }
function handleNewConversation(){
  if (loading || requestRef.current) {
    return
  }
  const newid = crypto.randomUUID()
  setSessionId(newid)
  setMessages([])
  setInput("")
  setError("")
}


  return (
    <div className="app-shell">
      <Header onNewConversation = {handleNewConversation} 
      loading = {loading} />
      <MessageList messages = {messages} />
      {loading && (
        <p className="loading-message">正在回答… </p>
        )}
      {error && (<p className="error-message">{error}</p>)}
    
      <ChatInput input = {input}
      onInputChange = {handleInputChange} 
      onSend = {handleSubmit}
      loading= {loading} />

     
    </div>
  )
}
export default App
