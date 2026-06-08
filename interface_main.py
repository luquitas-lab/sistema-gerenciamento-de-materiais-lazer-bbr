import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime
import os
import sys
import threading 
import servico_checklist
from backend_gerenciador import BancoDeDados
import platform
import subprocess

def obter_area_de_trabalho():
    home = os.path.expanduser("~")
    # Testa os caminhos mais comuns no Windows com OneDrive e sistemas locais
    caminhos = [
        os.path.join(home, "OneDrive", "Área de Trabalho"),
        os.path.join(home, "OneDrive", "Desktop"),
        os.path.join(home, "Desktop"),
        os.path.join(home, "Área de Trabalho")
    ]
    for caminho in caminhos:
        if os.path.exists(caminho):
            return caminho
    return os.path.join(home, "Desktop") # Fallback padrão de segurança

# =======================================================
# JANELAS SECUNDÁRIAS (Monitores, Materiais, Movimentações e Relatórios continuam idênticas visualmente)p
# =======================================================

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

    def atualizar_listas(self):
        try:
            monitores_db = self.sistema.listar_monitores()
            lista_formatada = [f"{m[0]} - {m[1]}" for m in monitores_db]
            self.combo_atualizar['values'] = lista_formatada
            self.combo_deletar['values'] = lista_formatada
            if lista_formatada:
                self.combo_atualizar.current(0)
                self.combo_deletar.current(0)
            else:
                self.combo_atualizar.set('')
                self.combo_deletar.set('')
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
            # Passando o ID do monitor para auditoria
            self.sistema.criar_entrada(data_texto, quantidade, id_mat, id_monitor=id_monitor)
            messagebox.showinfo("Sucesso", "Entrada registada! Histórico gravado.", parent=self)
            self.entry_qtd_ent.delete(0, tk.END)
            self.atualizar_combos_mov() 
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao registar entrada: {e}", parent=self)

    def confirmar_dano(self):
        selecionado = self.combo_mat_dano.get()
        qtd_texto = self.entry_qtd_dano.get()

        id_mat = int(selecionado.split(" - ")[0])
        materiais_db = self.sistema.listar_materiais()
        material_atual = next((m for m in materiais_db if m[0] == id_mat), None)
        
        if material_atual and quantidade > material_atual[2]:
            messagebox.showerror("Erro", f"Estoque insuficiente! Disponível: {material_atual[2]}", parent=self)
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
            # Passando o ID do monitor para auditoria
            self.sistema.criar_danos(data_texto, quantidade, id_mat, id_monitor=id_monitor)
            messagebox.showinfo("Sucesso", "Dano/Perda registado! Histórico gravado.", parent=self)
            self.entry_qtd_dano.delete(0, tk.END)
            self.atualizar_combos_mov()  
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao registar dano: {e}", parent=self)

class JanelaHistorico(tk.Toplevel):
    def __init__(self, master, sistema):
        super().__init__(master)
        self.sistema = sistema
        self.title("Histórico de Movimentações")
        self.geometry("700x400")
        self.grab_set()

        colunas = ("ID", "Monitor", "Data", "Ação", "Detalhes")
        self.tree = ttk.Treeview(self, columns=colunas, show="headings")
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.carregar_historico()

    def carregar_historico(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for log in self.sistema.listar_historico():
            self.tree.insert("", "end", values=log)


class JanelaRelatorio(tk.Toplevel):
    def __init__(self, master, sistema):
        super().__init__(master)
        self.sistema = sistema
        self.title("Gerar Relatório")
        self.geometry("300x200")
        self.transient(master)
        self.grab_set()

        try:
            monitores_db = self.sistema.listar_monitores()
        except Exception as e:
            messagebox.showerror("Erro", str(e), parent=self)
            self.destroy()
            return
        
        if not monitores_db:
            messagebox.showwarning("Aviso", "Você precisa cadastrar pelo menos um monitor primeiro para gerar o relatório!", parent=self)
            self.destroy()
            return

        self.lista_monitores = [f"{linha[0]} - {linha[1]}" for linha in monitores_db]

        tk.Label(self, text="Quem está gerando este relatório?", font=("Arial", 11, "bold")).pack(pady=15)
        self.monitor_selecionado = tk.StringVar(self)
        self.monitor_selecionado.set(self.lista_monitores[0]) 
        menu_monitores = tk.OptionMenu(self, self.monitor_selecionado, *self.lista_monitores)
        menu_monitores.pack(pady=10)
        tk.Button(self, text="Gerar Relatório", command=self.confirmar_e_gerar, bg="blue", fg="white", font=("Arial", 10, "bold")).pack(pady=15)

    def confirmar_e_gerar(self):
        monitor_selecionado = self.monitor_selecionado.get()
        nome_responsavel = monitor_selecionado.split(" - ", 1)[1]
        agora = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
        nome_arquivo = f"Relatorio_Inventario_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.txt"
        
        # 🟢 NÍVEL 2: CAMINHOS ABSOLUTOS
        caminho_desktop = obter_area_de_trabalho()
        pasta_relatorios = os.path.join(caminho_desktop, "Relatorios_TXT")

        if not os.path.exists(pasta_relatorios):
            os.makedirs(pasta_relatorios)

        caminho_arquivo = os.path.join(pasta_relatorios, nome_arquivo)
        
        try:
            materiais = self.sistema.listar_materiais()
            with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
                arquivo.write("=" * 70 + "\n")
                arquivo.write("     RELATÓRIO OFICIAL DE INVENTÁRIO\n")
                arquivo.write("=" * 70 + "\n")
                arquivo.write(f"Documento gerado em: {agora}\n\n")
                arquivo.write("--- POSIÇÃO ATUAL DO ESTOQUE ---\n\n")
                if not materiais:
                    arquivo.write("Nenhum material cadastrado no sistema.\n")
                else:
                    arquivo.write(f"{'ID':<5} | {'NOME DO MATERIAL':<25} | {'QTD':<5} | {'OBSERVAÇÕES'}\n")
                    arquivo.write("-" * 70 + "\n")
                    for mat in materiais:
                        obs = mat[3] if mat[3] else "Nenhuma"
                        # Garante que nomes muito longos não quebrem a tabela
                        nome_formatado = mat[1][:22] + "..." if len(mat[1]) > 25 else mat[1]
                        arquivo.write(f"{mat[0]:<5} | {nome_formatado:<25} | {mat[2]:<5} | {obs}\n")
                arquivo.write("\n" + "=" * 70 + "\n")
                arquivo.write(f"Relatório gerado e conferido por: {nome_responsavel}\n")
                arquivo.write("=" * 70 + "\n")
            
            messagebox.showinfo("Sucesso", f"Relatório gerado com sucesso!\n\nSalvo em: {caminho_arquivo}", parent=self)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar o documento: {e}", parent=self)


# =======================================================
# JANELA DE CHECK-LIST (Agora com Threading e Scroll seguro)
# =======================================================

class JanelaChecklist(tk.Toplevel):
    def __init__(self, master, sistema):
        super().__init__(master)
        self.sistema = sistema
        self.title("Check-list Diário")
        self.geometry("1000x700")
        self.transient(master)
        self.grab_set()
        self.bind("<Destroy>", self._desativar_scroll)

        self.entradas_checklist = {}
        self.lista_entries = []

        tk.Label(self, text="📝 Check-list de Materiais", font=("Arial", 16, "bold")).pack(pady=15)

        if not self._configurar_monitor_responsavel():
            return

        self._configurar_canvas()
        self._carregar_materiais()

        # Botão salvo em uma variável para podermos desativá-lo durante o Threading
        self.btn_salvar = tk.Button(self, text="Salvar e Registrar Check-list", command=self.iniciar_salvamento, bg="#ff9900", font=("Arial", 11, "bold"))
        self.btn_salvar.pack(pady=20)

    def _configurar_monitor_responsavel(self):
        try:
            monitores_db = self.sistema.listar_monitores()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar monitores: {e}", parent=self)
            self.destroy()
            return False

        if not monitores_db:
            messagebox.showwarning("Aviso", "Você precisa cadastrar pelo menos um monitor antes de realizar o check-list!", parent=self)
            self.destroy()
            return False

        lista_monitores = [f"{m[0]} - {m[1]}" for m in monitores_db]
        frame_monitor = tk.Frame(self)
        frame_monitor.pack(pady=10)
        tk.Label(frame_monitor, text="Monitor Responsável:", font=("Arial", 11, "bold")).pack(side="left", padx=5)
        self.combo_monitor_resp = ttk.Combobox(frame_monitor, values=lista_monitores, state="readonly", width=25)
        self.combo_monitor_resp.current(0)
        self.combo_monitor_resp.pack(side="left", padx=5)
        return True

    def _configurar_canvas(self):
        # --- SOLUÇÃO DO BUG: CABEÇALHO FIXO ---
        # Criamos um frame fora do Canvas para que os títulos nunca sumam
        self.frame_cabecalho = tk.Frame(self)
        self.frame_cabecalho.pack(fill="x", padx=10, pady=(10, 0))
        
        tk.Label(self.frame_cabecalho, text="Material", font=("Arial", 10, "bold"), width=35, anchor="w").grid(row=0, column=0, padx=5)
        tk.Label(self.frame_cabecalho, text="Esperado", font=("Arial", 10, "bold"), width=10).grid(row=0, column=1, padx=5)
        tk.Label(self.frame_cabecalho, text="Encontrado", font=("Arial", 10, "bold"), width=12).grid(row=0, column=2, padx=5)
        tk.Label(self.frame_cabecalho, text="Observação", font=("Arial", 10, "bold"), width=15).grid(row=0, column=3, padx=5)
        tk.Label(self.frame_cabecalho, text="Quarto", font=("Arial", 10, "bold"), width=10).grid(row=0, column=4, padx=5)
        tamanhos_colunas = [280, 90, 110, 130, 90]
        for i, tamanho in enumerate(tamanhos_colunas):
            self.frame_cabecalho.grid_columnconfigure(i, minsize=tamanho)

        # --- ÁREA SCROLLABLE ---
        self.frame_container = tk.Frame(self)
        self.frame_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.canvas = tk.Canvas(self.frame_container)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(self.frame_container, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.frame_lista = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame_lista, anchor="nw")
        self.frame_lista.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Manutenção do isolamento de evento do scroll
        self.frame_container.bind("<Enter>", self._ativar_scroll)
        self.frame_container.bind("<Leave>", self._desativar_scroll)

    def _ativar_scroll(self, event):
        self.bind("<MouseWheel>", self.rolar_mouse)
        self.bind("<Button-4>", self.rolar_mouse)
        self.bind("<Button-5>", self.rolar_mouse)

    def _desativar_scroll(self, event):
        self.unbind("<MouseWheel>")
        self.unbind("<Button-4>")
        self.unbind("<Button-5>")

    def rolar_mouse(self, event):
        try:
            if getattr(event, 'delta', 0) != 0:
                direcao = int(-1 * (event.delta / abs(event.delta)))
                self.canvas.yview_scroll(direcao, "units")
            elif getattr(event, 'num', 0) != 0:
                if event.num == 4:
                    self.canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    self.canvas.yview_scroll(1, "units")
        except Exception:
            pass

    def mover_foco(self, event, direcao, index):
        novo_index = index + direcao
        if 0 <= novo_index < len(self.lista_entries):
            self.lista_entries[novo_index].focus_set()

    def _carregar_materiais(self):
        try:
            materiais = self.sistema.listar_materiais()
        except Exception as e:
            messagebox.showerror("Erro", str(e), parent=self)
            return
        tamanhos_colunas = [280, 90, 110, 130, 90]
        for i, tamanho in enumerate(tamanhos_colunas):
            self.frame_lista.grid_columnconfigure(i, minsize=tamanho)
            
        if not materiais:
            tk.Label(self.frame_lista, text="Nenhum material cadastrado no sistema.", fg="red").grid(row=0, column=0)
            return

        for i, mat in enumerate(materiais):
            id_mat, nome, qtd_esperada = mat[0], mat[1], mat[2]
            linha = i  # Agora começa na linha 0 dentro do frame_lista, já que o cabeçalho saiu

            tk.Label(self.frame_lista, text=nome, width=35, anchor="w").grid(row=linha, column=0, pady=5, padx=5)
            tk.Label(self.frame_lista, text=str(qtd_esperada), width=10).grid(row=linha, column=1, pady=5, padx=5)

            entry_qtd = tk.Entry(self.frame_lista, width=10)
            entry_qtd.grid(row=linha, column=2, pady=5, padx=5)

            combo_obs = ttk.Combobox(self.frame_lista, values=["", "Pendente", "Danificado"], state="readonly", width=12)
            combo_obs.current(0)
            combo_obs.grid(row=linha, column=3, pady=5, padx=5)
            combo_obs.bind("<MouseWheel>", lambda e: "break")
            combo_obs.bind("<Button-4>", lambda e: "break")
            combo_obs.bind("<Button-5>", lambda e: "break")

            entry_quarto = tk.Entry(self.frame_lista, width=10)
            entry_quarto.grid(row=linha, column=4, pady=5, padx=5)

            self.entradas_checklist[id_mat] = (nome, qtd_esperada, entry_qtd, combo_obs, entry_quarto)
            self.lista_entries.append(entry_qtd)

        for index, entry in enumerate(self.lista_entries):
            entry.bind("<Up>", lambda event, idx=index: self.mover_foco(event, -1, idx))
            entry.bind("<Down>", lambda event, idx=index: self.mover_foco(event, 1, idx))

        if self.lista_entries:
            self.lista_entries[0].focus_set()

    def iniciar_salvamento(self):
        monitor_selecionado = self.combo_monitor_resp.get()
        monitor_responsavel = monitor_selecionado.split(" - ", 1)[1]
        
        itens_verificados = []
        for id_mat, dados in self.entradas_checklist.items():
            nome, qtd_esperada, entry, combo_obs, entry_quarto = dados
            itens_verificados.append({
                'id_mat': id_mat, # <-- ADICIONE ESTA LINHA AQUI
                'nome': nome,
                'esperado': qtd_esperada,
                'encontrado_txt': entry.get(),
                'obs': combo_obs.get() or "-",
                'quarto': entry_quarto.get().strip() or "-"
            })

        self.btn_salvar.config(state="disabled", text="Gerando Relatório e Gráficos... Aguarde!")

        def tarefa_paralela():
            resultado = servico_checklist.processar_checklist(monitor_responsavel, itens_verificados)
            if self.winfo_exists():
                self.after(0, lambda: self.finalizar_salvamento(resultado))

        threading.Thread(target=tarefa_paralela, daemon=True).start()

    def finalizar_salvamento(self, resultado):
        if not self.winfo_exists():
            return
        if not resultado["sucesso"]:
            messagebox.showerror("Erro", resultado["erro"], parent=self)
            self.btn_salvar.config(state="normal", text="Salvar e Registrar Check-list") # Reativa o botão
            return
        
        monitor_selecionado = self.combo_monitor_resp.get()
        id_monitor = int(monitor_selecionado.split(" - ")[0])
        data_atual = datetime.now().strftime("%Y-%m-%d")
        
        try:
            for acao in resultado.get("acoes_bd", []):
                if acao['tipo'] == 'falta':
                    self.sistema.criar_danos(data_atual, acao['qtd'], acao['id_mat'], id_monitor)
                elif acao['tipo'] == 'sobra':
                    self.sistema.criar_entrada(data_atual, acao['qtd'], acao['id_mat'], id_monitor)
        except Exception as e:
            messagebox.showerror("Erro de Banco", f"Relatório gerado, mas houve erro ao atualizar o estoque: {e}", parent=self)
            self.btn_salvar.config(state="normal", text="Salvar e Registrar Check-list")
            return
        try:
            sistema_os = platform.system()
            if sistema_os == "Windows":
                os.startfile(resultado["nome_imagem"])
            elif sistema_os == "Darwin": # macOS
                subprocess.Popen(["open", resultado["nome_imagem"]])
            else: # Linux
                subprocess.Popen(["xdg-open", resultado["nome_imagem"]])
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir a imagem gerada: {e}", parent=self)

        alertas = resultado["alertas"]
        nome_arquivo = resultado["nome_arquivo_txt"]

        if alertas:
            mensagem_final = f"Check-list pronto '{nome_arquivo}' e gráfico gerado!\n\nAtenção aos Alertas:\n\n" + "\n".join(alertas)
            messagebox.showwarning("Atenção!", mensagem_final, parent=self)
        else:
            messagebox.showinfo("Sucesso", f"Check-list perfeito! Nenhum item faltando.\nRelatório '{nome_arquivo}' e gráfico salvos com sucesso.", parent=self)

        self.destroy()

# =======================================================
# CLASSE APP (A Janela Principal e Gerenciadora)
# =======================================================

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("📦 MATERIAIS")
        
        self.sistema = BancoDeDados()

        self._configurar_geometria()
        self.protocol("WM_DELETE_WINDOW", self.fechar_sistema)
        self._construir_menu()

    def _configurar_geometria(self):
        largura_janela = 400
        altura_janela = 500
        largura_tela = self.winfo_screenwidth()
        altura_tela = self.winfo_screenheight()
        pos_x = (largura_tela // 2) - (largura_janela // 2)
        pos_y = (altura_tela // 2) - (altura_janela // 2)
        self.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

    def _construir_menu(self):
        tk.Label(self, text="MENU PRINCIPAL", font=("Arial", 18, "bold")).pack(pady=30)
        tk.Button(self, text="1. Gerenciar Monitores", command=lambda: self.abrir_tela(JanelaMonitor), width=30, height=2).pack(pady=10)
        tk.Button(self, text="2. Gerenciar Materiais", command=lambda: self.abrir_tela(JanelaMaterial), width=30, height=2).pack(pady=10)
        tk.Button(self, text="3. Registrar Entradas e Perdas", command=lambda: self.abrir_tela(JanelaMovimentacoes), width=30, height=2, bg="#f0f0f0").pack(pady=10)
        tk.Button(self, text="4. Realizar Check-list Diário", command=lambda: self.abrir_tela(JanelaChecklist), width=30, height=2).pack(pady=10)
        tk.Button(self, text="5. Gerar Relatório de Estoque", command=lambda: self.abrir_tela(JanelaRelatorio), width=30, height=2, bg="#e6e6e6").pack(pady=10)
        tk.Button(self, text="6. Ver Histórico de Ações", command=lambda: self.abrir_tela(JanelaHistorico), width=30, height=2).pack(pady=10)
        tk.Button(self, text="Sair do Sistema", command=self.fechar_sistema, bg="red", fg="white", width=20).pack(pady=40)

    # 🟢 Função Central de Controle de Janelas (Singleton)
    def abrir_tela(self, ClasseDaJanela):
        ClasseDaJanela(self, self.sistema)

    def fechar_sistema(self):
        try:
            self.sistema.fechar_conexao()
        except Exception:
            pass 
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()