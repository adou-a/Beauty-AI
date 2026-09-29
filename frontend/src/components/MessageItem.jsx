function MessageItem({role, content}){
    return(
        <div>{role === "user" ? "用户" : "Beauty-AI"}：{content}</div>
    )
}

export default MessageItem