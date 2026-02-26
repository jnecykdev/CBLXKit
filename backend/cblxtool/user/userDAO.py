# user/userDAO.py
from abc import ABC, abstractmethod

class UserDAO(ABC):
    @abstractmethod
    def create_user(self, username, password, email, telephone=None, birth_date=None, image=None):
        """Cria um novo usuário."""
        pass

    @abstractmethod
    def authenticate_user(self, username, password):
        """Autentica um usuário."""
        pass

    @abstractmethod
    def get_user_by_email(self, email):
        """Obtém um usuário pelo e-mail."""
        pass

    @abstractmethod
    def get_user_by_id(self, user_id):
        """Obtém um usuário pelo id."""
        pass
        
    @abstractmethod
    def update_user(self, user, username=None, telephone=None, birth_date=None, image=None):
        """Atualiza um usuário."""
        pass