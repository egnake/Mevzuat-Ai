"""
Mevzuat-AI Flask Application
Generated and Developed by Ege Parlak (egnake)
"""

import os
# Suppress TensorFlow logging and OneDNN warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import warnings
# Suppress deprecation and other warnings
warnings.filterwarnings('ignore')

import tempfile
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

from rag_engine import ingest_documents, query_rag, get_system_info

# FLASK APP SETUP

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()

ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ROUTES - PAGES

@app.route('/')
def index():
    """Serve the main application page."""
    return render_template('index.html')


# ROUTES - API

@app.route('/api/upload', methods=['POST'])
def upload_files():
    """Handle PDF file uploads."""
    if 'files' not in request.files:
        return jsonify({'success': False, 'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    
    if not files or files[0].filename == '':
        return jsonify({'success': False, 'error': 'No files selected'}), 400
    
    uploaded_files = []
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_name = f"{uuid.uuid4().hex}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
            file.save(filepath)
            uploaded_files.append({
                'path': filepath,
                'filename': filename,
                'size': os.path.getsize(filepath)
            })
    
    if not uploaded_files:
        return jsonify({'success': False, 'error': 'No valid PDF files'}), 400
    
    return jsonify({
        'success': True,
        'files': [{'name': f['filename'], 'size': f['size']} for f in uploaded_files],
        'paths': [f['path'] for f in uploaded_files],
        'filenames': [f['filename'] for f in uploaded_files]
    })


@app.route('/api/analyze', methods=['POST'])
def analyze_documents():
    """Analyze uploaded PDF documents."""
    data = request.get_json()
    
    if not data or 'files' not in data:
        return jsonify({'success': False, 'error': 'No file info provided'}), 400
    
    pdf_files = []
    for i, path in enumerate(data['files']):
        pdf_files.append({
            'path': path,
            'filename': data.get('filenames', ['document.pdf'])[i] if i < len(data.get('filenames', [])) else 'document.pdf'
        })
    
    try:
        num_chunks = ingest_documents(pdf_files)
        return jsonify({
            'success': True,
            'chunks': num_chunks,
            'message': f'{num_chunks} metin parçası başarıyla indekslendi.'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat/query requests."""
    data = request.get_json()
    
    if not data or 'question' not in data:
        return jsonify({'success': False, 'error': 'No question provided'}), 400
    
    question = data['question'].strip()
    
    if not question:
        return jsonify({'success': False, 'error': 'Empty question'}), 400
    
    try:
        result = query_rag(question)
        return jsonify({
            'success': True,
            'answer': result['answer'],
            'sources': result['sources']
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/system-info', methods=['GET'])
def system_info():
    """Get system configuration info."""
    try:
        info = get_system_info()
        return jsonify({'success': True, **info})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# MAIN

if __name__ == '__main__':
    # Ensure directories exist
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    print("\n" + "="*60)
    print("🏛️  Mevzuat-AI - Turkish Legal Assistant")
    print("="*60)
    print(f"📍 Server running at: http://localhost:5000")
    print(f"📁 Upload folder: {app.config['UPLOAD_FOLDER']}")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
