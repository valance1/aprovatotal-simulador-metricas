import pandas as pd
import re
from bs4 import BeautifulSoup
from unidecode import unidecode
from openpyxl import load_workbook

dataSim = []

# Abra o arquivo e leia o conteúdo
with open('data.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Crie um objeto BeautifulSoup
soup = BeautifulSoup(content, 'html.parser')

# Encontre todas as divs que contêm os dados do simulado
simulados = soup.find_all('div', {'class': 'bg-color-lightest flex w-full rounded-md p-4 xs:flex-col xs:items-start xs:gap-xl lg:flex-row lg:items-center lg:justify-between'})

# Para cada simulado, extraia as informações desejadas
for simulado in simulados:
    data = simulado.find('p', {'class': 'text-sm font-notoSans text-mono-color-darkest font-normal'}).text
    nome = simulado.find("h4", class_="font-poppins").text
    questoes = simulado.find('p', text=lambda t: t and "Questões" in t).text
    aproveitamento = simulado.find('span', text=lambda t: t and "%" in t).text

    data_simulado = {}
    data_simulado['data'] = re.search(r'\d{2}/\d{2}/\d{4}', data).group()
    data_simulado['nome'] = unidecode(re.sub(r'\d{2}/\d{2}/\d{4}', '', nome).strip()).split()[0]
    data_simulado['questoes'] = int(re.search(r'\d+', questoes).group())
    data_simulado['aproveitamento'] = int(re.search(r'\d+', aproveitamento).group())

    dataSim.append(data_simulado)

    # Imprima as informações
    #print(f'Data: {data}, Nome: {nome}, Questões: {questoes}, Aproveitamento: {aproveitamento}')
    #print(dataSim)


df = pd.DataFrame(dataSim)

# Escreva o DataFrame em um arquivo Excel
df.to_excel('simuladosBruto.xlsx', index=False)
print("Done")
