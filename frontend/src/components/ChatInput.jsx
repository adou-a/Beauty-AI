function ChatInput({input,onInputChange, onSend}){
    return(
        <div>
            <input placeholder="请输入你的问题" 
            value = {input} 
            onChange={(event) => onInputChange(event.target.value)}/>
            <button onClick = {onSend}>发送</button>
        </div>
    )
}

export default ChatInput