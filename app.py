import json
import uuid
import os
import re
from flask import Flask, render_template, request, redirect, url_for
import markdown
from datetime import datetime


app = Flask(__name__)

# 配置笔记存储目录和时间信息存储文件
NOTES_DIR = 'notes'
TIME_INFO_FILE = 'time_info.json'
if not os.path.exists(NOTES_DIR):
    os.makedirs(NOTES_DIR)

# 初始化时间信息存储文件
if not os.path.exists(TIME_INFO_FILE):
    with open(TIME_INFO_FILE, 'w', encoding='utf-8') as file:
        json.dump({}, file)

def load_time_info():
    try:
        with open(TIME_INFO_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_time_info(time_info):
    try:
        with open(TIME_INFO_FILE, 'w', encoding='utf-8') as file:
            json.dump(time_info, file, indent=4)
    except IOError as e:
        print(f"Error saving time info: {e}")

def read_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    except IOError as e:
        print(f"Error reading file {filepath}: {e}")
        return None

def write_file(filepath, content):
    try:
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(content)
        return True
    except IOError as e:
        print(f"Error writing to file {filepath}: {e}")
        return False

def get_article_ids():
    notes = [f for f in os.listdir(NOTES_DIR) if f.endswith('.md')]
    return {note: load_time_info().get(note, {}).get('id', None) for note in notes}

@app.route('/')
def index():
    # 获取所有笔记文件
    notes = [f for f in os.listdir(NOTES_DIR) if f.endswith('.md')]
    # 提取每个文件的标题和时间
    note_titles = []
    time_info = load_time_info()
    for note in notes:
        # 使用文件名作为标题
        title = note.replace('.md', '')
        # 获取时间信息
        time_str = time_info.get(note, {}).get('time', '')
        note_titles.append((note, title, time_str))
    # 按时间倒序排列
    note_titles.sort(key=lambda x: x[2], reverse=True)
    return render_template('index.html', notes=note_titles)

@app.route('/view/<filename>')
def view_note(filename):
    # 读取笔记文件内容
    filepath = os.path.join(NOTES_DIR, filename)
    content = read_file(filepath)
    if content is None:
        return redirect(url_for('index'))
    
    # 使用markdown库渲染Markdown内容，并启用代码块扩展
    html_content = markdown.markdown(content, extensions=['markdown.extensions.codehilite'])
    
    # 获取当前笔记的时间信息
    time_info = load_time_info()
    update_time = time_info.get(filename, {}).get('time', '')
    
    return render_template('view_note.html', 
                         filename=filename, 
                         content=html_content, 
                         update_time=update_time)

@app.route('/edit/<filename>', methods=['GET', 'POST'])
def edit_note(filename):
    if request.method == 'POST':
        # 保存编辑后的笔记标题和内容
        new_title = request.form['title']
        content = request.form['content']
        original_file_path = os.path.join(NOTES_DIR, filename)
        
        # 检查标题是否发生了变化
        if new_title != filename.replace('.md', ''):
            # 生成新的文件名
            new_filename = new_title + '.md'
            new_file_path = os.path.join(NOTES_DIR, new_filename)
            
            # 重命名文件
            try:
                os.rename(original_file_path, new_file_path)
                filename = new_filename
            except OSError as e:
                print(f"Error renaming file: {e}")
                return redirect(url_for('edit_note', filename=filename))
        
        # 更新时间信息
        time_info = load_time_info()
        old_id = time_info.get(filename, {}).get('id', None)
        if filename in time_info:
            del time_info[filename]
        
        new_id = str(uuid.uuid4())
        time_info[filename] = {
            'id': new_id,
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        save_time_info(time_info)
        
        # 删除旧的ID对应的文章信息
        if old_id is not None:
            article_ids = get_article_ids()
            note = next((n for n, id in article_ids.items() if id == old_id), None)
            if note:
                time_info.pop(note, None)
                save_time_info(time_info)
        
        # 保存编辑后的内容
        if not write_file(new_file_path if 'new_file_path' in locals() else original_file_path, content):
            return redirect(url_for('edit_note', filename=filename))
        
        return redirect(url_for('view_note', filename=filename))
    else:
        # 读取笔记文件内容用于编辑
        filepath = os.path.join(NOTES_DIR, filename)
        content = read_file(filepath)
        if content is None:
            return redirect(url_for('index'))
            
        # 提取标题
        title = content.split('\n')[0].replace('# ', '')
        return render_template('edit_note.html', 
                            filename=filename, 
                            content=content, 
                            title=title)

@app.route('/new', methods=['GET', 'POST'])
def new_note():
    if request.method == 'POST':
        # 创建新的笔记文件
        filename = request.form['filename'] + '.md'
        content = request.form['content']
        filepath = os.path.join(NOTES_DIR, filename)
        
        # 检查文件是否已存在
        if os.path.exists(filepath):
            return render_template('new_note.html', 
                                error="文件已存在，请使用不同的名称")
        
        # 获取当前时间
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        note_id = str(uuid.uuid4())
        
        # 保存文件内容
        if not write_file(filepath, content):
            return render_template('new_note.html', 
                                error="保存文件时出错，请重试")
        
        # 更新时间信息
        time_info = load_time_info()
        time_info[filename] = {
            'id': note_id,
            'time': current_time
        }
        save_time_info(time_info)
        
        return redirect(url_for('view_note', filename=filename))
    else:
        return render_template('new_note.html')

@app.route('/delete/<filename>', methods=['POST'])
def delete_note(filename):
    filepath = os.path.join(NOTES_DIR, filename)
    
    # 删除笔记文件
    try:
        os.remove(filepath)
    except OSError as e:
        print(f"Error deleting file {filepath}: {e}")
        return redirect(url_for('view_note', filename=filename))
    
    # 删除时间信息
    time_info = load_time_info()
    if filename in time_info:
        del time_info[filename]
        if not save_time_info(time_info):
            print(f"Error saving time info after deleting {filename}")
    
    return redirect(url_for('index'))

# 每次保存文章后，检查JSON文件中的文件名是否与notes目录下的实际文件名匹配
def clean_time_info():
    time_info = load_time_info()
    notes = [f for f in os.listdir(NOTES_DIR) if f.endswith('.md')]
    for note in list(time_info.keys()):
        if note not in notes:
            del time_info[note]
    save_time_info(time_info)

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=5007)  # 运行Flask应用在5007端口上
    
    app.run(debug=True)
