from flask import Flask, request, render_template, redirect, url_for, send_file, jsonify
import os, re
import uuid
import zipfile
from whatsapp_chat_viewer import parse_chat, get_chat_preview

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
    
    return redirect(url_for('show_parsing_settings'))
            
        
@app.route('/settings')
def show_parsing_settings():
    
    global current_file_dir
    chat_preview = get_chat_preview(current_file_dir)
    
    return render_template('settings.html', preview=chat_preview)
        
        
   
@app.route('/parsing', methods=['POST'])
def parse_file():     
    
    me = request.form.get('me', '')
    attachment = request.form.get('attachment', 'Attachment')
    
    print(f"me: {me}")
    print(f"attachment: {attachment}")
    
    global current_file_dir
    
    # parsing happens here; after settings have been set
    # loading bar for parsing happens in js / html
    
    if not parse_chat(current_file_dir, me, attachment):
        return redirect(url_for('show_error'))
    else:
        return redirect(url_for('download_parsed'))

        
@app.route('/download')
def download_parsed():
    return render_template('download.html', current_dir=current_file_dir)
        
if __name__ == '__main__':
    app.run(debug=True)