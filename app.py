from flask import Flask, render_template, request, send_file
import os
import zipfile
import subprocess
import shutil

# ------------------------------
# 1. Create Flask app
# ------------------------------
app = Flask(__name__)

# ------------------------------
# 2. Home page
# ------------------------------
@app.route('/')
def index():
    return render_template('index.html')

# ------------------------------
# 3. Download route
# ------------------------------
@app.route('/download', methods=['POST'])
def download_website():
    url = request.form.get('url')
    if not url:
        return "Missing URL", 400

    folder = "site_download"
    zip_path = "website.zip"

    # clean old files
    if os.path.exists(folder):
        shutil.rmtree(folder)
    if os.path.exists(zip_path):
        os.remove(zip_path)

    try:
        # Run wget mirror command
        cmd = [
            "wget", "-E", "-H", "-k", "-p", "-nd",
            "-P", folder, url
        ]
        subprocess.run(cmd, check=True, timeout=60)

        # Create ZIP
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder):
                for file in files:
                    path = os.path.join(root, file)
                    arcname = os.path.relpath(path, folder)
                    zipf.write(path, arcname)

        return send_file(zip_path, as_attachment=True)

    except subprocess.TimeoutExpired:
        return "Download timed out (site too large or slow).", 500
    except Exception as e:
        return f"Error: {e}", 500


# ------------------------------
# 4. Run app
# ------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
