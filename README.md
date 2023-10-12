# Foodgram

## Описание

Продуктовый помощник позволяет в один клик собрать список покупок для  
приготовления блюд по предварительно выбранным рецептам.

## Технологии

- Python
- Django
- Django Rest Framework
- PostgreSQL

## Запуск backend-части проекта в dev-режиме на Linux

1. Установите и настройте СУБД [PostgreSQL](https://www.postgresql.org/)
2. Склонируйте репозиторий и перейдите в директорию проекта

    ```shell
    git clone https://github.com/mign0n/foodgram-project-react.git && cd foodgram-project-react
    ```

3. Установите виртуальное окружение, установите зависимости, выполните миграции
с помощью команды:

    ```shell
    make install
    ```

4. Скопируйте файл для переменных окружения (при необходимости измените их)

   ```shell
   cp .env.example .env
   ```

5. Запустите сервер:

    ```shell
    make run
    ```

6. Перейдите по адресу `127.0.0.1:8000/api/docs/swagger-ui`. Эта страница  
содержит интерактивную документацию по API.

## Запуск всего проекта в docker контейнерах на Linux

1. Установите docker и docker-compose [docs.docker.com](https://docs.docker.com/get-docker/)
2. Склонируйте репозиторий и перейдите в директорию проекта

    ```shell
    git clone https://github.com/mign0n/foodgram-project-react.git && cd foodgram-project-react
    ```

3. Скопируйте файл для переменных окружения (при необходимости измените их)

   ```shell
   cp .env.example .env
   ```

4. Перейдите в директорию `infra`, создайте необходимые контейнеры и запустите  
их

   ```shell
   cd infra
   sudo docker-compose build && sudo docker-compose up
   ```

5. Затем, выполните миграции, соберите static-файлы и скопируйте их в  
директорию, доступную веб-серверу

   ```shell
   sudo docker compose exec backend python manage.py migrate
   sudo docker compose exec backend python manage.py collectstatic
   sudo docker compose exec backend cp -r /app/foodgram/static/. /backend_static/static/
   ```

6. Создайте суперпользователя django

   ```shell
   sudo docker compose exec backend python manage.py createsuperuser
   ```

7. Загрузите ингредиенты в базу данных

   ```shell
   sudo docker compose exec backend python manage.py load_data -f ../data/ingredients.csv
   ```

8. С помощью админ-панели django создайте несколько тегов. Все готово.
   - Интерактивная документация по API: `localhost/api/docs/swagger-ui`;
   - Главная страница сайта: `localhost`.
