### Контекст

- Тестовый проект
- Результатом создания проекта будет бэкенд-сервер, который возвращает клиенту JSON-структуры
- В 2018 году Джеймс Клир написал книгу «Атомные привычки», которая посвящена приобретению новых полезных привычек и искоренению старых плохих привычек. Заказчик прочитал книгу, впечатлился и обратился к вам с запросом реализовать трекер полезных привычек.
- В рамках учебного курсового проекта реализуйте бэкенд-часть SPA веб-приложения.


### Для запуска необходимо:

- Склонировать репозиторий
  ``` PowerShell
  https://github.com/Nudlik/drf_spa.git
  ```

  - Запустить и поднять через докер или пропустить и проделать пункты ниже
    ``` PowerShell
    docker-compose build
    ```
    - Запуск контейнеров на фоне с флагом -d
    ``` PowerShell
    docker-compose up 
    ```

- Cоздать виртуальное окружение
  ``` PowerShell
  - python -m venv venv
  ```

- Активировать виртуальное окружение
  ``` PowerShell
  .\venv\Scripts\activate
  ```

- Установить зависимости
  ``` PowerShell
  pip install -r requirements.txt
  ```

- Прописать в .env ваши настройки(пример файла .env.example):

- Приминить миграции
  ``` PowerShell
  python .\manage.py migrate
  ```

- Запустить брокер redis, заходим в wsl
  ``` PowerShell
  sudo service redis-server start
  ```

- Запускаем worker в Celery
  ``` PowerShell
  celery -A config worker -l INFO -P eventlet
  ```
  
- Запускаем периодические задачи Celery beat
  ``` PowerShell
  celery -A config beat -l INFO -S django
  ```

- Запустить программу из консоли/среды разработки
  ``` PowerShell
  python .\manage.py runserver
  ```
