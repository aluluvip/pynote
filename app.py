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
    with open(TIME_INFO_FILE, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_time_info(time_info):
    with open(TIME_INFO_FILE, 'w', encoding='utf-8') as file:
        json.dump(time_info, file, indent=4)

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
    # 读取笔记文件内容并转换为HTML
    with open(os.path.join(NOTES_DIR, filename), 'r', encoding='utf-8') as file:
        content = file.read()
        # 使用markdown库渲染Markdown内容，并启用代码块扩展
        html_content = markdown.markdown(content, extensions=['markdown.extensions.codehilite'])
        # 获取当前笔记的时间信息
        time_info = load_time_info()
        update_time = time_info.get(filename, {}).get('time', '')
    return render_template('view_note.html', filename=filename, content=html_content, update_time=update_time)

@app.route('/edit/<filename>', methods=['GET', 'POST'])
def edit_note(filename):
    if request.method == 'POST':
        # 保存编辑后的笔记标题和内容
        new_title = request.form['title']
        content = request.form['content']
        # 获取原始文件的完整路径
        original_file_path = os.path.join(NOTES_DIR, filename)
        
        # 检查标题是否发生了变化
        if new_title != filename.replace('.md', ''):
            # 生成新的文件名
            new_filename = new_title + '.md'
            new_file_path = os.path.join(NOTES_DIR, new_filename)
            
            # 重命名文件
            os.rename(original_file_path, new_file_path)
            
            # 更新文件名变量
            filename = new_filename
        else:
            # 如果标题没有变化，使用原始文件路径
            new_file_path = original_file_path
        
        # 更新时间信息，生成新的ID并删除旧的文章信息
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
        
        # 去除多余的空行
        content = re.sub(r'\n\s*\n', '\n', content)
        
        # 将编辑后的内容写入文件，并更新修改时间
        with open(new_file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        # 重定向到新生成的文章页面
        return redirect(url_for('view_note', filename=filename))
    else:
        # 读取笔记文件内容用于编辑
        with open(os.path.join(NOTES_DIR, filename), 'r', encoding='utf-8') as file:
            content = file.read()
            # 提取标题
            title = content.split('\n')[0].replace('# ', '')
        return render_template('edit_note.html', filename=filename, content=content, title=title)

@app.route('/new', methods=['GET', 'POST'])
def new_note():
    if request.method == 'POST':
        # 创建新的笔记文件
        filename = request.form['filename'] + '.md'
        content = request.form['content']
        # 获取当前时间
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 生成一个唯一的ID
        note_id = str(uuid.uuid4())
        
        # 将内容写入文件
        with open(os.path.join(NOTES_DIR, filename), 'w', encoding='utf-8') as file:
            file.write(content)
        
        # 更新时间信息
        time_info = load_time_info()
        time_info[filename] = {
            'id': note_id,
            'time': current_time
        }
        save_time_info(time_info)
        
        # 重定向到新生成的文章页面
        return redirect(url_for('view_note', filename=filename))
    else:
        return render_template('new_note.html')

@app.route('/delete/<filename>', methods=['POST'])
def delete_note(filename):
    # 删除笔记文件
    os.remove(os.path.join(NOTES_DIR, filename))
    
    # 删除时间信息
    time_info = load_time_info()
    if filename in time_info:
        del time_info[filename]
        save_time_info(time_info)
    
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
