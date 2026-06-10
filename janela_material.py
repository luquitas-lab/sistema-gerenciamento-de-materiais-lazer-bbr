import tkinter as tk
from tkinter import ttk, messagebox

class JanelaMaterial(tk.Toplevel):
    def __init__(self, master, sistema):
        super().__init__(master)
        self.sistema = sistema
        self.title("Gerenciar Materiais")
        self.geometry("400x530") # Altura ajustada para caber o seletor
        self.transient(master)
        self.grab_set()

        # Configura o seletor de monitor antes de desenhar as abas
        if not self._configurar_monitor_responsavel():
            return

        self.abas = ttk.Notebook(self)
        self.abas.pack(fill="both", expand=True, padx=10, pady=10)

        self.aba_cadastrar = tk.Frame(self.abas)
        self.aba_atualizar = tk.Frame(self.abas)
        self.aba_deletar = tk.Frame(self.abas)

        self.abas.add(self.aba_cadastrar, text="Cadastrar Novo")
        self.abas.add(self.aba_atualizar, text="Atualizar")
        self.abas.add(self.aba_deletar, text="Deletar")

        self._construir_aba_cadastrar()
        self._construir_aba_atualizar()
        self._construir_aba_deletar()
        self.atualizar_listas_mat()

    def _configurar_monitor_responsavel(self):
        try:
            monitores_db = self.sistema.listar_monitores()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar monitores: {e}", parent=self)
            self.destroy()
            return False

        if not monitores_db:
            messagebox.showwarning("Aviso", "Você precisa cadastrar pelo menos um monitor antes de gerenciar materiais!", parent=self)
            self.destroy()
            return False

        lista_monitores = [f"{m[0]} - {m[1]}" for m in monitores_db]
        frame_monitor = tk.Frame(self)
        frame_monitor.pack(pady=10)
        tk.Label(frame_monitor, text="Monitor Responsável:", font=("Arial", 11, "bold")).pack(side="left", padx=5)
        self.combo_monitor_resp = ttk.Combobox(frame_monitor, values=lista_monitores, state="readonly", width=20)
        self.combo_monitor_resp.current(0)
        self.combo_monitor_resp.pack(side="left", padx=5)
        return True

    def _construir_aba_cadastrar(self):
        tk.Label(self.aba_cadastrar, text="Gerenciar Materiais", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(self.aba_cadastrar, text="Nome do Material (ex: Raquete):").pack()
        self.entry_nome = tk.Entry(self.aba_cadastrar, width=30)
        self.entry_nome.pack(pady=2)
        tk.Label(self.aba_cadastrar, text="Quantidade Inicial no Estoque:").pack()
        self.entry_quantidade = tk.Entry(self.aba_cadastrar, width=30)
        self.entry_quantidade.pack(pady=2)
        tk.Label(self.aba_cadastrar, text="Observações (Marca, Cor, etc):").pack()
        self.entry_obs = tk.Entry(self.aba_cadastrar, width=30)
        self.entry_obs.pack(pady=2)
        tk.Button(self.aba_cadastrar, text="Salvar Material", command=self.salvar_material, bg="#0052cc", fg="white", font=("Arial", 10, "bold")).pack(pady=15)

    def _construir_aba_atualizar(self):
        tk.Label(self.aba_atualizar, text="Atualizar Material", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(self.aba_atualizar, text="Selecione o Material antigo:").pack()
        self.combo_atualizar_mat = ttk.Combobox(self.aba_atualizar, state="readonly", width=27)
        self.combo_atualizar_mat.pack(pady=2)
        self.combo_atualizar_mat.bind("<<ComboboxSelected>>", self.preencher_dados_atuais)
        tk.Label(self.aba_atualizar, text="Novo Nome:").pack()
        self.entry_novo_nome_mat = tk.Entry(self.aba_atualizar, width=30)
        self.entry_novo_nome_mat.pack(pady=2)
        tk.Label(self.aba_atualizar, text="Novas Observações:").pack()
        self.entry_novas_obs = tk.Entry(self.aba_atualizar, width=30)
        self.entry_novas_obs.pack(pady=2)
        tk.Button(self.aba_atualizar, text="Atualizar Material", command=self.btn_atualizar_mat_click, bg="#0052cc", fg="white", font=("Arial", 10, "bold")).pack(pady=15)

    def preencher_dados_atuais(self, event=None):
        selecionado = self.combo_atualizar_mat.get()
        if not selecionado: return
        
        id_mat = int(selecionado.split(" - ")[0])
        materiais_db = self.sistema.listar_materiais()
        material = next((m for m in materiais_db if m[0] == id_mat), None)
        
        if material:
            self.entry_novo_nome_mat.delete(0, tk.END)
            self.entry_novo_nome_mat.insert(0, material[1])  # Preenche o nome
            
            self.entry_novas_obs.delete(0, tk.END)
            if material[3]:  # Preenche a observação se ela existir
                self.entry_novas_obs.insert(0, material[3])

    def _construir_aba_deletar(self):
        tk.Label(self.aba_deletar, text="Deletar Material", font=("Arial", 14, "bold"), fg="red").pack(pady=15)
        tk.Label(self.aba_deletar, text="Selecione o Material:").pack()
        self.combo_deletar_mat = ttk.Combobox(self.aba_deletar, state="readonly", width=27)
        self.combo_deletar_mat.pack(pady=5)
        tk.Button(self.aba_deletar, text="🗑️ Deletar Material", command=self.btn_deletar_mat_click, bg="red", fg="white", font=("Arial", 10, "bold")).pack(pady=20)

    def atualizar_listas_mat(self):
        # 1. Salva o ID atual antes de recarregar a lista
        sel_atual = self.combo_atualizar_mat.get().split(" - ")[0] if self.combo_atualizar_mat.get() else None
        sel_del = self.combo_deletar_mat.get().split(" - ")[0] if self.combo_deletar_mat.get() else None

        try:
            materiais_db = self.sistema.listar_materiais()
            lista_formatada = [f"{m[0]} - {m[1]}" for m in materiais_db]
            self.combo_atualizar_mat['values'] = lista_formatada
            self.combo_deletar_mat['values'] = lista_formatada
            
            if lista_formatada:
                # 2. Procura a posição do ID antigo e restaura o foco
                idx_atual = next((i for i, v in enumerate(lista_formatada) if v.startswith(f"{sel_atual} - ")), 0)
                self.combo_atualizar_mat.current(idx_atual)
                
                idx_del = next((i for i, v in enumerate(lista_formatada) if v.startswith(f"{sel_del} - ")), 0)
                self.combo_deletar_mat.current(idx_del)
                
                self.preencher_dados_atuais()
            else:
                self.combo_atualizar_mat.set('')
                self.combo_deletar_mat.set('')
                # Resolve o Bug 2 (leia abaixo)
                self.entry_novo_nome_mat.delete(0, tk.END)
                self.entry_novas_obs.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar listas: {e}", parent=self)

    def salvar_material(self):
        nome = self.entry_nome.get().strip()
        quantidade_texto = self.entry_quantidade.get()
        observacoes = self.entry_obs.get()
        
        if nome == "" or quantidade_texto == "":
            messagebox.showerror("Erro", "Nome e quantidade são obrigatórios!", parent=self)
            return
            
        nomes_existentes = [item.split(" - ", 1)[1].lower() for item in self.combo_atualizar_mat['values']]
        if nome.lower() in nomes_existentes:
            messagebox.showwarning("Aviso", f"Já existe um material com o nome '{nome}' cadastrado!", parent=self)
            return

        try:
            quantidade = int(quantidade_texto)
            if quantidade < 0:
                messagebox.showerror("Erro", "A quantidade inicial não pode ser negativa!", parent=self)
                return
        except ValueError:
            messagebox.showerror("Erro", "A quantidade deve ser um número inteiro!", parent=self)
            return
            
        try:
            monitor_selecionado = self.combo_monitor_resp.get()
            id_monitor = int(monitor_selecionado.split(" - ")[0])
            self.sistema.criar_material(nome, quantidade, observacoes, id_monitor=id_monitor)
            messagebox.showinfo("Sucesso", f"Material '{nome}' cadastrado!", parent=self)
            self.entry_nome.delete(0, tk.END)
            self.entry_quantidade.delete(0, tk.END)
            self.entry_obs.delete(0, tk.END)
            self.atualizar_listas_mat() 
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {e}", parent=self)

    def btn_atualizar_mat_click(self):
        selecionado = self.combo_atualizar_mat.get()
        novo_nome = self.entry_novo_nome_mat.get().strip()
        novas_obs = self.entry_novas_obs.get()
        
        if not selecionado or novo_nome == "":
            messagebox.showerror("Erro", "Selecione o material e preencha o novo nome!", parent=self)
            return
        
        nome_antigo = selecionado.split(" - ", 1)[1]
            
        if novo_nome.lower() != nome_antigo.lower():
            nomes_existentes = [item.split(" - ", 1)[1].lower() for item in self.combo_atualizar_mat['values']]
            if novo_nome.lower() in nomes_existentes:
                messagebox.showwarning("Aviso", f"Já existe outro material chamado '{novo_nome}' no sistema!", parent=self)
                return

        id_mat = int(selecionado.split(" - ")[0])
        monitor_selecionado = self.combo_monitor_resp.get()
        id_monitor = int(monitor_selecionado.split(" - ")[0])
        
        try:
            self.sistema.atualizar_material(id_mat, novo_nome, novas_obs, id_monitor=id_monitor)
            messagebox.showinfo("Sucesso", "Material atualizado com sucesso e log registrado!", parent=self)
            self.entry_novo_nome_mat.delete(0, tk.END)
            self.entry_novas_obs.delete(0, tk.END)
            self.atualizar_listas_mat()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {e}", parent=self)

    def btn_deletar_mat_click(self):
        selecionado = self.combo_deletar_mat.get()
        if not selecionado:
            messagebox.showerror("Erro", "Selecione um material para deletar!", parent=self)
            return
        resposta = messagebox.askyesno("Confirmar Exclusão", f"Você tem certeza que deseja deletar o material:\n\n{selecionado}?", parent=self)
        if resposta:
            id_mat = int(selecionado.split(" - ")[0])
            monitor_selecionado = self.combo_monitor_resp.get()
            id_monitor = int(monitor_selecionado.split(" - ")[0])
            try:
                self.sistema.deletar_material(id_mat, id_monitor=id_monitor)
                messagebox.showinfo("Sucesso", "Material deletado do sistema!", parent=self)
                self.atualizar_listas_mat()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao apagar o material: {e}", parent=self)