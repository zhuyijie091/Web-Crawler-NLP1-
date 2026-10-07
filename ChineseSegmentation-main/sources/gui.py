import tkinter as tk
import os
import subprocess




window = tk.Tk()
window.title("中文分词")
frame = tk.Frame()


greeting = tk.Label(master=frame, text="中文分词 by huyiwen")
entry = tk.Entry(master=frame)
btn_submit = tk.Button(master=frame, text="提交")

greeting.pack()
entry.pack()
btn_submit.pack(side=tk.RIGHT, padx=10, ipadx=10)

def submit(event):
    sent = entry.get()
    print(sent)
    entry.delete(0, tk.END)

    p = subprocess.run(["./a.out"], input=bytes(sent, encoding="UTF-8"), capture_output=True)

    entry.insert(0, p.stdout.decode(encoding="UTF-8"))

btn_submit.bind("<Button-1>", submit)

frame.pack(fill=tk.X)
window.mainloop()

os.system("g++ -std=c++17 main.cpp -o a.out")
