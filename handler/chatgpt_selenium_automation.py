from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
import time
import socket
import threading
import os



class ChatGPTAutomation:

    def __init__(self, chrome_path="chromium", chrome_driver_path="chromedriver"):
        """
        This constructor automates the following steps:
        1. Open a Chrome browser with remote debugging enabled at a specified URL.
        2. Prompt the user to complete the log-in/registration/human verification, if required.
        3. Connect a Selenium WebDriver to the browser instance after human verification is completed.

        :param chrome_path: file path to chrome.exe (ex. C:\\Users\\User\\...\\chromedriver.exe)
        :param chrome_driver_path: file path to chrome.exe (ex. C:\\Users\\User\\...\\chromedriver.exe)
        """

        self.chrome_path = chrome_path
        self.chrome_driver_path = chrome_driver_path

        url = r"https://chat.openai.com"
        free_port = self.find_available_port()
        self.launch_chrome_with_remote_debugging(free_port, url)
        self.wait_for_human_verification()
        self.driver = self.setup_webdriver(free_port)



    def find_available_port(self):
        """ This function finds and returns an available port number on the local machine by creating a temporary
            socket, binding it to an ephemeral port, and then closing the socket. """

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]



    def launch_chrome_with_remote_debugging(self, port, url):
        """ Launches a new Chrome instance with remote debugging enabled on the specified port and navigates to the
            provided url """

        def open_chrome():
            chrome_cmd = f"{self.chrome_path} --remote-debugging-port={port} --user-data-dir=remote-profile {url}"
            os.system(chrome_cmd)

        chrome_thread = threading.Thread(target=open_chrome)
        chrome_thread.start()



    def setup_webdriver(self, port):
        """  Initializes a Selenium WebDriver instance, connected to an existing Chrome browser
             with remote debugging enabled on the specified port"""

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
        driver = webdriver.Chrome(executable_path=self.chrome_driver_path, options=chrome_options)
        return driver



    def send_prompt_to_chatgpt(self, prompt):
        """ Sends a message to ChatGPT and waits for 20 seconds for the response """

        input_box = self.driver.find_element(by=By.XPATH, value='//textarea[contains(@placeholder, "Send a message")]')
        input_box.clear()  # Clear the input box first
        for char in prompt:
            input_box.send_keys(char)
        #self.driver.execute_script(f"arguments[0].value = '{prompt}';", input_box)
        time.sleep(1)
        input_box.submit()
        #input_box.send_keys(Keys.RETURN)


    def return_chatgpt_conversation(self):
        """
        :return: returns a list of items, even items are the submitted questions (prompts) and odd items are chatgpt response
        """

        return self.driver.find_elements(by=By.CSS_SELECTOR, value='div.text-base')



    def save_conversation(self, file_name):
        """
        It saves the full chatgpt conversation of the tab open in chrome into a text file, with the following format:
            prompt: ...
            response: ...
            delimiter
            prompt: ...
            response: ...

        :param file_name: name of the file where you want to save
        """

        directory_name = "conversations"
        if not os.path.exists(directory_name):
            os.makedirs(directory_name)

        delimiter = "|^_^|"
        chatgpt_conversation = self.return_chatgpt_conversation()
        with open(os.path.join(directory_name, file_name), "a") as file:
            for i in range(0, len(chatgpt_conversation), 2):
                file.write(
                    f"prompt: {chatgpt_conversation[i].text}\nresponse: {chatgpt_conversation[i + 1].text}\n\n{delimiter}\n\n")



    def wait_for_response(self):
        """Waits for the response to complete by waiting for the 'Stop generating' button to disappear"""

        response_elements = []
        last_msg = None

        # wait for the start of response
        while not response_elements  or last_msg.strip() == "":
            time.sleep(1)
            response_elements = self.driver.find_elements(by=By.CSS_SELECTOR, value='div.text-base')
            if not response_elements:
                continue
            last_msg = response_elements[-1].text

        # wait for the "Stop generating button to disapear
        stop_generating_button = self.driver.find_elements(by=By.XPATH, value='//button[contains(text(), "Stop generating")]')
        while stop_generating_button:
            time.sleep(1)
            stop_generating_button = self.driver.find_elements(by=By.XPATH, value='//button[contains(text(), "Stop generating")]')

        last_msg2 = None
        while last_msg != last_msg2:
            last_msg2 = last_msg
            time.sleep(2)
            last_msg = response_elements[-1].text



    def return_last_response(self):
        """ :return: the text of the last chatgpt response """

        self.wait_for_response()
        response_elements = self.driver.find_elements(by=By.CSS_SELECTOR, value='div.text-base')
        return response_elements[-1].text



    def wait_for_human_verification(self):
        print("You need to manually complete the log-in or the human verification if required.")

        while True:
            user_input = input(
                "Enter 'y' if you have completed the log-in or the human verification, or 'n' to check again: ").lower()

            if user_input == 'y':
                print("Continuing with the automation process...")
                break
            elif user_input == 'n':
                print("Waiting for you to complete the human verification...")
                time.sleep(5)  # You can adjust the waiting time as needed
            else:
                print("Invalid input. Please enter 'y' or 'n'.")



    def get_conversations_list(self):
        """Returns a list of conversations displayed on the left side"""

        #conversation_elements = self.driver.find_elements(by=By.CSS_SELECTOR, value='div.conversation')
        chat_elements = self.driver.find_elements(by=By.XPATH, value='//li[contains(@class, "relative")]')

        for i, element in enumerate(chat_elements, 1):
            title_element = element.find_element(by=By.CSS_SELECTOR, value='div.flex-1')
            print(i, ":", title_element.text)


    def select_conversation(self, chat_id):
        """Selects a chat conversation by clicking on it based on the chat_id"""

        chat_elements = self.driver.find_elements(by=By.XPATH, value='//li[contains(@class, "relative")]')
        if chat_id > 0 and chat_id <= len(chat_elements):
            chat_elements[chat_id - 1].click()
        else:
            print("Invalid chat_id provided")


    def quit(self):
        """ Closes the browser and terminates the WebDriver session."""
        print("Closing the browser...")
        self.driver.close()
        self.driver.quit()




