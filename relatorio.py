# Arquivo: relatorio.py
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import numpy as np
import os

def criar_grafico(dados_grafico, monitor_responsavel, data_hora, caminho_txt):
    materiais = []
    esperado = []
    encontrado = []
    anotacoes_grafico = [] 
    
    # Extrai os dados diretamente do dicionário enviado pelo serviço
    for dado in dados_grafico:
        materiais.append(dado['material'])
        esperado.append(dado['esperado'])
        encontrado.append(dado['encontrado'])
        anotacoes_grafico.append(dado['anotacao'])

    # Configuração dos dados do gráfico (inverte para ficar de cima para baixo)
    materiais = materiais[::-1]
    esperado = esperado[::-1]
    encontrado = encontrado[::-1]
    anotacoes_grafico = anotacoes_grafico[::-1]

    # Mantendo o tamanho 16x16 e fontes ajustadas que você escolheu
    fig, ax = plt.subplots(figsize=(16, 16))
    y = np.arange(len(materiais))
    altura = 0.35

    ax.barh(y + altura/2, esperado, altura, label='Esperado', color='#d3d3d3')
    cores_encontrado = ['#ff6666' if enc < esp else '#66b3ff' for enc, esp in zip(encontrado, esperado)]
    barras_enc = ax.barh(y - altura/2, encontrado, altura, label='Encontrado', color=cores_encontrado)

    # Textos e Eixos
    ax.set_xlabel('Quantidade de Itens', fontsize=16, fontweight='bold')
    
    if data_hora:
        titulo_grafico = f'Relatório de Check-list Diário\nConferido por: {monitor_responsavel}   |   {data_hora}'
    else:
        titulo_grafico = f'Relatório de Check-list Diário\nConferido por: {monitor_responsavel}'
        
    ax.set_title(titulo_grafico, fontsize=22, fontweight='bold')
    
    ax.set_yticks(y)
    ax.set_yticklabels(materiais, fontsize=15)
    ax.tick_params(axis='x', labelsize=14)
    ax.legend(fontsize=14)
    
    labels_personalizados = [f"{enc}{anot}" for enc, anot in zip(encontrado, anotacoes_grafico)]
    ax.bar_label(barras_enc, labels=labels_personalizados, padding=5, color='#333333', fontweight='bold', fontsize=15)
    
    ax.margins(x=0.40)
    plt.tight_layout()

    # Salvando na Área de Trabalho
    caminho_desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    pasta_destino = os.path.join(caminho_desktop, "Graficos_Checklist")
    
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
    
    # Usa o nome do arquivo txt original como base para dar o mesmo nome ao PNG
    nome_base = os.path.basename(caminho_txt).replace('.txt', '.png')
    nome_imagem = os.path.join(pasta_destino, nome_base)
    
    plt.savefig(nome_imagem, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Sucesso! Gráfico salvo na Área de Trabalho em: {nome_imagem}")
    
    return nome_imagem