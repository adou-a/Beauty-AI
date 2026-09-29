import MessageItem from "./MessageItem";

function MessageList({messages}){

    return(
        <div>
            {messages.length === 0 ? <div> 你好，我是Beauty-AI。 </div>:
        messages.map((message) => {
            return(
                <MessageItem
                 key = {message.id}
                 role = {message.role}
                 content = {message.content}
                 />
                  
                   
            )
        })}
        </div>
    )
}

export default MessageList