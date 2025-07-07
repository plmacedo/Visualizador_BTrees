class BTreeNode:
    def __init__(self, t, folha=False):
        self.t = t
        self.folha = folha
        self.keys = []
        self.filhos = []

    def clone(self):
        new_node = BTreeNode(self.t, self.folha)
        new_node.keys = list(self.keys)
        new_node.filhos = [child.clone() for child in self.filhos]
        return new_node

    def buscar(self, k):
        i = 0
        while i < len(self.keys) and k > self.keys[i]:
            i += 1
        if i < len(self.keys) and self.keys[i] == k:
            return self
        if self.folha:
            return None
        return self.filhos[i].buscar(k)

    # --- Funções de remoção com rastreamento e caminho ---
    def remover(self, k, trace_callback=None, path=None):
        if path is None:
            path = []
        idx = self.encontrar_chave(k)
        if trace_callback:
            trace_callback(f"Analisando nó {self.keys} para remover {k}", path)
        if idx < len(self.keys) and self.keys[idx] == k:
            if self.folha:
                self.keys.pop(idx)
                if trace_callback:
                    trace_callback(f"Removeu chave {k} de folha {self.keys}", path)
            else:
                self.remover_de_no_folha(idx, trace_callback, path)
        else:
            if self.folha:
                if trace_callback:
                    trace_callback(f"Chave {k} não encontrada na folha {self.keys}", path)
                return
            if len(self.filhos[idx].keys) < self.t:
                self.preencher(idx, trace_callback, path + [idx])
                if trace_callback:
                    trace_callback(f"Preenchido filho {idx} antes de remover {k}", path + [idx])
            if idx > len(self.keys):
                self.filhos[idx - 1].remover(k, trace_callback, path + [idx - 1])
            else:
                self.filhos[idx].remover(k, trace_callback, path + [idx])

    def encontrar_chave(self, k):
        idx = 0
        while idx < len(self.keys) and self.keys[idx] < k:
            idx += 1
        return idx

    def remover_de_no_folha(self, idx, trace_callback=None, path=None):
        k = self.keys[idx]
        if len(self.filhos[idx].keys) >= self.t:
            pred = self.get_predecessor(idx)
            self.keys[idx] = pred
            if trace_callback:
                trace_callback(f"Substituindo {k} pelo predecessor {pred}", path)
            self.filhos[idx].remover(pred, trace_callback, path + [idx])
        elif len(self.filhos[idx + 1].keys) >= self.t:
            succ = self.get_sucessor(idx)
            self.keys[idx] = succ
            if trace_callback:
                trace_callback(f"Substituindo {k} pelo sucessor {succ}", path)
            self.filhos[idx + 1].remover(succ, trace_callback, path + [idx + 1])
        else:
            if trace_callback:
                trace_callback(f"Fazendo merge dos filhos {idx} e {idx+1} para remover {k}", path)
            self.fundir(idx, trace_callback, path)
            self.filhos[idx].remover(k, trace_callback, path + [idx])

    def get_predecessor(self, idx):
        atual = self.filhos[idx]
        while not atual.folha:
            atual = atual.filhos[-1]
        return atual.keys[-1]

    def get_sucessor(self, idx):
        atual = self.filhos[idx + 1]
        while not atual.folha:
            atual = atual.filhos[0]
        return atual.keys[0]

    def preencher(self, idx, trace_callback=None, path=None):
        if path is None:
            path = []
        if idx != 0 and len(self.filhos[idx - 1].keys) >= self.t:
            if trace_callback:
                trace_callback(f"Pegando chave emprestada do irmão à esquerda do filho {idx}", path)
            self.pegar_do_anterior(idx, trace_callback, path)
        elif idx != len(self.keys) and len(self.filhos[idx + 1].keys) >= self.t:
            if trace_callback:
                trace_callback(f"Pegando chave emprestada do irmão à direita do filho {idx}", path)
            self.pegar_do_proximo(idx, trace_callback, path)
        else:
            if idx != len(self.keys):
                if trace_callback:
                    trace_callback(f"Fazendo merge do filho {idx} com o filho {idx+1}", path)
                self.fundir(idx, trace_callback, path)
            else:
                if trace_callback:
                    trace_callback(f"Fazendo merge do filho {idx-1} com o filho {idx}", path)
                self.fundir(idx - 1, trace_callback, path)

    def pegar_do_anterior(self, idx, trace_callback=None, path=None):
        filho = self.filhos[idx]
        irmao = self.filhos[idx - 1]
        filho.keys.insert(0, self.keys[idx - 1])
        if not filho.folha:
            filho.filhos.insert(0, irmao.filhos.pop())
        self.keys[idx - 1] = irmao.keys.pop()
        if trace_callback:
            trace_callback(f"Pegou chave do irmão à esquerda para filho {idx}", path + [idx])

    def pegar_do_proximo(self, idx, trace_callback=None, path=None):
        filho = self.filhos[idx]
        irmao = self.filhos[idx + 1]
        filho.keys.append(self.keys[idx])
        if not filho.folha:
            filho.filhos.append(irmao.filhos.pop(0))
        self.keys[idx] = irmao.keys.pop(0)
        if trace_callback:
            trace_callback(f"Pegou chave do irmão à direita para filho {idx}", path + [idx])

    def fundir(self, idx, trace_callback=None, path=None):
        filho = self.filhos[idx]
        irmao = self.filhos[idx + 1]
        filho.keys.append(self.keys[idx])
        filho.keys.extend(irmao.keys)
        if not filho.folha:
            filho.filhos.extend(irmao.filhos)
        self.keys.pop(idx)
        self.filhos.pop(idx + 1)
        if trace_callback:
            trace_callback(f"Merge realizado entre filhos {idx} e {idx+1}", path + [idx])

class BTree:
    def __init__(self, t=2):
        self.raiz = BTreeNode(t, True)
        self.t = t

    def insere_com_trace(self, key, trace_callback):
        raiz = self.raiz
        if len(raiz.keys) == 2 * self.t - 1:
            new_root = BTreeNode(self.t, False)
            new_root.filhos.append(self.raiz)
            self.split_filho_com_trace(new_root, 0, trace_callback, path=[])
            self.raiz = new_root
            trace_callback("Nova raiz criada após split", [])
            self.insert_recursivo_com_trace(new_root, key, trace_callback, path=[])
        else:
            self.insert_recursivo_com_trace(raiz, key, trace_callback, path=[])

    def insert_recursivo_com_trace(self, node, key, trace_callback, path):
        i = len(node.keys) - 1
        if node.folha:
            node.keys.append(None)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                i -= 1
            node.keys[i + 1] = key
            trace_callback(f"Inseriu chave {key}", path)
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            trace_callback(f"Descendo para o filho {i}", path)
            if len(node.filhos[i].keys) == 2 * self.t - 1:
                self.split_filho_com_trace(node, i, trace_callback, path=path)
                if key > node.keys[i]:
                    i += 1
            self.insert_recursivo_com_trace(node.filhos[i], key, trace_callback, path + [i])

    def split_filho_com_trace(self, parent, i, trace_callback, path):
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
        trace_callback(f"Split no filho {i}, promoveu chave {middle_key}", path + [i])

    def remover_com_trace(self, key, trace_callback):
        if not self.raiz:
            return
        self.raiz.remover(key, trace_callback, path=[])
        if len(self.raiz.keys) == 0:
            if self.raiz.folha:
                self.raiz = BTreeNode(self.t, True)
            else:
                self.raiz = self.raiz.filhos[0]
        if trace_callback:
            trace_callback(f"Remoção finalizada para chave {key}", [])
