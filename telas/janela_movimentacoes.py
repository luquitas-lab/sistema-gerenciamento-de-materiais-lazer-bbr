import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class JanelaMovimentacoes(tk.Toplevel):
    def __init__(self, master, sistema):
        super().__init__(master)
        self.sistema = sistema
        self.title("Movimentações de Estoque")
        self.geometry("450x480") # Altura ajustada
        self.transient(master)
        self.grab_set()

        # Configura o seletor de monitor antes de desenhar as abas
        if not self._configurar_monitor_responsavel():
            return

        self.abas = ttk.Notebook(self)
        self.abas.pack(fill="both", expand=True, padx=10, pady=10)

        self.aba_entrada = tk.Frame(self.abas)
        self.aba_dano = tk.Frame(self.abas)

        self.abas.add(self.aba_entrada, text="Registar Entrada")
        self.abas.add(self.aba_dano, text="Registar Dano/Perda")

        self._construir_aba_entrada()
        self._construir_aba_dano()
        self.atualizar_combos_mov()

    
    def _configurar_monitor_responsavel(self):
        try:
            monitores_db = self.sistema.listar_monitores()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar monitores: {e}", parent=self)
            self.destroy()
            return False

        if not monitores_db:
            messagebox.showwarning("Aviso", "Você precisa cadastrar pelo menos um monitor antes de realizar movimentações!", parent=self)
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

    def _construir_aba_entrada(self):
        tk.Label(self.aba_entrada, text="Registar Entrada de Material", font=("Arial", 14, "bold"), fg="green").pack(pady=15)
        tk.Label(self.aba_entrada, text="Selecione o Material:").pack()
        self.combo_mat_ent = ttk.Combobox(self.aba_entrada, state="readonly", width=35)
        self.combo_mat_ent.pack(pady=5)
        tk.Label(self.aba_entrada, text="Quantidade a Adicionar:").pack()
        self.entry_qtd_ent = tk.Entry(self.aba_entrada, width=15)
        self.entry_qtd_ent.pack(pady=5)
        tk.Label(self.aba_entrada, text="Data (ANO-MÊS-DIA):").pack()
        self.entry_data_ent = tk.Entry(self.aba_entrada, width=15)
        self.entry_data_ent.insert(0, datetime.now().strftime("%Y-%m-%d"))  
        self.entry_data_ent.pack(pady=5)
        tk.Button(self.aba_entrada, text="📥 Confirmar Entrada", command=self.confirmar_entrada, bg="green", fg="white", font=("Arial", 10, "bold")).pack(pady=20)

    def _construir_aba_dano(self):
        tk.Label(self.aba_dano, text="Registar Material Danificado ou Perdido", font=("Arial", 14, "bold"), fg="red").pack(pady=15)
        tk.Label(self.aba_dano, text="Selecione o Material:").pack()
        self.combo_mat_dano = ttk.Combobox(self.aba_dano, state="readonly", width=35)
        self.combo_mat_dano.pack(pady=5)
        tk.Label(self.aba_dano, text="Quantidade Danificada/Perdida:").pack()
        self.entry_qtd_dano = tk.Entry(self.aba_dano, width=15)
        self.entry_qtd_dano.pack(pady=5)
        tk.Label(self.aba_dano, text="Data (ANO-MÊS-DIA):").pack()
        self.entry_data_dano = tk.Entry(self.aba_dano, width=15)
        self.entry_data_dano.insert(0, datetime.now().strftime("%Y-%m-%d"))  
        self.entry_data_dano.pack(pady=5)
        tk.Button(self.aba_dano, text="⚠️ Confirmar Baixa", command=self.confirmar_dano, bg="red", fg="white", font=("Arial", 10, "bold")).pack(pady=20)

    def atualizar_combos_mov(self):
        try:
            materiais_db = self.sistema.listar_materiais()
            lista_formatada = [f"{m[0]} - {m[1]} (Atual: {m[2]})" for m in materiais_db]
            self.combo_mat_ent['values'] = lista_formatada
            self.combo_mat_dano['values'] = lista_formatada
            if lista_formatada:
                self.combo_mat_ent.current(0)
                self.combo_mat_dano.current(0)
            else:
                self.combo_mat_ent.set('')
                self.combo_mat_dano.set('')
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar materiais: {e}", parent=self)

    def confirmar_entrada(self):
        selecionado = self.combo_mat_ent.get()
        qtd_texto = self.entry_qtd_ent.get()
        data_texto = self.entry_data_ent.get()
        if not selecionado or qtd_texto == "" or data_texto == "":
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!", parent=self)
            return
        try:
            quantidade = int(qtd_texto)
            if quantidade <= 0:
                messagebox.showerror("Erro", "A quantidade deve ser maior que zero!", parent=self)
                return
        except ValueError:
            messagebox.showerror("Erro", "A quantidade deve ser um número inteiro!", parent=self)
            return
        try:
            datetime.strptime(data_texto, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido. Use ANO-MÊS-DIA (Ex: 2024-12-25)", parent=self)
            return
            
        id_mat = int(selecionado.split(" - ")[0])
        monitor_selecionado = self.combo_monitor_resp.get()
        id_monitor = int(monitor_selecionado.split(" - ")[0])
        
        try:
            self.sistema.criar_entrada(data_texto, quantidade, id_mat, id_monitor=id_monitor)
            messagebox.showinfo("Sucesso", "Entrada registada! Histórico gravado.", parent=self)
            self.entry_qtd_ent.delete(0, tk.END)
            self.atualizar_combos_mov() 
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao registar entrada: {e}", parent=self)

    def confirmar_dano(self):
        selecionado = self.combo_mat_dano.get()
        qtd_texto = self.entry_qtd_dano.get()
        data_texto = self.entry_data_dano.get() # CORREÇÃO 2: Capturando a data

        if not selecionado or qtd_texto == "" or data_texto == "":
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!", parent=self)
            return

        try:
            quantidade = int(qtd_texto)
            if quantidade <= 0:
                messagebox.showerror("Erro", "A quantidade deve ser maior que zero!", parent=self)
                return
        except ValueError:
            messagebox.showerror("Erro", "A quantidade deve ser um número inteiro!", parent=self)
            return

        id_mat = int(selecionado.split(" - ")[0])
        materiais_db = self.sistema.listar_materiais()
        material_atual = next((m for m in materiais_db if m[0] == id_mat), None)
        
        if material_atual and quantidade > material_atual[2]:
            messagebox.showerror("Erro", f"Estoque insuficiente! Disponível: {material_atual[2]}", parent=self)
            return
        
        try:
            datetime.strptime(data_texto, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido. Use ANO-MÊS-DIA (Ex: 2024-12-25)", parent=self)
            return
            
        monitor_selecionado = self.combo_monitor_resp.get()
        id_monitor = int(monitor_selecionado.split(" - ")[0])
        
        try:
            self.sistema.criar_danos(data_texto, quantidade, id_mat, id_monitor=id_monitor)
            messagebox.showinfo("Sucesso", "Dano/Perda registado! Histórico gravado.", parent=self)
            self.entry_qtd_dano.delete(0, tk.END)
            self.atualizar_combos_mov()  
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao registar dano: {e}", parent=self)