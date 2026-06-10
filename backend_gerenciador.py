import sqlite3
from datetime import datetime
from contextlib import contextmanager
import os
from typing import Optional
import sys

class BancoDeDados:
    def __init__(self, nome_banco: str = 'materiais.db'):
        if getattr(sys, 'frozen', False):
            pasta_documentos = os.path.join(os.path.expanduser("~"), "Documents", "Sistema_Materiais")
            if not os.path.exists(pasta_documentos):
                os.makedirs(pasta_documentos)
            diretorio_atual = pasta_documentos
        else:
            diretorio_atual = os.path.dirname(os.path.abspath(__file__))
            
        self.nome_banco = os.path.join(diretorio_atual, nome_banco)
        self._inicializar_esquema()

    @contextmanager
    def _conectar(self):
        """
        Gerenciador de contexto para criar conexões efêmeras.
        Garante o fechamento do banco e ativa as chaves estrangeiras a cada operação.
        """
        conn = sqlite3.connect(self.nome_banco)
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
        finally:
            conn.close()

    def fechar_conexao(self) -> None:
        """
        Mantido apenas para compatibilidade. Como as conexões agora são dinâmicas,
        não há conexão persistente para fechar quando o aplicativo encerra.
        """
        pass

    def _inicializar_esquema(self) -> None:
        try:
            with self._conectar() as conn:
                with conn: # Gerencia o Commit/Rollback da transação
                    
                    conn.execute('''
                    CREATE TABLE IF NOT EXISTS monitor (
                        id_monitor INTEGER PRIMARY KEY AUTOINCREMENT, 
                        nome TEXT NOT NULL,
                        ativo INTEGER DEFAULT 1
                    )
                    ''')

                    conn.execute('''
                    CREATE TABLE IF NOT EXISTS material (
                        id_material INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        quantidade_material INT,
                        observacoes TEXT,
                        ativo INTEGER DEFAULT 1
                    )    
                    ''')

                    # Tenta adicionar a coluna caso o banco já exista com a versão antiga
                    try:
                        conn.execute("ALTER TABLE monitor ADD COLUMN ativo INTEGER DEFAULT 1")
                    except sqlite3.OperationalError:
                        pass # A coluna já existe

                    try:
                        conn.execute("ALTER TABLE material ADD COLUMN ativo INTEGER DEFAULT 1")
                    except sqlite3.OperationalError:
                        pass # A coluna já existe

                    conn.execute('''
                    CREATE TABLE IF NOT EXISTS entrada (
                        id_entrada INTEGER PRIMARY KEY AUTOINCREMENT,
                        entrada DATE,
                        quantidade_entrada INT,
                        id_material INT,
                        FOREIGN KEY (id_material) REFERENCES material(id_material)
                    )
                    ''')

                    conn.execute('''
                    CREATE TABLE IF NOT EXISTS danos (
                        id_danos INTEGER PRIMARY KEY AUTOINCREMENT,
                        data_danos DATE,
                        quantidade_danos INT,
                        id_material INT,
                        FOREIGN KEY (id_material) REFERENCES material(id_material)
                    )
                    ''')

                    conn.execute('''
                    CREATE TABLE IF NOT EXISTS historico_movimentacoes (
                        id_log INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_monitor INTEGER,
                        data_hora DATETIME,
                        acao TEXT NOT NULL,
                        detalhes TEXT,
                        FOREIGN KEY (id_monitor) REFERENCES monitor(id_monitor)
                    )
                    ''')

                    # Triggers mantidos sem alteração
                    conn.execute('''
                    CREATE TRIGGER IF NOT EXISTS atualiza_material_entrada
                    AFTER INSERT ON entrada BEGIN
                        UPDATE material SET quantidade_material = quantidade_material + NEW.quantidade_entrada WHERE id_material = NEW.id_material;
                    END;
                    ''')

                    conn.execute('''
                    CREATE TRIGGER IF NOT EXISTS atualiza_material_danos
                    AFTER INSERT ON danos BEGIN
                        UPDATE material SET quantidade_material = quantidade_material - NEW.quantidade_danos WHERE id_material = NEW.id_material;
                    END;
                    ''')

                    conn.execute('''
                    CREATE TRIGGER IF NOT EXISTS devolve_material_danos
                    AFTER DELETE ON danos BEGIN
                        UPDATE material SET quantidade_material = quantidade_material + OLD.quantidade_danos WHERE id_material = OLD.id_material;
                    END;
                    ''')

                    conn.execute('''
                    CREATE TRIGGER IF NOT EXISTS reverte_material_entrada
                    AFTER DELETE ON entrada BEGIN                                           
                        UPDATE material SET quantidade_material = quantidade_material - OLD.quantidade_entrada WHERE id_material = OLD.id_material;
                    END;
                    ''')

        except sqlite3.Error as e:
            raise Exception(f"Erro ao criar esquema do banco: {e}")

    # =================================================================
    # FUNÇÃO INTERNA DE LOG
    # =================================================================
    def _registrar_log(self, conn: sqlite3.Connection, id_monitor: int, acao: str, detalhes: str) -> None:
        """
        Recebe a conexão aberta da função pai para registrar no mesmo ciclo de transação.
        """
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            "INSERT INTO historico_movimentacoes (id_monitor, data_hora, acao, detalhes) VALUES (?, ?, ?, ?)",
            (id_monitor, agora, acao, detalhes)
        )

    # =================================================================
    # CADASTRAR/create
    # =================================================================
    def criar_monitor(self, nome: str) -> bool:
        try:
            with self._conectar() as conn:
                with conn:
                    conn.execute("INSERT INTO monitor (nome) VALUES (?)", (nome,))
            return True
        except sqlite3.Error as e:
            raise Exception(f"Erro ao criar monitor: {e}")

    def criar_material(self, nome: str, quantidade_material: int, observacoes: str = "", id_monitor: int = None) -> bool:
        try:
            with self._conectar() as conn:
                with conn:
                    cursor = conn.execute("INSERT INTO material (nome, quantidade_material, observacoes) VALUES (?, ?, ?)", (nome, quantidade_material, observacoes))
                    if id_monitor:
                        id_criado = cursor.lastrowid
                        self._registrar_log(conn, id_monitor, "CRIACAO_MATERIAL", f"Material '{nome}' (ID: {id_criado}) criado com {quantidade_material} unidades.")
            return True
        except sqlite3.Error as e:
            raise Exception(f"Erro ao criar material: {e}")

    def criar_entrada(self, data_entrada: str, quantidade_entrada: int, id_material: int, id_monitor: Optional[int] = None) -> bool:
        try:
            with self._conectar() as conn:
                with conn:
                    conn.execute("INSERT INTO entrada (entrada, quantidade_entrada, id_material) VALUES (?, ?, ?)", (data_entrada, quantidade_entrada, id_material))
                    self._registrar_log(conn, id_monitor, "ENTRADA", f"Adicionado {quantidade_entrada} unidades ao material ID {id_material}")
            return True
        except sqlite3.Error as e:
            raise Exception(f"Erro ao registrar entrada: {e}") from e

    def criar_danos(self, data_danos: str, quantidade_danos: int, id_material: int, id_monitor: int = None) -> bool:
        try:
            with self._conectar() as conn:
                with conn:
                    conn.execute("INSERT INTO danos (data_danos, quantidade_danos, id_material) VALUES (?,?,?)", (data_danos, quantidade_danos, id_material))
                    self._registrar_log(conn, id_monitor, "DANO_PERDA", f"Baixa de {quantidade_danos} unidades do material ID {id_material}")
            return True
        except sqlite3.Error as e:
            raise Exception(f"Erro ao registrar danos/perdas: {e}")

    # =================================================================
    # LER/read
    # =================================================================
    def listar_monitores(self) -> list:
        try:
            with self._conectar() as conn:
                # Retorna apenas os ativos
                return conn.execute("SELECT * FROM monitor WHERE ativo = 1").fetchall()
        except sqlite3.Error as e:
            raise Exception(f"Erro ao listar monitores: {e}")

    def listar_materiais(self) -> list:
        try:
            with self._conectar() as conn:
                # Retorna apenas os ativos
                return conn.execute("SELECT * FROM material WHERE ativo = 1").fetchall()
        except sqlite3.Error as e:
            raise Exception(f"Erro ao listar materiais: {e}")

    def listar_entradas(self) -> list:
        try:
            with self._conectar() as conn:
                return conn.execute("SELECT * FROM entrada").fetchall()
        except sqlite3.Error as e:
            raise Exception(f"Erro ao listar entradas: {e}")

    def listar_danos(self) -> list:
        try:
            with self._conectar() as conn:
                return conn.execute("SELECT * FROM danos").fetchall()
        except sqlite3.Error as e:
            raise Exception(f"Erro ao listar danos: {e}")

    def listar_historico(self) -> list:
        try:
            with self._conectar() as conn:
                return conn.execute('''
                    SELECT h.id_log, m.nome, h.data_hora, h.acao, h.detalhes 
                    FROM historico_movimentacoes h
                    LEFT JOIN monitor m ON h.id_monitor = m.id_monitor
                    ORDER BY h.id_log DESC
                ''').fetchall()
        except sqlite3.Error as e:
            raise Exception(f"Erro ao listar histórico: {e}")

    # =================================================================
    # ATUALIZAR/update
    # =================================================================
    def atualizar_monitor(self, id_monitor: int, nome: str) -> bool:
        try:
            with self._conectar() as conn:
                with conn:
                    conn.execute("UPDATE monitor SET nome = ? WHERE id_monitor = ?", (nome, id_monitor))
            return True
        except sqlite3.Error as e:
            raise Exception(f"Erro ao atualizar monitor: {e}")

    def atualizar_material(self, id_material: int, nome: str, observacoes: str, id_monitor: int = None) -> bool:
        try:
            with self._conectar() as conn:
                with conn:
                    conn.execute('''
                        UPDATE material 
                        SET nome = ?, observacoes = ? 
                        WHERE id_material = ?
                    ''', (nome, observacoes, id_material))
                    
                    self._registrar_log(conn, id_monitor, "ATUALIZACAO_MANUAL", f"Material ID {id_material} alterado para: {nome}")
            return True
        except sqlite3.Error as e:
            raise Exception(f"Erro ao atualizar material: {e}")

    # =================================================================
    # DELETAR/delete
    # =================================================================
    def deletar_monitor(self, id_monitor: int) -> bool:
        try:
            with self._conectar() as conn:
                with conn:
                    # Soft Delete: apenas desativa
                    conn.execute("UPDATE monitor SET ativo = 0 WHERE id_monitor = ?", (id_monitor,))
            return True
        except sqlite3.Error as e:
            raise Exception(f"Erro ao deletar monitor: {e}")

    def deletar_material(self, id_material: int, id_monitor: int = None) -> bool:
        try:
            with self._conectar() as conn:
                with conn:
                    conn.execute("UPDATE material SET ativo = 0 WHERE id_material = ?", (id_material,))
                    if id_monitor:
                        self._registrar_log(conn, id_monitor, "MATERIAL_ELIMINADO", f"Material ID {id_material} foi desativado do sistema.")
            return True
        except sqlite3.Error as e:
            raise Exception(f"Erro ao deletar material: {e}")