from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons

from datetime import datetime
import time

# Função para fazer login e navegar até a tela de simulados
def navigate_to_simulados(email, password):
    login_url = 'https://app.aprovatotal.com.br/login'
    simulados_url = 'https://app.aprovatotal.com.br/simulados/provas'
    
    # Inicializar o driver do Selenium
    driver = webdriver.Chrome() 
    
    # Fazendo login
    driver.get(login_url)
    time.sleep(5)
    driver.find_element("name", 'email').send_keys(email)
    driver.find_element("name", 'password').send_keys(password)
    driver.find_element(By.TAG_NAME, 'button').click()
    
    # Esperar um pouco para a página carregar completamente
    time.sleep(10)
    
    # Navegar até a tela de simulados
    driver.get(simulados_url)
    
    # Esperar um pouco para a página carregar completamente
    time.sleep(10)
    
    # Obtendo os dados da página após a navegação
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Fechar o driver após obter os dados
    driver.quit()
    
    return soup

# Função para extrair e plotar os dados
def extract_simulados_data(soup):
    print(soup.prettify())
    data_list = []
    for div in soup.select('div.flex.w-fit.flex-col.gap-sm'):
        print(div.prettify())
        data = {
            "Data": datetime.strptime(div.find("p", class_="text-sm").text.split("em ")[1], '%d/%m/%Y, às %H:%M'),
            "Disciplina": div.find("h4", class_="font-poppins").text.split()[0].lower(),
            "Aproveitamento": float(div.find_all("span", class_="xs:hidden")[0].text.split("%")[0])
        }
        data_list.append(data)


    print(data_list)
    #df = pd.DataFrame(data_list)
    return data_list

# Função para agrupar os simulados por disciplina
def group_simulados_by_disciplina(simulados_data):
    grouped_simulados = {}
    for simulado in simulados_data:
        disciplina = simulado["Disciplina"]
        if disciplina not in grouped_simulados:
            grouped_simulados[disciplina] = {"Data": [], "Aproveitamento": []}
        grouped_simulados[disciplina]["Data"].append(simulado["Data"])
        grouped_simulados[disciplina]["Aproveitamento"].append(simulado["Aproveitamento"])
    return grouped_simulados

def plot_simulados(grouped_simulados, selected_disciplinas):
    fig, ax = plt.subplots()
    lines_by_label = {}
    for disciplina, data in grouped_simulados.items():
        if not data['Data']:  # Verifica se há dados para a disciplina
            continue
        line, = ax.plot(data["Data"], data["Aproveitamento"], marker='o', linestyle='-', label=disciplina)
        lines_by_label[disciplina] = line
    if lines_by_label:  # Verifica se há linhas para adicionar à legenda
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    rax = ax.inset_axes([0.0, 0.0, 0.12, 0.2])
    labels = list(lines_by_label.keys())
    visibility = [True]*len(labels)  # Todas as checkboxes iniciam marcadas
    line_colors = [l.get_color() for l in lines_by_label.values()]
    check = CheckButtons(
        ax=rax,
        labels=labels,
        actives=visibility,
        label_props={'color': line_colors},
        frame_props={'edgecolor': line_colors},
        check_props={'facecolor': line_colors},
    )

    def callback(label):
        index = labels.index(label)
        visibility[index] = not visibility[index]
        lines_by_label[label].set_visible(visibility[index])
        plt.draw()

    check.on_clicked(callback)

    # Adiciona uma dica de ferramenta com data e porcentagem
    annot = ax.annotate("", xy=(0,0), xytext=(20,20),
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="w"),
            arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def update_annot(ind, line):
        x,y = line.get_data()
        annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
        text = f"{x[ind['ind'][0]].strftime('%Y-%m-%d')}: {y[ind['ind'][0]]}%"
        annot.set_text(text)

    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            for line in lines_by_label.values():
                cont, ind = line.contains(event)
                if cont and line.get_visible():
                    update_annot(ind, line)
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                    return
        if vis:
            annot.set_visible(False)
            fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", hover)

    plt.xlabel('Data')
    plt.ylabel('Aproveitamento (%)')
    plt.ylim(0, None)
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    #plt.legend()
    plt.show()

# Dados de login
email = input("Insira seu email: ")
password = input("Insira sua senha: ")

# Loop para atualizar os dados a cada intervalo
while True:
    soup = navigate_to_simulados(email, password)
    simulados_data = extract_simulados_data(soup)
    grouped_simulados = group_simulados_by_disciplina(simulados_data)
    disciplinas = list(grouped_simulados.keys())
    print(disciplinas)
    
    # Remover duplicatas e ordenar disciplinas alfabeticamente
    disciplinas = sorted(set([disciplina.capitalize() for disciplina in disciplinas]))
    #selected_disciplinas = ["biologia"]

    plot_simulados(grouped_simulados, disciplinas)
    # Intervalo de 1 hora
    time.sleep(3600)
