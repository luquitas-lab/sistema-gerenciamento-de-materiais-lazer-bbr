Sistema de Gerenciamento de Materiais e Estoque

Um sistema desktop desenvolvido em Python para o controle eficiente de inventário, registro de movimentações e auditoria de materiais através de check-lists diários. O sistema gera relatórios automatizados em texto e gráficos visuais para facilitar a tomada de decisão.

Funcionalidades

- Gestão de Usuários: Cadastro (sem autenticação), atualização e exclusão (soft delete) dos responsáveis pelo estoque.
- Gestão de Materiais: Controle completo do inventário (CRUD), com registro de quantidade inicial e observações.
- Movimentações de Estoque: Registro de Entradas (adição de novos itens).
- Registro de Danos/Perdas (baixa de itens com defeito ou extraviados).
- Triggers automáticas no banco de dados para recalcular o estoque instantaneamente.
- Check-list Diário Inteligente:
  * Conferência item a item do estoque atual.
  * Identificação automática de faltas ou sobras.
  * Geração automática de relatórios em `.txt` e gráficos em `.png` salvos direto na Área de Trabalho do usuário.
- Histórico e Auditoria: Log detalhado de todas as ações realizadas no sistema, vinculadas ao monitor responsável.

Tecnologias e Bibliotecas Utilizadas

Linguagem: Python 3
Interface Gráfica (GUI):`tkinter` e `ttk` 
Banco de Dados: `sqlite3` 
Geração de Gráficos: `matplotlib` e `numpy`
Concorrência: `threading` 

Estrutura do Projeto

A arquitetura foi dividida para separar a lógica de negócios, banco de dados e interface gráfica:

- `interface_main.py`: Ponto de entrada do aplicativo. Contém todas as janelas e a lógica de interação do usuário (Frontend).
- `backend_gerenciador.py`: Responsável pela conexão, criação do esquema, *triggers* e operações (CRUD) no banco de dados SQLite (`materiais.db`).
- `servico_checklist.py`: Lógica de negócios e validação matemática para o processamento do check-list e geração de alertas/arquivos de texto.
- `relatorio.py`: Módulo focado na renderização do gráfico de barras horizontal comparando o estoque "Esperado" vs "Encontrado".

 Onde os relatórios são salvos?
 
O sistema foi feito pensado em um público com o minimo de conhecimento em informática, então foi feito de forma inteligente para localizar o desktop automaticamente (seja no Windows, Mac ou Linux). 
Ao gerar relatórios ou realizar o Check-list, o sistema criará as seguintes pastas no seu desktop:

- Relatorios_TXT/: Para os relatórios textuais de inventário.
- Graficos_Checklist/: Para os relatórios visuais em .png.
