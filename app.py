import os
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory
from livereload import Server
from werkzeug.utils import secure_filename  # IMPORTANTE

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
app.config['OUTPUT_FOLDER'] = 'outputs'
ALLOWED_EXTENSIONS = {'xml'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

archive = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_multi():
    # name="files" no input
    files = request.files.getlist('files')
    if not files:
        return jsonify(error='Nenhum arquivo'), 400

    saved = []
    for f in files:
        if not f or f.filename == '':
            continue
        if not allowed_file(f.filename):
            return jsonify(error=f'Extensão não permitida: {f.filename}'), 400

        filename = secure_filename(f.filename)
        # Evita colisão de nomes
        base, ext = os.path.splitext(filename)
        unique_name = f"{base}_{uuid.uuid4().hex[:8]}{ext}"
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_name))
        saved.append(unique_name)

    if not saved:
        return jsonify(error='Nenhum arquivo válido para salvar'), 400

    archive.append({unique_name, len(saved)})
    convert_archive()
    return jsonify(ok=True, saved=saved, count=len(saved))

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.errorhandler(413)
def too_large(e):
    return jsonify(error='Arquivo muito grande (413)'), 413

def convert_archive():
    print("convertido")
    print(archive[0])

if __name__ == '__main__':
    server = Server(app.wsgi_app)
    server.watch('templates/')
    server.watch('static/')
    server.serve(port=5500, debug=True)
    