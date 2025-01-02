from flask import Flask, request, render_template, session, send_file, flash, redirect, url_for
import pandas as pd
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Set a secret key for session management
app.secret_key = os.urandom(24)

# Define the upload folder and allowed extensions
UPLOAD_FOLDER = 'C:/Users/zaiba/Downloads/tempupload'  # Change to your desired upload folder
ALLOWED_EXTENSIONS = {'csv', 'txt', 'xls', 'xlsx'}

# Define Netset format headers
NETSET_HEADERS = ['SKU', 'Part no', 'Manufacturer', 'Description', 'Price', 'Quantity', 'Weight', 'EAN', 'Condition', 'Cat1', 'Cat2', 'min sales qty']

# Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_headers(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext in ['.csv', '.txt']:
            df = pd.read_csv(file_path, encoding='utf-8')
        elif ext in ['.xls', '.xlsx']:
            df = pd.read_excel(file_path)
        return df.columns.tolist()
    except (UnicodeDecodeError, ValueError) as e:
        try:
            if ext in ['.csv', '.txt']:
                df = pd.read_csv(file_path, encoding='iso-8859-1')
                return df.columns.tolist()
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            return None
    return None

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(url_for('upload_file'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(url_for('upload_file'))
        
        if file and allowed_file(file.filename):
            session_key = str(uuid.uuid4())
            session['session_key'] = session_key
            
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            session['file_path'] = file_path
            
            headers = get_file_headers(file_path)
            if headers:
                return render_template('upload.html', headers=headers, session_key=session_key)
            else:
                flash('Unable to read file headers', 'error')
                return redirect(url_for('upload_file'))
    
    return render_template('upload.html', headers=None, session_key=None)

@app.route('/reorder/<session_key>', methods=['POST'])
def reorder_file(session_key):
    new_order = request.form.get('new_order')
    delimiter = request.form.get('delimiter')
    extension = request.form.get('extension')
    rename_headers = request.form.get('rename_headers')
    
    if new_order:
        file_path = session.get('file_path')
        if not file_path:
            flash('File not found', 'error')
            return redirect(url_for('upload_file'))
        
        try:
            df = pd.read_excel(file_path)  # Updated to handle Excel files
        except (UnicodeDecodeError, ValueError) as e:
            try:
                df = pd.read_csv(file_path, encoding='iso-8859-1')
            except Exception as e:
                flash('Error: Unable to decode the file', 'error')
                return redirect(url_for('upload_file'))
        
        order = [col.strip() for col in new_order.split(',')]
        existing_columns = df.columns.tolist()
        
        new_columns = {}
        current_blank_column = 1
        
        for col in order:
            if col == '*':
                new_columns[f'*_{current_blank_column}'] = [''] * len(df)
                current_blank_column += 1
            else:
                if col in existing_columns:
                    new_columns[col] = df[col]
                else:
                    flash(f'Column "{col}" does not exist in the original file', 'error')
                    return redirect(url_for('upload_file'))
        
        new_df = pd.DataFrame(new_columns)
        
        if rename_headers:
            if len(order) >= len(NETSET_HEADERS):
                new_df.columns = NETSET_HEADERS
            else:
                flash('Not enough columns specified for Netset format. Please add more columns or disable the option.', 'error')
                return redirect(url_for('upload_file'))
        
        delimiter_char = ',' if delimiter == 'comma' else '\t'
        
        new_file_path = os.path.join(UPLOAD_FOLDER, f'{session_key}_output.{extension}')
        new_df.to_csv(new_file_path, index=False, sep=delimiter_char)
        
        return send_file(new_file_path, as_attachment=True, download_name=f'output.{extension}')
    
    flash('Invalid order input', 'error')
    return redirect(url_for('upload_file'))

if __name__ == '__main__':
    app.run(debug=True)
