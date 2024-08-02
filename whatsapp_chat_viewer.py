import os, re

def parse_chat(current_file_dir, me="", attachment_term="Attachment"):
    
    if os.path.isdir(current_file_dir):
        if os.path.isfile(os.path.join(current_file_dir, "_chat.txt")):
            chat_txt = os.path.join(current_file_dir, "_chat.txt")
    else:
        # contains no _chat.txt
        # return redirect(url_for('show_error'))
        # returns shouldn handle anything about flask in here; as this is just the module; ill react to the false inside app
        return False
    
    chat_messages = []

    print(f"me: {me}")
    print(f"attachment_term: {attachment_term}")

    with open(chat_txt, "r", encoding="utf-8") as file:
        
        for line in file:
            
            match = re.match(r"\[(\d{2}.\d{2}.\d{2}, \d{1,2}:\d{2}:\d{2}\s[AP]M)\] (.*?): (.*)", line)
            if match:
                timestamp, sender, message = match.groups()
                chat_messages.append((timestamp, sender, message))



    html_content = ""
    temp = 0

    for timestamp, sender, message in chat_messages:
        
        if temp < 10:
            print(f"sender: {sender}")
        
        temp += 1
        
        html_content += "<div class=\"message_container\">"
        
        if(sender == me):
            html_content += f"<div class=\"message own\"><div>{sender}:</div><div>{message}"
        else:
            html_content += f"<div class=\"message\"><div>{sender}:</div><div>{message}"

        attachments = re.findall(fr"<{attachment_term}: (.*?)>", message)
        for attachment in attachments:
            attachment_path = os.path.join(current_file_dir, attachment)
            html_content += f'<br><a target="_blank" href="{attachment_path}"><img src="{attachment_path}" alt="Attachment">'

        html_content += f"</div><div>{timestamp}</div></div></div>"
    
    # replace with ٩(｡•́‿•̀｡)۶
    build_html(html_content, current_file_dir)
    return True
        
        
        
def get_chat_preview(current_file_dir):

    print(current_file_dir)
    
    if os.path.isdir(current_file_dir):
        if os.path.isfile(os.path.join(current_file_dir, "_chat.txt")):
            chat_txt = os.path.join(current_file_dir, "_chat.txt")
    else:
        # contains no _chat.txt
        # return redirect(url_for('show_error'))
        # returns shouldn handle anything about flask in here; as this is just the module; ill react to the false inside app
        return False
    
    with open(chat_txt, 'r', encoding='utf-8') as f:
        return f.read(3000)
    
    

def build_html(html_content, current_file_dir):
    
    html_start = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Chat</title>
        <style>
    """
    
    with open('static/chat.css', 'r') as css_file:
        css_content = css_file.read()
    
    html_end = """
        </style>
    </head>
    <body class="chat">
    """

    html_close = """
    </body>
    </html>
    """
    
    with open(os.path.join(current_file_dir, "index.html"), "w") as file:
        file.write(f"{html_start}\n{css_content}\n{html_end}\n{html_content}\n{html_close}")