import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
import platform
import subprocess
from datetime import datetime
import servico_checklist


class JanelaChecklist(tk.Toplevel):
    def __init__(self, master, sistema):
        super().__init__(master)
        self.sistema = sistema
        self.title("Check-list Diário")
        self.geometry("1000x700")
        self.transient(master)
        self.grab_set()
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

        self.mouse_no_canvas = False
        # Manutenção do isolamento de evento do scroll
        self.frame_container.bind("<Enter>", self._mouse_entrou)
        self.frame_container.bind("<Leave>", self._mouse_saiu)

        self.bind("<MouseWheel>", self.rolar_mouse)
        self.bind("<Button-4>", self.rolar_mouse)
        self.bind("<Button-5>", self.rolar_mouse)

    def _mouse_entrou(self, event):
        self.mouse_no_canvas = True

    def _mouse_saiu(self, event):
        self.mouse_no_canvas = False

    def rolar_mouse(self, event):
        # 1ª Trava: Cancela a rolagem se o mouse estiver fora do container
        if not getattr(self, 'mouse_no_canvas', False):
            return
            
        # 2ª Trava: Cancela a rolagem da tela se o cursor estiver sobre um Combobox 
        if isinstance(event.widget, ttk.Combobox):
            return

        # Executa a rolagem normalmente
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
            
            # --- CORREÇÃO: Faz a tela rolar automaticamente acompanhando o cursor ---
            fracao_rolagem = novo_index / len(self.lista_entries)
            self.canvas.yview_moveto(fracao_rolagem)    
        return "break"

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
        if not self.entradas_checklist:
            messagebox.showwarning("Aviso", "Não há materiais para verificar no check-list!", parent=self)
            return
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
            try:
                resultado = servico_checklist.processar_checklist(monitor_responsavel, itens_verificados)
                if self.winfo_exists():
                    self.after(0, lambda: self.finalizar_salvamento(resultado))
            except Exception as e:
                # Se falhar catastroficamente, avisa o usuário e reativa a interface
                if self.winfo_exists():
                    self.after(0, lambda err=e: messagebox.showerror("Erro Crítico", f"Falha ao processar o checklist: {err}", parent=self))
                    self.after(0, lambda: self.btn_salvar.config(state="normal", text="Salvar e Registrar Check-list"))

        threading.Thread(target=tarefa_paralela, daemon=True).start()

    def finalizar_salvamento(self, resultado):
        if not self.winfo_exists():
            return
        if not resultado["sucesso"]:
            messagebox.showerror("Erro", resultado["erro"], parent=self)
            self.btn_salvar.config(state="normal", text="Salvar e Registrar Check-list") # Reativa o botão
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
