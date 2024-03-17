from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

habit_docs = """
    Конечная точка API, позволяющая просматривать и редактировать привычки.

    list: Перечислить все привычки пользователя

    create: Создать привычку

    retrieve: Просмотреть привычку пользователя

    update: Обновить привычку

    partial_update: Частичное обновление привычки

    destroy: Удалить привычку

    published: Перечислить все общественные привычки

    test: Тестирование периодических напоминаний
    """

habit_docs_test =\
    swagger_auto_schema(
        methods=['get'],
        operation_summary='Endpoint для тестирования периодических напоминаний',
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={'res': openapi.Schema(type=openapi.TYPE_STRING)}
            )
        }
    )
