# BStarTreeGUI.py

from BStarTree import BStarTree # Alterado
import tkinter as tk
import copy

class BStarTreeGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Visualizador de Árvore B*") # Alterado

        self.canvas = tk.Canvas(master, width=1200, height=700, bg='white')
        self.canvas.pack()

        self.entry = tk.Entry(master)
        self.entry.pack(side=tk.LEFT)
        self.entry.focus()

        self.insert_btn = tk.Button(master, text="Inserir", command=self.inserir_chave)
        self.insert_btn.pack(side=tk.LEFT)

        self.delete_btn = tk.Button(master, text="Remover", command=self.remover_chave)
        self.delete_btn.pack(side=tk.LEFT)

        self.status_label = tk.Label(master, text="", fg="darkgreen")
        self.status_label.pack()

        self.speed_scale = tk.Scale(
            master,
            from_=100,
            to=3000,
            orient=tk.HORIZONTAL,
            label="Tempo entre passos (ms)",
            length=250
        )
        self.speed_scale.set(1000)
        self.speed_scale.pack(side=tk.LEFT)
        
        # Instancia a BStarTree com grau t=3
        try:
            self.btree = BStarTree(t=3) # Alterado
        except ValueError as e:
            self.status_label.config(text=str(e), fg="red")
            self.insert_btn.config(state=tk.DISABLED)
            self.delete_btn.config(state=tk.DISABLED)

        self.animation_steps = []

    def inserir_chave(self):
        try:
            key = int(self.entry.get())
            self.entry.delete(0, tk.END)
            self.animation_steps = []
            def trace_callback(message, highlighted_path):
                cloned_root = self.clone_tree(self.btree.raiz)
                self.animation_steps.append((cloned_root, message, highlighted_path))
            self.btree.insere_com_trace(key, trace_callback)
            self.play_animation()
        except ValueError:
            pass

    def remover_chave(self):
        try:
            key = int(self.entry.get())
            self.entry.delete(0, tk.END)
            self.animation_steps = []
            def trace_callback(message, highlighted_path):
                cloned_root = self.clone_tree(self.btree.raiz)
                self.animation_steps.append((cloned_root, message, highlighted_path))
            self.btree.remover_com_trace(key, trace_callback)
            self.play_animation()
        except ValueError:
            pass

    def clone_tree(self, node):
        return copy.deepcopy(node)

    def play_animation(self, index=0):
        if index >= len(self.animation_steps):
            final_root = self.animation_steps[-1][0] if self.animation_steps else self.btree.raiz
            self.canvas.delete("all")
            self.status_label.config(text="Animação concluída.")
            total_width = self.calculo_comprimento_total(final_root)
            initial_x = self.canvas.winfo_width() // 2 - total_width // 2
            self.calcular_posicoes(final_root, x=initial_x)
            self.desenho_node_recursivo(final_root)
            return
        
        node, message, highlighted_path = self.animation_steps[index]
        self.canvas.delete("all")
        self.status_label.config(text=message)
        total_width = self.calculo_comprimento_total(node)
        initial_x = self.canvas.winfo_width() // 2 - total_width // 2
        self.calcular_posicoes(node, x=initial_x)
        self.desenho_node_recursivo(node, highlighted_path)
        delay = self.speed_scale.get()
        self.master.after(delay, lambda: self.play_animation(index + 1))

    def calculo_comprimento_total(self, node):
        if not node or node.folha:
            return max(40 * len(node.keys), 60) if node else 60
        total = 0
        for child in node.filhos:
            total += self.calculo_comprimento_total(child) + 20
        return total

    def calcular_posicoes(self, node, depth=0, x=0):
        if not node: return 0
        if node.folha:
            width = max(40 * len(node.keys), 60)
            node._x = x + width // 2
            node._y = depth * 80 + 50
            return width
        
        child_widths = []
        for child in node.filhos:
            child_widths.append(self.calcular_posicoes(child, depth + 1, x + sum(child_widths) + 20 * len(child_widths)))

        total_width = sum(child_widths) + 20 * (len(child_widths) -1) if child_widths else 0
        
        node._x = x + total_width // 2
        node._y = depth * 80 + 50
        return total_width

    def desenho_node_recursivo(self, node, highlighted_path=None, current_path=None):
        if not node: return
        if current_path is None:
            current_path = []
        x, y = node._x, node._y
        text = " | ".join(map(str, node.keys))
        width = max(40 * len(node.keys), 60)
        
        fill_color = "lightyellow" # Cor para nós da B*
        outline_color = "orange"
        
        if highlighted_path is not None and current_path == highlighted_path:
            self.canvas.create_rectangle(x - width // 2, y - 20, x + width // 2, y + 20, outline="red", width=4, fill=fill_color)
        else:
            self.canvas.create_rectangle(x - width // 2, y - 20, x + width // 2, y + 20, fill=fill_color, outline=outline_color, width=2)
            
        self.canvas.create_text(x, y, text=text, font=("Helvetica", 10))
        
        if not node.folha:
            for idx, child in enumerate(node.filhos):
                if hasattr(child, '_x'):
                    cx, cy = child._x, child._y
                    self.canvas.create_line(x, y + 20, cx, cy - 20, fill=outline_color)
                    self.desenho_node_recursivo(child, highlighted_path, current_path + [idx])