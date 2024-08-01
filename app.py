from flask import Flask, request, render_template, redirect, url_for, send_file, jsonify
import os, re
import uuid
import zipfile

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024 #1gb?
app.config['UPLOAD_FOLDER'] = 'temp'

#keep current html as var
current_file_dir = "" 

def load_default_html(html):
    with open('temp.html', 'r') as file:
        return file.read()


@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/error')
def show_error():
    return render_template('error.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    
    global current_file_dir
    
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        return redirect(request.url)
    
    if file:
        
        
        file_uuid = str(uuid.uuid4())
        
        # creates working dir for parsing
        current_file_dir = os.path.join(app.config['UPLOAD_FOLDER'], file_uuid)
        os.makedirs(current_file_dir, exist_ok=True)
        
        
        if zipfile.is_zipfile(file):
        
            # extracts contents of the zip into filedir
            with zipfile.ZipFile(file, 'r') as zip_ref:
                zip_ref.extractall(current_file_dir)
            
        elif file.filename.lower().endswith(('.txt')):
            # saves txt into path
            file.save(os.path.join(current_file_dir, "_chat.txt"))
            
        else:
            return redirect(url_for('show_error'))
    
    
    # handle loading bar / parsing progress in js / html
    parse_ws_archive()
    return redirect(url_for('download_parsed'))
            
        
        
def parse_ws_archive():
    
    global current_file_dir
    
    if os.path.isdir(current_file_dir):
        if os.path.isfile(os.path.join(current_file_dir, "_chat.txt")):
            chat_txt = os.path.join(current_file_dir, "_chat.txt")
    else:
        # contains no _chat.txt
        return redirect(url_for('show_error'))
    
    chat_messages = []


    with open(chat_txt, "r", encoding="utf-8") as file:
        
        for line in file:
            
            match = re.match(r"\[(\d{2}.\d{2}.\d{2}, \d{1,2}:\d{2}:\d{2}\s[AP]M)\] (.*?): (.*)", line)
            if match:
                timestamp, sender, message = match.groups()
                chat_messages.append((timestamp, sender, message))



    html_content = ""

    for timestamp, sender, message in chat_messages:
        
        if(sender == "simon"):
            html_content += f"<div class=\"message own\"><div>{sender}:</div><div>{message}"
        else:
            html_content += f"<div class=\"message\"><div>{sender}:</div><div>{message}"

        attachments = re.findall(r"<Anhang: (.*?)>", message)
        for attachment in attachments:
            attachment_path = current_file_dir + attachment
            
            html_content += f'<br><a target="_blank" href="{attachment_path}"><img src="{attachment_path}" alt="Attachment">'

        html_content += f"</div><div>{timestamp}</div></div>"
        
        
    with open(os.path.join(current_file_dir, "index.html"), "w") as file:
        file.write(html_content)
        
    # at the end; redirect to the download page
    
    #
        
        
@app.route('/download')
def download_parsed():
    return render_template('download.html', current_dir=current_file_dir)
        
if __name__ == '__main__':
    app.run(debug=True)