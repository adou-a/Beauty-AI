function ChatInput({input,onInputChange, onSend,loading}){
    return(
        <div
        className="chat-input">
            <input placeholder="请输入你的问题" 
            value = {input} 
            onChange={(event) => onInputChange(event.target.value)}/>
            <button onClick = {onSend} disabled = {loading}>发送
                
            </button>
        </div>
    )
}

export default ChatInput