# TreeVisualizerGUI.py

import tkinter as tk
import copy

class TreeVisualizerGUI:
    HORIZONTAL_SPACING = 30
    VERTICAL_SPACING = 90

    def __init__(self, master, tree_class, tree_name, t_param, colors):
        self.master = master
        self.master.title(f"Visualizador de {tree_name}")
        self.master.geometry("1200x800")
        self.colors = colors

        status_frame = tk.Frame(master)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(5, 10))
        
        self.status_label = tk.Label(status_frame, text="", fg=self.colors['status'])
        self.status_label.pack(side=tk.LEFT)
        
        self.disk_access_label = tk.Label(status_frame, text="Acessos a Disco: 0 leituras, 0 escritas", fg="black", font=("Helvetica", 10, "bold"))
        self.disk_access_label.pack(side=tk.RIGHT)

        control_frame = tk.Frame(master)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        self.entry = tk.Entry(control_frame)
        self.entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,5))
        self.entry.focus()

        self.insert_btn = tk.Button(control_frame, text="Inserir", command=self.inserir_chave)
        self.insert_btn.pack(side=tk.LEFT, padx=5)

        self.delete_btn = tk.Button(control_frame, text="Remover", command=self.remover_chave)
        self.delete_btn.pack(side=tk.LEFT)

        self.speed_scale = tk.Scale(
            control_frame, from_=100, to=3000, orient=tk.HORIZONTAL,
            label="Tempo entre passos (ms)", length=250
        )
        self.speed_scale.set(1000)
        self.speed_scale.pack(side=tk.RIGHT, padx=10)

        self.canvas = tk.Canvas(master, bg='white')
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        try:
            self.btree = tree_class(t=t_param)
        except ValueError as e:
            self.status_label.config(text=str(e), fg="red")
            self.insert_btn.config(state=tk.DISABLED)
            self.delete_btn.config(state=tk.DISABLED)

        self.animation_steps = []
        self.master.update_idletasks()
        self.desenhar_arvore(self.btree.raiz, f"Árvore {tree_name} (t={t_param}) inicializada.")

    def inserir_chave(self):
        try:
            key = int(self.entry.get())
            self.entry.delete(0, tk.END)
            self.animation_steps = []
            
            def trace_callback(message, highlighted_path, disk_counter):
                cloned_root = copy.deepcopy(self.btree.raiz)
                self.animation_steps.append((cloned_root, message, highlighted_path, disk_counter.copy()))
            
            self.btree.insere_com_trace(key, trace_callback)
            self.play_animation()
        except ValueError:
            self.status_label.config(text="Erro: Por favor, insira um número inteiro.", fg="red")
        except Exception as e:
            self.status_label.config(text=f"Erro inesperado: {e}", fg="red")
            # Para debug, imprime o erro completo no console
            import traceback
            traceback.print_exc()

    def remover_chave(self):
        try:
            key = int(self.entry.get())
            self.entry.delete(0, tk.END)
            self.animation_steps = []

            def trace_callback(message, highlighted_path, disk_counter):
                cloned_root = copy.deepcopy(self.btree.raiz)
                self.animation_steps.append((cloned_root, message, highlighted_path, disk_counter.copy()))

            self.btree.remover_com_trace(key, trace_callback)
            self.play_animation()
        except ValueError:
            self.status_label.config(text="Erro: Por favor, insira um número inteiro.", fg="red")
        except Exception as e:
            self.status_label.config(text=f"Erro inesperado: {e}", fg="red")
            import traceback
            traceback.print_exc()

    def play_animation(self, index=0):
        if index >= len(self.animation_steps):
            if self.animation_steps:
                final_root, _, _, final_disk_counter = self.animation_steps[-1]
                self.desenhar_arvore(final_root, "Animação concluída.", disk_counter=final_disk_counter)
            return
        
        node, message, highlighted_path, disk_counter = self.animation_steps[index]
        self.desenhar_arvore(node, message, highlighted_path, disk_counter)
        
        delay = self.speed_scale.get()
        self.master.after(delay, lambda: self.play_animation(index + 1))

    def desenhar_arvore(self, root_node, message, highlighted_path=None, disk_counter=None):
        self.canvas.delete("all")
        self.status_label.config(text=message)
        
        if disk_counter:
            reads = disk_counter.get('reads', 0)
            writes = disk_counter.get('writes', 0)
            self.disk_access_label.config(text=f"Acessos a Disco: {reads} leituras, {writes} escritas")
        else:
            self.disk_access_label.config(text="Acessos a Disco: 0 leituras, 0 escritas")
        
        if not root_node or (not root_node.keys and root_node.folha):
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            self.canvas.create_text(
                canvas_width / 2, canvas_height / 2,
                text="Árvore vazia", font=("Helvetica", 16, "italic"), fill="grey"
            )
            return

        self.calcular_posicoes(root_node, 0, self.canvas.winfo_width() / 2)
        self.desenho_node_recursivo(root_node, highlighted_path)
    
    # --- FUNÇÕES DE DESENHO CORRIGIDAS PARA SEREM GENÉRICAS ---

    def _get_children(self, node):
        """Função auxiliar para obter a lista de filhos, não importa o nome do atributo."""
        return getattr(node, 'children', getattr(node, 'filhos', []))

    def get_node_width(self, node):
        text = " | ".join(map(str, node.keys))
        return max(25 * len(text), 70)

    def calcular_posicoes(self, node, depth, x, parent_x=None):
        if node is None:
            return

        node._y = depth * self.VERTICAL_SPACING + 60
        node._x = x
        
        if not node.folha:
            children = self._get_children(node)
            children_widths = [self.get_subtree_width(child) for child in children]
            total_width = sum(children_widths) + self.HORIZONTAL_SPACING * (len(children) - 1)
            
            current_x = x - total_width / 2
            
            for i, child in enumerate(children):
                subtree_width = children_widths[i]
                child_x = current_x + subtree_width / 2
                self.calcular_posicoes(child, depth + 1, child_x, parent_x=node._x)
                current_x += subtree_width + self.HORIZONTAL_SPACING

    def get_subtree_width(self, node):
        if node is None:
            return 0
        if node.folha:
            return self.get_node_width(node)
        
        children = self._get_children(node)
        children_total_width = sum(self.get_subtree_width(child) for child in children)
        spacing = self.HORIZONTAL_SPACING * (len(children) - 1)
        
        return max(self.get_node_width(node), children_total_width + spacing)

    def desenho_node_recursivo(self, node, highlighted_path=None, current_path=None):
        if not node: return
        if current_path is None: current_path = []
        
        x, y = node._x, node._y
        width = self.get_node_width(node)
        
        is_bplus_leaf = hasattr(node, 'next') and node.folha
        fill_color = self.colors['fill']
        if is_bplus_leaf:
            fill_color = "#C8E6C9" if self.colors['fill'] == '#9ACD32' else self.colors['fill']
        
        outline_color = self.colors['outline']
        
        if highlighted_path is not None and current_path == highlighted_path:
            self.canvas.create_rectangle(x - width / 2, y - 20, x + width / 2, y + 20, outline="red", width=3, fill=fill_color)
        else:
            self.canvas.create_rectangle(x - width / 2, y - 20, x + width / 2, y + 20, fill=fill_color, outline=outline_color, width=2)
            
        text = " | ".join(map(str, node.keys))
        self.canvas.create_text(x, y, text=text, font=("Helvetica", 10, "bold"))
        
        if is_bplus_leaf and node.next and hasattr(node.next, '_x'):
            self.canvas.create_line(x + width / 2, y, node.next._x - self.get_node_width(node.next) / 2, node.next._y,
                                    arrow=tk.LAST, dash=(5, 3), fill="blue")

        if not node.folha:
            children = self._get_children(node)
            for idx, child in enumerate(children):
                if hasattr(child, '_x'):
                    cx, cy = child._x, child._y
                    self.canvas.create_line(x, y + 20, cx, cy - 20, fill=outline_color, width=1.5)
                    self.desenho_node_recursivo(child, highlighted_path, current_path + [idx])