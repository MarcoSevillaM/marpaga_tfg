from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
"""
Clase que genera el token de activación de la cuenta

"""
class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    Funcion que genera el token de activación de la cuenta

    Args:
        self (AccountActivationTokenGenerator): El objeto de la clase AccountActivationTokenGenerator
        user (User): El usuario al que se le generará el token
        timestamp (int): El tiempo en el que se generará el token
    
    Returns:
        str: El token de activación de la cuenta
    """
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )

account_activation_token = AccountActivationTokenGenerator()