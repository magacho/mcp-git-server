def gerar_relatorio_extensoes(extensoes_processadas, extensoes_descartadas):
    print("\n===== RELATÓRIO DE EXTENSÕES DE ARQUIVO =====")
    print("Processados:")
    if extensoes_processadas:
        for ext, count in sorted(extensoes_processadas.items(), key=lambda x: -x[1]):
            print(f"  {ext or '[sem extensão]'}: {count}")
    else:
        print("  Nenhum arquivo processado.")

    print("\nDescartados:")
    if extensoes_descartadas:
        for ext, count in sorted(extensoes_descartadas.items(), key=lambda x: -x[1]):
            print(f"  {ext or '[sem extensão]'}: {count}")
    else:
        print("  Nenhum arquivo descartado.")
    print("=============================================\n")

def gerar_relatorio_tokens(total_tokens_gerados):
    print(f"===== RELATÓRIO DE TOKENS =====")
    print(f"Total estimado de tokens enviados para embeddings: {total_tokens_gerados}")
    print("="*40)