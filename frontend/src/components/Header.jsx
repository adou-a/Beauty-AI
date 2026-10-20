function Header({onNewConversation,loading}){
    return (
        <div className="app-header">
            <header>Beauty-AI</header>
            <button onClick={onNewConversation} disabled = {loading}>新建对话</button>
        </div>
    )
}

export default Header