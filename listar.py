import os
import shutil
from datetime import datetime

try:
    import pathspec
except ImportError:
    pathspec = None


def carregar_gitignore(pasta_raiz):
    """Carrega regras do .gitignore."""
    gitignore = os.path.join(pasta_raiz, ".gitignore")
    if not pathspec or not os.path.exists(gitignore):
        return None
    with open(gitignore, "r", encoding="utf-8") as f:
        return pathspec.PathSpec.from_lines("gitwildmatch", f)


def ignorado_por_gitignore(caminho_relativo, spec):
    """Verifica se caminho está no .gitignore."""
    if spec is None:
        return False
    return spec.match_file(caminho_relativo.replace("\\", "/"))


def limpar_caches_python(pasta_raiz, spec=None):
    """
    Remove recursivamente:
      - pastas __pycache__
      - arquivos .pyc, .pyo, .pyd
    Respeita .gitignore e os diretórios padrão ignorados.
    """
    ignorar_diretorios = {
        "__pycache__",
        ".git",
        ".venv", "venv", "env",
        "node_modules",
        ".idea", ".vscode",
        ".pytest_cache", ".mypy_cache",
        ".coverage",
        "dist", "build"
    }
    extensoes_cache = {".pyc", ".pyo", ".pyd"}

    for raiz, diretorios, arquivos in os.walk(pasta_raiz):
        rel_raiz = os.path.relpath(raiz, pasta_raiz)
        if ignorado_por_gitignore(rel_raiz, spec):
            continue

        # Filtra diretórios a percorrer (evita entrar em pastas proibidas)
        diretorios[:] = [
            d for d in diretorios
            if d not in ignorar_diretorios
            and not ignorado_por_gitignore(os.path.join(rel_raiz, d), spec)
        ]

        # Remove pastas __pycache__
        for d in diretorios[:]:
            if d == "__pycache__":
                caminho_pasta = os.path.join(raiz, d)
                try:
                    shutil.rmtree(caminho_pasta)
                    print(f"🗑️  Removida: {caminho_pasta}")
                    diretorios.remove(d)  # evita andar dentro dela
                except Exception as e:
                    print(f"❌ Erro ao remover {caminho_pasta}: {e}")

        # Remove arquivos de cache
        for arquivo in arquivos:
            if any(arquivo.endswith(ext) for ext in extensoes_cache):
                caminho_arquivo = os.path.join(raiz, arquivo)
                try:
                    os.remove(caminho_arquivo)
                    print(f"🗑️  Removido: {caminho_arquivo}")
                except Exception as e:
                    print(f"❌ Erro ao remover {caminho_arquivo}: {e}")


def listar_pasta_corrente_txt():
    pasta_raiz = os.getcwd()
    nome_projeto = os.path.basename(pasta_raiz)
    arquivo_saida = os.path.join(pasta_raiz, "estrutura_projeto.txt")

    ignorar_diretorios = {
        "__pycache__",
        ".git",
        ".venv", "venv", "env",
        "node_modules",
        ".idea", ".vscode",
        ".pytest_cache", ".mypy_cache",
        ".coverage",
        "dist", "build"
    }
    ignorar_extensoes = {
        ".pyc", ".pyo", ".pyd",
        ".log", ".tmp", ".temp", ".bak", ".swp",
        ".sqlite-shm", ".sqlite-wal"
    }
    ignorar_arquivos = {".DS_Store", "Thumbs.db"}

    spec = carregar_gitignore(pasta_raiz)

    # 🔥 PASSO 1: Remover todos os caches Python antes de gerar a estrutura
    print("🧹 Procurando e removendo caches Python...")
    limpar_caches_python(pasta_raiz, spec)
    print("✅ Limpeza concluída.\n")

    # 🔥 PASSO 2: Gerar a estrutura do projeto (com os caches já eliminados)
    linhas = []
    linhas.append(f"Projeto: {nome_projeto}")
    linhas.append(f"Gerado em: {datetime.now():%d/%m/%Y %H:%M:%S}")
    linhas.append("=" * 80)

    for raiz, diretorios, arquivos in os.walk(pasta_raiz):
        rel_raiz = os.path.relpath(raiz, pasta_raiz)
        if ignorado_por_gitignore(rel_raiz, spec):
            continue

        diretorios[:] = [
            d for d in diretorios
            if d not in ignorar_diretorios
            and not ignorado_por_gitignore(os.path.join(rel_raiz, d), spec)
        ]

        nivel = raiz.replace(pasta_raiz, "").count(os.sep)
        indentacao = "│   " * nivel
        nome_dir = os.path.basename(raiz)

        if nivel == 0:
            linhas.append(f"📁 {nome_dir}/")
        else:
            linhas.append(f"{indentacao}├── 📁 {nome_dir}/")

        sub_indentacao = "│   " * (nivel + 1)
        arquivos.sort()

        for arquivo in arquivos:
            if arquivo in ignorar_arquivos:
                continue
            extensao = os.path.splitext(arquivo)[1].lower()
            if extensao in ignorar_extensoes:
                continue

            caminho_completo = os.path.join(raiz, arquivo)
            caminho_relativo = os.path.relpath(caminho_completo, pasta_raiz)

            if ignorado_por_gitignore(caminho_relativo, spec):
                continue

            try:
                tamanho = os.path.getsize(caminho_completo)
                tamanho_kb = round(tamanho / 1024, 2)
                linhas.append(f"{sub_indentacao}├── 📄 {arquivo} ({tamanho_kb} KB)")
            except Exception:
                linhas.append(f"{sub_indentacao}├── 📄 {arquivo}")

    with open(arquivo_saida, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))

    print("\n✅ Estrutura gerada com sucesso!")
    print(f"📄 Arquivo: {arquivo_saida}")


if __name__ == "__main__":
    listar_pasta_corrente_txt()