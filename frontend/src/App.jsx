
//把App.css的样式加载到当前前端应用里
import './App.css'
import Header from './components/Header'
import ChatInput from './components/ChatInput'
import MessageList from './components/MessageList'
import { useState, useEffect ,useRef} from 'react'
// Restore the real API after testing by changing this import to './api/chat'.
import { sendMessage } from './api/chat.mock'

function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [sessionId, setSessionId] = useState(()=>{
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
  setError(err.message)
  setInput(prevInput => {if (prevInput === ""){
    return submittedMessage}else{ return prevInput}})
}
finally{
setLoading(false)
requestRef.current = false
}
 }



  return (
    <div>
      <Header />
      <MessageList messages = {messages} />
      <ChatInput input = {input}
      onInputChange = {handleInputChange} 
      onSend = {handleSubmit}/>

     
    </div>
  )
}
export default App
