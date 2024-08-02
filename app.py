from flask import Flask, request, render_template, redirect, url_for, send_file, jsonify
import os, re
import uuid
import zipfile
from whatsapp_chat_viewer import parse_chat, get_chat_preview

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024 #2gb?
app.config['UPLOAD_FOLDER'] = 'temp'

#keep current html as var
current_file_dir = "" 
error_message = "" 

def load_default_html(html):
    with open('temp.html', 'r') as file:
        return file.read()


@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/error')
def show_error():
    global error_message
    return render_template('error.html', error_msg=error_message)


@app.route('/upload', methods=['POST'])
def upload_file():
    
    global current_file_dir, error_message
    
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
            error_message = "uploading the file"
            return redirect(url_for('show_error'))
    
    return redirect(url_for('show_parsing_settings'))
            
        
@app.route('/settings')
def show_parsing_settings():
    
    global current_file_dir
    chat_preview = get_chat_preview(current_file_dir)
    
    return render_template('settings.html', preview=chat_preview)
        
        
   
@app.route('/parsing', methods=['POST'])
def parse_file():     
    
    global error_message, current_file_dir
    
    me = request.values.get('me', '')
    attachment = request.values.get('attachment', 'Attachment')
    
    print(f"from route me: {me}")
    print(f"from route attachment_term: {attachment}")
    
    # parsing happens here; after settings have been set
    # loading bar for parsing happens in js / html
    
    if not parse_chat(current_file_dir, me, attachment):
        error_message = "parsing the message"
        return redirect(url_for('show_error'))
    else:
        return redirect(url_for('download_parsed'))

        
@app.route('/download')
def download_parsed():
    
    current_working_directory = os.getcwd()
    
    path = os.path.join(current_working_directory, current_file_dir)
    
    return render_template('download.html', current_dir=path)



        
@app.route('/view')
def view_chat():
    return render_template(f'{current_file_dir}/index.html')
        
if __name__ == '__main__':
    app.run(debug=True)