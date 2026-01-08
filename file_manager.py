import os
import csv

def salvar_em_txt(uf, municipios):
    nome_arquivo = f"municipios_{uf}.txt"
    caminho_arquivo = os.path.join("Municipios", nome_arquivo)
    with open(caminho_arquivo, 'w', encoding='utf-8') as arquivo:
        arquivo.write(f"Municípios do Estado {uf}\n\n")
        
        for municipio in municipios:
            nome = municipio.get('nome')
            microrregiao = municipio.get('microrregiao', {}).get('nome', 'N/A')
            mesorregiao = municipio.get('microrregiao', {}).get('mesorregiao', {}).get('nome', 'N/A')
            
            conteudo = (f"📍 Município: {nome}\n"
                        f"   Microrregião: {microrregiao}\n"
                        f"   Mesorregião: {mesorregiao}\n"
                        f"{'-' * 30}\n")
            
            arquivo.write(conteudo)
    return caminho_arquivo



def salvar_em_csv(uf, municipios):
    nome_arquivo = f"municipios_{uf}.csv"
    caminho_arquivo = os.path.join("Municipios", nome_arquivo)
    
    cabecalho = ['Município', 'Microrregião', 'Mesorregião']
    
    with open(caminho_arquivo, 'w', encoding='utf-8', newline='') as arquivo:
    
        escritor_csv = csv.writer(arquivo)
        escritor_csv.writerow(cabecalho)
        
        for municipio in municipios:
            escritor_csv.writerow([
                municipio.get('nome'),
                municipio.get('microrregiao', {}).get('nome', 'N/A'),
                municipio.get('microrregiao', {}).get('mesorregiao', {}).get('nome', 'N/A')
            ])
    return caminho_arquivo
    