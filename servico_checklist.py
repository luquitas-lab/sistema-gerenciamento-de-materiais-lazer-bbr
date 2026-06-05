
import os
from datetime import datetime
import relatorio

def processar_checklist(monitor_responsavel, itens_verificados):
    """
    Recebe o nome do monitor e uma lista de dicionários contendo os dados do checklist.
    Retorna um dicionário com o status da operação, alertas e caminhos dos arquivos.
    """
    agora_completo = datetime.now()
    agora_str = agora_completo.strftime("%d/%m/%Y às %H:%M:%S")

    alertas = []
    detalhes_relatorio = []
    
    # NOVA LISTA: Guardará os dados estruturados para o gráfico
    dados_grafico = [] 

    # 1. VALIDAÇÃO E LÓGICA DE NEGÓCIO (MATEMÁTICA)
    for item in itens_verificados:
        nome = item['nome']
        qtd_esperada = item['esperado']
        qtd_texto = item['encontrado_txt']
        obs_texto = item['obs']
        quarto_texto = item['quarto']

        # Validações de entrada
        if qtd_texto == "":
            return {"sucesso": False, "erro": f"Você esqueceu de preencher a quantidade de '{nome}'."}

        try:
            qtd_encontrada = int(qtd_texto)
        except ValueError:
            return {"sucesso": False, "erro": f"A quantidade de '{nome}' deve ser um número inteiro!"}

        status_txt = "OK"
        info_extra = []
        texto_anotacao = "" # Texto que vai aparecer na ponta da barra no gráfico
        
        # Preparação das anotações
        if obs_texto != "-":
            info_extra.append(f"Obs: {obs_texto}")
            
            obs_lower = obs_texto.lower()
            if obs_lower in ['pendente', 'danificado']:
                nome_formatado = obs_lower.capitalize()
                if quarto_texto and quarto_texto != '-':
                    texto_anotacao = f"   [{nome_formatado} no Qto: {quarto_texto}]"
                else:
                    texto_anotacao = f"   [{nome_formatado}]"
                
        if quarto_texto != "-":
            info_extra.append(f"Qto: {quarto_texto}")

        aviso_extra = f" - ({' | '.join(info_extra)})" if info_extra else ""

        # Lógica de Faltas e Sobras
        if qtd_encontrada < qtd_esperada:
            diferenca = qtd_esperada - qtd_encontrada
            alertas.append(f"⚠️ Faltam {diferenca}x '{nome}'{aviso_extra} (Anotado no relatório)")
            status_txt = f"FALTAM {diferenca}"

        elif qtd_encontrada > qtd_esperada:
            sobra = qtd_encontrada - qtd_esperada
            alertas.append(f"❓ Sobram {sobra}x '{nome}'{aviso_extra} (Anotado no relatório)")
            status_txt = f"SOBRAM {sobra}"

        # Guarda a linha formatada para o TXT
        detalhes_relatorio.append(
            f"{nome:<35} | {qtd_esperada:<9} | {qtd_encontrada:<10} | {status_txt:<15} | {obs_texto:<12} | {quarto_texto}"
        )
        
        # Guarda os dados limpos para o Gráfico
        dados_grafico.append({
            'material': nome,
            'esperado': qtd_esperada,
            'encontrado': qtd_encontrada,
            'anotacao': texto_anotacao
        })

    # 2. GERAÇÃO DO ARQUIVO TXT
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    pasta_textos = os.path.join(diretorio_atual, "Relatorios_TXT")
    
    if not os.path.exists(pasta_textos):
        os.makedirs(pasta_textos)
        
    nome_base_txt = f"Checklist_{agora_completo.strftime('%Y-%m-%d_%H%M%S')}.txt"
    nome_arquivo_txt = os.path.join(pasta_textos, nome_base_txt)
    
    try:
        with open(nome_arquivo_txt, "w", encoding="utf-8") as arquivo:
            arquivo.write("=" * 105 + "\n")
            arquivo.write("                                RELATÓRIO DE CHECK-LIST DIÁRIO\n")
            arquivo.write("=" * 105 + "\n")
            arquivo.write(f"Data e Hora da Conferência: {agora_str}\n")
            arquivo.write(f"Conferido por (Monitor): {monitor_responsavel}\n\n")

            arquivo.write(f"{'MATERIAL':<35} | {'ESPERADO':<9} | {'ENCONTRADO':<10} | {'STATUS':<15} | {'OBSERVAÇÃO':<12} | {'QUARTO'}\n")
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
        return {"sucesso": False, "erro": f"Erro ao gerar o arquivo txt: {e}"}

    # 3. GERAÇÃO DO GRÁFICO (AGORA PASSANDO DADOS ESTRUTURADOS)
    try:
        nome_imagem = relatorio.criar_grafico(
            dados_grafico=dados_grafico, 
            monitor_responsavel=monitor_responsavel, 
            data_hora=agora_str, 
            caminho_txt=nome_arquivo_txt
        )
    except Exception as e:
        return {"sucesso": False, "erro": f"Erro ao gerar o gráfico em PNG: {e}"}

    # Retorna tudo o que a interface precisa saber
    return {
        "sucesso": True,
        "alertas": alertas,
        "nome_arquivo_txt": nome_arquivo_txt,
        "nome_imagem": nome_imagem
    }