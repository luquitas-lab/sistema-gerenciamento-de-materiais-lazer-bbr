
import tkinter as tk
from backend_gerenciador import BancoDeDados

from telas.janela_monitor import JanelaMonitor
from telas.janela_material import JanelaMaterial
from telas.janela_movimentacoes import JanelaMovimentacoes
from telas.janela_checklist import JanelaChecklist
from telas.janela_historico_relatorio import JanelaHistorico, JanelaRelatorio

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