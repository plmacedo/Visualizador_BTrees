# main.py

import tkinter as tk
from Btree import BTree
from BStarTree import BStarTree
from TreeVisualizerGUI import TreeVisualizerGUI

class AppSelector:
    def __init__(self, master):
        self.master = master
        self.master.title("Seletor de Visualizador de Árvore")
        self.master.geometry("400x200")

        label = tk.Label(master, text="Escolha qual tipo de árvore você deseja visualizar:", font=("Helvetica", 12))
        label.pack(pady=20)

        btree_button = tk.Button(master, text="Árvore B (t=2)", command=self.launch_btree, font=("Helvetica", 10), bg="lightblue")
        btree_button.pack(pady=10, fill=tk.X, padx=50)

        bstree_button = tk.Button(master, text="Árvore B* (t=3)", command=self.launch_bstree, font=("Helvetica", 10), bg="lightyellow")
        bstree_button.pack(pady=10, fill=tk.X, padx=50)

    def launch_btree(self):
        self.master.destroy()  # Fecha a janela de seleção
        root = tk.Tk()
        colors = {'fill': 'lightblue', 'outline': 'blue', 'status': 'blue'}
        TreeVisualizerGUI(root, BTree, "Árvore B", t_param=2, colors=colors)
        root.mainloop()

    def launch_bstree(self):
        self.master.destroy()  # Fecha a janela de seleção
        root = tk.Tk()
        colors = {'fill': 'lightyellow', 'outline': 'orange', 'status': 'darkgreen'}
        TreeVisualizerGUI(root, BStarTree, "Árvore B*", t_param=3, colors=colors)
        root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = AppSelector(root)
    root.mainloop()