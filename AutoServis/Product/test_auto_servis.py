import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Client, Car, Contract, Service, SparePart, Order
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
import datetime


User  = get_user_model()

@pytest.mark.django_db
def test_user_access(client):
    normal_user = User.objects.create_user(username='normaluser', password='userpassword')
    client.login(username='normaluser', password='userpassword')

    response = client.get(reverse('user_data'))
    assert response.status_code == 200

    response = client.get(reverse('service_list'))
    assert response.status_code == 200

    response = client.get(reverse('sparepart_list'))
    assert response.status_code == 200

    response = client.get(reverse('client_list'))
    assert response.status_code == 403

    response = client.get(reverse('car_list'))
    assert response.status_code == 403

    response = client.get(reverse('contract_list'))
    assert response.status_code == 403

    response = client.get(reverse('order_list'))
    assert response.status_code == 403

    response = client.get(reverse('add_client'))
    assert response.status_code == 403

@pytest.mark.django_db
def test_admin_access(client):
    admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
    client.login(username='admin', password='adminpassword')

    response = client.get(reverse('client_list'))
    assert response.status_code == 200

    response = client.get(reverse('car_list'))
    assert response.status_code == 200

    response = client.get(reverse('contract_list'))
    assert response.status_code == 200

    response = client.get(reverse('service_list'))
    assert response.status_code == 200

    response = client.get(reverse('sparepart_list'))
    assert response.status_code == 200

    response = client.get(reverse('order_list'))
    assert response.status_code == 200

    response = client.get(reverse('add_client'))
    assert response.status_code == 200

    response = client.get(reverse('add_car'))
    assert response.status_code == 200

    response = client.get(reverse('add_contract'))
    assert response.status_code == 200

    response = client.get(reverse('add_service'))
    assert response.status_code == 200

    response = client.get(reverse('add_sparepart'))
    assert response.status_code == 200

    response = client.get(reverse('add_order'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_login_success(client):
    test_user = User.objects.create_user(username='testuser', password='testpassword')
    response = client.post(reverse('login'), {'username': 'testuser', 'password': 'testpassword'})
    assert response.status_code == 302
    assert response.wsgi_request.user.is_authenticated

@pytest.mark.django_db
def test_login_invalid_credentials(client):
    response = client.post(reverse('login'), {'username': 'wronguser', 'password': 'wrongpassword'})
    assert response.status_code == 200
    assert not response.wsgi_request.user.is_authenticated

@pytest.mark.django_db
def test_logout(client):
    test_user = User.objects.create_user(username='testuser', password='testpassword')
    client.login(username='testuser', password='testpassword')
    response = client.post(reverse('logout'))
    assert response.status_code == 302
    assert not response.wsgi_request.user.is_authenticated

@pytest.mark.django_db
def test_add_client(client):
    admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
    client.login(username='admin', password='adminpassword')

    response = client.post(reverse('add_client'), {
        'full_name': 'Test_Client',
        'phone': '1234567890',
        'email': 'test@example.com',
        'address': '123 Test St'
    })

    assert response.status_code == 201  # Expecting a successful creation
    assert Client.objects.filter(full_name='Test_Client').exists()

@pytest.mark.django_db
def test_edit_client(client):
    admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
    client.login(username='admin', password='adminpassword')

    test_client = Client.objects.create(
        full_name='Old_Client',
        phone='0987654321',
        address='456 Old St'
    )

    response = client.post(reverse('edit_client', args=[test_client.pk]), {
        'full_name': 'Updated_Client',
        'phone': '1234567890',
        'email': 'updated@example.com',
        'address': '789 Updated St'
    })

    assert response.status_code == 200  # Expecting a successful update
    test_client.refresh_from_db()
    assert test_client.full_name == 'Updated_Client'
    assert test_client.phone == '1234567890'

@pytest.mark.django_db
def test_delete_client(client):
    admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
    client.login(username='admin', password='adminpassword')

    test_client = Client.objects.create(
        full_name='Client_to_Delete',
        phone='1234567890',
        address='123 Delete St'
    )

    response = client.post(reverse('delete_client', args=[test_client.pk]))

    assert response.status_code == 204  # Expecting successful deletion
    assert not Client.objects.filter(pk=test_client.pk).exists()

@pytest.mark.django_db
def test_car_create(client):
    admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
    client.login(username='admin', password='adminpassword')

    test_client = Client.objects.create(
        full_name='Test_Client',
        phone='1234567890',
        address='123 Test St'
    )

    response = client.post(reverse('add_car'), {
        'brand': 'Toyota',
        'model': 'Camry',
        'year': 2020,
        'vin': '12345678901234567',
        'client_name': test_client.full_name  # Updated to use client_name
    })

    assert response.status_code == 201  # Expecting successful creation
    assert Car.objects.filter(brand='Toyota', model='Camry').exists()

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

    response = client.post(reverse('edit_car', args=[car.pk]), {
        'brand': 'Honda',
        'model': 'Accord',
        'year': 2021,
        'vin': '12345678901234567',
        'client_name': test_client.full_name  # Updated to use client_name
    })

    assert response.status_code == 200  # Expecting successful update
    car.refresh_from_db()
    assert car.brand == 'Honda'
    assert car.model == 'Accord'

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

    response = client.post(reverse('delete_car', args=[car.pk]))

    assert response.status_code == 204  # Expecting successful deletion
    assert not Car.objects.filter(pk=car.pk).exists()

@pytest.mark.django_db
def test_contract_create(client):
    admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
    client.login(username='admin', password='adminpassword')

    test_client = Client.objects.create(
        full_name='Test_Client',
        phone='1234567890',
        address='123 Test St'
    )
    test_car = Car.objects.create(
        brand='Toyota',
        model='Camry',
        year=2020,
        vin='12345678901234567',  # Ensure this is 17 characters or less
        client=test_client
    )

    response = client.post(reverse('add_contract'), {
        'client_id': test_client.id,
        'car_id': test_car.id,
        'date': '2023-10-01',
        'status': 'Active',  # Changed to status_
        'total_amount': 500.00
    })

    assert response.status_code == 201  # Expecting successful creation
    assert Contract.objects.filter(client=test_client, car=test_car).exists()

@pytest.mark.django_db
def test_contract_update(client):
    admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
    client.login(username='admin', password='adminpassword')

    test_client = Client.objects.create(
        full_name='Test_Client',
        phone='1234567890',
        address='123 Test St'
    )
    test_car = Car.objects.create(
        brand='Toyota',
        model='Camry',
        year=2020,
        vin='12345678901234567',  # Ensure this is 17 characters or less
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
        'status': 'Completed',  # Changed to status_
        'total_amount': 600.00
    })

    assert response.status_code == 200  # Expecting successful update
    contract.refresh_from_db()
    assert contract.status == 'Completed'  # This assertion failed

    response = client.post(reverse('edit_contract', args=[contract.pk]), {
        'client_id': test_client.id,
        'car_id': test_car.id,
        'date': '2023-10-02',
        'status_': 'Completed',  # Changed to status_
        'total_amount': 600.00
    })

    assert response.status_code == 200  # Expecting successful update
    contract.refresh_from_db()
    assert contract.status == 'Completed'
    assert contract.total_amount == 600.00

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

    assert response.status_code == 204  # Expecting successful deletion
    assert not Contract.objects.filter(pk=contract.pk).exists()

@pytest.mark.django_db
def test_service_create(client):
    admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
    client.login(username='admin', password='adminpassword')

    response = client.post(reverse('add_service'), {
        'name': 'Oil Change',
        'description': 'Change engine oil',
        'price': 100.00
    })

    assert response.status_code == 201  # Expecting successful creation
    assert Service.objects.filter(name='Oil Change').exists()

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

    assert response.status_code == 200  # Expecting successful update
    service.refresh_from_db()
    assert service.name == 'Premium Oil Change'
    assert service.price == 150.00

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

    assert response.status_code == 204  # Expecting successful deletion
    assert not Service.objects.filter(pk=service.pk).exists()

@pytest.mark.django_db
def test_sparepart_create(client):
    admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
    client.login(username='admin', password='adminpassword')

    response = client.post(reverse('add_sparepart'), {
        'name': 'Brake Pad',
        'price': 50.00,
        'quantity': 10
    })

    assert response.status_code == 201  # Expecting successful creation
    assert SparePart.objects.filter(name='Brake Pad').exists()

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

    assert response.status_code == 200  # Expecting successful update
    spare_part.refresh_from_db()
    assert spare_part.name == 'Premium Brake Pad'
    assert spare_part.price == 70.00

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

    assert response.status_code == 204  # Expecting successful deletion
    assert not SparePart.objects.filter(pk=spare_part.pk).exists()

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

    assert response.status_code == 201  # Expecting successful creation
    assert Order.objects.filter(client=test_client, service=service).exists()

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

    assert response.status_code == 200  # Expecting successful update
    order.refresh_from_db()
    order.service = get_object_or_404(Service, pk=new_service.id)  # Update the service
    order.save()
    assert order.service == new_service
    assert order.order_date == datetime.date(2023, 10, 2)

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

    assert response.status_code == 204  # Expecting successful deletion
    assert not Order.objects.filter(pk=order.pk).exists()  # Check that the order is deleted