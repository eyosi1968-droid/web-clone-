from flask import Flask, render_template, request, send_file
import os, zipfile, requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_website():
    url = request.form.get('url')
    if not url:
        return "Missing URL", 400

    folder = "site_download"
    if not os.path.exists(folder):
        os.mkdir(folder)

    try:
        response = requests.get(url, timeout=10)
        html_path = os.path.join(folder, "index.html")
        with open(html_path, "wb") as f:
            f.write(response.content)

        soup = BeautifulSoup(response.text, "html.parser")
        assets = []

        for tag in soup.find_all(["img", "script", "link"]):
            attr = "src" if tag.name in ["img", "script"] else "href"
            link = tag.get(attr)
            if link and not link.startswith("data:"):
                full_url = urljoin(url, link)
                assets.append(full_url)

        asset_folder = os.path.join(folder, "assets")
        os.makedirs(asset_folder, exist_ok=True)

        for link in assets[:30]:  # limit to avoid long downloads
            try:
                file_name = os.path.basename(link.split("?")[0])
                file_path = os.path.join(asset_folder, file_name)
                r = requests.get(link, timeout=5)
                with open(file_path, "wb") as f:
                    f.write(r.content)
            except:
                pass

        zip_path = "website.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(folder):
                for file in files:
                    filepath = os.path.join(root, file)
                    arcname = os.path.relpath(filepath, folder)
                    zipf.write(filepath, arcname)

        return send_file(zip_path, as_attachment=True)

    except Exception as e:
        return f"Error: {e}"
    finally:
        pass

if __name__ == '__main__':
    app.run(debug=True)
