document.addEventListener("DOMContentLoaded", () => {
    // Chatbot elements
    const chatbotToggle = document.getElementById("chatbotToggle")
    const chatbotContainer = document.getElementById("chatbotContainer")
    const chatbotMinimize = document.getElementById("chatbotMinimize")
    const chatbotMessages = document.getElementById("chatbotMessages")
    const chatbotInput = document.getElementById("chatbotInput")
    const chatbotSend = document.getElementById("chatbotSend")
    const chatbotSuggestions = document.getElementById("chatbotSuggestions")
  
    // Toggle chatbot visibility
    chatbotToggle.addEventListener("click", () => {
      chatbotContainer.classList.add("active")
      chatbotInput.focus()
    })
  
    // Minimize chatbot
    chatbotMinimize.addEventListener("click", () => {
      chatbotContainer.classList.remove("active")
    })
  
    // Send message on button click
    chatbotSend.addEventListener("click", () => {
      sendMessage()
    })
  
    // Send message on Enter key
    chatbotInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        sendMessage()
      }
    })
  
    // Handle suggestion buttons
    chatbotSuggestions.addEventListener("click", (e) => {
      if (e.target.classList.contains("suggestion-btn")) {
        const question = e.target.getAttribute("data-question")
        chatbotInput.value = question
        sendMessage()
      }
    })
  
    // Function to send message
    function sendMessage() {
      const message = chatbotInput.value.trim()
  
      if (message) {
        // Add user message to chat
        addMessage(message, "user")
  
        // Clear input
        chatbotInput.value = ""
  
        // Get bot response
        getBotResponse(message)
      }
    }
  
    // Function to add message to chat
    function addMessage(message, sender) {
      const messageElement = document.createElement("div")
      messageElement.classList.add("message", `${sender}-message`)
  
      const messageContent = document.createElement("div")
      messageContent.classList.add("message-content")
      messageContent.textContent = message
  
      messageElement.appendChild(messageContent)
      chatbotMessages.appendChild(messageElement)
  
      // Scroll to bottom
      chatbotMessages.scrollTop = chatbotMessages.scrollHeight
    }
  
    // Function to add bot action buttons
    function addBotActionButtons(actions) {
      const lastBotMessage = chatbotMessages.querySelector(".bot-message:last-child")
  
      if (lastBotMessage) {
        const actionButtons = document.createElement("div")
        actionButtons.classList.add("bot-action-buttons")
  
        actions.forEach((action) => {
          const button = document.createElement("button")
          button.classList.add("bot-action-button")
          button.textContent = action.text
          button.addEventListener("click", () => {
            window.location.href = action.url
          })
  
          actionButtons.appendChild(button)
        })
  
        lastBotMessage.appendChild(actionButtons)
      }
    }
  
    // Function to get bot response
    function getBotResponse(message) {
      // Show typing indicator
      addMessage("Typing...", "bot")
  
      // Send request to server
      fetch("/chatbot/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: message }),
      })
        .then((response) => response.json())
        .then((data) => {
          // Remove typing indicator
          chatbotMessages.removeChild(chatbotMessages.lastChild)
  
          // Add bot response
          addMessage(data.answer, "bot")
  
          // Add action buttons based on response type
          if (data.type === "book") {
            addBotActionButtons([{ text: "View Book", url: `/books/view/${data.book_id}` }])
          } else if (data.type === "profile") {
            addBotActionButtons([{ text: "Go to Profile", url: "/auth/profile" }])
          } else if (data.type === "browse") {
            addBotActionButtons([{ text: "Browse Books", url: "/books" }])
          } else if (data.type === "login") {
            addBotActionButtons([{ text: "Login", url: "/auth/login" }])
          }
        })
        .catch((error) => {
          // Remove typing indicator
          chatbotMessages.removeChild(chatbotMessages.lastChild)
  
          // Add error message
          addMessage("Sorry, I encountered an error. Please try again later.", "bot")
          console.error("Error:", error)
        })
    }
  })
  