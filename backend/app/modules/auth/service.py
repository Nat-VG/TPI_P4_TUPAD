from app.modules.usuarios.service import UsuarioService

# Auth reutiliza la lógica de usuarios (register / authenticate).
AuthService = UsuarioService
