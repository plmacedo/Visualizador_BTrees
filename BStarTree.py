# BStarTree.py
import math

# A classe BStarTreeNode é idêntica à BTreeNode,
# pois reutilizamos a lógica de remoção (com merge 2-para-1).
class BStarTreeNode:
    def __init__(self, t, folha=False):
        self.t = t
        self.folha = folha
        self.keys = []
        self.filhos = []

    def encontrar_chave(self, k):
        idx = 0
        while idx < len(self.keys) and self.keys[idx] < k:
            idx += 1
        return idx
    
    # Métodos de remoção (reutilizados da B-Tree, com contadores)
    def remover(self, k, trace_callback, path, disk_counter):
        disk_counter['reads'] += 1
        trace_callback(f"Analisando nó {self.keys} para remover {k}", path, disk_counter)
        idx = self.encontrar_chave(k)
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
            flag = idx == len(self.keys)
            if len(self.filhos[idx].keys) < self.t:
                self.preencher(idx, trace_callback, path, disk_counter)
            if flag and idx > len(self.keys):
                self.filhos[idx - 1].remover(k, trace_callback, path + [idx - 1], disk_counter)
            else:
                self.filhos[idx].remover(k, trace_callback, path + [idx], disk_counter)

    def remover_de_no_nao_folha(self, idx, trace_callback, path, disk_counter):
        k = self.keys[idx]
        if len(self.filhos[idx].keys) >= self.t:
            pred = self.get_predecessor(idx, disk_counter)
            self.keys[idx] = pred
            disk_counter['writes'] += 1
            trace_callback(f"Substituindo {k} pelo predecessor {pred}", path, disk_counter)
            self.filhos[idx].remover(pred, trace_callback, path + [idx], disk_counter)
        elif len(self.filhos[idx+1].keys) >= self.t:
            succ = self.get_sucessor(idx, disk_counter)
            self.keys[idx] = succ
            disk_counter['writes'] += 1
            trace_callback(f"Substituindo {k} pelo sucessor {succ}", path, disk_counter)
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

    def preencher(self, idx, trace_callback, path, disk_counter):
        if idx != 0 and len(self.filhos[idx-1].keys) >= self.t:
            self.pegar_do_anterior(idx, trace_callback, path, disk_counter)
        elif idx != len(self.keys) and len(self.filhos[idx+1].keys) >= self.t:
            self.pegar_do_proximo(idx, trace_callback, path, disk_counter)
        else:
            if idx != len(self.keys):
                self.fundir(idx, trace_callback, path, disk_counter)
            else:
                self.fundir(idx-1, trace_callback, path, disk_counter)

    def pegar_do_anterior(self, idx, trace_callback, path, disk_counter):
        filho = self.filhos[idx]; irmao = self.filhos[idx-1]
        disk_counter['reads'] += 2; disk_counter['writes'] += 3
        filho.keys.insert(0, self.keys[idx-1])
        if not filho.folha: filho.filhos.insert(0, irmao.filhos.pop())
        self.keys[idx-1] = irmao.keys.pop()
        trace_callback(f"Pegou chave emprestada do irmão à esquerda", path, disk_counter)

    def pegar_do_proximo(self, idx, trace_callback, path, disk_counter):
        filho = self.filhos[idx]; irmao = self.filhos[idx+1]
        disk_counter['reads'] += 2; disk_counter['writes'] += 3
        filho.keys.append(self.keys[idx])
        if not filho.folha: filho.filhos.append(irmao.filhos.pop(0))
        self.keys[idx] = irmao.keys.pop(0)
        trace_callback(f"Pegou chave emprestada do irmão à direita", path, disk_counter)

    def fundir(self, idx, trace_callback, path, disk_counter):
        filho = self.filhos[idx]; irmao = self.filhos[idx+1]
        disk_counter['reads'] += 2; disk_counter['writes'] += 2
        filho.keys.append(self.keys.pop(idx))
        filho.keys.extend(irmao.keys)
        if not filho.folha: filho.filhos.extend(irmao.filhos)
        self.filhos.pop(idx+1)
        trace_callback(f"Merge realizado", path, disk_counter)


class BStarTree:
    def __init__(self, t=3):
        if t < 3:
            raise ValueError("O grau 't' para a Árvore B* deve ser no mínimo 3.")
        self.raiz = BStarTreeNode(t, True)
        self.t = t

    def insere_com_trace(self, key, trace_callback):
        disk_counter = {'reads': 0, 'writes': 0}
        raiz = self.raiz
        disk_counter['reads'] += 1
        if len(raiz.keys) == 2 * self.t - 1:
            new_root = BStarTreeNode(self.t, False)
            new_root.filhos.append(self.raiz)
            disk_counter['writes'] += 1
            self.split_filho_1_para_2(new_root, 0, trace_callback, [], disk_counter)
            self.raiz = new_root
            trace_callback("Nova raiz criada após split", [], disk_counter)
            self.insert_recursivo_com_trace(new_root, key, trace_callback, [], disk_counter)
        else:
            self.insert_recursivo_com_trace(raiz, key, trace_callback, [], disk_counter)

    def insert_recursivo_com_trace(self, node, key, trace_callback, path, disk_counter):
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
                self.handle_filho_cheio(node, i, trace_callback, path, disk_counter)
                i = len(node.keys)
                while i > 0 and key < node.keys[i-1]:
                    i -= 1
            self.insert_recursivo_com_trace(node.filhos[i], key, trace_callback, path + [i], disk_counter)

    def handle_filho_cheio(self, parent, child_idx, trace_callback, path, disk_counter):
        if child_idx < len(parent.filhos) - 1:
            disk_counter['reads'] += 1
            if len(parent.filhos[child_idx + 1].keys) < 2 * self.t - 1:
                trace_callback(f"Nó filho cheio. Redistribuindo com irmão direito.", path, disk_counter)
                self.redistribuir_chaves(parent, child_idx, child_idx + 1, trace_callback, path, disk_counter)
                return
        if child_idx > 0:
            disk_counter['reads'] += 1
            if len(parent.filhos[child_idx - 1].keys) < 2 * self.t - 1:
                trace_callback(f"Nó filho cheio. Redistribuindo com irmão esquerdo.", path, disk_counter)
                self.redistribuir_chaves(parent, child_idx, child_idx - 1, trace_callback, path, disk_counter)
                return
        
        if child_idx < len(parent.filhos) - 1:
             trace_callback(f"Irmãos cheios. Tentando split 2-para-3 com irmão direito.", path, disk_counter)
             self.split_filho_2_para_3(parent, child_idx, trace_callback, path, disk_counter)
        else:
             trace_callback(f"Irmãos cheios. Tentando split 2-para-3 com irmão esquerdo.", path, disk_counter)
             self.split_filho_2_para_3(parent, child_idx - 1, trace_callback, path, disk_counter)

    def redistribuir_chaves(self, parent, full_node_idx, other_node_idx, trace_callback, path, disk_counter):
        disk_counter['writes'] += 3
        full_node = parent.filhos[full_node_idx]
        other_node = parent.filhos[other_node_idx]
        if full_node_idx > other_node_idx:
            other_node.keys.append(parent.keys[other_node_idx])
            parent.keys[other_node_idx] = full_node.keys.pop(0)
            if not full_node.folha:
                other_node.filhos.append(full_node.filhos.pop(0))
        else:
            other_node.keys.insert(0, parent.keys[full_node_idx])
            parent.keys[full_node_idx] = full_node.keys.pop()
            if not full_node.folha:
                other_node.filhos.insert(0, full_node.filhos.pop())
        trace_callback(f"Chaves redistribuídas", path, disk_counter)

    def split_filho_1_para_2(self, parent, i, trace_callback, path, disk_counter):
        disk_counter['writes'] += 3
        t = self.t
        y = parent.filhos[i]
        z = BStarTreeNode(t, y.folha)
        middle_key = y.keys[t - 1]
        z.keys = y.keys[t:]
        y.keys = y.keys[:t - 1]
        if not y.folha:
            z.filhos = y.filhos[t:]
            y.filhos = y.filhos[:t]
        parent.filhos.insert(i + 1, z)
        parent.keys.insert(i, middle_key)
        trace_callback(f"Split 1-para-2 no filho {i}, promoveu {middle_key}", path, disk_counter)
        
    def split_filho_2_para_3(self, parent, i, trace_callback, path, disk_counter):
        disk_counter['writes'] += 4
        t = self.t
        y = parent.filhos[i]
        z = parent.filhos[i + 1]
        parent_key = parent.keys.pop(i)
        w = BStarTreeNode(t, y.folha)
        all_keys = y.keys + [parent_key] + z.keys
        all_children = y.filhos + z.filhos
        
        key_up1_idx = (len(all_keys) // 3)
        key_up2_idx = 2 * (len(all_keys) // 3) + 1
        key_up1 = all_keys[key_up1_idx]
        key_up2 = all_keys[key_up2_idx]
        
        y.keys = all_keys[:key_up1_idx]
        w.keys = all_keys[key_up1_idx + 1:key_up2_idx]
        z.keys = all_keys[key_up2_idx + 1:]

        if not y.folha:
            children_split1 = (len(all_children) // 3)
            children_split2 = 2 * (len(all_children) // 3)
            y.filhos = all_children[:children_split1]
            w.filhos = all_children[children_split1:children_split2]
            z.filhos = all_children[children_split2:]

        parent.keys.insert(i, key_up1)
        parent.keys.insert(i + 1, key_up2)
        parent.filhos.insert(i + 1, w)
        trace_callback(f"Split 2-para-3. Promoveu {key_up1} e {key_up2}", path, disk_counter)

    def remover_com_trace(self, key, trace_callback):
        disk_counter = {'reads': 0, 'writes': 0}
        if not self.raiz:
            trace_callback("Remoção finalizada.", [], disk_counter)
            return

        self.raiz.remover(key, trace_callback, [], disk_counter)
        if len(self.raiz.keys) == 0 and not self.raiz.folha:
            disk_counter['reads'] += 1
            self.raiz = self.raiz.filhos[0]
        trace_callback(f"Remoção finalizada para chave {key}", [], disk_counter)