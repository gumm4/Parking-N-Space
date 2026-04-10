import tkinter as tk
import sqlite3
from tkinter import messagebox,ttk,filedialog
import matplotlib.pyplot as plt
from fpdf import FDPF
from datetime import datetime,date

#----------------------------------------------------------------------BANCO DE DADOS--------------------------------------------------------------------------#

database = sqlite3.connect("vagas.db")
cursor = database.cursor()

#-------------------------------------------------------------------Tabela de CLientes-------------------------------------------------------------------------#

cursor.execute("""
               
CREATE TABLE IF NOT EXISTS clientes (
    
    cpf PRIMARY KEY INTEGER,
    nome TEXT,
    placa VARCHAR,
    quantidade INTEGER AUTOINCREMENT

)
"""
)

database.commit()
#--------------------------------------------------------------------------------------------------------------------------------------------------------------#

#-------------------------------------------------------------------Tabela das Vagas---------------------------------------------------------------------------#


cursor.execute("""
               
CREATE TABLE IF NOT EXISTS vaga (
    
    id INTEGER AUTOINCREMENT
    data TEXT,
    hora_entrada TEXT,
    hora_saida TEXT,
    placa PRIMARY KEY VARHCAR,
    tempo INTEGER,
    valor REAL,
    pagamento TEXT
)
"""
)


database.commit()

#--------------------------------------------------------------------------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------------------------------------------------------------------------#

cadastro = 0
listar = 0
atualizar = 0
excluir = 0
registros = []



#------------------------------------------------------------------FUNÇÕES-------------------------------------------------------------------------------------#

#----------------------------------------------------------------Cadastrar-------------------------------------------------------------------------------------#

def cadastro():
    
    nome            = entrada_nome.get.strip()
    cpf             = entrada_cpf.get.strip()
    placa           = entrada_placa.get.strip()
    quantidade      = int(quantidade) + 1
    
    """
    if cpf_cadastrado == cpf:
        
        messagebox.showinfo("Sucesso","Bem vindo de volta")  
    """
    
    if nome == "" or cpf == "" or placa == "":
        
        messagebox.showerror("Erro", "Todos os campos devem ser preenchidos")
        return
    else:
        
        cursor.execute("""
                   
        INSERT INTO clientes (cpf,nome,placa,quantidade)
        VALUES (?,?,?,?)
        
        """,(cpf,nome,placa,quantidade)
        )
        
        database.commit()
        messagebox.showinfo("Sucesso","Cadastro do Cliente feito com sucesso!")
    
#--------------------------------------------------------------------------------------------------------------------------------------------------------------#
    
    
def cadastrar_vaga():
    
    data            = date.today()
    hora_e          = datetime.now()
    hora_entrada    = hora_e.strftime("%H:%M:%S")
    hora_saida      = entrada_hora_saida.get().strip()
    tempo           = int(entrada_hora_inicio.get().strip()) - int(entrada_hora_saida.get().strip())
    valor           = tempo * 3
    pagamento       = entrada_pag.get().strip()
    
    if data == "" or hora_entrada == "" or hora_saida == "":
        
        messagebox.showerror("Erro","Todos os campos devem ser preenchidos")
        return
    
    cursor.execute("""
        
        INSERT INTO vagas (data,hora_entrada,hora_saida,tempo,valor)           
        VALUES(?,?,?,?,?)
        """(data,hora_entrada,hora_saida,tempo,valor)
    )
    
    database.commit()
    messagebox.showinfo("Sucesso","Vaga reservada com sucesso!")


    #--Listar--#
    
def listar():
    
    cursor.execute("SELECT * FROM clientes")
    registros = cursor.fetchall()
    listagem.delete(1.0, tk.END)
    
    for r in registros:
        
        listagem.insert(tk.END, f"{r}\n")
        
    cursor.execute("SELECT tempo * 3 FROM clientes ")
    valor_total = cursor.fetchall()
    
    cursor.execute("""
                
        INSERT INTO clientes(valor)
        VALUES(?)  
    """)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------#
  
#------------------------------------------------------------------Atualizar-----------------------------------------------------------------------------------#
        
def atualizar():
    
    cpf_cadastrado = entrada_cpf.get().strip()
    novo_pagamento = entrada_pag.get().strip()
    
    if cpf_cadastrado  == "" or not cpf_cadastrado.isdigit():
        
        messagebox.showerror("Erro","O CPF deve conter somente números.")
        return
    if novo_pagamento not in ["Recebido", "A Pagar"]:
        
        messagebox.showerror("Erro","O Pagamento deve ser 'Recebido' ou 'A Pagar'.")
        
    cursor.execute("UPDATE clientes SET pagamento = ? WHERE cpf = ? ", (novo_pagamento, cpf_cadastrado))
    database.commit()
    messagebox.showinfo("Sucesso","Pagamento atualizado com Sucesso!")

#--------------------------------------------------------------------------------------------------------------------------------------------------------------#

#--Excluir--#
    
def excluir():
    
    cpf_cadastrado = entrada_cpf.get().strip()
    
    if cpf_cadastrado == "" or not cpf_cadastrado.isdigit():
        messagebox.showerror("Erro","O CPF deve conter apenas números.")
        return
    
    cursor.execute("DELETE FROM clientes WHERE cpf = ?", (cpf_cadastrado))
    database.commit()
    messagebox.showinfo("Sucesso","O cliente foi excluído com sucesso!")
  
#--------------------------------------------------------------------------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------------------------------------------------------------------------#
  
"""def check_out():
    
    id_vaga = entrada_id.get().strip()
    
    if id_vaga == '' or not id_vaga.isdigit():
        
        messagebox.showerror("Erro","O campo de ID deve ser preenchido obrigatoriamente")
"""

#--------------------------------------------------------------------------------------------------------------------------------------------------------------#

#------------------------------------------------------------------Recebimento---------------------------------------------------------------------------------#

def recebimento():
    
    placa_registrada = entrada_placa.get().strip()
    hora_saida = entrada_hora_saida.get().strip()
    
    valor = int(hora_entrada) - int(hora_saida)
    
    cursor.execute("SELECT data, hora_saida FROM vagas")
    
    registro = cursor.fetchone()
    lista_receber.delete(1.0, tk.END)
    for r in registros:
        
        lista_receber.insert(tk.END, f"{r}\n")
        
    pagamento = entrada_pag.get().strip()
    
    cursor.execute("UPDATE vaga SET pagamento = ? WHERE id = ?"(pagamento,id_vaga))
        
#--------------------------------------------------------------------------------------------------------------------------------------------------------------#

#--------------------------------------------------------------FUNÇÃO DE RELATÓRIOS----------------------------------------------------------------------------#



def top_5():
       
    cursor.execute(
    """
    
    SELECT placa, COUNT(*) as vezes_usadas
    FROM  vagas
    GROUP BY placa
    ORDER BY vezes_usadas
    LIMIT 5
                  
    """
)

def relatorio_cliente():
    
    cursor.execute("SELECT * FROM clientes")
    registros = cursor.fetchall()
    cliente_relatorio.delete("1.0", tk.END)
    cliente_relatorio.insert(tk.END, f"{r}\n")

def pagamentos_pendentes():
    
    
    cursor.execute("SELECT *  FROM clientes WHERE pagamento = 'A pagar'")
    registros = cursor.fetchall()
    relatorio_pag.delete("1.0", tk.END)
    relatorio_pag.insert(tk.END, f"{r}\n")
    
def pagamentos_recebidos():
    
    cursor.execute("SELECT pagamento FROM clientes GROUP BY pagamentos")
    registros = cursor.fetchall()
    relatorio_pag.delete("1.0", tk.END)
    relatorio.pag.insert(tk.END, f"{r[0]}:  R$ {r[1]:.2f}\n")
