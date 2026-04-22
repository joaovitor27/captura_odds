import os
from rich.console import Console
from rich.theme import Theme

# Tema personalizado para padronizar as cores do nosso CLI
custom_theme = Theme({
    "info": "bold cyan",
    "success": "bold green",
    "warning": "bold yellow",
    "danger": "bold red",
    "highlight": "bold magenta"
})

console = Console(theme=custom_theme)

def clear_screen():
    """Limpa a tela do terminal para dar um aspecto de aplicativo."""
    os.system('cls' if os.name == 'nt' else 'clear')
