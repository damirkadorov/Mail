# Обновляем пакеты и устанавливаем нужные системные утилиты
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv xvfb libnss3 -y

# Создаем папку для бота и переходим в нее
mkdir elektrine_bot && cd elektrine_bot

# Создаем и активируем виртуальное окружение (обязательно для Debian 12+)
python3 -m venv venv
source venv/bin/activate

# Устанавливаем библиотеки Python
pip install seleniumbase faker

# Устанавливаем драйвер Chrome через seleniumbase
seleniumbase install chromedriver
