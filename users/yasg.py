user_docs = """
    Конечная точка API, позволяющая просматривать и редактировать пользователей.

    list: Перечислить всех пользователей

    create: Создать пользователя

    retrieve: Просмотреть пользователя

    update: Обновить пользователя

    partial_update: Частичное обновление пользователя

    destroy: Удалить пользователя

    """

token_docs_pair = """
    Принимает набор учетных данных пользователя и возвращает пару веб-токенов доступа и обновления JSON 
    для подтверждения аутентификации этих учетных данных.
    """

token_docs_refresh = """
    Принимает веб-токен JSON типа обновления и возвращает веб-токен JSON типа доступа, 
    если токен обновления действителен.
    """
