import os
from flask import Blueprint, render_template, request, current_app, redirect , send_file, session, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
from .forms import LoginForm

main = Blueprint('main', __name__)

@main.route('/home')
@login_required
def home():
    form = LoginForm()
    error2 = "Welcome, " + current_user.name + "!"
    # List to hold file data
    files = []
    # Get the upload folder path from the config
    upload_folder = current_app.config['UPLOAD_FOLDER']
    # Loop through files in the upload folder and collect metadata
    for file in os.listdir(upload_folder):
        file_path = os.path.join(upload_folder, file)
        file_size = os.path.getsize(file_path)
        file_type = file.split('.')[-1]
        uploaded_at = datetime.fromtimestamp(os.path.getmtime(file_path))

        files.append({
            'filename': file,
            'uploaded_at': uploaded_at,
            'file_type': file_type,
            'file_size': file_size
        })
    return render_template('home.html', name=current_user.name, form=form, files=files, error2=error2)

@main.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        # Get the upload folder from app config
        upload_folder = current_app.config['UPLOAD_FOLDER']
        # Save the file
        f.save(os.path.join(upload_folder, secure_filename(f.filename)))
        # Flash success message
        flash('File uploaded successfully!', 'success')
        # Redirect back to homepage with the new file list
        return redirect(url_for('main.home'))
    return render_template('upload.html')

@main.route("/delete", methods=['POST'])
def delete_file():
    choose = request.form['choose']
    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], choose))
    return redirect("http://127.0.0.1:5000/home", code=302)

@main.route('/download', methods=['GET', 'POST'])
def download_file():
    filename = request.form.get('filename')
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    return send_file(file_path, as_attachment=True)