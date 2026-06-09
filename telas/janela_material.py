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
        tk.Label(self.aba_atualizar, text="Novo Nome:").pack()
        self.entry_novo_nome_mat = tk.Entry(self.aba_atualizar, width=30)
        self.entry_novo_nome_mat.pack(pady=2)
        tk.Label(self.aba_atualizar, text="Nova Quantidade:").pack()
        self.entry_nova_qtd = tk.Entry(self.aba_atualizar, width=30)
        self.entry_nova_qtd.pack(pady=2)
        tk.Label(self.aba_atualizar, text="Novas Observações:").pack()
        self.entry_novas_obs = tk.Entry(self.aba_atualizar, width=30)
        self.entry_novas_obs.pack(pady=2)
        tk.Button(self.aba_atualizar, text="Atualizar Material", command=self.btn_atualizar_mat_click, bg="#0052cc", fg="white", font=("Arial", 10, "bold")).pack(pady=15)

    def _construir_aba_deletar(self):
        tk.Label(self.aba_deletar, text="Deletar Material", font=("Arial", 14, "bold"), fg="red").pack(pady=15)
        tk.Label(self.aba_deletar, text="Selecione o Material:").pack()
        self.combo_deletar_mat = ttk.Combobox(self.aba_deletar, state="readonly", width=27)
        self.combo_deletar_mat.pack(pady=5)
        tk.Button(self.aba_deletar, text="🗑️ Deletar Material", command=self.btn_deletar_mat_click, bg="red", fg="white", font=("Arial", 10, "bold")).pack(pady=20)

    def atualizar_listas_mat(self):
        try:
            materiais_db = self.sistema.listar_materiais()
            lista_formatada = [f"{m[0]} - {m[1]}" for m in materiais_db]
            self.combo_atualizar_mat['values'] = lista_formatada
            self.combo_deletar_mat['values'] = lista_formatada
            if lista_formatada:
                self.combo_atualizar_mat.current(0)
                self.combo_deletar_mat.current(0)
            else:
                self.combo_atualizar_mat.set('')
                self.combo_deletar_mat.set('')
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar listas: {e}", parent=self)

    def salvar_material(self):
        nome = self.entry_nome.get().strip()
        quantidade_texto = self.entry_quantidade.get()
        observacoes = self.entry_obs.get()
        
        if nome == "" or quantidade_texto == "":
            messagebox.showerror("Erro", "Nome e quantidade são obrigatórios!", parent=self)
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
        nova_qtd_texto = self.entry_nova_qtd.get()
        novas_obs = self.entry_novas_obs.get()
        
        if not selecionado or novo_nome == "" or nova_qtd_texto == "":
            messagebox.showerror("Erro", "Selecione o material, preencha o novo nome e a quantidade!", parent=self)
            return
            
        try:
            nova_qtd = int(nova_qtd_texto)
            if nova_qtd < 0:
                messagebox.showerror("Erro", "A nova quantidade não pode ser negativa!", parent=self)
                return
        except ValueError:
            messagebox.showerror("Erro", "A nova quantidade deve ser um número inteiro!", parent=self)
            return
            
        id_mat = int(selecionado.split(" - ")[0])
        monitor_selecionado = self.combo_monitor_resp.get()
        id_monitor = int(monitor_selecionado.split(" - ")[0]) # Extrai o ID do monitor
        
        try:
            # Enviando o id_monitor para o backend para fins de log de auditoria
            self.sistema.atualizar_material(id_mat, novo_nome, nova_qtd, novas_obs, id_monitor=id_monitor)
            messagebox.showinfo("Sucesso", "Material atualizado com sucesso e log registrado!", parent=self)
            self.entry_novo_nome_mat.delete(0, tk.END)
            self.entry_nova_qtd.delete(0, tk.END)
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