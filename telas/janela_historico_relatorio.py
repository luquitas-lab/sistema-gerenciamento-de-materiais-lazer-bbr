import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os
from servico_checklist import obter_area_de_trabalho

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