class BTreeNode:
    def __init__(self, t, leaf=False):
        self.t = t
        self.leaf = leaf
        self.keys = []
        self.children = []

    def clone(self):
        """Faz uma cópia rasa da árvore, usada para animação"""
        new_node = BTreeNode(self.t, self.leaf)
        new_node.keys = list(self.keys)
        new_node.children = [child.clone() for child in self.children]
        return new_node

class BTree:
    def __init__(self, t=2):
        self.root = BTreeNode(t, True)
        self.t = t

    def insert_with_trace(self, key, trace_callback):
        root = self.root
        if len(root.keys) == 2 * self.t - 1:
            new_root = BTreeNode(self.t, False)
            new_root.children.append(self.root)
            self._split_child_with_trace(new_root, 0, trace_callback)
            self.root = new_root
            trace_callback("Nova raiz criada após split")
            self._insert_non_full_with_trace(new_root, key, trace_callback)
        else:
            self._insert_non_full_with_trace(root, key, trace_callback)

    def _insert_non_full_with_trace(self, node, key, trace_callback):
        i = len(node.keys) - 1
        if node.leaf:
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
            if len(node.children[i].keys) == 2 * self.t - 1:
                self._split_child_with_trace(node, i, trace_callback)
                if key > node.keys[i]:
                    i += 1
            self._insert_non_full_with_trace(node.children[i], key, trace_callback)

    def _split_child_with_trace(self, parent, i, trace_callback):
        t = self.t
        y = parent.children[i]
        z = BTreeNode(t, y.leaf)

        middle_key = y.keys[t - 1]
        z.keys = y.keys[t:]
        y.keys = y.keys[:t - 1]

        if not y.leaf:
            z.children = y.children[t:]
            y.children = y.children[:t]

        parent.children.insert(i + 1, z)
        parent.keys.insert(i, middle_key)

        trace_callback("Split no filho {}, promoveu chave {}".format(i, middle_key))