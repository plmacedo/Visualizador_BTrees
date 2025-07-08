# BPlusTree.py

class BPlusTreeNode:
    def __init__(self, t, folha=False):
        self.t = t
        self.folha = folha
        self.keys = []
        self.children = []
        self.next = None
        self.parent = None

class BPlusTree:
    def __init__(self, t=3):
        self.t = t
        self.raiz = BPlusTreeNode(t, True)

    def insere_com_trace(self, key, trace_callback):
        disk_counter = {'reads': 0, 'writes': 0}
        raiz = self.raiz
        disk_counter['reads'] += 1
        
        if len(raiz.keys) == 2 * self.t - 1:
            nova_raiz = BPlusTreeNode(self.t, False)
            nova_raiz.children.append(self.raiz)
            self.raiz.parent = nova_raiz
            self._split_child(nova_raiz, 0, trace_callback, [], disk_counter)
            self.raiz = nova_raiz
            trace_callback("Nova raiz criada após split", [], disk_counter)
        
        self._inserir_nao_cheio(self.raiz, key, trace_callback, [], disk_counter)

    def _inserir_nao_cheio(self, node, k, trace_callback, path, disk_counter):
        trace_callback(f"Analisando nó {node.keys} para inserir {k}", path, disk_counter)
        
        if node.folha:
            i = 0
            while i < len(node.keys) and k > node.keys[i]:
                i += 1
            node.keys.insert(i, k)
            disk_counter['writes'] += 1
            trace_callback(f"Inseriu chave {k} na folha", path, disk_counter)
        else:
            i = 0
            while i < len(node.keys) and k > node.keys[i]:
                i += 1
            
            trace_callback(f"Descendo para filho {i}", path + [i], disk_counter)
            disk_counter['reads'] += 1
            
            if len(node.children[i].keys) == 2 * self.t - 1:
                self._split_child(node, i, trace_callback, path, disk_counter)
                if k > node.keys[i]:
                    i += 1
            self._inserir_nao_cheio(node.children[i], k, trace_callback, path + [i], disk_counter)

    def _split_child(self, parent, i, trace_callback, path, disk_counter):
        disk_counter['writes'] += 3
        t = self.t
        full_node = parent.children[i]
        novo_node = BPlusTreeNode(t, full_node.folha)
        novo_node.parent = parent

        if full_node.folha:
            mid = t
            novo_node.keys = full_node.keys[mid:]
            full_node.keys = full_node.keys[:mid]
            novo_node.next = full_node.next
            full_node.next = novo_node
            parent.keys.insert(i, novo_node.keys[0])
        else:
            mid = t - 1
            parent.keys.insert(i, full_node.keys.pop(mid))
            novo_node.keys = full_node.keys[mid:]
            full_node.keys = full_node.keys[:mid]
            novo_node.children = full_node.children[mid + 1:]
            for child in novo_node.children:
                child.parent = novo_node
            full_node.children = full_node.children[:mid + 1]

        parent.children.insert(i + 1, novo_node)
        trace_callback(f"Split no filho {i}, promoveu chave {parent.keys[i]}", path, disk_counter)
    

    # --- LÓGICA DE REMOÇÃO COMPLETAMENTE REESCRITA (VERSÃO 2) ---
    
    def remover_com_trace(self, key, trace_callback):
        disk_counter = {'reads': 0, 'writes': 0}
        self._remover_recursivo(self.raiz, key, trace_callback, [], disk_counter)
        trace_callback(f"Remoção finalizada para chave {key}", [], disk_counter)

    def _remover_recursivo(self, node, k, trace_callback, path, disk_counter):
        disk_counter['reads'] += 1
        trace_callback(f"Analisando nó {node.keys} para remover {k}", path, disk_counter)

        if node.folha:
            if k in node.keys:
                # Remove a chave e o valor associado
                node.keys.remove(k)
                disk_counter['writes'] += 1
                trace_callback(f"Removeu chave {k} da folha", path, disk_counter)
                
                # Após a remoção, se o nó estiver em underflow e não for a raiz, rebalanceia
                if len(node.keys) < self.t - 1 and node != self.raiz:
                    self._rebalancear_folha(node, trace_callback, path, disk_counter)
            else:
                trace_callback(f"Chave {k} não encontrada na folha", path, disk_counter)
            return

        # Para nós internos, encontra o filho correto para descer
        i = 0
        while i < len(node.keys) and k >= node.keys[i]:
            i += 1

        filho_a_descer = node.children[i]
        trace_callback(f"Descendo para o filho {i}", path + [i], disk_counter)
        
        # Estratégia Top-Down: Garante que o filho tenha chaves suficientes ANTES de descer
        if len(filho_a_descer.keys) == self.t - 1:
            self._preencher_filho(node, i, trace_callback, path, disk_counter)
            # A estrutura pode ter mudado, recalcula o caminho
            i = 0
            while i < len(node.keys) and k >= node.keys[i]:
                i += 1
        
        self._remover_recursivo(node.children[i], k, trace_callback, path + [i], disk_counter)

    def _preencher_filho(self, parent, child_idx, trace_callback, path, disk_counter):
        # Tenta emprestar do irmão esquerdo
        if child_idx > 0 and len(parent.children[child_idx - 1].keys) > self.t - 1:
            trace_callback(f"Filho {child_idx} com poucas chaves. Pegando emprestado do irmão esquerdo.", path, disk_counter)
            self._pegar_do_anterior(parent, child_idx, disk_counter)
        # Tenta emprestar do irmão direito
        elif child_idx < len(parent.keys) and len(parent.children[child_idx + 1].keys) > self.t - 1:
            trace_callback(f"Filho {child_idx} com poucas chaves. Pegando emprestado do irmão direito.", path, disk_counter)
            self._pegar_do_proximo(parent, child_idx, disk_counter)
        # Se não der para emprestar, faz o merge
        else:
            if child_idx < len(parent.keys):
                trace_callback(f"Não pode pegar emprestado. Fazendo merge com irmão direito.", path, disk_counter)
                self._fundir_filhos(parent, child_idx, trace_callback, path, disk_counter)
            else:
                trace_callback(f"Não pode pegar emprestado. Fazendo merge com irmão esquerdo.", path, disk_counter)
                self._fundir_filhos(parent, child_idx - 1, trace_callback, path, disk_counter)
                
    def _pegar_do_anterior(self, parent, child_idx, disk_counter):
        disk_counter['reads'] += 2; disk_counter['writes'] += 3
        filho = parent.children[child_idx]
        irmao = parent.children[child_idx - 1]
        
        # Move chave/filho do irmão para o filho atual através do pai
        filho.keys.insert(0, irmao.keys.pop())
        if not irmao.folha:
            filho.children.insert(0, irmao.children.pop())
            filho.children[0].parent = filho
        
        # Atualiza a chave no pai
        parent.keys[child_idx - 1] = filho.keys[0]

    def _pegar_do_proximo(self, parent, child_idx, disk_counter):
        disk_counter['reads'] += 2; disk_counter['writes'] += 3
        filho = parent.children[child_idx]
        irmao = parent.children[child_idx + 1]

        filho.keys.append(irmao.keys.pop(0))
        if not irmao.folha:
            filho.children.append(irmao.children.pop(0))
            filho.children[-1].parent = filho
        
        parent.keys[child_idx] = irmao.keys[0]

    def _fundir_filhos(self, parent, idx_esquerdo, trace_callback, path, disk_counter):
        disk_counter['reads'] += 2; disk_counter['writes'] += 2
        no_esquerdo = parent.children[idx_esquerdo]
        no_direito = parent.children[idx_esquerdo + 1]

        # Move todas as chaves e filhos do nó direito para o esquerdo
        no_esquerdo.keys.extend(no_direito.keys)
        if not no_esquerdo.folha:
            no_esquerdo.children.extend(no_direito.children)
            for child in no_direito.children:
                child.parent = no_esquerdo
        else:
            # Se for folha, atualiza a lista encadeada
            no_esquerdo.next = no_direito.next
        
        # Remove a chave e o ponteiro do pai
        parent.keys.pop(idx_esquerdo)
        parent.children.pop(idx_esquerdo + 1)
        
        trace_callback("Merge completado.", path + [idx_esquerdo], disk_counter)

        # Se o pai ficar vazio (e não for a raiz), ele também precisa ser removido
        if not parent.keys and parent == self.raiz:
            self.raiz = no_esquerdo
            no_esquerdo.parent = None

    def _rebalancear_folha(self, folha, trace_callback, path, disk_counter):
        # Esta função simplificada lida com rebalanceamento PÓS remoção na folha
        # É chamada quando a folha está em underflow
        parent = folha.parent
        if parent is None: return # Raiz

        idx_no_pai = parent.children.index(folha)

        # Tenta pegar emprestado do irmão esquerdo
        if idx_no_pai > 0 and len(parent.children[idx_no_pai - 1].keys) > self.t - 1:
            trace_callback(f"Folha com poucas chaves. Pegando do irmão esquerdo.", path, disk_counter)
            self._pegar_do_anterior(parent, idx_no_pai, disk_counter)
        # Tenta pegar emprestado do irmão direito
        elif idx_no_pai < len(parent.keys) and len(parent.children[idx_no_pai + 1].keys) > self.t - 1:
            trace_callback(f"Folha com poucas chaves. Pegando do irmão direito.", path, disk_counter)
            self._pegar_do_proximo(parent, idx_no_pai, disk_counter)
        # Faz merge
        else:
            if idx_no_pai < len(parent.keys):
                trace_callback(f"Não pode pegar emprestado. Fazendo merge com irmão direito.", path, disk_counter)
                self._fundir_filhos(parent, idx_no_pai, trace_callback, path, disk_counter)
            else:
                trace_callback(f"Não pode pegar emprestado. Fazendo merge com irmão esquerdo.", path, disk_counter)
                self._fundir_filhos(parent, idx_no_pai - 1, trace_callback, path, disk_counter)