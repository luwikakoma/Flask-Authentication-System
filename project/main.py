import os
from flask import Blueprint, render_template, request, current_app, redirect , send_file, session, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
from .forms import UploadFileForm, CreateFolderForm, DeleteFileForm, LoginForm

main = Blueprint('main', __name__)

@main.route('/home')
@login_required
def home():
    login_form = LoginForm()
    create_folder_form = CreateFolderForm()
    upload_file_form = UploadFileForm()
    delete_file_form = DeleteFileForm()
    error2 = "Welcome, " + current_user.name + "!"

    upload_folder = current_app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    folders = [folder for folder in os.listdir(upload_folder) if os.path.isdir(os.path.join(upload_folder, folder))]

    return render_template(
        'home.html',
        folders=folders,
        name=current_user.name,
        login_form=login_form,  # Pass login form
        create_folder_form=create_folder_form,  # Pass create folder form
        upload_file_form=upload_file_form,  # Pass upload file form
        delete_file_form=delete_file_form,
        error2=error2
    )

@main.route('/upload/<foldername>', methods=['GET', 'POST'])
def upload_file(foldername):
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part in the request', 'danger')
            return redirect(request.url)

        f = request.files['file']
        if f.filename == '':
            flash('No file selected for upload', 'warning')
            return redirect(request.url)

        # Ensure folder exists
        folder_path = os.path.join(current_app.config['UPLOAD_FOLDER'], foldername)
        os.makedirs(folder_path, exist_ok=True)

        # Save the file securely
        filename = secure_filename(f.filename)
        file_path = os.path.join(folder_path, filename)

        # Prevent overwriting by renaming if needed
        counter = 1
        while os.path.exists(file_path):
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{counter}{ext}"
            file_path = os.path.join(folder_path, filename)
            counter += 1

        f.save(file_path)
        flash('File uploaded successfully!', 'success')

        return redirect(url_for('main.view_folder', foldername=foldername))
    
    return render_template('upload.html', foldername=foldername)

# @main.route("/delete/<foldername>", methods=['POST'])
# def delete_file(foldername, filename):
#     """Delete a file from a specific folder."""
#     file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], foldername, filename)

#     if os.path.exists(file_path):
#         os.remove(file_path)
#         flash('File deleted successfully!', 'success')
#     else:
#         flash('File not found!', 'danger')

#     return redirect(url_for('main.view_folder', foldername=foldername))

# @main.route('/download/<foldername>', methods=['POST'])
# def download_file(foldername, filename):
#     """Download a file from a specific folder."""
#     file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], foldername, filename)

#     if os.path.exists(file_path):
#         return send_file(file_path, as_attachment=True)
#     else:
#         flash('File not found!', 'danger')
#         return redirect(url_for('main.view_folder', foldername=foldername))

# @main.route('/folder/<foldername>')
# def view_folder(foldername):
#     """List all files inside the selected folder."""
#     upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], foldername)

#     if not os.path.exists(upload_folder) or not os.path.isdir(upload_folder):
#         flash("Folder does not exist!", "danger")
#         return redirect(url_for('main.home'))

#     files = []
#     for file in os.listdir(upload_folder):
#         file_path = os.path.join(upload_folder, file)
#         if os.path.isfile(file_path):
#             files.append({
#                 'filename': file,
#                 'uploaded_at': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S'),
#                 'file_type': file.split('.')[-1],
#                 'file_size': os.path.getsize(file_path)
#             })

#     upload_file_form = UploadFileForm()
#     create_folder_form = CreateFolderForm()
#     delete_file_form = DeleteFileForm()

#     return render_template("folder.html", foldername=foldername,upload_file_form=upload_file_form,create_folder_form=create_folder_form, delete_file_form=delete_file_form, files=files)


@main.route('/create_folder', methods=['POST'])
def create_folder():
    form = CreateFolderForm()

    if form.validate_on_submit():
        folder_name = form.foldername.data.strip()  # Ensure it's a string

        if not folder_name:  # Prevent empty folder names
            flash("Folder name cannot be empty!", "danger")
            return redirect(url_for("main.home"))

        upload_folder = current_app.config['UPLOAD_FOLDER']
        new_folder_path = os.path.join(upload_folder, folder_name)

        if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)
            flash(f"Folder '{folder_name}' created successfully!", "success")
        else:
            flash("Folder already exists!", "warning")

    return redirect(url_for("main.home"))

@main.route('/folder/<foldername>')
def view_folder(foldername):
    """List all files inside the selected folder with pagination."""
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], foldername)

    if not os.path.exists(upload_folder) or not os.path.isdir(upload_folder):
        flash("Folder does not exist!", "danger")
        return redirect(url_for('main.home'))

    # Pagination setup
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of files per page

    # Collect all files with details
    all_files = []
    for file in os.listdir(upload_folder):
        file_path = os.path.join(upload_folder, file)
        if os.path.isfile(file_path):
            all_files.append({
                'filename': file,
                'uploaded_at': datetime.fromtimestamp(os.path.getmtime(file_path)),
                'file_type': file.split('.')[-1] if '.' in file else 'Unknown',
                'file_size': os.path.getsize(file_path),
                'get_readable_size': lambda size=os.path.getsize(file_path): _get_readable_size(size)
            })

    # Sort files by modification time (most recent first)
    all_files.sort(key=lambda x: x['uploaded_at'], reverse=True)

    # Implement pagination
    total_files = len(all_files)
    total_pages = (total_files + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    files = all_files[start:end]

    upload_file_form = UploadFileForm()
    create_folder_form = CreateFolderForm()
    delete_file_form = DeleteFileForm()

    return render_template(
        "folder.html", 
        foldername=foldername,
        upload_file_form=upload_file_form,
        create_folder_form=create_folder_form, 
        delete_file_form=delete_file_form, 
        files=files,
        current_page=page,
        total_pages=total_pages
    )

def _get_readable_size(size):
    """Convert file size to human-readable format."""
    for unit in ['bytes', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

@main.route('/download/<foldername>')
def download_file(foldername, filename):
    """Download a file from a specific folder."""
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], foldername, filename)

    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        flash('File not found!', 'danger')
        return redirect(url_for('main.view_folder', foldername=foldername, filename=filename))

@main.route('/delete/<foldername>', methods=['GET', 'POST'])
def delete_file(foldername, filename):
    """Delete a file from a specific folder."""
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], foldername, filename)

    if os.path.exists(file_path):
        os.remove(file_path)
        flash('File deleted successfully!', 'success')
    else:
        flash('File not found!', 'danger')

    return redirect(url_for('main.view_folder', foldername=foldername, filename=filename))
# @main.route("/delete/<foldername>", methods=['POST'])
# def delete_file(foldername, filename):
#     """Delete a file from a specific folder."""
#     file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], foldername, filename)

#     if os.path.exists(file_path):
#         os.remove(file_path)
#         flash('File deleted successfully!', 'success')
#     else:
#         flash('File not found!', 'danger')

#     return redirect(url_for('main.view_folder', foldername=foldername))