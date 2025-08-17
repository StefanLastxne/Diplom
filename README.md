# Diplom: UI + API autotests for ChangeNOW

## Описание
Проект — дипломная работа по автоматизации тестирования.  
Тестируем сервис обмена криптовалют [ChangeNOW](https://changenow.io/en) по UI и API.  

Автотесты покрывают:  
- **UI**: 5 кейсов (главная → Explore → exchange, ввод адреса, Confirm → переход на страницу транзакции и проверки формы).  
- **API**: 5 кейсов (currencies v2, exchange-amount v1, create exchange v1, exchanges v2, currencies-to v1, негативные).  

Структура проекта:
src/
api/
client.py # клиент с requests.Session
endpoints.py # эндпоинты
ui/
pages/... # PageObject'ы (если используешь)
tests/
test_ui.py # UI тесты
test_api.py # API тесты
conftest.py # фикстуры pytest
pytest.ini
requirements.txt
.env.example

## Подготовка окружения
1. Установить зависимости:  
   pip install -r requirements.txt
Скопировать .env.example → .env и заполнить при необходимости:

## env
API_BASE=https://api.changenow.io
FROM=btc
TO=eth
AMOUNT=0.01
PAYOUT_ADDRESS=YOUR_ETH_ADDRESS
API_KEY=         # опционально: нужен для /v2/exchanges и /exchange-amount

## Запуск тестов
### Все тесты:
pytest -q

### Только UI:
pytest -m ui -q

### Только API:
pytest -m api -q

### Allure-отчёт:
pytest -q --alluredir=allure-results
allure serve allure-results