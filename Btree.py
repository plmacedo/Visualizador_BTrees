class BTreeNode:
    def __init__(self, t, folha=False):
        self.t = t
        self.folha = folha
        self.keys = []
        self.filhos = []

    def clone(self):
        """Faz uma cópia rasa da árvore, usada para animação"""
        new_node = BTreeNode(self.t, self.folha)
        new_node.keys = list(self.keys)
        new_node.filhos = [child.clone() for child in self.filhos]
        return new_node

class BTree:
    def __init__(self, t=2):
        self.raiz = BTreeNode(t, True)
        self.t = t

    def insere_com_trace(self, key, trace_callback): ## realiza a inserção lidando com a raiz cheia (com rastreamento)
        raiz = self.raiz
        if len(raiz.keys) == 2 * self.t - 1:
            new_root = BTreeNode(self.t, False)
            new_root.filhos.append(self.raiz)
            self.split_filho_com_trace(new_root, 0, trace_callback)
            self.raiz = new_root
            trace_callback("Nova raiz criada após split") ## captura o estado da árvore no momento e armazena para a animação visual posteriormente
            self.insert_recursivo_com_trace(new_root, key, trace_callback)
        else:
            self.insert_recursivo_com_trace(raiz, key, trace_callback)

    def insert_recursivo_com_trace(self, node, key, trace_callback): ## inserção recursiva em nó não-cheio. (com rastreamento)
        i = len(node.keys) - 1
        if node.folha:
            node.keys.append(None)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                i -= 1
            node.keys[i + 1] = key
            trace_callback("Inseriu chave {}".format(key))
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            trace_callback("Descendo para o filho {}".format(i))
            if len(node.filhos[i].keys) == 2 * self.t - 1:
                self.split_filho_com_trace(node, i, trace_callback)
                if key > node.keys[i]:
                    i += 1
            self.insert_recursivo_com_trace(node.filhos[i], key, trace_callback)

    def split_filho_com_trace(self, parent, i, trace_callback): ##divide nó filho cheio, promove a chave do meio ao parent e cria novo irmão a direita. (Com rastreamento)
        t = self.t
        y = parent.filhos[i]
        z = BTreeNode(t, y.folha)

        middle_key = y.keys[t - 1]
        z.keys = y.keys[t:]
        y.keys = y.keys[:t - 1]

        if not y.folha:
            z.filhos = y.filhos[t:]
            y.filhos = y.filhos[:t]

        parent.filhos.insert(i + 1, z)
        parent.keys.insert(i, middle_key)

        trace_callback("Split no filho {}, promoveu chave {}".format(i, middle_key))