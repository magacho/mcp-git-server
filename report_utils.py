def generate_extensions_report(extensoes_processadas, extensoes_descartadas):
    print("\n===== FILE EXTENSION REPORT =====")
    print("Processed:")
    if extensoes_processadas:
        for ext, count in sorted(extensoes_processadas.items(), key=lambda x: -x[1]):
            print(f"  {ext or '[no extension]'}: {count}")
    else:
        print("  No files processed.")

    print("\nDiscarded:")
    if extensoes_descartadas:
        for ext, count in sorted(extensoes_descartadas.items(), key=lambda x: -x[1]):
            print(f"  {ext or '[no extension]'}: {count}")
    else:
        print("  No files discarded.")
    print("=============================================\n")

def generate_tokens_report(total_tokens_gerados):
    print(f"===== TOKEN REPORT =====")
    print(f"Total estimated tokens sent for embeddings: {total_tokens_gerados}")
    print("="*40)