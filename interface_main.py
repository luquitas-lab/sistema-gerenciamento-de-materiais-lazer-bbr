import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from backend_gerenciador import BancoDeDados
import threading


sistema = BancoDeDados()


#        FUNÇÕES PARA ABRIR TELAS


def abrir_janela_monitor():
    janela_monitor = tk.Toplevel(janela_principal)
    janela_monitor.title("Gerenciar Monitores")
    janela_monitor.geometry("400x350")
    janela_monitor.transient(janela_principal)

    # Cria o "Controlador de Abas" (Notebook)
    abas = ttk.Notebook(janela_monitor)
    abas.pack(fill="both", expand=True, padx=10, pady=10)

    # Cria as três abas (Frames)
    aba_cadastrar = tk.Frame(abas)
    aba_atualizar = tk.Frame(abas)
    aba_deletar = tk.Frame(abas)

    # Adiciona as abas no painel principal
    abas.add(aba_cadastrar, text="Cadastrar Novo")
    abas.add(aba_atualizar, text="Atualizar")
    abas.add(aba_deletar, text="Deletar")

    
    # LÓGICA COMPARTILHADA (ATUALIZAR LISTAS)
    
    def atualizar_listas():
        # USO DA NOVA API (Sem SQL direto)
        monitores_db = sistema.listar_monitores()
        
        lista_formatada = [f"{m[0]} - {m[1]}" for m in monitores_db]
        
        combo_atualizar['values'] = lista_formatada
        combo_deletar['values'] = lista_formatada
        
        if lista_formatada:
            combo_atualizar.current(0)
            combo_deletar.current(0)
        else:
            combo_atualizar.set('')
            combo_deletar.set('')

    
    # ABA 1: CADASTRAR
    
    def salvar_monitor():
        nome = entry_nome_mon.get()
        if nome == "":
            messagebox.showerror("Erro", "O nome é obrigatório!", parent=janela_monitor)
            return
        try:
            sistema.criar_monitor(nome)
            messagebox.showinfo("Sucesso", f"Monitor '{nome}' cadastrado!", parent=janela_monitor)
            entry_nome_mon.delete(0, tk.END)
            atualizar_listas() 
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {e}", parent=janela_monitor)

    tk.Label(aba_cadastrar, text="Cadastrar Novo Monitor", font=("Arial", 14, "bold")).pack(pady=15)
    tk.Label(aba_cadastrar, text="Nome do Monitor:").pack()
    entry_nome_mon = tk.Entry(aba_cadastrar, width=30)
    entry_nome_mon.pack(pady=5)
    tk.Button(aba_cadastrar, text="Salvar Monitor", command=salvar_monitor, bg="green", fg="white", font=("Arial", 10, "bold")).pack(pady=20)

    
    # ABA 2: ATUALIZAR
   
    def btn_atualizar_click():
        selecionado = combo_atualizar.get()
        novo_nome = entry_novo_nome.get()
        
        if not selecionado or novo_nome == "":
            messagebox.showerror("Erro", "Selecione um monitor e digite o novo nome!", parent=janela_monitor)
            return
        
        id_mon = int(selecionado.split(" - ")[0])
        try:
            sistema.atualizar_monitor(id_mon, novo_nome)
            messagebox.showinfo("Sucesso", "Monitor atualizado com sucesso!", parent=janela_monitor)
            entry_novo_nome.delete(0, tk.END)
            atualizar_listas()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {e}", parent=janela_monitor)

    tk.Label(aba_atualizar, text="Atualizar Nome do Monitor", font=("Arial", 14, "bold")).pack(pady=15)
    tk.Label(aba_atualizar, text="Selecione o Monitor antigo:").pack()
    combo_atualizar = ttk.Combobox(aba_atualizar, state="readonly", width=27)
    combo_atualizar.pack(pady=5)
    
    tk.Label(aba_atualizar, text="Digite o Novo Nome:").pack()
    entry_novo_nome = tk.Entry(aba_atualizar, width=30)
    entry_novo_nome.pack(pady=5)
    tk.Button(aba_atualizar, text="Atualizar Nome", command=btn_atualizar_click, bg="#0052cc", fg="white", font=("Arial", 10, "bold")).pack(pady=15)

   
    # ABA 3: DELETAR
    
    def btn_deletar_click():
        selecionado = combo_deletar.get()
        if not selecionado:
            messagebox.showerror("Erro", "Selecione um monitor para deletar!", parent=janela_monitor)
            return
            
        resposta = messagebox.askyesno("Confirmar Exclusão", f"Você tem certeza que deseja deletar:\n\n{selecionado}?", parent=janela_monitor)
        
        if resposta:
            id_mon = int(selecionado.split(" - ")[0])
            try:
                sistema.deletar_monitor(id_mon)
                messagebox.showinfo("Sucesso", "Monitor deletado do sistema!", parent=janela_monitor)
                atualizar_listas()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro: {e}", parent=janela_monitor)

    tk.Label(aba_deletar, text="Deletar Monitor", font=("Arial", 14, "bold"), fg="red").pack(pady=15)
    tk.Label(aba_deletar, text="Selecione o Monitor:").pack()
    combo_deletar = ttk.Combobox(aba_deletar, state="readonly", width=27)
    combo_deletar.pack(pady=5)
    tk.Button(aba_deletar, text="🗑️ Deletar Monitor", command=btn_deletar_click, bg="red", fg="white", font=("Arial", 10, "bold")).pack(pady=20)

    # Roda a função pela primeira vez para preencher as listas com quem já está no banco
    atualizar_listas()


def abrir_janela_material():
    janela_material = tk.Toplevel(janela_principal)
    janela_material.title("Gerenciar Materiais")
    janela_material.geometry("400x480") 
    janela_material.transient(janela_principal)

    abas = ttk.Notebook(janela_material)
    abas.pack(fill="both", expand=True, padx=10, pady=10)

    aba_cadastrar = tk.Frame(abas)
    aba_atualizar = tk.Frame(abas)
    aba_deletar = tk.Frame(abas)

    abas.add(aba_cadastrar, text="Cadastrar Novo")
    abas.add(aba_atualizar, text="Atualizar")
    abas.add(aba_deletar, text="Deletar")

    
    # ATUALIZAR AS LISTAS 
    
    def atualizar_listas_mat():
        # USO DA NOVA API
        materiais_db = sistema.listar_materiais()
        lista_formatada = [f"{m[0]} - {m[1]}" for m in materiais_db]
        
        combo_atualizar_mat['values'] = lista_formatada
        combo_deletar_mat['values'] = lista_formatada
        
        if lista_formatada:
            combo_atualizar_mat.current(0)
            combo_deletar_mat.current(0)
        else:
            combo_atualizar_mat.set('')
            combo_deletar_mat.set('')

    
    # ABA 1: Gerenciar Materiais
    
    def salvar_material():
        nome = entry_nome.get()
        quantidade_texto = entry_quantidade.get()
        observacoes = entry_obs.get()

        if nome == "" or quantidade_texto == "":
            messagebox.showerror("Erro", "Nome e quantidade são obrigatórios!", parent=janela_material)
            return

        try:
            quantidade = int(quantidade_texto)
        except ValueError:
            messagebox.showerror("Erro", "A quantidade deve ser um número inteiro!", parent=janela_material)
            return

        try:
            sistema.criar_material(nome, quantidade, observacoes)
            messagebox.showinfo("Sucesso", f"Material '{nome}' cadastrado!", parent=janela_material)
            
            entry_nome.delete(0, tk.END)
            entry_quantidade.delete(0, tk.END)
            entry_obs.delete(0, tk.END)
            atualizar_listas_mat() 
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {e}", parent=janela_material)

    tk.Label(aba_cadastrar, text="Gerenciar Materiais", font=("Arial", 14, "bold")).pack(pady=10)
    tk.Label(aba_cadastrar, text="Nome do Material (ex: Raquete):").pack()
    entry_nome = tk.Entry(aba_cadastrar, width=30)
    entry_nome.pack(pady=2)

    tk.Label(aba_cadastrar, text="Quantidade Inicial no Estoque:").pack()
    entry_quantidade = tk.Entry(aba_cadastrar, width=30)
    entry_quantidade.pack(pady=2)

    tk.Label(aba_cadastrar, text="Observações (Marca, Cor, etc):").pack()
    entry_obs = tk.Entry(aba_cadastrar, width=30)
    entry_obs.pack(pady=2)

    tk.Button(aba_cadastrar, text="Salvar Material", command=salvar_material, bg="#0052cc", fg="white", font=("Arial", 10, "bold")).pack(pady=15)

    
    # ABA 2: ATUALIZAR MATERIAL
    
    def btn_atualizar_mat_click():
        selecionado = combo_atualizar_mat.get()
        novo_nome = entry_novo_nome_mat.get()
        nova_qtd_texto = entry_nova_qtd.get()
        novas_obs = entry_novas_obs.get()
        
        if not selecionado or novo_nome == "" or nova_qtd_texto == "":
            messagebox.showerror("Erro", "Selecione o material, preencha o novo nome e a quantidade!", parent=janela_material)
            return
            
        try:
            nova_qtd = int(nova_qtd_texto)
        except ValueError:
            messagebox.showerror("Erro", "A nova quantidade deve ser um número inteiro!", parent=janela_material)
            return
        
        id_mat = int(selecionado.split(" - ")[0])
        try:
            sistema.atualizar_material(id_mat, novo_nome, nova_qtd, novas_obs)
            messagebox.showinfo("Sucesso", "Material atualizado com sucesso!", parent=janela_material)
            entry_novo_nome_mat.delete(0, tk.END)
            entry_nova_qtd.delete(0, tk.END)
            entry_novas_obs.delete(0, tk.END)
            atualizar_listas_mat()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {e}", parent=janela_material)

    tk.Label(aba_atualizar, text="Atualizar Material", font=("Arial", 14, "bold")).pack(pady=10)
    tk.Label(aba_atualizar, text="Selecione o Material antigo:").pack()
    combo_atualizar_mat = ttk.Combobox(aba_atualizar, state="readonly", width=27)
    combo_atualizar_mat.pack(pady=2)
    
    tk.Label(aba_atualizar, text="Novo Nome:").pack()
    entry_novo_nome_mat = tk.Entry(aba_atualizar, width=30)
    entry_novo_nome_mat.pack(pady=2)

    tk.Label(aba_atualizar, text="Nova Quantidade:").pack()
    entry_nova_qtd = tk.Entry(aba_atualizar, width=30)
    entry_nova_qtd.pack(pady=2)

    tk.Label(aba_atualizar, text="Novas Observações:").pack()
    entry_novas_obs = tk.Entry(aba_atualizar, width=30)
    entry_novas_obs.pack(pady=2)

    tk.Button(aba_atualizar, text="Atualizar Material", command=btn_atualizar_mat_click, bg="#0052cc", fg="white", font=("Arial", 10, "bold")).pack(pady=15)

    
    # ABA 3: DELETAR MATERIAL
   
    def btn_deletar_mat_click():
        selecionado = combo_deletar_mat.get()
        if not selecionado:
            messagebox.showerror("Erro", "Selecione um material para deletar!", parent=janela_material)
            return
            
        resposta = messagebox.askyesno("Confirmar Exclusão", f"Você tem certeza que deseja deletar o material:\n\n{selecionado}?", parent=janela_material)
        
        if resposta:
            id_mat = int(selecionado.split(" - ")[0])
            try:
                sistema.deletar_material(id_mat)
                messagebox.showinfo("Sucesso", "Material deletado do sistema!", parent=janela_material)
                atualizar_listas_mat()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro: {e}", parent=janela_material)

    tk.Label(aba_deletar, text="Deletar Material", font=("Arial", 14, "bold"), fg="red").pack(pady=15)
    tk.Label(aba_deletar, text="Selecione o Material:").pack()
    combo_deletar_mat = ttk.Combobox(aba_deletar, state="readonly", width=27)
    combo_deletar_mat.pack(pady=5)
    tk.Button(aba_deletar, text="🗑️ Deletar Material", command=btn_deletar_mat_click, bg="red", fg="white", font=("Arial", 10, "bold")).pack(pady=20)

    atualizar_listas_mat()


def abrir_janela_checklist():
    from datetime import date, datetime
    import tkinter as tk
    from tkinter import ttk, messagebox

    janela_checklist = tk.Toplevel(janela_principal)
    janela_checklist.title("Check-list Diário")
    janela_checklist.geometry("1000x990")
    janela_checklist.transient(janela_principal)

    tk.Label(janela_checklist, text="📝 Check-list de Materiais", font=("Arial", 16, "bold")).pack(pady=15)

    
    # SISTEMA DE ROLAGEM (CANVAS + SCROLLBAR)
    
    frame_container = tk.Frame(janela_checklist)
    frame_container.pack(fill="both", expand=True, padx=10, pady=10)

    canvas = tk.Canvas(frame_container)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(frame_container, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)

    frame_lista = tk.Frame(canvas)
    canvas.create_window((0, 0), window=frame_lista, anchor="nw")

    def atualizar_scrollregion(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    frame_lista.bind("<Configure>", atualizar_scrollregion)

    def rolar_mouse(event):
        try:
            if getattr(event, 'delta', 0) != 0:
                direcao = int(-1 * (event.delta / abs(event.delta)))
                canvas.yview_scroll(direcao, "units")
            elif getattr(event, 'num', 0) != 0:
                if event.num == 4:
                    canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    canvas.yview_scroll(1, "units")
        except Exception:
            pass

    janela_checklist.bind_all("<MouseWheel>", rolar_mouse)
    janela_checklist.bind_all("<Button-4>", rolar_mouse)
    janela_checklist.bind_all("<Button-5>", rolar_mouse)

    
    # BUSCA DE DADOS E MONTAGEM DA LISTA
    
    try:
        # USO DA NOVA API
        materiais = sistema.listar_materiais()
    except Exception as e:
        messagebox.showerror("Erro", str(e), parent=janela_checklist)
        return

    if not materiais:
        tk.Label(frame_lista, text="Nenhum material cadastrado no sistema.", fg="red").grid(row=0, column=0)
        return

    tk.Label(frame_lista, text="Material", font=("Arial", 10, "bold"), width=35, anchor="w").grid(row=0, column=0, padx=5)
    tk.Label(frame_lista, text="Esperado", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=5)
    tk.Label(frame_lista, text="Encontrado", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5)
    tk.Label(frame_lista, text="Observação", font=("Arial", 10, "bold")).grid(row=0, column=3, padx=5)
    tk.Label(frame_lista, text="Quarto", font=("Arial", 10, "bold")).grid(row=0, column=4, padx=5)

    entradas_checklist = {}
    lista_entries = []

    for i, mat in enumerate(materiais):
        id_mat = mat[0]
        nome = mat[1]
        qtd_esperada = mat[2]

        linha = i + 1

        tk.Label(frame_lista, text=nome, width=35, anchor="w").grid(row=linha, column=0, pady=5, padx=5)
        tk.Label(frame_lista, text=str(qtd_esperada)).grid(row=linha, column=1, pady=5, padx=5)

        entry_qtd = tk.Entry(frame_lista, width=10)
        entry_qtd.grid(row=linha, column=2, pady=5, padx=5)

        opcoes_obs = ["", "Pendente", "Danificado"]
        combo_obs = ttk.Combobox(frame_lista, values=opcoes_obs, state="readonly", width=12)
        combo_obs.current(0)
        combo_obs.grid(row=linha, column=3, pady=5, padx=5)

        combo_obs.bind("<MouseWheel>", lambda e: "break")
        combo_obs.bind("<Button-4>", lambda e: "break")
        combo_obs.bind("<Button-5>", lambda e: "break")

        entry_quarto = tk.Entry(frame_lista, width=10)
        entry_quarto.grid(row=linha, column=4, pady=5, padx=5)

        entradas_checklist[id_mat] = (nome, qtd_esperada, entry_qtd, combo_obs, entry_quarto)
        lista_entries.append(entry_qtd)

    
    # NAVEGAÇÃO COM AS SETAS DO TECLADO
   
    def mover_foco(event, direcao, index):
        novo_index = index + direcao
        if 0 <= novo_index < len(lista_entries):
            lista_entries[novo_index].focus_set()

    for index, entry in enumerate(lista_entries):
        entry.bind("<Up>", lambda event, idx=index: mover_foco(event, -1, idx))
        entry.bind("<Down>", lambda event, idx=index: mover_foco(event, 1, idx))

    if lista_entries:
        lista_entries[0].focus_set()

    
    # SALVAR CHECKLIST E GERAR TXT
    
    def salvar_checklist():
        agora_completo = datetime.now()
        agora_str = agora_completo.strftime("%d/%m/%Y às %H:%M:%S")

        alertas = []
        detalhes_relatorio = []

        for id_mat, dados in entradas_checklist.items():
            nome, qtd_esperada, entry, combo_obs, entry_quarto = dados

            qtd_texto = entry.get()
            obs_texto = combo_obs.get() or "-"
            quarto_texto = entry_quarto.get().strip() or "-"

            if qtd_texto == "":
                messagebox.showerror("Erro", f"Você esqueceu de preencher a quantidade de '{nome}'.", parent=janela_checklist)
                return

            try:
                qtd_encontrada = int(qtd_texto)
            except ValueError:
                messagebox.showerror("Erro", f"A quantidade de '{nome}' deve ser um número!", parent=janela_checklist)
                return

            status_txt = "OK"

            info_extra = []
            if obs_texto != "-":
                info_extra.append(f"Obs: {obs_texto}")
            if quarto_texto != "-":
                info_extra.append(f"Qto: {quarto_texto}")

            aviso_extra = f" - ({' | '.join(info_extra)})" if info_extra else ""

            if qtd_encontrada < qtd_esperada:
                diferenca = qtd_esperada - qtd_encontrada
                alertas.append(f"⚠️ Faltam {diferenca}x '{nome}'{aviso_extra} (Anotado no relatório)")
                status_txt = f"FALTAM {diferenca}"

            elif qtd_encontrada > qtd_esperada:
                sobra = qtd_encontrada - qtd_esperada
                alertas.append(f"❓ Sobram {sobra}x '{nome}'{aviso_extra} (Anotado no relatório)")
                status_txt = f"SOBRAM {sobra}"

            detalhes_relatorio.append(
                f"{nome:<35} | {qtd_esperada:<9} | {qtd_encontrada:<10} | {status_txt:<15} | {obs_texto:<12} | {quarto_texto}")

        nome_arquivo = f"Checklist_{agora_completo.strftime('%Y-%m-%d_%H%M%S')}.txt"
        try:
            with open(nome_arquivo, "w", encoding="utf-8") as arquivo:
                arquivo.write("=" * 105 + "\n")
                arquivo.write("                                RELATÓRIO DE CHECK-LIST DIÁRIO\n")
                arquivo.write("=" * 105 + "\n")
                arquivo.write(f"Data e Hora da Conferência: {agora_str}\n\n")

                arquivo.write(
                    f"{'MATERIAL':<35} | {'ESPERADO':<9} | {'ENCONTRADO':<10} | {'STATUS':<15} | {'OBSERVAÇÃO':<12} | {'QUARTO'}\n")
                arquivo.write("-" * 105 + "\n")

                for linha in detalhes_relatorio:
                    arquivo.write(linha + "\n")

                arquivo.write("\n" + "=" * 105 + "\n")
                arquivo.write("RESUMO DE DIVERGÊNCIAS E ANOTAÇÕES:\n")
                if alertas:
                    for alerta in alertas:
                        arquivo.write(alerta + "\n")
                else:
                    arquivo.write("Nenhuma divergência de quantidade encontrada. Estoque perfeito!\n")
                arquivo.write("=" * 105 + "\n")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar o arquivo txt: {e}", parent=janela_checklist)
            return





        # 3. Exibir os avisos na interface ANTES de iniciar o processo do WhatsApp
        if alertas:
            mensagem_final = f"Check-list pronto '{nome_arquivo}'!\n\nAtenção aos Alertas:\n\n" + "\n".join(
                alertas)
            messagebox.showwarning("Atenção!", mensagem_final, parent=janela_checklist)
        else:
            messagebox.showinfo("Sucesso",
                                f"Check-list perfeito! Nenhum item faltando.\nRelatório '{nome_arquivo}' salvo.",
                                parent=janela_checklist)



        # 5. Fechar a janela do checklist instantaneamente
        janela_checklist.unbind_all("<MouseWheel>")
        janela_checklist.unbind_all("<Button-4>")
        janela_checklist.unbind_all("<Button-5>")
        janela_checklist.destroy()

    def ao_fechar():
        janela_checklist.unbind_all("<MouseWheel>")
        janela_checklist.unbind_all("<Button-4>")
        janela_checklist.unbind_all("<Button-5>")
        janela_checklist.destroy()

    janela_checklist.protocol("WM_DELETE_WINDOW", ao_fechar)

    tk.Button(janela_checklist, text="Salvar e Registrar Check-list", command=salvar_checklist, bg="#ff9900",
              font=("Arial", 11, "bold")).pack(pady=20)


def abrir_janela_relatorio():
    try:
        # USO DA NOVA API
        monitores_db = sistema.listar_monitores()
    except Exception as e:
        messagebox.showerror("Erro", str(e))
        return
    
    if not monitores_db:
        messagebox.showwarning("Aviso", "Você precisa cadastrar pelo menos um monitor primeiro para gerar o relatório!")
        return

    # Ajuste de índice: agora monitores_db traz (id_monitor, nome), então nome é linha[1]
    lista_monitores = [linha[1] for linha in monitores_db]

    janela_rel = tk.Toplevel(janela_principal)
    janela_rel.title("Gerar Relatório")
    janela_rel.geometry("300x200")
    janela_rel.transient(janela_principal)

    tk.Label(janela_rel, text="Quem está gerando este relatório?", font=("Arial", 11, "bold")).pack(pady=15)

    monitor_selecionado = tk.StringVar(janela_rel)
    monitor_selecionado.set(lista_monitores[0]) 

    menu_monitores = tk.OptionMenu(janela_rel, monitor_selecionado, *lista_monitores)
    menu_monitores.pack(pady=10)

    def confirmar_e_gerar():
        from datetime import datetime
        
        nome_responsavel = monitor_selecionado.get()
        agora = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
        nome_arquivo = f"Relatorio_Inventario_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.txt"
        
        try:
            # USO DA NOVA API
            materiais = sistema.listar_materiais()
            
            with open(nome_arquivo, "w", encoding="utf-8") as arquivo:
                arquivo.write("=" * 70 + "\n")
                arquivo.write("     RELATÓRIO OFICIAL DE INVENTÁRIO - LAZER\n")
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
                        arquivo.write(f"{mat[0]:<5} | {mat[1]:<25} | {mat[2]:<5} | {obs}\n")
                
                arquivo.write("\n" + "=" * 70 + "\n")
                arquivo.write(f"Relatório gerado e conferido por: {nome_responsavel}\n")
                arquivo.write("=" * 70 + "\n")
            
            messagebox.showinfo("Sucesso", f"Relatório gerado com sucesso!\n\nSalvo como: {nome_arquivo}", parent=janela_rel)
            janela_rel.destroy()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar o documento: {e}", parent=janela_rel)

    tk.Button(janela_rel, text="Gerar Relatório", command=confirmar_e_gerar, bg="blue", fg="white", font=("Arial", 10, "bold")).pack(pady=15)

def abrir_janela_movimentacoes():
        from datetime import datetime

        janela_mov = tk.Toplevel(janela_principal)
        janela_mov.title("Movimentações de Stock")
        janela_mov.geometry("450x420")
        janela_mov.transient(janela_principal)

        # Criação das abas
        abas = ttk.Notebook(janela_mov)
        abas.pack(fill="both", expand=True, padx=10, pady=10)

        aba_entrada = tk.Frame(abas)
        aba_dano = tk.Frame(abas)

        abas.add(aba_entrada, text="Registar Entrada")
        abas.add(aba_dano, text="Registar Dano/Perda")

        # Função partilhada para carregar e atualizar os materiais disponíveis
        def atualizar_combos_mov():
            materiais_db = sistema.listar_materiais()
            # Mostra o ID, Nome e a quantidade atual em stock
            lista_formatada = [f"{m[0]} - {m[1]} (Atual: {m[2]})" for m in materiais_db]

            combo_mat_ent['values'] = lista_formatada
            combo_mat_dano['values'] = lista_formatada

            if lista_formatada:
                combo_mat_ent.current(0)
                combo_mat_dano.current(0)
            else:
                combo_mat_ent.set('')
                combo_mat_dano.set('')

        # --- LÓGICA DA ABA 1: REGISTAR ENTRADA ---
        def confirmar_entrada():
            selecionado = combo_mat_ent.get()
            qtd_texto = entry_qtd_ent.get()
            data_texto = entry_data_ent.get()

            if not selecionado or qtd_texto == "" or data_texto == "":
                messagebox.showerror("Erro", "Todos os campos são obrigatórios!", parent=janela_mov)
                return

            try:
                quantidade = int(qtd_texto)
                if quantidade <= 0:
                    messagebox.showerror("Erro", "A quantidade deve ser maior que zero!", parent=janela_mov)
                    return
            except ValueError:
                messagebox.showerror("Erro", "A quantidade deve ser um número inteiro!", parent=janela_mov)
                return

            id_mat = int(selecionado.split(" - ")[0])
            try:
                # Chama a função do seu backend
                sistema.criar_entrada(data_texto, quantidade, id_mat)
                messagebox.showinfo("Sucesso", "Entrada de stock registada! O saldo foi atualizado.", parent=janela_mov)
                entry_qtd_ent.delete(0, tk.END)
                atualizar_combos_mov()  # Atualiza os números na interface
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao registar entrada: {e}", parent=janela_mov)

        # Layout Aba 1
        tk.Label(aba_entrada, text="Registar Entrada de Material", font=("Arial", 14, "bold"), fg="green").pack(pady=15)
        tk.Label(aba_entrada, text="Selecione o Material:").pack()
        combo_mat_ent = ttk.Combobox(aba_entrada, state="readonly", width=35)
        combo_mat_ent.pack(pady=5)

        tk.Label(aba_entrada, text="Quantidade a Adicionar:").pack()
        entry_qtd_ent = tk.Entry(aba_entrada, width=15)
        entry_qtd_ent.pack(pady=5)

        tk.Label(aba_entrada, text="Data (ANO-MÊS-DIA):").pack()
        entry_data_ent = tk.Entry(aba_entrada, width=15)
        entry_data_ent.insert(0, datetime.now().strftime("%Y-%m-%d"))  # Insere a data de hoje por defeito
        entry_data_ent.pack(pady=5)

        tk.Button(aba_entrada, text="📥 Confirmar Entrada", command=confirmar_entrada, bg="green", fg="white",
                  font=("Arial", 10, "bold")).pack(pady=20)

        # REGISTAR DANOS/PERDAS
        def confirmar_dano():
            selecionado = combo_mat_dano.get()
            qtd_texto = entry_qtd_dano.get()
            data_texto = entry_data_dano.get()

            if not selecionado or qtd_texto == "" or data_texto == "":
                messagebox.showerror("Erro", "Todos os campos são obrigatórios!", parent=janela_mov)
                return

            try:
                quantidade = int(qtd_texto)
                if quantidade <= 0:
                    messagebox.showerror("Erro", "A quantidade deve ser maior que zero!", parent=janela_mov)
                    return
            except ValueError:
                messagebox.showerror("Erro", "A quantidade deve ser um número inteiro!", parent=janela_mov)
                return

            id_mat = int(selecionado.split(" - ")[0])
            try:
                # Chama a função do seu backend
                sistema.criar_danos(data_texto, quantidade, id_mat)
                messagebox.showinfo("Sucesso", "Dano/Perda registado! O saldo foi reduzido.", parent=janela_mov)
                entry_qtd_dano.delete(0, tk.END)
                atualizar_combos_mov()  # Atualiza os números na interface
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao registar dano: {e}", parent=janela_mov)

        # Layout Aba 2
        tk.Label(aba_dano, text="Registar Material Danificado ou Perdido", font=("Arial", 14, "bold"), fg="red").pack(
            pady=15)
        tk.Label(aba_dano, text="Selecione o Material:").pack()
        combo_mat_dano = ttk.Combobox(aba_dano, state="readonly", width=35)
        combo_mat_dano.pack(pady=5)

        tk.Label(aba_dano, text="Quantidade Danificada/Perdida:").pack()
        entry_qtd_dano = tk.Entry(aba_dano, width=15)
        entry_qtd_dano.pack(pady=5)

        tk.Label(aba_dano, text="Data (ANO-MÊS-DIA):").pack()
        entry_data_dano = tk.Entry(aba_dano, width=15)
        entry_data_dano.insert(0, datetime.now().strftime("%Y-%m-%d"))  # Insere a data de hoje por defeito
        entry_data_dano.pack(pady=5)

        tk.Button(aba_dano, text="⚠️ Confirmar Baixa", command=confirmar_dano, bg="red", fg="white",
                  font=("Arial", 10, "bold")).pack(pady=20)

        # Inicializa os comboboxes com os dados do banco
        atualizar_combos_mov()



# ==========================================
#        CONSTRUÇÃO DA JANELA PRINCIPAL
# ==========================================

janela_principal = tk.Tk()
janela_principal.title("📦 MATERIAIS BBR - LAZER")

largura_janela = 400
altura_janela = 500

largura_tela = janela_principal.winfo_screenwidth()
altura_tela = janela_principal.winfo_screenheight()

pos_x = (largura_tela // 2) - (largura_janela // 2)
pos_y = (altura_tela // 2) - (altura_janela // 2)

janela_principal.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

# ==========================================
# FECHAMENTO SEGURO
# ==========================================
def fechar_sistema():
    """Garante que o banco de dados será fechado antes do programa encerrar."""
    try:
        sistema.fechar_conexao()
    except Exception:
        pass # Se der erro ao fechar, apenas ignora e força a saída
    janela_principal.destroy()

# Associa o clique no 'X' vermelho da janela principal ao fechamento seguro
janela_principal.protocol("WM_DELETE_WINDOW", fechar_sistema)

# ==========================================

tk.Label(janela_principal, text="MENU PRINCIPAL", font=("Arial", 18, "bold")).pack(pady=30)

tk.Button(janela_principal, text="1. Gerenciar Monitores", command=abrir_janela_monitor, width=30, height=2).pack(pady=10)
tk.Button(janela_principal, text="2. Gerenciar Materiais", command=abrir_janela_material, width=30, height=2).pack(pady=10)
tk.Button(janela_principal, text="3. Registrar Entradas e Perdas", command=abrir_janela_movimentacoes, width=30, height=2, bg="#f0f0f0").pack(pady=10)
tk.Button(janela_principal, text="4. Realizar Check-list Diário", command=abrir_janela_checklist, width=30, height=2).pack(pady=10)
tk.Button(janela_principal, text="5. Gerar Relatório de Estoque", command=abrir_janela_relatorio, width=30, height=2, bg="#e6e6e6").pack(pady=10)

# O botão Sair agora chama o fechamento seguro em vez de um 'destroy' direto
tk.Button(janela_principal, text="Sair do Sistema", command=fechar_sistema, bg="red", fg="white", width=20).pack(pady=40)

janela_principal.mainloop()