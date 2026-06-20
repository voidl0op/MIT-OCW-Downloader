from flask import Flask, request, Response, render_template, jsonify
from download import download_course_resources
import threading
import queue
import builtins
import tkinter as tk
from tkinter import filedialog
import webbrowser
from threading import Timer
import sys
import os

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

app = Flask(__name__,
    template_folder=resource_path('templates'),
    static_folder=resource_path('static')
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/browse')
def browse():
    folder = ''
    try:
        root = tk.Tk()
        root.withdraw()
        root.wm_attributes('-topmost', True)
        root.update()
        folder = filedialog.askdirectory(parent=root)
        root.destroy()
    except Exception as e:
        return jsonify({'folder': '', 'error': str(e)})
    return jsonify({'folder': folder})

@app.route('/download')
def download():
    url = request.args.get('url')
    folder = request.args.get('folder')

    if not url:
        return Response("No URL provided", status=400)
    if not folder:
        return Response("No folder provided", status=400)

    def generate():
        q = queue.Queue()
        original_print = builtins.print

        def custom_print(*args, **kwargs):
            msg = ' '.join(str(a) for a in args)
            q.put(msg)

        builtins.print = custom_print

        def run():
            download_course_resources(url, folder)
            q.put(None)

        thread = threading.Thread(target=run)
        thread.start()

        while True:
            msg = q.get()
            if msg is None:
                break
            yield f"data: {msg}\n\n"

        builtins.print = original_print

    return Response(generate(), mimetype='text/event-stream')

def open_browser():
    webbrowser.open('http://127.0.0.1:5000') # Opens it autommaticcally so i don't have to open it each time

if __name__ == "__main__":
    Timer(1, open_browser).start()
    app.run(debug=True, threaded=False, use_reloader=False)