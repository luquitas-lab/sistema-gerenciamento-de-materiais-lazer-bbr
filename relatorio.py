# Arquivo: relatorio.py
import matplotlib.pyplot as plt
import numpy as np
import os

def criar_grafico(caminho_do_arquivo):
    materiais = []
    esperado = []
    encontrado = []
    
    # NOVA LISTA: Para guardar apenas as anotações separadas dos nomes
    anotacoes_grafico = [] 
    
    monitor_responsavel = "Não identificado"

    # Leitura do arquivo TXT
    with open(caminho_do_arquivo, 'r', encoding='utf-8') as arquivo:
        ler_linhas = False
        for linha in arquivo:
            
            if 'Conferido por (Monitor):' in linha:
                monitor_responsavel = linha.split(':')[1].strip()
            
            if '---' in linha:
                ler_linhas = True
                continue
            if '====' in linha and ler_linhas:
                break
            
            if ler_linhas and '|' in linha:
                colunas = linha.split('|')
                nome_material = colunas[0].strip()
                
                if nome_material:
                    try:
                        qtd_esp = int(colunas[1].strip())
                        qtd_enc = int(colunas[2].strip())
                        
                        # LÓGICA SEPARADA: O nome do material fica intacto
                        texto_anotacao = ""
                        
                        if len(colunas) >= 6:
                            observacao = colunas[4].strip()
                            quarto = colunas[5].strip()
                            
                            # Prepara o texto que vai para a ponta da barra
                            if observacao.lower() == 'pendente':
                                if quarto and quarto != '-':
                                    texto_anotacao = f"   [Pendente no Qto: {quarto}]"
                                else:
                                    texto_anotacao = f"   [Pendente]"
                            elif observacao.lower() == 'danificado':
                                texto_anotacao = f"   [Danificado]"

                        materiais.append(nome_material)
                        esperado.append(qtd_esp)
                        encontrado.append(qtd_enc)
                        anotacoes_grafico.append(texto_anotacao) # Guarda o aviso nesta lista
                        
                    except (ValueError, IndexError):
                        continue

    # Configuração dos dados do gráfico
    materiais = materiais[::-1]
    esperado = esperado[::-1]
    encontrado = encontrado[::-1]
    anotacoes_grafico = anotacoes_grafico[::-1] # Inverte os avisos para acompanhar a ordem

    fig, ax = plt.subplots(figsize=(12, 14))
    y = np.arange(len(materiais))
    altura = 0.35

    ax.barh(y + altura/2, esperado, altura, label='Esperado', color='#d3d3d3')
    cores_encontrado = ['#ff6666' if enc < esp else '#66b3ff' for enc, esp in zip(encontrado, esperado)]
    barras_enc = ax.barh(y - altura/2, encontrado, altura, label='Encontrado', color=cores_encontrado)

    ax.set_xlabel('Quantidade de Itens')
    
    titulo_grafico = f'Relatório de Check-list Diário\nConferido por: {monitor_responsavel}'
    ax.set_title(titulo_grafico, fontsize=14, fontweight='bold')
    
    ax.set_yticks(y)
    ax.set_yticklabels(materiais)
    ax.legend()
    
    # ------------------------------------------------------------------
    # O SEGREDO ESTÁ AQUI: Rótulos customizados nas barras
    # Junta a quantidade encontrada com o texto de anotação
    labels_personalizados = [f"{enc}{anot}" for enc, anot in zip(encontrado, anotacoes_grafico)]
    ax.bar_label(barras_enc, labels=labels_personalizados, padding=5, color='#333333', fontweight='bold')
    
    # Dá 25% de espaço extra na direita para garantir que as frases caibam na imagem
    ax.margins(x=0.25)
    # ------------------------------------------------------------------

    plt.tight_layout()

    # Salvando na Área de Trabalho
    caminho_desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    pasta_destino = os.path.join(caminho_desktop, "Graficos_Checklist")
    
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
    
    nome_base = os.path.basename(caminho_do_arquivo).replace('.txt', '.png')
    nome_imagem = os.path.join(pasta_destino, nome_base)
    
    plt.savefig(nome_imagem, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Sucesso! Gráfico salvo na Área de Trabalho em: {nome_imagem}")
    
    return nome_imagem