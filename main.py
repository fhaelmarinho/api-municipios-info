from api_service import get_municipio_info
from file_manager import salvar_em_txt


def main():
    
    uf = input("Digite a UF do estado (ex: SP, RJ, MG, PR, BA, etc): ").upper().strip()
    
    if len(uf) != 2:
        print("Por favor, digite uma UF válida com apenas 2 letras.")
        return

    municipios = get_municipio_info(uf)

    if not municipios:
        print(f"Nenhum município encontrado para a UF: {uf}. Verifique se a sigla está correta.")
        return


    print(f"\nMunicípios do Estado {uf}\n")
    
    for municipio in municipios:
        nome = municipio.get('nome')
        microrregiao = municipio.get('microrregiao', {}).get('nome', 'N/A')
        mesorregiao = municipio.get('microrregiao', {}).get('mesorregiao', {}).get('nome', 'N/A')
            
        conteudo = salvar_em_txt(uf, municipios)
        
        print(f"📍 Município: {nome}\n"
            f"   Microrregião: {microrregiao}\n"
            f"   Mesorregião: {mesorregiao}\n"
            f"{'-' * 30}\n")
            
        print(conteudo)

if __name__ == "__main__":
    main()