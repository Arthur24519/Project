import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Client, Car, Contract, Service, SparePart, Order
from django.contrib.auth import get_user_model

User  = get_user_model()

@pytest.mark.django_db
def test_user_access(client):
    # Создаем тестового обычного пользователя
    normal_user = User.objects.create_user(username='normaluser', password='userpassword')

    # Логинимся как обычный пользователь
    client.login(username='normaluser', password='userpassword')

    # Проверяем доступ к страницам, доступным только обычным пользователям
    response = client.get(reverse('user_data'))
    assert response.status_code == 200  # Обычный пользователь должен иметь доступ

    response = client.get(reverse('service_list'))
    assert response.status_code == 200  # Обычный пользователь должен иметь доступ

    response = client.get(reverse('sparepart_list'))
    assert response.status_code == 200  # Обычный пользователь должен иметь доступ

    # Проверяем доступ к страницам, доступным только администраторам
    response = client.get(reverse('client_list'))
    assert response.status_code == 403  # Обычный пользователь не должен иметь доступ

    response = client.get(reverse('car_list'))
    assert response.status_code == 403  # Обычный пользователь не должен иметь доступ

    response = client.get(reverse('contract_list'))
    assert response.status_code == 403  # Обычный пользователь не должен иметь доступ

    response = client.get(reverse('order_list'))
    assert response.status_code == 403  # Обычный пользователь не должен иметь доступ

    response = client.get(reverse('add_client'))
    assert response.status_code == 403  # Обычный пользователь не должен иметь доступ

@pytest.mark.django_db
def test_admin_access(client):
    # Создаем тестового администратора
    admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
    
    # Логинимся как администратор
    client.login(username='admin', password='adminpassword')

    # Проверяем доступ ко всем страницам
    response = client.get(reverse('client_list'))
    assert response.status_code == 200  # Администратор должен иметь доступ

    response = client.get(reverse('car_list'))
    assert response.status_code == 200  # Администратор должен иметь доступ

    response = client.get(reverse('contract_list'))
    assert response.status_code == 200  # Администратор должен иметь доступ

    response = client.get(reverse('service_list'))
    assert response.status_code == 200  # Администратор должен иметь доступ

    response = client.get(reverse('sparepart_list'))
    assert response.status_code == 200  # Администратор должен иметь доступ

    response = client.get(reverse('order_list'))
    assert response.status_code == 200  # Администратор должен иметь доступ

    response = client.get(reverse('add_client'))
    assert response.status_code == 200  # Администратор должен иметь доступ

    response = client.get(reverse('add_car'))
    assert response.status_code == 200  # Администратор должен иметь доступ

    response = client.get(reverse('add_contract'))
    assert response.status_code == 200  # Администратор должен иметь доступ

    response = client.get(reverse('add_service'))
    assert response.status_code == 200  # Администратор должен иметь доступ

    response = client.get(reverse('add_sparepart'))
    assert response.status_code == 200  # Администратор должен иметь доступ

    response = client.get(reverse('add_order'))
    assert response.status_code == 200  # Администратор должен иметь доступ

@pytest.mark.django_db
def test_login_success(client):
    # Создаем тестового пользователя
    test_user = User.objects.create_user(username='testuser', password='testpassword')

    # Пытаемся войти в систему с правильными данными
    response = client.post(reverse('login'), {'username': 'testuser', 'password': 'testpassword'})
    
    # Проверяем, что вход был успешным
    assert response.status_code == 302  # Ожидаем перенаправление после успешного вход assert response.wsgi_request.user.is_authenticated  # Проверяем, что пользователь аутентифицирован

@pytest.mark.django_db
def test_login_invalid_credentials(client):
    # Пытаемся войти в систему с неправильными данными
    response = client.post(reverse('login'), {'username': 'wronguser', 'password': 'wrongpassword'})
    
    # Проверяем, что вход не был успешным
    assert response.status_code == 200  # Ожидаем, что страница загрузится снова
    assert not response.wsgi_request.user.is_authenticated  # Проверяем, что пользователь не аутентифицирован

@pytest.mark.django_db
def test_logout(client):
    # Создаем тестового пользователя и входим в систему
    test_user = User.objects.create_user(username='testuser', password='testpassword')
    client.login(username='testuser', password='testpassword')  # Входим в систему

    # Выходим из системы
    response = client.post(reverse('logout'))
    
    # Проверяем, что выход был успешным
    assert response.status_code == 302  # Ожидаем перенаправление после выхода
    assert not response.wsgi_request.user.is_authenticated  # Проверяем, что пользователь не аутентифицирован

User  = get_user_model()

@pytest.mark.django_db
def test_add_client(client):
    # Создаем тестового администратора
    admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
    
    # Логинимся как администратор
    client.login(username='admin', password='adminpassword')

    # Пытаемся добавить нового клиента
    response = client.post(reverse('add_client'), {
        'full_name': 'Test_Client',
        'phone': '1234567890',
        'email': 'test@example.com',
        'address': '123 Test St'
    })

    # Проверяем, что клиент был успешно добавлен
    if response.status_code != 302:
        print(response.content)  # Выводим содержимое ответа для отладки
        # Выводим ошибки формы, если они есть
        if hasattr(response, 'context'):
            print("Response context:", response.context)

    assert response.status_code == 302  # Ожидаем перенаправление после успешного добавления
    assert Client.objects.filter(full_name='Test_Client').exists()  # Проверяем, что клиент существует

@pytest.mark.django_db
def test_edit_client(client):
    # Создаем тестового администратора
    admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
    
    # Логинимся как администратор
    client.login(username='admin', password='adminpassword')

    # Создаем тестового клиента
    test_client = Client.objects.create(
        full_name='Old_Client',
        phone='0987654321',
        encrypted_email='gAAAAABoCE_NCrzBIaU8VO6aUAkoduLTeEfBJBGEz1yenWo2ByJhRuCwr-EeG22bpMcMVxxpNVVDSxHzrSLyKgFTMMdP1RkC6w==',  # Зашифрованный email
        address='456 Old St'
    )

    # Пытаемся редактировать клиента
    response = client.post(reverse('edit_client', args=[test_client.pk]), {
        'full_name': 'Updated_Client',
        'phone': '1234567890',
        'email': 'updated@example.com',
        'address': '789 Updated St'
    })

    # Проверяем, что клиент был успешно обновлен
    if response.status_code != 302:
        print(response.content)  # Выводим содержимое ответа для отладки
        # Выводим ошибки формы, если они есть
        if hasattr(response, 'context'):
            print("Response context:", response.context)

    assert response.status_code == 302  # Ожидаем перенаправление после успешного редактирования
    test_client.refresh_from_db()  # Обновляем объект из базы данных
    assert test_client.full_name == 'Updated_Client'  # Проверяем, что имя клиента обновлено
    assert test_client.phone == '1234567890'  # Проверяем, что телефон обновлен

User  = get_user_model()

@pytest.mark.django_db
def test_delete_client(client):
    # Создаем тестового администратора
    admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
    
    # Логинимся как администратор
    client.login(username='admin', password='adminpassword')

    # Создаем тестового клиента
    test_client = Client()
    test_client.full_name = 'Client_to_Delete'
    test_client.phone = '1234567890'
    test_client.set_email('delete@example.com')  # Используем метод для установки зашифрованного email
    test_client.address = '123 Delete St'
    test_client.save()

    # Пытаемся удалить клиента
    response = client.post(reverse('delete_client', args=[test_client.pk]))

    # Проверяем, что клиент был успешно удален
    assert response.status_code == 302  # Ожидаем перенаправление после успешного удаления
    assert not Client.objects.filter(pk=test_client.pk).exists()  # Проверяем, что клиент больше не существует

@pytest.mark.django_db
def test_car_create(client):
    admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
    client.login(username='admin', password='adminpassword')

    # Создаем тестового клиента
    test_client = Client.objects.create(
        full_name='Test_Client',
        phone='1234567890',
        address='123 Test St'
    )

    response = client.post(reverse('add_car'), {  # Change 'car_create' to 'add_car'
        'brand': 'Toyota',
        'model': 'Camry',
        'year': 2020,
        'vin': '12345678901234567',
        'client_id': test_client.id
    })

    assert response.status_code == 302  # Ожидаем перенаправление
    assert Car.objects.filter(brand='Toyota', model='Camry').exists()  # Проверяем, что автомобиль создан

@pytest.mark.django_db
def test_car_update(client):
    admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
    client.login(username='admin', password='adminpassword')

    test_client = Client.objects.create(
        full_name='Test_Client',
        phone='1234567890',
        address='123 Test St'
    )
    car = Car.objects.create(
        brand='Toyota',
        model='Camry',
        year=2020,
        vin='12345678901234567',
        client=test_client
    )

    response = client.post(reverse('edit_car', args=[car.pk]), {  # Change 'car_update' to 'edit_car'
        'brand': 'Honda',
        'model': 'Accord',
        'year': 2021,
        'vin': '12345678901234567',
        'client_id': test_client.id
    })

    assert response.status_code == 302  # Ожидаем перенаправление
    car.refresh_from_db()
    assert car.brand == 'Honda'  # Проверяем, что бренд обновлен
    assert car.model == 'Accord'  # Проверяем, что модель обновлена

@pytest.mark.django_db
def test_car_delete(client):
    admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
    client.login(username='admin', password='adminpassword')

    test_client = Client.objects.create(
        full_name='Test_Client',
        phone='1234567890',
        address='123 Test St'
    )
    car = Car.objects.create(
        brand='Toyota',
        model='Camry',
        year=2020,
        vin='12345678901234567',
        client=test_client
    )

    response = client.post(reverse('delete_car', args=[car.pk]))  # Change 'car_delete' to 'delete_car'

    assert response.status_code == 302  # Ожидаем перенаправление
    assert not Car.objects.filter(pk=car.pk).exists()  # Проверяем, что автомобиль удален

@pytest.mark.django_db
def test_contract_create(client):
    admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
    client.login(username='admin', password='adminpassword')

    test_client = Client.objects.create(
        full_name='Test Client',
        phone='1234567890',
        address='123 Test St'
    )
    test_car = Car.objects.create(
        brand='Toyota',
        model='Camry',
        year=2020,
        vin='12345678901234567',
        client=test_client
    )

    response = client.post(reverse('add_contract'), {
        'client_id': test_client.id,
        'car_id': test_car.id,
        'date': '2023-10-01',
        'status': 'Active',
        'total_amount': 500.00
    })

    assert response.status_code == 302  # Ожидаем перенаправление
    assert Contract.objects.filter(client=test_client, car=test_car).exists()  # Проверяем, что договор создан

@pytest.mark.django_db
def test_contract_update(client):
    admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
    client.login(username='admin', password='adminpassword')

    test_client = Client.objects.create(
        full_name='Test Client',
        phone='1234567890',
        address='123 Test St'
    )
    test_car = Car.objects.create(
        brand='Toyota',
        model='Camry',
        year=2020,
        vin='12345678901234567',
        client=test_client
    )
    contract = Contract.objects.create(
        client=test_client,
        car=test_car,
        date='2023-10-01',
        status='Active',
        total_amount=500.00
    )

    response = client.post(reverse('edit_contract', args=[contract.pk]), {
        'client_id': test_client.id,
        'car_id': test_car.id,
        'date': '2023-10-02',
        'status': 'Completed',
        'total_amount': 600.00
    })

    assert response.status_code == 302  # Ожидаем перенаправление
    contract.refresh_from_db()
    assert contract.status == 'Completed'  # Проверяем, что статус обновлен
    assert contract.total_amount == 600.00  # Проверяем, что сумма обновлена

@pytest.mark.django_db
def test_contract_delete(client):
    admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
    client.login(username='admin', password='adminpassword')

    test_client = Client.objects.create(
        full_name='Test Client',
        phone='1234567890',
        address='123 Test St'
    )
    test_car = Car.objects.create(
        brand='Toyota',
        model='Camry',
        year=2020,
        vin='12345678901234567',
        client=test_client
    )
    contract = Contract.objects.create(
        client=test_client,
        car=test_car,
        date='2023-10-01',
        status='Active',
        total_amount=500.00
    )

    response = client.post(reverse('delete_contract', args=[contract.pk]))

    assert response.status_code == 302  # Ожидаем перенаправление
    assert not Contract.objects.filter(pk=contract.pk).exists()  # Проверяем, что автомобиль удален

@pytest.mark.django_db
def test_contract_create(client):
    admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
    client.login(username='admin', password='adminpassword')

    test_client = Client.objects.create(
        full_name='Test Client',
        phone='1234567890',
        address='123 Test St'
    )
    test_car = Car.objects.create(
        brand='Toyota',
        model='Camry',
        year=2020,
        vin='12345678901234567',
        client=test_client
    )

    response = client.post(reverse('add_contract'), {
        'client_id': test_client.id,
        'car_id': test_car.id,
        'date': '2023-10-01',
        'status': 'Active',
        'total_amount': 500.00
    })

    assert response.status_code == 302  # Ожидаем перенаправление
    assert Contract.objects.filter(client=test_client, car=test_car).exists()  # Проверяем, что договор создан

@pytest.mark.django_db
def test_contract_update(client):
    admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
    client.login(username='admin', password='adminpassword')

    test_client = Client.objects.create(
        full_name='Test Client',
        phone='1234567890',
        address='123 Test St'
    )
    test_car = Car.objects.create(
        brand='Toyota',
        model='Camry',
        year=2020,
        vin='12345678901234567',
        client=test_client
    )
    contract = Contract.objects.create(
        client=test_client,
        car=test_car,
        date='2023-10-01',
        status='Active',
        total_amount=500.00
    )

    response = client.post(reverse('edit_contract', args=[contract.pk]), {
        'client_id': test_client.id,
        'car_id': test_car.id,
        'date': '2023-10-02',
        'status': 'Completed',
        'total_amount': 600.00
    })

    assert response.status_code == 302  # Ожидаем перенаправление
    contract.refresh_from_db()
    assert contract.status == 'Completed'  # Проверяем, что статус обновлен
    assert contract.total_amount == 600.00  # Проверяем, что сумма обновлена

@pytest.mark.django_db
def test_contract_delete(client):
    admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
    client.login(username='admin', password='adminpassword')

    test_client = Client.objects.create(
        full_name='Test Client',
        phone='1234567890',
        address='123 Test St'
    )
    test_car = Car.objects.create(
        brand='Toyota',
        model='Camry',
        year=2020,
        vin='12345678901234567',
        client=test_client
    )
    contract = Contract.objects.create(
        client=test_client,
        car=test_car,
        date='2023-10-01',
        status='Active',
        total_amount=500.00
    )

    response = client.post(reverse('delete_contract', args=[contract.pk]))

    assert response.status_code == 302  # Ожидаем перенаправление
    assert not Contract.objects.filter (pk=contract.pk).exists()  # Проверяем, что договор удален

### Тесты для услуг
@pytest.mark.django_db
def test_service_create(client):
    admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
    client.login(username='admin', password='adminpassword')

    response = client.post(reverse('add_service'), {
        'name': 'Oil Change',
        'description': 'Change engine oil',
        'price': 100.00
    })

    assert response.status_code == 302  # Ожидаем перенаправление
    assert Service.objects.filter(name='Oil Change').exists()  # Проверяем, что услуга создана

@pytest.mark.django_db
def test_service_update(client):
    admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
    client.login(username='admin', password='adminpassword')

    service = Service.objects.create(
        name='Oil Change',
        description='Change engine oil',
        price=100.00
    )

    response = client.post(reverse('edit_service', args=[service.pk]), {
        'name': 'Premium Oil Change',
        'description': 'Change engine oil with premium oil',
        'price': 150.00
    })

    assert response.status_code == 302  # Ожидаем перенаправление
    service.refresh_from_db()
    assert service.name == 'Premium Oil Change'  # Проверяем, что название обновлено
    assert service.price == 150.00  # Проверяем, что цена обновлена

@pytest.mark.django_db
def test_service_delete(client):
    admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
    client.login(username='admin', password='adminpassword')

    service = Service.objects.create(
        name='Oil Change',
        description='Change engine oil',
        price=100.00
    )

    response = client.post(reverse('delete_service', args=[service.pk]))

    assert response.status_code == 302  # Ожидаем перенаправление
    assert not Service.objects.filter(pk=service.pk).exists()  # Проверяем, что услуга удалена

@pytest.mark.django_db
def test_sparepart_create(client):
    admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
    client.login(username='admin', password='adminpassword')

    response = client.post(reverse('add_sparepart'), {
        'name': 'Brake Pad',
        'price': 50.00,
        'quantity': 10
    })

    assert response.status_code == 302  # Ожидаем перенаправление
    assert SparePart.objects.filter(name='Brake Pad').exists()  # Проверяем, что запчасть создана

@pytest.mark.django_db
def test_sparepart_update(client):
    admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
    client.login(username='admin', password='adminpassword')

    spare_part = SparePart.objects.create(
        name='Brake Pad',
        price=50.00,
        quantity=10
    )

    response = client.post(reverse('edit_sparepart', args=[spare_part.pk]), {
        'name': 'Premium Brake Pad',
        'price': 70.00,
        'quantity': 5
    })

    assert response.status_code == 302  # Ожидаем перенаправление
    spare_part.refresh_from_db()
    assert spare_part.name == 'Premium Brake Pad'  # Проверяем, что название обновлено
    assert spare_part.price == 70.00  # Проверяем, что цена обновлена

@pytest.mark.django_db
def test_sparepart_delete(client):
    admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
    client.login(username='admin', password='adminpassword')

    spare_part = SparePart.objects.create(
        name='Brake Pad',
        price=50.00,
        quantity=10
    )

    response = client.post(reverse('delete_sparepart', args=[spare_part.pk]))

    assert response.status_code == 302  # Ожидаем перенаправление
    assert not SparePart.objects.filter(pk=spare_part.pk).exists()  # Проверяем, что запчасть удалена

@pytest.mark.django_db
def test_order_create(client):
    admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
    client.login(username='admin', password='adminpassword')

    test_client = Client.objects.create(
        full_name='Test Client',
        phone='1234567890',
        address='123 Test St'
    )
    service = Service.objects.create(
        name='Oil Change',
        description='Change engine oil',
        price=100.00
    )

    response = client.post(reverse('add_order'), {
        'client_id': test_client.id,
        'service_id': service.id,
        'order_date': '2023-10-01'
    })

    assert response.status_code == 302  # Ожидаем перенаправление
    assert Order.objects.filter(client=test_client, service=service).exists()  # Проверяем, что заказ создан

import datetime

@pytest.mark.django_db
def test_order_update(client):
    admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
    client.login(username='admin', password='adminpassword')

    test_client = Client.objects.create(
        full_name='Test Client',
        phone='1234567890',
        address='123 Test St'
    )
    service = Service.objects.create(
        name='Oil Change',
        description='Change engine oil',
        price=100.00
    )
    order = Order.objects.create(
        client=test_client,
        service=service,
        order_date='2023-10-01'
    )

    new_service = Service.objects.create(
        name='Tire Rotation',
        description='Rotate tires',
        price=50.00
    )

    response = client.post(reverse('edit_order', args=[order.pk]), {
        'client_id': test_client.id,
        'service_id': new_service.id,
        'order_date': '2023-10-02'
    })

    assert response.status_code == 302  # Ожидаем перенаправление
    order.refresh_from_db()
    assert order.service == new_service  # Проверяем, что услуга обновлена
    assert order.order_date == datetime.date(2023, 10, 2)  # Проверяем, что дата обновлена

@pytest.mark.django_db
def test_order_delete(client):
    admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
    client.login(username='admin', password='adminpassword')

    test_client = Client.objects.create(
        full_name='Test Client',
        phone='1234567890',
        address='123 Test St'
    )
    service = Service.objects.create(
        name='Oil Change',
        description='Change engine oil',
        price=100.00
    )
    order = Order.objects.create(
        client=test_client,
        service=service,
        order_date='2023-10-01'
    )

    response = client.post(reverse('delete_order', args=[order.pk]))

    assert response.status_code == 302  # Ожидаем перенаправление
    assert not Order.objects.filter(pk=order.pk).exists()  # Проверяем, что заказ удален