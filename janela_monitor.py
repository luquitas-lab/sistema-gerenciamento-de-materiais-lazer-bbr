import tkinter as tk
from tkinter import ttk, messagebox

class JanelaMonitor(tk.Toplevel):
    def __init__(self, master, sistema):
        super().__init__(master)
        self.sistema = sistema
        self.title("Gerenciar Monitores")
        self.geometry("400x350")
        self.transient(master)
        self.grab_set()
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
        self.atualizar_listas()

    def _construir_aba_cadastrar(self):
        tk.Label(self.aba_cadastrar, text="Cadastrar Novo Monitor", font=("Arial", 14, "bold")).pack(pady=15)
        tk.Label(self.aba_cadastrar, text="Nome do Monitor:").pack()
        self.entry_nome_mon = tk.Entry(self.aba_cadastrar, width=30)
        self.entry_nome_mon.pack(pady=5)
        tk.Button(self.aba_cadastrar, text="Salvar Monitor", command=self.salvar_monitor, bg="green", fg="white", font=("Arial", 10, "bold")).pack(pady=20)

    def _construir_aba_atualizar(self):
        tk.Label(self.aba_atualizar, text="Atualizar Nome do Monitor", font=("Arial", 14, "bold")).pack(pady=15)
        tk.Label(self.aba_atualizar, text="Selecione o Monitor antigo:").pack()
        self.combo_atualizar = ttk.Combobox(self.aba_atualizar, state="readonly", width=27)
        self.combo_atualizar.pack(pady=5)
        self.combo_atualizar.bind("<<ComboboxSelected>>", self.preencher_dados_atuais)
        tk.Label(self.aba_atualizar, text="Digite o Novo Nome:").pack()
        self.entry_novo_nome = tk.Entry(self.aba_atualizar, width=30)
        self.entry_novo_nome.pack(pady=5)
        tk.Button(self.aba_atualizar, text="Atualizar Nome", command=self.btn_atualizar_click, bg="#0052cc", fg="white", font=("Arial", 10, "bold")).pack(pady=15)

    def _construir_aba_deletar(self):
        tk.Label(self.aba_deletar, text="Deletar Monitor", font=("Arial", 14, "bold"), fg="red").pack(pady=15)
        tk.Label(self.aba_deletar, text="Selecione o Monitor:").pack()
        self.combo_deletar = ttk.Combobox(self.aba_deletar, state="readonly", width=27)
        self.combo_deletar.pack(pady=5)
        tk.Button(self.aba_deletar, text="🗑️ Deletar Monitor", command=self.btn_deletar_click, bg="red", fg="white", font=("Arial", 10, "bold")).pack(pady=20)

    def preencher_dados_atuais(self, event=None):
        selecionado = self.combo_atualizar.get()
        if not selecionado: return
        id_mon = int(selecionado.split(" - ")[0])
        monitores_db = self.sistema.listar_monitores()
        monitor = next((m for m in monitores_db if m[0] == id_mon), None)
        if monitor:
            self.entry_novo_nome.delete(0, tk.END)
            self.entry_novo_nome.insert(0, monitor[1])

    def atualizar_listas(self):
        sel_atual = self.combo_atualizar.get().split(" - ")[0] if self.combo_atualizar.get() else None
        try:
            monitores_db = self.sistema.listar_monitores()
            lista_formatada = [f"{m[0]} - {m[1]}" for m in monitores_db]
            self.combo_atualizar['values'] = lista_formatada
            self.combo_deletar['values'] = lista_formatada
            if lista_formatada:
                idx_atual = next((i for i, v in enumerate(lista_formatada) if v.startswith(f"{sel_atual} - ")), 0)
                self.combo_atualizar.current(idx_atual)
                self.combo_deletar.current(0)
                self.preencher_dados_atuais()
            else:
                self.combo_atualizar.set('')
                self.combo_deletar.set('')
                self.entry_novo_nome.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar listas: {e}", parent=self)

    def salvar_monitor(self):
        nome = self.entry_nome_mon.get().strip()
        if nome == "":
            messagebox.showerror("Erro", "O nome é obrigatório!", parent=self)
            return
        try:
            self.sistema.criar_monitor(nome)
            messagebox.showinfo("Sucesso", f"Monitor '{nome}' cadastrado!", parent=self)
            self.entry_nome_mon.delete(0, tk.END)
            self.atualizar_listas() 
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {e}", parent=self)

    def btn_atualizar_click(self):
        selecionado = self.combo_atualizar.get()
        novo_nome = self.entry_novo_nome.get().strip()
        if not selecionado or novo_nome == "":
            messagebox.showerror("Erro", "Selecione um monitor e digite o novo nome!", parent=self)
            return
        id_mon = int(selecionado.split(" - ")[0])
        try:
            self.sistema.atualizar_monitor(id_mon, novo_nome)
            messagebox.showinfo("Sucesso", "Monitor atualizado com sucesso!", parent=self)
            self.entry_novo_nome.delete(0, tk.END)
            self.atualizar_listas()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {e}", parent=self)

    def btn_deletar_click(self):
        selecionado = self.combo_deletar.get()
        if not selecionado:
            messagebox.showerror("Erro", "Selecione um monitor para deletar!", parent=self)
            return
        resposta = messagebox.askyesno("Confirmar Exclusão", f"Você tem certeza que deseja deletar:\n\n{selecionado}?", parent=self)
        if resposta:
            id_mon = int(selecionado.split(" - ")[0])
            try:
                self.sistema.deletar_monitor(id_mon)
                messagebox.showinfo("Sucesso", "Monitor deletado do sistema!", parent=self)
                self.atualizar_listas()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro: {e}", parent=self)