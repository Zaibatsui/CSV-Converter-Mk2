from flask import Flask, request, render_template, session, send_file, flash, send_from_directory
import pandas as pd
import os
import uuid
import csv
from werkzeug.utils import secure_filename

app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory("static", "favicon.ico", mimetype="image/vnd.microsoft.icon")

app.secret_key = os.urandom(24)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'txt', 'xls', 'xlsx'}
NETSET_HEADERS = ['SKU', 'Part no', 'Manufacturer', 'Description', 'Price', 'Quantity', 'Weight', 'EAN', 'Condition', 'Cat1', 'Cat2', 'min sales qty']
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def sniff_delimiter(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        sample = f.read(2048)
        try:
            return csv.Sniffer().sniff(sample).delimiter
        except csv.Error:
            return ','  # Default to comma if detection fails

def get_file_headers(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext in ['.csv', '.txt']:
            delimiter = sniff_delimiter(file_path)
            df = pd.read_csv(file_path, encoding='utf-8', sep=delimiter)
        elif ext in ['.xls', '.xlsx']:
            df = pd.read_excel(file_path, engine="openpyxl")
        return df.columns.tolist()
    except (UnicodeDecodeError, ValueError):
        try:
            if ext in ['.csv', '.txt']:
                delimiter = sniff_delimiter(file_path)
                df = pd.read_csv(file_path, encoding='iso-8859-1', sep=delimiter)
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
            return render_template('upload.html', headers=None, session_key=None)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'error')
            return render_template('upload.html', headers=None, session_key=None)

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
            return render_template('upload.html', headers=None, session_key=None)

        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext in ['.csv', '.txt']:
                detected_delimiter = sniff_delimiter(file_path)
                df = pd.read_csv(file_path, sep=detected_delimiter, encoding='utf-8')
            else:
                df = pd.read_excel(file_path)
        except (UnicodeDecodeError, ValueError):
            try:
                df = pd.read_csv(file_path, sep=sniff_delimiter(file_path), encoding='iso-8859-1')
            except Exception:
                flash('Error: Unable to decode the file', 'error')
                return render_template('upload.html', headers=None, session_key=session_key)

        order = [col.strip() for col in new_order.split(',')]
        existing_columns = df.columns.tolist()

        new_columns = {}
        current_blank_column = 1

        for col in order:
            if col == '*':
                new_columns[f'*_{current_blank_column}'] = [''] * len(df)
                current_blank_column += 1
            elif col in existing_columns:
                new_columns[col] = df[col]
            else:
                new_columns[col] = [''] * len(df)

        new_df = pd.DataFrame(new_columns)

        if rename_headers:
            if len(order) >= len(NETSET_HEADERS):
                new_df.columns = NETSET_HEADERS
            else:
                flash('Not enough columns specified for Netset format. Please add more columns or disable the option.', 'error')
                return render_template('upload.html', headers=existing_columns, session_key=session_key)

        delimiter_char = ',' if delimiter == 'comma' else '\t'
        new_file_path = os.path.join(UPLOAD_FOLDER, f'{session_key}_output.{extension}')
        new_df.to_csv(new_file_path, index=False, sep=delimiter_char)

        return send_file(new_file_path, as_attachment=True, download_name=f'output.{extension}')

    return 'Invalid order input'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
