from handler.chatgpt_selenium_automation import ChatGPTAutomation

# Create an instance
chatgpt = ChatGPTAutomation()

chatgpt.get_conversations_list()

chat_id = input("chat number:")

if chat_id == 0:
    print("Starting new chat")
else:
    chatgpt.select_conversation(int(chat_id))
    response = chatgpt.return_last_response()
    print("ai: {", response, "}")
    print("===========================")

while True:
    # Define a prompt and send it to chatGPT
    prompt = input("me: ")
    
    if prompt == 'q':
        break

    chatgpt.send_prompt_to_chatgpt(prompt)

    # Retrieve the last response from chatGPT
    response = chatgpt.return_last_response()
    print("ai: {", response, "}")
    print("===========================")

# Save the conversation to a text file
file_name = "conversation.txt"
chatgpt.save_conversation(file_name)

# Close the browser and terminate the WebDriver session
chatgpt.quit()
