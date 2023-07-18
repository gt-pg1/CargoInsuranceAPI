
# CargoInsuranceAPI

Сервис для расчета стоимости страхования грузов, разработанный на Python 3.10 с использованием FastAPI и Tortoise ORM. Данные хранятся в PostgreSQL.

## Описание

Сервис позволяет загрузить тарифы из JSON-файла и вычислять стоимость страхования на основе объявленной стоимости груза и актуального на заданную дату тарифа.

## Установка и Запуск

1.  Клонирование проекта:

```bash
git clone https://github.com/gt-pg1/CargoInsuranceAPI
```

2.  Перед запуском необходимо создать файл `.env` в корневой папке проекта с следующим содержимым:

        DB_USER=admin
        DB_PASSWORD=admin
        DB_NAME=CargoInsurance
        DB_HOST=db
        DB_PORT=5432
        RATES_FILE=rates.json

    Здесь `RATES_FILE` - это путь к JSON-файлу с тарифами.


3.  Запуск сервиса с помощью Docker Compose:

    _Перед запуском нужно убедиться, что 5432 порт свободен._

```bash
sudo docker-compose up
```

## Используемые технологии
-   Python 3.10
-   FastAPI
-   Tortoise
-   Asyncpg
-   Python-dotenv
-   PostgreSQL 15
-   Docker

## API

1.  Загрузка данных из JSON-файла в базу данных. Запрос POST на `http://localhost:8000/loaddata`. В теле запроса можно указать JSON объект с ключом `json_file`, в котором указан путь к JSON-файлу. Если параметр не указан, будет использован файл, указанный в `.env` в переменной `RATES_FILE`.
    
2.  Расчет стоимости страхования. Запрос GET на `http://localhost:8000/calculate_insurance`. В параметрах запроса необходимо указать дату (`date`), тип груза (`cargo_type`) и объявленную стоимость (`declared_value`).
    

Пример структуры JSON файла с тарифами:

        {
          "2023-07-10": [
            {"cargo_type": "Glass", "rate": "0.04"},
            {"cargo_type": "Wood", "rate": "0.03"},
            {"cargo_type": "Metal", "rate": "0.05"},
            {"cargo_type": "Plastic", "rate": "0.02"},
            {"cargo_type": "Other", "rate": "0.01"}
          ]
        }

## Примеры тестовых данных и использования API

В папке проекта есть пример тестового JSON файла `rates.json`. Вы можете использовать его для тестирования функциональности загрузки данных.

Удобнее тестировать через [Swagger UI интерфейс](http://localhost:8000/docs).

Для загрузки данных из этого файла в базу данных используйте следующий запрос:

```bash
curl -X POST http://localhost:8000/loaddata
``` 

_(Опционально) В теле запроса передайте:_

        {
          "json_file": "rates.json"
        }

Или нажмите **Try it out** -> **Execute** в Swagger.

После загрузки данных вы можете проверить расчет стоимости страхования с помощью запроса (запрос работает для файла `rates.json` из репозитория):

```bash
curl -X GET "http://localhost:8000/calculate_insurance?date=2023-07-10&cargo_type=Glass&declared_value=10000"
```

В Swagger передайте значения:

        date: 2023-07-10
        cargo_type: Glass
        declared_value: 10000

Этот запрос вернет стоимость страхования для груза типа "Glass" на дату "2023-07-10" с объявленной стоимостью 10000.