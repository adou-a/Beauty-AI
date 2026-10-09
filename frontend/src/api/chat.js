

export async function sendMessage(sessionId,message) {
    const requestBody = JSON.stringify({
        session_id: sessionId,
        message: message
    })
    let response
    try{
     response = await fetch("http://localhost:8000/agent/chat/",
         { 
         method: "POST",
         headers: { "Content-Type": "application/json" },
         body: requestBody
        }
    )



    } catch (error) {
        const networkError = new Error("Network request failed")
        networkError.status = null
        networkError.code = "network_error"

        throw networkError
    }
    let data
    try{
    data = await response.json()}
    catch(error){
        const parseError = new Error("Invalid JSON response")
        parseError.status = response.status
        parseError.code = "invalid_response"
        throw parseError
    }


    if  (response.ok){
        if(
            data === null || typeof data !== "object" || typeof data.answer !== "string"
        ){
            const contractError = new Error("Invalid answer response")
            contractError.status = response.status
            contractError.code = "invalid_response"
            throw contractError
        }
        return data.answer
    }
    
    else{
        const error = new Error(data.message)
        error.status = response.status
        error.code = data.code
        throw error
        
        
    }
        
}