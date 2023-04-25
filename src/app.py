import datetime
import hashlib
import zipfile
from pathlib import Path
import datetime as dt
import os
import pwd
import logging
from flask import(
    Flask,
    request,
    render_template,
    redirect,
    session,
    url_for,
    send_file,
    abort
)


app = Flask(__name__)

def log_action(message):
    with open('app.log', 'a') as log_file:
        log_file.write('[{}] {}\n'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message))
 
def generate_key(login):
    return hashlib.md5(str(login).encode('utf-8')).hexdigest()
app.secret_key='19970901'

@app.route('/')
def index():
    return render_template('login.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            pwd.getpwnam(username)
            log_action('User {} authenticated successfully.'.format(username))
        except KeyError:
            log_action('Failed authentication attempt for user {}.'.format(username))
            return render_template('login.html', error='Invalid username or password')
        shadow = open('/etc/shadow').read().splitlines()
        for line in shadow:
            fields = line.split(':')
            if fields[0] == username:
                hash_value = fields[1]
                break
        else:
            return render_template('login.html', error='Invalid username or password')
        salt = hash_value[:11]
        import crypt
        if crypt.crypt(password, salt) == hash_value:
            response=app.make_response(render_template('app.html'))
            session['username'] = username
            logging.info('User %s logged in' % username)
            response.set_cookie('access_time',str(datetime.now()))
            return response
        else:
            return render_template('login.html', error='Invalid username or password')
    else:
        return render_template('login.html')

@app.route('/home')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    dir_path = request.args.get('dir', session['home_dir'])
    
    if not os.path.isdir(dir_path):
        return "Invalid directory path"
    
    files = []
    directories = []
    
    for f in os.listdir(dir_path):
        path = os.path.join(dir_path, f)
        if os.path.isdir(path):
            directories.append(f)
        elif os.path.isfile(path) and f.endswith('.txt'):
            files.append(f)
    
    return render_template('app.html', directories=directories, files=files, dir_path=dir_path)

@app.route('/view_file')
def view_file():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    file_path = request.args.get('file')
    
    if not os.path.isfile(file_path):
        return "Invalid file path"
    
    with open(file_path, 'r') as f:
        file_content = f.read()
    
    return render_template('view_file.html', file_content=file_content)

@app.route('/logout')
def logout():
    if 'username' not in session:
        return redirect(url_for('login'))
    logging.info('User %s logged out' % session['username'])
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/download/<filename>')
def download(filename):
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    home_dir = pwd.getpwnam(username).pw_dir
    filepath = os.path.join(home_dir, filename)
    return app.send_file(filepath, as_attachment=True)

@app.route('/download_home_dir')
def download_home_dir():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    home_dir = pwd.getpwnam(username).pw_dir
    zip_filename = username + '_home_dir.zip'
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for dirpath, dirnames, filenames in os.walk(home_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                zipf.write(filepath, os.path.relpath(filepath, home_dir))
    return send_file(zip_filename, as_attachment=True)

@app.route('/search', methods=['GET', 'POST'])
def search():
    # Récupération des paramètres de recherche depuis le formulaire
    search_term = request.form['search_term']
    extension = request.form['extension']
    # Chemin du répertoire personnel de l'utilisateur
    home_directory = os.path.expanduser("~")
    # Recherche des fichiers correspondants au nom et à l'extension spécifiés
    files = []
    for dirpath, dirnames, filenames in os.walk(home_directory):
        for filename in filenames:
            if filename.endswith(extension) and search_term in filename:
                file_path = os.path.join(dirpath, filename)
                file_size = os.path.getsize(file_path)
                files.append({
                    'name': filename,
                    'path': file_path,
                    'size': file_size
                })
    # Affichage des résultats dans une table HTML
    return render_template('results.html', files=files)

@app.route('/get_filesize')   
def get_filesize(filename):
    filepath = os.path.join(pwd.getpwnam(session['username']).pw_dir, filename)
    return os.path.getsize(filepath)

@app.route('/get_directorysize')
def get_directorysize():
    user_dir = os.path.join(os.path.expanduser('~'), 'Documents')  # Path to user directory
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(user_dir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    # Convert to human-readable format
    units = ['bytes', 'KB', 'MB', 'GB', 'TB']
    size = total_size
    for unit in units:
        if size < 1024:
            break
        size /= 1024
    return f"The size of the user's directory is {size:.2f} {unit}."

@app.route('/get_modification_time')   
def get_modification_time(filename):
    filepath = os.path.join(pwd.getpwnam(session['username']).pw_dir, filename)
    return datetime.datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S')

@app.route('/get_space_used')   
def get_space_used():
    home_dir = pwd.getpwnam(session['username']).pw_dir
    size = sum(os.path.getsize(os.path.join(dirpath, filename)) for dirpath, dirnames, filenames in os.walk(home_dir) for filename in filenames)
    return format(size / (1024 * 1024), '.2f') + ' MB'


##########Files handler



FolderPath = os.path.expanduser("~")


def getReadableByteSize(num, suffix='B') -> str:
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Y', suffix)

def getTimeStampString(tSec: float) -> str:
    tObj = dt.datetime.fromtimestamp(tSec)
    tStr = dt.datetime.strftime(tObj, '%Y-%m-%d %H:%M:%S')
    return tStr

def getIconClassForFilename(fName):
    fileExt = Path(fName).suffix
    fileExt = fileExt[1:] if fileExt.startswith(".") else fileExt
    fileTypes = ["aac", "ai", "bmp", "cs", "css", "csv", "doc", "docx", "exe", "gif", "heic", "html", "java", "jpg", "js", "json", "jsx", "key", "m4p", "md", "mdx", "mov", "mp3",
                 "mp4", "otf", "pdf", "php", "png", "pptx", "psd", "py", "raw", "rb", "sass", "scss", "sh", "sql", "svg", "tiff", "tsx", "ttf", "txt", "wav", "woff", "xlsx", "xml", "yml"]
    fileIconClass = f"bi bi-filetype-{fileExt}" if fileExt in fileTypes else "bi bi-file-earmark"
    return fileIconClass

# route handler
@app.route('/reports/', defaults={'reqPath': ''})
@app.route('/reports/<path:reqPath>')
def getFiles(reqPath):
    # Join the base and the requested path
    # could have done os.path.join, but safe_join ensures that files are not fetched from parent folders of the base folder
    absPath = safe_join(FolderPath, reqPath)

    # Return 404 if path doesn't exist
    if not os.path.exists(absPath):
        return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(absPath):
        return send_file(absPath)

    # Show directory contents
    def fObjFromScan(x):
        fileStat = x.stat()
        # return file information for rendering
        return {'name': x.name,
                'fIcon': "bi bi-folder-fill" if os.path.isdir(x.path) else getIconClassForFilename(x.name),
                'relPath': os.path.relpath(x.path, FolderPath).replace("\\", "/"),
                'mTime': getTimeStampString(fileStat.st_mtime),
                'size': getReadableByteSize(fileStat.st_size)}
    fileObjs = [fObjFromScan(x) for x in os.scandir(absPath)]
    # get parent directory url
    parentFolderPath = os.path.relpath(
        Path(absPath).parents[0], FolderPath).replace("\\", "/")
    return render_template('browser.html', data={'files': fileObjs,
                                                 'parentFolder': parentFolderPath})

##############

@app.errorhandler(Exception)
def error(exception):
    return render_template('error.html',error=
     {
        "ip":request.remote_addr,
        "method":request.method,
        "error" :'sorry im here '
    })
if __name__=='__main__':
    import logging
    from logging.handlers import RotatingFileHandler

    handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    
    app.run(host="0.0.0.0",port=8070,debug=True)