# Btree.py

class BTreeNode:
    def __init__(self, t, folha=False):
        self.t = t
        self.folha = folha
        self.keys = []
        self.filhos = []

    # A lógica de remoção reside no próprio nó, de forma recursiva.
    def remover(self, k, trace_callback, path, disk_counter):
        disk_counter['reads'] += 1
        trace_callback(f"Analisando nó {self.keys} para remover {k}", path, disk_counter)
        
        idx = 0
        while idx < len(self.keys) and self.keys[idx] < k:
            idx += 1

        if idx < len(self.keys) and self.keys[idx] == k:
            if self.folha:
                self.keys.pop(idx)
                disk_counter['writes'] += 1
                trace_callback(f"Removeu chave {k} da folha", path, disk_counter)
            else:
                self.remover_de_no_nao_folha(idx, trace_callback, path, disk_counter)
        else:
            if self.folha:
                trace_callback(f"Chave {k} não encontrada", path, disk_counter)
                return

            filho_a_descer = self.filhos[idx]
            if len(filho_a_descer.keys) < self.t:
                self.preencher_filho(idx, trace_callback, path, disk_counter)
            
            if idx > len(self.keys):
                self.filhos[idx - 1].remover(k, trace_callback, path + [idx-1], disk_counter)
            else:
                self.filhos[idx].remover(k, trace_callback, path + [idx], disk_counter)

    def remover_de_no_nao_folha(self, idx, trace_callback, path, disk_counter):
        k = self.keys[idx]
        if len(self.filhos[idx].keys) >= self.t:
            pred = self.get_predecessor(idx, disk_counter)
            trace_callback(f"Substituindo {k} pelo predecessor {pred}", path, disk_counter)
            self.keys[idx] = pred
            disk_counter['writes'] += 1
            self.filhos[idx].remover(pred, trace_callback, path + [idx], disk_counter)
        elif len(self.filhos[idx+1].keys) >= self.t:
            succ = self.get_sucessor(idx, disk_counter)
            trace_callback(f"Substituindo {k} pelo sucessor {succ}", path, disk_counter)
            self.keys[idx] = succ
            disk_counter['writes'] += 1
            self.filhos[idx+1].remover(succ, trace_callback, path + [idx + 1], disk_counter)
        else:
            trace_callback(f"Fazendo merge dos filhos {idx} e {idx+1}", path, disk_counter)
            self.fundir(idx, trace_callback, path, disk_counter)
            self.filhos[idx].remover(k, trace_callback, path + [idx], disk_counter)

    def get_predecessor(self, idx, disk_counter):
        atual = self.filhos[idx]
        disk_counter['reads'] += 1
        while not atual.folha:
            atual = atual.filhos[-1]
            disk_counter['reads'] += 1
        return atual.keys[-1]

    def get_sucessor(self, idx, disk_counter):
        atual = self.filhos[idx+1]
        disk_counter['reads'] += 1
        while not atual.folha:
            atual = atual.filhos[0]
            disk_counter['reads'] += 1
        return atual.keys[0]

    def preencher_filho(self, idx, trace_callback, path, disk_counter):
        if idx > 0 and len(self.filhos[idx - 1].keys) >= self.t:
            self.pegar_do_anterior(idx, trace_callback, path, disk_counter)
        elif idx < len(self.filhos) - 1 and len(self.filhos[idx + 1].keys) >= self.t:
            self.pegar_do_proximo(idx, trace_callback, path, disk_counter)
        else:
            if idx < len(self.keys):
                self.fundir(idx, trace_callback, path, disk_counter)
            else:
                self.fundir(idx - 1, trace_callback, path, disk_counter)

    def pegar_do_anterior(self, idx, trace_callback, path, disk_counter):
        disk_counter['reads'] += 2; disk_counter['writes'] += 3
        filho = self.filhos[idx]
        irmao = self.filhos[idx - 1]
        filho.keys.insert(0, self.keys[idx-1])
        if not irmao.folha:
            filho.filhos.insert(0, irmao.filhos.pop())
        parent_key = irmao.keys.pop()
        self.keys[idx-1] = parent_key
        trace_callback("Pegou chave emprestada do irmão à esquerda", path, disk_counter)

    def pegar_do_proximo(self, idx, trace_callback, path, disk_counter):
        disk_counter['reads'] += 2; disk_counter['writes'] += 3
        filho = self.filhos[idx]
        irmao = self.filhos[idx + 1]
        filho.keys.append(self.keys[idx])
        if not irmao.folha:
            filho.filhos.append(irmao.filhos.pop(0))
        self.keys[idx] = irmao.keys.pop(0)
        trace_callback("Pegou chave emprestada do irmão à direita", path, disk_counter)

    def fundir(self, idx, trace_callback, path, disk_counter):
        disk_counter['reads'] += 2; disk_counter['writes'] += 2
        filho = self.filhos[idx]
        irmao = self.filhos[idx + 1]
        filho.keys.append(self.keys.pop(idx))
        filho.keys.extend(irmao.keys)
        if not filho.folha:
            filho.filhos.extend(irmao.filhos)
        self.filhos.pop(idx + 1)
        trace_callback("Merge realizado.", path + [idx], disk_counter)


class BTree:
    def __init__(self, t=2):
        self.raiz = BTreeNode(t, True)
        self.t = t

    def insere_com_trace(self, key, trace_callback):
        disk_counter = {'reads': 0, 'writes': 0}
        raiz = self.raiz
        disk_counter['reads'] += 1
        if len(raiz.keys) == 2 * self.t - 1:
            nova_raiz = BTreeNode(self.t, False)
            nova_raiz.filhos.append(self.raiz)
            disk_counter['writes'] += 1
            self._split_filho(nova_raiz, 0, trace_callback, [], disk_counter)
            self.raiz = nova_raiz
            trace_callback("Nova raiz criada após split", [], disk_counter)
            self._insert_recursivo(self.raiz, key, trace_callback, [], disk_counter)
        else:
            self._insert_recursivo(self.raiz, key, trace_callback, [], disk_counter)

    def _insert_recursivo(self, node, key, trace_callback, path, disk_counter):
        trace_callback(f"Analisando nó {node.keys} para inserir {key}", path, disk_counter)
        i = len(node.keys) - 1
        if node.folha:
            node.keys.append(None)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                i -= 1
            node.keys[i + 1] = key
            disk_counter['writes'] += 1
            trace_callback(f"Inseriu chave {key}", path, disk_counter)
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            
            disk_counter['reads'] += 1
            if len(node.filhos[i].keys) == 2 * self.t - 1:
                self._split_filho(node, i, trace_callback, path, disk_counter)
                if key > node.keys[i]:
                    i += 1
            self._insert_recursivo(node.filhos[i], key, trace_callback, path + [i], disk_counter)

    def _split_filho(self, parent, i, trace_callback, path, disk_counter):
        disk_counter['writes'] += 3
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
        trace_callback(f"Split no filho {i}, promoveu chave {middle_key}", path, disk_counter)

    def remover_com_trace(self, key, trace_callback):
        disk_counter = {'reads': 0, 'writes': 0}
        if not self.raiz:
            trace_callback("Remoção finalizada.", [], disk_counter)
            return
        
        # A chamada inicial é feita na raiz, que então usa seus próprios métodos
        self.raiz.remover(key, trace_callback, [], disk_counter)

        if len(self.raiz.keys) == 0 and not self.raiz.folha:
            disk_counter['reads'] += 1
            self.raiz = self.raiz.filhos[0]

        trace_callback(f"Remoção finalizada para chave {key}", [], disk_counter)