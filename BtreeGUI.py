from Btree import BTree
import tkinter as tk
from tkinter import simpledialog
import copy

class BTreeGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Visualizador de Árvore B")
        self.canvas = tk.Canvas(master, width=800, height=600, bg='white')
        self.canvas.pack()

        self.entry = tk.Entry(master)
        self.entry.pack(side=tk.LEFT)
        self.entry.focus()

        self.insert_btn = tk.Button(master, text="Inserir", command=self.inserir_chave)
        self.insert_btn.pack(side=tk.LEFT)

        self.status_label = tk.Label(master, text="", fg="blue")
        self.status_label.pack()

        self.btree = BTree(t=2)
        self.animation_steps = []

    def inserir_chave(self):
        try:
            key = int(self.entry.get())
            self.entry.delete(0, tk.END)
            self.animation_steps = []

            def trace_callback(message):
                cloned_root = self.clone_tree(self.btree.raiz)
                self.animation_steps.append((cloned_root, message))

            # Use a versão com rastreamento da inserção
            self.btree.insere_com_trace(key, trace_callback)

            # Mostra a animação completa
            self.play_animation()
        except ValueError:
            pass

    def clone_tree(self, node):
        return copy.deepcopy(node)

    def play_animation(self, index=0):
        if index >= len(self.animation_steps):
            return
        node, message = self.animation_steps[index]
        self.canvas.delete("all")
        self.status_label.config(text=message)
        total_width = self.calculo_comprimento_total(node)
        initial_x = self.canvas.winfo_width() // 2 - total_width // 2
        self.calcular_posicoes(node, x=initial_x)
        self.desenho_node_recursivo(node)
        self.master.after(1000, lambda: self.play_animation(index + 1))

    def calculo_comprimento_total(self, node):
        if node.folha:
            return max(40 * len(node.keys), 60)
        total = 0
        for child in node.filhos:
            total += self.calculo_comprimento_total(child) + 20
        return total

    def calcular_posicoes(self, node, depth=0, x=0):
        if node.folha:
            width = max(40 * len(node.keys), 60)
            node._x = x + width // 2
            node._y = depth * 70 + 50
            return width

        total_width = 0
        for child in node.filhos:
            subtree_width = self.calcular_posicoes(child, depth + 1, x + total_width)
            total_width += subtree_width + 20

        node._x = x + total_width // 2
        node._y = depth * 70 + 50
        return total_width

    def desenho_node_recursivo(self, node):
        x, y = node._x, node._y
        text = " | ".join(map(str, node.keys))
        width = max(40 * len(node.keys), 60)
        self.canvas.create_rectangle(x - width // 2, y - 20, x + width // 2, y + 20, fill="lightblue")
        self.canvas.create_text(x, y, text=text)

        if not node.folha:
            for child in node.filhos:
                cx, cy = child._x, child._y
                self.canvas.create_line(x, y + 20, cx, cy - 20)
                self.desenho_node_recursivo(child)

