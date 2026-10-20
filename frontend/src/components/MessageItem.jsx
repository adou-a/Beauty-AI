function MessageItem({role, content}){
    return(
        <div className={role === "user" ? "user-message": "assistant-message"}
        
        
        >{role === "user" ? "用户" : "Beauty-AI"}:{content}
        
        
        </div>
    )
}

export default MessageItem