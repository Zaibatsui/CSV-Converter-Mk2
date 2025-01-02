### README

# File Upload and Reformat Tool

This is a simple web-based tool that allows you to upload data files, rearrange columns, and download a cleaned-up, organized version of the file. It is designed to be user-friendly and works with common file types like Excel and CSV.

---

## Features

- **File Upload:** Upload files in formats such as Excel (.xls, .xlsx) or text (.csv, .txt).
- **Column Rearrangement:** Reorder columns to match your preferred structure or a standard format.
- **Header Renaming:** Optionally rename column headers to align with a predefined format.
- **Custom Output:** Choose the delimiter (comma or tab) and file extension for the output.
- **Secure Processing:** Files are handled securely and temporarily stored only for processing.

---

## How It Works

1. **Upload Your File:**
   - Go to the homepage.
   - Choose the file you want to upload (supported formats: `.csv`, `.txt`, `.xls`, `.xlsx`).

2. **View and Organize:**
   - The tool will display the headers of your file.
   - You can reorder the columns or rename them as needed.

3. **Download the File:**
   - Once you’re done, download the reformatted file in your chosen format (e.g., `.csv` or `.txt`).

---

## Requirements

### For Running Locally:
- Python 3.7+
- Flask
- Pandas
- Werkzeug

### Installation:
1. Clone or download this repository.
2. Install required Python libraries:
   ```bash
   pip install flask pandas
   ```

---

## Running the Application

1. Open your terminal.
2. Navigate to the directory where the script is located.
3. Run the application:
   ```bash
   python app.py
   ```
4. Open your browser and go to `http://127.0.0.1:5000/`.

---

## Customization

- **Upload Folder:** Files are temporarily stored in `C:/Users/zaiba/Downloads/tempupload` by default. You can change this path in the code (`UPLOAD_FOLDER` variable).
- **Allowed File Types:** Supported file extensions are `.csv`, `.txt`, `.xls`, and `.xlsx`. You can modify the allowed extensions by updating the `ALLOWED_EXTENSIONS` variable.
- **Netset Standard Format:** The predefined headers for the Netset format are stored in `NETSET_HEADERS`. Adjust this list as needed.

---

## Troubleshooting

- **"No file part" error:** Make sure to select a file before submitting.
- **"File not found" error:** Ensure the file is properly uploaded and hasn't been moved or deleted.
- **Headers not displayed:** Check that your file contains headers and is in a supported format.

---

## License

This project is open-source and available for modification and distribution. Use it freely to fit your needs.

---

## Support

If you encounter any issues or have questions, feel free to reach out by submitting an issue or contacting the developer.
