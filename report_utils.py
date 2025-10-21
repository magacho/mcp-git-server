def generate_extensions_report(processed_extensions, discarded_extensions):
    """
    Generate a report of processed and discarded file extensions
    
    Args:
        processed_extensions: Dictionary of processed file extensions
        discarded_extensions: Dictionary of discarded file extensions
    """
    print("\n===== FILE EXTENSIONS REPORT =====")
    print("Processed:")
    if processed_extensions:
        for ext, count in sorted(processed_extensions.items(), key=lambda x: -x[1]):
            print(f"  {ext or '[no extension]'}: {count}")
    else:
        print("  No files processed.")

    print("\nDiscarded:")
    if discarded_extensions:
        for ext, count in sorted(discarded_extensions.items(), key=lambda x: -x[1]):
            print(f"  {ext or '[no extension]'}: {count}")
    else:
        print("  No files discarded.")
    print("=" * 40 + "\n")

def generate_tokens_report(total_tokens_generated):
    """
    Generate a report of total tokens generated
    
    Args:
        total_tokens_generated: Total number of tokens
    """
    print(f"===== TOKENS REPORT =====")
    print(f"Total estimated tokens sent for embeddings: {total_tokens_generated}")
    print("=" * 40)