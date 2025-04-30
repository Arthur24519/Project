from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import Client, Car, Contract, Service, SparePart, Order
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from hashlib import sha256
from .forms import UserRegisterForm, UserLoginForm
from django.contrib.auth.mixins import UserPassesTestMixin
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg import openapi
from rest_framework import status as stat
from rest_framework.permissions import IsAuthenticated
from .serializers import ClientSerializer, ClientCreateSerializer, ClientUpdateSerializer, CarSerializer, CarCreateSerializer, CarUpdateSerializer, ContractSerializer, ContractCreateSerializer, ContractUpdateSerializer, ServiceSerializer, ServiceCreateSerializer, ServiceUpdateSerializer, SparePartSerializer, SparePartCreateSerializer, SparePartUpdateSerializer, OrderSerializer, OrderCreateSerializer, OrderUpdateSerializer


# Главная страница
def home(request):
    return render(request, "home.html")

# Представления для клиентов
class ClientListView(UserPassesTestMixin, APIView):
    def test_func(self):
        return self.request.user.is_staff

    @swagger_auto_schema(
        operation_description="Получить список клиентов",
        responses={200: openapi.Response('Успешно', ClientSerializer(many=True))}
    )
    def get(self, request):
        clients = Client.objects.all()
        serializer = ClientSerializer(clients, many=True)  # Сериализуем данные

        # Проверяем, является ли запрос API или HTML
        if request.accepted_renderer.format == 'json':
            return Response(serializer.data)  # Возвращаем сериализованные данные в формате JSON
        else:
            # Используем get_email() для отображения email
            clients_with_email = [(client, client.get_email()) for client in clients]
            return render(request, 'client_list.html', {'clients': clients_with_email})  # Возвращаем HTML-страницу

class ClientCreateView(UserPassesTestMixin, APIView):
    def test_func(self):
        return self.request.user.is_staff

    @swagger_auto_schema(
        operation_description="Создать нового клиента",
        request_body=ClientCreateSerializer,
        responses={
            201: openapi.Response('Клиент успешно создан', ClientCreateSerializer),
            400: 'Некорректные данные'
        }
    )
    def post(self, request):
        # Проверяем, является ли запрос API или HTML
        if request.accepted_renderer.format == 'json':
            serializer = ClientCreateSerializer(data=request.data)  # Используем сериализатор для валидации данных

            if serializer.is_valid():
                full_name = serializer.validated_data['full_name']
                phone = serializer.validated_data['phone']
                email = serializer.validated_data['email']
                address = serializer.validated_data['address']

                # Проверка на наличие пробелов в ФИО
                if ' ' in full_name:
                    return Response({"error": "ФИО не должно содержать пробелов."}, status=stat.HTTP_400_BAD_REQUEST)

                # Хешируем email для проверки существования
                hashed_email = sha256(email.encode()).hexdigest()
                if Client.objects.filter(encrypted_email=hashed_email).exists():
                    return Response({"error": "Клиент с таким email уже существует."}, status=stat.HTTP_400_BAD_REQUEST)

                try:
                    client = Client(full_name=full_name, phone=phone, address=address)
                    client.set_email(email)  # Зашифровываем email
                    client.save()
                    return Response(serializer.data, status=stat.HTTP_201_CREATED)  # Возвращаем созданного клиента
                except Exception as e:
                    return Response({"error": f"Произошла ошибка: {str(e)}"}, status=stat.HTTP_400_BAD_REQUEST)

            return Response(serializer.errors, status=stat.HTTP_400_BAD_REQUEST)  # Возвращаем ошибки валидации
        else:
            # Обработка HTML-запроса
            full_name = request.POST.get('full_name')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            address = request.POST.get('address')

            # Проверка на наличие пробелов в Ф ИО
            if ' ' in full_name:
                error_message = "ФИО не должно содержать пробелов."
                return render(request, 'client_form.html', {'error_message': error_message})

            if full_name and phone and email and address:
                # Хешируем email для проверки существования
                hashed_email = sha256(email.encode()).hexdigest()
                if Client.objects.filter(encrypted_email=hashed_email).exists():
                    error_message = "Клиент с таким email уже существует."
                    return render(request, 'client_form.html', {'error_message': error_message})

                try:
                    client = Client(full_name=full_name, phone=phone, address=address)
                    client.set_email(email)  # Зашифровываем email
                    client.save()
                    return redirect('client_list')
                except Exception as e:
                    error_message = f"Произошла ошибка: {str(e)}"
                    return render(request, 'client_form.html', {'error_message': error_message})

            error_message = "Некорректные данные."
            return render(request, 'client_form.html', {'error_message': error_message})

    def get(self, request):
        return render(request, 'client_form.html')  # Возвращаем HTML-форму для создания клиента

class ClientUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Обновить информацию о клиенте",
        request_body=ClientUpdateSerializer,
        responses={
            200: openapi.Response('Клиент успешно обновлен', ClientUpdateSerializer),
            400: 'Некорректные данные',
            404: 'Клиент не найден'
        }
    )
    def post(self, request, pk):
        # Проверяем, является ли запрос API или HTML
        if request.accepted_renderer.format == 'json':
            client = get_object_or_404(Client, pk=pk)
            serializer = ClientUpdateSerializer(client, data=request.data, partial=True)

            if serializer.is_valid():
                full_name = serializer.validated_data.get('full_name', client.full_name)
                phone = serializer.validated_data.get('phone', client.phone)
                email = serializer.validated_data.get('email', None)
                address = serializer.validated_data.get('address', client.address)

                # Проверка на наличие пробелов в ФИО
                if ' ' in full_name:
                    return Response({"error": "ФИО не должно содержать пробелов."}, status=stat.HTTP_400_BAD_REQUEST)

                if email:
                    client.set_email(email)  # Зашифровываем email

                client.full_name = full_name
                client.phone = phone
                client.address = address
                client.save()
                return Response(serializer.data, status=stat.HTTP_200_OK)  # Возвращаем обновленного клиента

            return Response(serializer.errors, status=stat.HTTP_400_BAD_REQUEST)  # Возвращаем ошибки валидации
        else:
            # Обработка HTML-запроса
            client = get_object_or_404(Client, pk=pk)
            full_name = request.POST.get('full_name', client.full_name)
            phone = request.POST.get('phone', client.phone)
            email = request.POST.get('email')
            address = request.POST.get('address', client.address)

            # Проверка на наличие пробелов в ФИО
            if ' ' in full_name:
                error_message = "ФИО не должно содержать пробелов."
                return render(request, 'client_form.html', {'client': client, 'error_message': error_message})

            if email:
                client.set_email(email)  # Зашифровываем email
            client.full_name = full_name
            client.phone = phone
            client.address = address
            client.save()
            return redirect('client_list')

    def get(self, request, pk):
        client = get_object_or_404(Client, pk=pk)
        return render(request, 'client_form.html', {'client': client})  # Возвращаем HTML-форму для обновления клиента

class ClientDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Удалить клиента",
        responses={
            204: 'Клиент успешно удален',
            404: 'Клиент не найден'
        }
    )
    def post(self, request, pk):
        # Проверяем, является ли запрос API или HTML
        if request.accepted_renderer.format == 'json':
            client = get_object_or_404(Client, pk=pk)
            try:
                client.delete()
                return Response(status=stat.HTTP_204_NO_CONTENT)  # Возвращаем статус 204 No Content
            except Exception as e:
                return Response({"error": f"Ошибка при удалении клиента: {str(e)}"}, status=stat .HTTP_400_BAD_REQUEST)
        else:
            # Обработка HTML-запроса
            client = get_object_or_404(Client, pk=pk)
            try:
                client.delete()
                messages.success(request, 'Клиент успешно удален.')
            except Exception as e:
                messages.error(request, f"Ошибка при удалении клиента: {str(e)}")
            return redirect('client_list')  # Перенаправляем на список клиентов

# Представления для автомобилей
class CarListView(UserPassesTestMixin, APIView):
    def test_func(self):
        return self.request.user.is_staff

    @swagger_auto_schema(
        operation_description="Получить список автомобилей",
        responses={200: openapi.Response('Успешно', CarSerializer(many=True))}
    )
    def get(self, request):
        # Проверяем, является ли запрос API или HTML
        if request.accepted_renderer.format == 'json':
            cars = Car.objects.all()
            serializer = CarSerializer(cars, many=True)  # Сериализуем данные
            return Response(serializer.data)  # Возвращаем сериализованные данные
        else:
            # Обработка HTML-запроса
            cars = Car.objects.all()
            return render(request, 'car_list.html', {'cars': cars})  # Возвращаем HTML-страницу
            
class CarCreateView(APIView):
    @swagger_auto_schema(
        operation_description="Создать новый автомобиль",
        request_body=CarCreateSerializer,
        responses={
            201: openapi.Response('Успешно создано', CarCreateSerializer),
            400: 'Некорректные данные'
        }
    )
    def post(self, request):
        if request.accepted_renderer.format == 'json':
            serializer = CarCreateSerializer(data=request.data)

            if serializer.is_valid():
                brand = serializer.validated_data['brand']
                model = serializer.validated_data['model']
                year = serializer.validated_data['year']
                vin = serializer.validated_data['vin']
                client_name = serializer.validated_data['client_name']  # Используем client_name для JSON

                # Проверка длины VIN
                if len(vin) > 17:
                    return Response({"error": "VIN не может превышать 17 символов."}, status=stat.HTTP_400_BAD_REQUEST)

                # Находим клиента по полному имени
                client = get_object_or_404(Client, full_name=client_name)  # Изменено на поиск по full_name
                Car.objects.create(brand=brand, model=model, year=year, vin=vin, client=client)
                return Response(serializer.data, status=stat.HTTP_201_CREATED)

            return Response(serializer.errors, status=stat.HTTP_400_BAD_REQUEST)
        else:
            # Обработка HTML-запроса
            brand = request.POST.get('brand')
            model = request.POST.get('model')
            year = request.POST.get('year')
            vin = request.POST.get('vin')
            client_id = request.POST.get('client_id')  # Используем client_id для HTML

            if len(vin) > 17:
                error_message = "VIN не может превышать 17 символов."
                return render(request, 'car_form.html', {'error_message': error_message})

            if brand and model and year and vin and client_id:
                # Находим клиента по ID
                client = get_object_or_404(Client, id=client_id)  # Изменено на поиск по ID
                Car.objects.create(brand=brand, model=model, year=year, vin=vin, client=client)
                return redirect('car_list')

            error_message = "Некорректные данные."
            return render(request, 'car_form.html', {'error_message': error_message})
            
    def get(self, request):
        clients = Client.objects.all()
        return render(request, 'car_form.html', {'clients': clients})

class CarUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Обновить информацию об автомобиле",
        request_body=CarUpdateSerializer,
        responses={
            200: openapi.Response('Автомобиль успешно обновлен', CarUpdateSerializer),
            400: 'Некорректные данные',
            404: 'Автомобиль не найден'
        }
    )
    def post(self, request, pk):
        # Проверяем, является ли запрос API или HTML
        if request.accepted_renderer.format == 'json':
            car = get_object_or_404(Car, pk=pk)
            serializer = CarUpdateSerializer(car, data=request.data, partial=True)

            if serializer.is_valid():
                brand = serializer.validated_data.get('brand', car.brand)
                model = serializer.validated_data.get('model', car.model)
                year = serializer.validated_data.get('year', car.year)
                vin = serializer.validated_data.get('vin', car.vin)
                client_id = serializer.validated_data.get('client_id', None)

                if client_id:
                    client = get_object_or_404(Client, pk=client_id)
                    car.client = client

                car.brand = brand
                car.model = model
                car.year = year
                car.vin = vin
                car.save()
                return Response(serializer.data, status=stat.HTTP_200_OK)  # Возвращаем обновленный автомобиль

            return Response(serializer.errors, status=stat.HTTP_400_BAD_REQUEST)  # Возвращаем ошибки валидации
        else:
            # Обработка HTML-запроса
            car = get_object_or_404(Car, pk=pk)
            brand = request.POST.get('brand', car.brand)
            model = request.POST.get('model', car.model)
            year = request.POST.get('year', car.year)
            vin = request.POST.get('vin', car.vin)
            client_id = request.POST.get('client_id')

            if client_id:
                client = get_object_or_404(Client, pk=client_id)
                car.client = client

            car.brand = brand
            car.model = model
            car.year = year
            car.vin = vin
            car.save()
            return redirect('car_list')  # Перенаправляем на список автомобилей

    def get(self, request, pk):
        car = get_object_or_404(Car, pk=pk)
        clients = Client.objects.all()  # Получаем всех клиентов
        return render(request, 'car_form.html', {'car': car, 'clients': clients})  # Передаем клиентов в контекст

class CarDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Удалить автомобиль",
        responses={
            204: 'Автомобиль успешно удален',
            404: 'Автомобиль не найден'
        }
    )
    def post(self, request, pk):
        # Проверяем, является ли запрос API или HTML
        if request.accepted_renderer.format == 'json':
            car = get_object_or_404(Car, pk=pk)
            try:
                car.delete()
                return Response(status=stat.HTTP_204_NO_CONTENT)  # Возвращаем статус 204 No Content
            except Exception as e:
                return Response({"error": f"Ошибка при удалении автомобиля: {str(e)}"}, status=stat.HTTP_400_BAD_REQUEST)
        else:
            # Обработка HTML-запроса
            car = get_object_or_404(Car, pk=pk)
            try:
                car.delete()
                messages.success(request, 'Автомобиль успешно удален.')
            except Exception as e:
                messages.error(request, f"Ошибка при удалении автомобиля: {str(e)}")
            return redirect('car_list')  # Перенаправляем на список автомобилей

# Представления для договоров
class ContractListView(UserPassesTestMixin, APIView):
    def test_func(self):
        return self.request.user.is_staff

    @swagger_auto_schema(
        operation_description="Получить список контрактов",
        responses={200: openapi.Response('Успешно', ContractSerializer(many=True))}
    )
    def get(self, request):
        # Проверяем, является ли запрос API или HTML
        if request.accepted_renderer.format == 'json':
            contracts = Contract.objects.all()
            serializer = ContractSerializer(contracts, many=True)  # Сериализуем данные
            return Response(serializer.data)  # Возвращаем сериализованные данные
        else:
            # Обработка HTML-запроса
            contracts = Contract.objects.all()
            return render(request, 'contract_list.html', {'contracts': contracts})  # Возвращаем HTML-страницу

class ContractCreateView(APIView):
    @swagger_auto_schema(
        operation_description="Создать новый контракт",
        request_body=ContractCreateSerializer,
        responses={
            201: openapi.Response('Контракт успешно создан', ContractCreateSerializer),
            400: 'Некорректные данные'
        }
    )
    def post(self, request):
        # Проверяем, является ли запрос API или HTML
        if request.accepted_renderer.format == 'json':
            serializer = ContractCreateSerializer(data=request.data)  # Используем сериализатор для проверки данных

            if serializer.is_valid():
                client_id = serializer.validated_data['client_id']
                date = serializer.validated_data['date']
                status = serializer.validated_data['status']
                total_amount = serializer.validated_data['total_amount']
                car_id = serializer.validated_data['car_id']

                client = get_object_or_404(Client, pk=client_id)
                car = get_object_or_404(Car, pk= car_id)

                Contract.objects.create(client=client, car=car, date=date, status=status, total_amount=total_amount)
                return Response(serializer.data, status=stat.HTTP_201_CREATED)  # Возвращаем созданный контракт

            return Response(serializer.errors, status=stat.HTTP_400_BAD_REQUEST)  # Возвращаем ошибки валидации
        else:
            # Обработка HTML-запроса
            clients = Client.objects.all()  # Получаем список клиентов для выбора
            client_id = request.POST.get('client_id')
            date = request.POST.get('date')
            status = request.POST.get('status')
            total_amount = request.POST.get('total_amount')
            car_id = request.POST.get('car_id')

            if client_id and date and status and total_amount and car_id:
                client = get_object_or_404(Client, pk=client_id)
                car = get_object_or_404(Car, pk=car_id)
                Contract.objects.create(client=client, car=car, date=date, status=status, total_amount=total_amount)
                return redirect('contract_list')

            error_message = "Некорректные данные."
            return render(request, 'contract_form.html', {'clients': clients, 'error_message': error_message})

    def get(self, request):
        clients = Client.objects.all()  # Получаем список клиентов для выбора
        return render(request, 'contract_form.html', {'clients': clients})  # Возвращаем HTML-форму для создания контракта

class ContractUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Обновить информацию о контракте",
        request_body=ContractUpdateSerializer,
        responses={
            200: openapi.Response('Контракт успешно обновлен', ContractUpdateSerializer),
            400: 'Некорректные данные',
            404: 'Контракт не найден'
        }
    )
    def post(self, request, pk):
        # Проверяем, является ли запрос API или HTML
        if request.accepted_renderer.format == 'json':
            contract = get_object_or_404(Contract, pk=pk)
            serializer = ContractUpdateSerializer(contract, data=request.data, partial=True)

            if serializer.is_valid():
                client_id = serializer.validated_data.get('client_id', contract.client.id)
                car_id = serializer.validated_data.get('car_id', contract.car.id)
                date = serializer.validated_data.get('date', contract.date)
                status = serializer.validated_data.get('status', contract.status)
                total_amount = serializer.validated_data.get('total_amount', contract.total_amount)

                if client_id:
                    contract.client = get_object_or_404(Client, pk=client_id)
                if car_id:
                    contract.car = get_object_or_404(Car, pk=car_id)

                contract.date = date
                contract.status = status
                contract.total_amount = total_amount
                contract.save()
                return Response(serializer.data, status=stat.HTTP_200_OK)  # Возвращаем обновленный контракт

            return Response(serializer.errors, status=stat.HTTP_400_BAD_REQUEST)  # Возвращаем ошибки валидации
        else:
            # Обработка HTML-запроса
            contract = get_object_or_404(Contract, pk=pk)
            clients = Client.objects.all()  # Получаем всех клиентов
            cars = Car.objects.all()  # Получаем всех автомобилей
            contract.date = request.POST.get('date', contract.date)
            contract.status = request.POST.get('status', contract.status)
            contract.total_amount = request.POST.get('total_amount', contract.total_amount)
            client_id = request.POST.get('client_id')
            car_id = request.POST.get('car_id')

            if client_id:
                contract.client = get_object_or_404(Client, pk=client_id)
            if car_id:
                contract.car = get_object_or_404(Car, pk=car_id)

            contract.save()
            return redirect('contract_list')  # Перенаправляем на список контрактов

    def get(self, request, pk):
        contract = get_object_or_404(Contract, pk=pk)
        clients = Client.objects.all()  # Получаем всех клиентов
        cars = Car.objects.all()  # Получаем всех автомобилей
        return render(request, 'contract_form.html', {
            'contract': contract,
            'clients': clients,
            'cars': cars
        })  # Возвращаем HTML-форму для обновления контракта

class ContractDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Удалить контракт",
        responses={
            204: 'Контракт успешно удален',
            404: 'Контракт не найден'
        }
    )
    def post(self, request, pk):
        # Проверяем, является ли запрос API или HTML
        if request.accepted_renderer.format == 'json':
            contract = get_object_or_404(Contract, pk=pk)
            try:
                contract.delete()
                return Response(status=stat.HTTP_204_NO_CONTENT)  # Возвращаем статус 204 No Content
            except Exception as e:
                return Response({"error": f"Ошибка при удалении контракта: {str(e)}"}, status=stat.HTTP_400_BAD_REQUEST)
        else:
            # Обработка HTML-запроса
            contract = get_object_or_404(Contract, pk=pk)
            try:
                contract.delete()
                messages.success(request, 'Контракт успешно удален.')
            except Exception as e:
                messages.error(request, f"Ошибка при удалении контракта: {str(e)}")
            return redirect('contract_list')  # Перенаправляем на список контрактов

# Представления для услуг
class ServiceListView(APIView):
    @swagger_auto_schema(
        operation_description="Получить список услуг",
        responses={200: openapi.Response("Успешно", ServiceSerializer(many=True))}
    )
    def get(self, request):
        services = Service.objects.all()
        serializer = ServiceSerializer(services, many=True)  # Сериализуем данные

        # Проверяем, является ли запрос API или HTML
        if request.accepted_renderer.format == 'json':
            return Response(serializer.data)  # Возвращаем сериализованные данные в формате JSON
        else:
            return render(request, 'service_list.html', {'services': services})  # Возвращаем HTML-страницу

class ServiceCreateView(APIView):
    @swagger_auto_schema(
        operation_description="Создать новую услугу",
        request_body=ServiceCreateSerializer,
        responses={201: openapi.Response('Услуга успешно создана', ServiceCreateSerializer), 400: 'Некорректные данные'}
    )
    def post(self, request):
        # Проверяем, является ли запрос API или HTML
        if request.accepted_renderer.format == 'json':
            serializer = ServiceCreateSerializer(data=request.data)  # Используем сериализатор для проверки данных

            if serializer.is_valid():
                name = serializer.validated_data['name']
                description = serializer.validated_data['description']
                price = serializer.validated_data['price']

                # Создаем новую услугу
                Service.objects.create(name=name, description=description, price=price)
                return Response(serializer.data, status=stat.HTTP_201_CREATED)  # Возвращаем созданную услугу

            return Response(serializer.errors, status=stat.HTTP_400_BAD_REQUEST)  # Возвращаем ошибки валидации
        else:
            # Обработка HTML-запроса
            name = request.POST.get('name')
            description = request.POST.get('description')
            price = request.POST.get('price')

            if name and description and price:
                try:
                    # Создаем новую услугу
                    Service.objects.create(name=name, description=description, price=price)
                    return redirect('service_list')
                except Exception as e:
                    error_message = f"Произошла ошибка: {str(e)}"
                    return render(request, 'service_form.html', {'error_message': error_message})

            error_message = "Некорректные данные."
            return render(request, 'service_form.html', {'error_message': error_message})

    def get(self, request):
        return render(request, 'service_form.html')  # Возвращаем HTML-форму для создания услуги

class ServiceUpdateView(APIView):
    @swagger_auto_schema(
        operation_description="Обновить информацию об услуге",
        request_body=ServiceUpdateSerializer,
        responses={200: openapi.Response('Услуга успешно обновлена', ServiceUpdateSerializer), 400: 'Некорректные данные', 404: 'Услуга не найдена'}
    )
    def post(self, request, pk):
        # Проверяем, является ли запрос API или HTML
        if request.accepted_renderer.format == 'json':
            service = get_object_or_404(Service, pk=pk)
            serializer = ServiceUpdateSerializer(service, data=request.data, partial=True)

            if serializer.is_valid():
                name = serializer.validated_data.get('name', service.name)
                description = serializer.validated_data.get('description', service.description)
                price = serializer.validated_data.get('price', service.price)

                service.name = name
                service.description = description
                service.price = price
                service.save()
                return Response(serializer.data, status=stat.HTTP_200_OK)  # Возвращаем обновленную услугу

            return Response(serializer.errors, status=stat.HTTP_400_BAD_REQUEST)  # Возвращаем ошибки валидации
        else:
            # Обработка HTML-запроса
            service = get_object_or_404(Service, pk=pk)
            name = request.POST.get('name', service.name)
            description = request.POST.get('description', service.description)
            price = request.POST.get('price', service.price)

            if name and description and price:
                service.name = name
                service.description = description
                service.price = price
                service.save()
                return redirect('service_list')

            error_message = "Некорректные данные."
            return render(request, 'service_form.html', {'service': service, 'error_message': error_message})

    def get(self, request, pk):
        service = get_object_or_404(Service, pk=pk)
        return render(request, 'service_form.html', {'service': service})  # Возвращаем HTML-форму для обновления услуги

class ServiceDeleteView(APIView):
    @swagger_auto_schema(
        operation_description="Удалить услугу",
        responses={204: 'Услуга успешно удалена', 404: 'Услуга не найдена'}
    )
    def post(self, request, pk):
        # Проверяем, является ли запрос API или HTML
        if request.accepted_renderer.format == 'json':
            service = get_object_or_404(Service, pk=pk)
            try:
                service.delete()
                return Response(status=stat.HTTP_204_NO_CONTENT)  # Возвращаем статус 204 «Нет содержимого»
            except Exception as e:
                return Response({"error": f"Ошибка при удалении услуги: {str(e)}"}, status=stat.HTTP_400_BAD_REQUEST)
        else:
            # Обработка HTML-запроса
            service = get_object_or_404(Service, pk=pk)
            try:
                service.delete()
                messages.success(request, 'Услуга успешно удалена.')
            except Exception as e:
                messages.error(request, f'Ошибка при удалении услуги: {str(e)}')
            return redirect('service_list')  # Перенаправляем на список услуг

# Представления для запчастей
class SparePartListView(APIView):
    @swagger_auto_schema(
        operation_description="Получить список запасных частей",
        responses={200: openapi.Response("Успешно", SparePartSerializer(many=True))}
    )
    def get(self, request):
        spare_parts = SparePart.objects.all()
        serializer = SparePartSerializer(spare_parts, many=True)  # Сериализуем данные

        # Проверяем, является ли запрос API или HTML
        if request.accepted_renderer.format == 'json':
            return Response(serializer.data)  # Возвращаем сериализованные данные в формате JSON
        else:
            return render(request, 'sparepart_list.html', {'spare_parts': spare_parts})  # Возвращаем HTML-страницу

class SparePartCreateView(APIView):
    @swagger_auto_schema(
        operation_description="Создать новую запчасть",
        request_body=SparePartCreateSerializer,
        responses={201: openapi.Response('Запчасть успешно создана', SparePartCreateSerializer), 400: 'Некорректные данные'}
    )
    def post(self, request):
        # Проверяем, является ли запрос API или HTML
        if request.accepted_renderer.format == 'json':
            serializer = SparePartCreateSerializer(data=request.data)  # Используем сериализатор для проверки данных

            if serializer.is_valid():
                name = serializer.validated_data['name']
                price = serializer.validated_data['price']
                quantity = serializer.validated_data['quantity']

                # Создаем новую запчасть
                SparePart.objects.create(name=name, price=price, quantity=quantity)
                return Response(serializer.data, status=stat.HTTP_201_CREATED)  # Возвращаем созданную запчасть

            return Response(serializer.errors, status=stat.HTTP_400_BAD_REQUEST)  # Возвращаем ошибки валидации
        else:
            # Обработка HTML-запроса
            name = request.POST.get('name')
            price = request.POST.get('price')
            quantity = request.POST.get('quantity')

            if name and price and quantity:
                try:
                    # Создаем новую запчасть
                    SparePart.objects.create(name=name, price=price, quantity=quantity)
                    return redirect('sparepart_list')
                except Exception as e:
                    error_message = f"Произошла ошибка: {str(e)}"
                    return render(request, 'sparepart_form.html', {'error_message': error_message})

            error_message = "Некорректные данные."
            return render(request, 'sparepart_form.html', {'error_message': error_message})

    def get(self, request):
        return render(request, 'sparepart_form.html')  # Возвращаем HTML-форму для создания запчасти

class SparePartUpdateView(APIView):
    @swagger_auto_schema(
        operation_description="Обновить информацию о запчасти",
        request_body=SparePartUpdateSerializer,
        responses={200: openapi.Response('Запчасть успешно обновлена', SparePartUpdateSerializer), 400: 'Некорректные данные', 404: 'Запчасть не найдена'}
    )
    def post(self, request, pk):
        # Проверяем, является ли запрос API или HTML
        if request.accepted_renderer.format == 'json':
            spare_part = get_object_or_404(SparePart, pk=pk)
            serializer = SparePartUpdateSerializer(spare_part, data=request.data, partial=True)

            if serializer.is_valid():
                name = serializer.validated_data.get('name', spare_part.name)
                price = serializer.validated_data.get('price', spare_part.price)
                quantity = serializer.validated_data.get('quantity', spare_part.quantity)

                spare_part.name = name
                spare_part.price = price
                spare_part.quantity = quantity
                spare_part.save()
                return Response(serializer.data, status=stat.HTTP_200_OK)  # Возвращаем обновленную запчасть

            return Response(serializer.errors, status=stat.HTTP_400_BAD_REQUEST)  # Возвращаем ошибки валидации
        else:
            # Обработка HTML-запроса
            spare_part = get_object_or_404(SparePart, pk=pk)
            name = request.POST.get('name', spare_part.name)
            price = request.POST.get('price', spare_part.price)
            quantity = request.POST.get('quantity', spare_part.quantity)

            if name and price and quantity:
                spare_part.name = name
                spare_part.price = price
                spare_part.quantity = quantity
                spare_part.save()
                return redirect('sparepart_list')

            error_message = "Некорректные данные."
            return render(request, 'sparepart_form.html', {'spare_part': spare_part, 'error_message': error_message})

    def get(self, request, pk):
        spare_part = get_object_or_404(SparePart, pk=pk)
        return render(request, 'sparepart_form.html', {'spare_part': spare_part})  # Возвращаем HTML-форму для обновления запчасти

class SparePartDeleteView(APIView):
    @swagger_auto_schema(
        operation_description="Удалить запчасть",
        responses={204: 'Запчасть успешно удалена', 404: 'Запчасть не найдена'}
    )
    def post(self, request, pk):
        # Проверяем, является ли запрос API или HTML
        if request.accepted_renderer.format == 'json':
            spare_part = get_object_or_404(SparePart, pk=pk)
            try:
                spare_part.delete()
                return Response(status=stat.HTTP_204_NO_CONTENT)  # Возвращаем статус 204 «Нет содержимого»
            except Exception as e:
                return Response({"error": f"Ошибка при удалении запчасти: {str(e)}"}, status=stat.HTTP_400_BAD_REQUEST)
        else:
            # Обработка HTML-запроса
            spare_part = get_object_or_404(SparePart, pk=pk)
            try:
                spare_part.delete()
                messages.success(request, 'Запчасть успешно удалена.')
            except Exception as e:
                messages.error(request, f"Ошибка при удалении запчасти: {str(e)}")
            return redirect('sparepart_list')  # Перенаправляем на список запчастей

# Представления для заказов
class OrderListView(UserPassesTestMixin, APIView):
    def test_func(self):
        return self.request.user.is_staff

    @swagger_auto_schema(
        operation_description="Получить список заказов",
        responses={200: openapi.Response('Успешно', OrderSerializer(many=True))}
    )
    def get(self, request):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)  # Сериализуем данные

        # Проверяем, является ли запрос API или HTML
        if request.accepted_renderer.format == 'json':
            return Response(serializer.data)  # Возвращаем сериализованные данные в формате JSON
        else:
            return render(request, 'order_list.html', {'orders': orders})  # Возвращаем HTML-страницу

class OrderCreateView(APIView):
    @swagger_auto_schema(
        operation_description="Создать новый заказ",
        request_body=OrderCreateSerializer,
        responses={201: openapi.Response('Заказ успешно создан', OrderCreateSerializer), 400: 'Некорректные данные'}
    )
    def post(self, request):
        # Проверяем, является ли запрос API или HTML
        if request.accepted_renderer.format == 'json':
            serializer = OrderCreateSerializer(data =request.data)  # Используем сериализатор для проверки данных

            if serializer.is_valid():
                client_id = serializer.validated_data['client_id']
                service_id = serializer.validated_data['service_id']
                order_date = serializer.validated_data['order_date']

                client = get_object_or_404(Client, pk=client_id)
                service = get_object_or_404(Service, pk=service_id)

                # Создаем новый заказ
                Order.objects.create(client=client, service=service, order_date=order_date)
                return Response(serializer.data, status=stat.HTTP_201_CREATED)  # Возвращаем созданный заказ

            return Response(serializer.errors, status=stat.HTTP_400_BAD_REQUEST)  # Возвращаем ошибки валидации
        else:
            # Обработка HTML-запроса
            clients = Client.objects.all()  # Получаем список клиентов
            services = Service.objects.all()  # Получаем все услуги
            client_id = request.POST.get('client_id')
            service_id = request.POST.get('service_id')
            order_date = request.POST.get('order_date')

            if client_id and service_id and order_date:  # Проверяем наличие всех необходимых данных
                client = get_object_or_404(Client, pk=client_id)
                service = get_object_or_404(Service, pk=service_id)  # Получаем объект Service
                Order.objects.create(client=client, service=service, order_date=order_date)  # Сохраняем заказ
                return redirect('order_list')

            return render(request, 'order_form.html', {'clients': clients, 'services': services, 'error_message': "Некорректные данные."})

    def get(self, request):
        clients = Client.objects.all()  # Получаем список клиентов
        services = Service.objects.all()  # Получаем все услуги
        return render(request, 'order_form.html', {'clients': clients, 'services': services})  # Возвращаем HTML-форму для создания заказа

class OrderUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Обновить информацию о заказе",
        request_body=OrderUpdateSerializer,
        responses={
            200: openapi.Response('Заказ успешно обновлен', OrderUpdateSerializer),
            400: 'Некорректные данные',
            404: 'Заказ не найден'
        }
    )
    def post(self, request, pk):
        # Проверяем, является ли запрос API или HTML
        if request.accepted_renderer.format == 'json':
            order = get_object_or_404(Order, pk=pk)
            serializer = OrderUpdateSerializer(order, data=request.data, partial=True)

            if serializer.is_valid():
                order.order_date = serializer.validated_data.get('order_date', order.order_date)
                client_id = serializer.validated_data.get('client_id')
                service_id = serializer.validated_data.get('service_id')

                if client_id:
                    order.client = get_object_or_404(Client, pk=client_id)
                if service_id:
                    order.service = get_object_or_404(Service, pk=service_id)

                order.save()
                return Response(serializer.data, status=stat.HTTP_200_OK)  # Возвращаем обновленный заказ

            return Response(serializer.errors, status=stat.HTTP_400_BAD_REQUEST)  # Возвращаем ошибки валидации
        else:
            # Обработка HTML-запроса
            order = get_object_or_404(Order, pk=pk)
            order.order_date = request.POST.get('order_date', order.order_date)
            client_id = request.POST.get('client_id')
            service_id = request.POST.get('service_id')

            if client_id:
                order.client = get_object_or_404(Client, pk=client_id)
            if service_id:
                order.service = get_object_or_404(Service, pk=service_id)

            order.save()
            return redirect('order_list')

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        clients = Client.objects.all()  # Получаем всех клиентов
        services = Service.objects.all()  # Получаем все услуги
        return render(request, 'order_form.html', {
            'order': order,
            'clients': clients,
            'services': services
        })  # Возвращаем HTML-форму для обновления заказа

class OrderDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Удалить заказ",
        responses={
            204: 'Заказ успешно удален',
            404: 'Заказ не найден'
        }
    )
    def post(self, request, pk):
        # Проверяем, является ли запрос API или HTML
        if request.accepted_renderer.format == 'json':
            order = get_object_or_404(Order, pk=pk)
            try:
                order.delete()
                return Response(status=stat.HTTP_204_NO_CONTENT)  # Возвращаем статус 204 No Content
            except Exception as e:
                return Response({"error": f"Ошибка при удалении заказа: {str(e)}"}, status=stat.HTTP_400_BAD_REQUEST)
        else:
            # Обработка HTML-запроса
            order = get_object_or_404(Order, pk=pk)
            try:
                order.delete()
                messages.success(request, 'Заказ успешно удален.')
            except Exception as e:
                messages.error(request, f"Ошибка при удалении заказа: {str(e)}")
            return redirect('order_list')  # Перенаправляем на список заказов

# Регистрация
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваш аккаунт создан! Вы можете войти.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Переход на главную страницу после входа
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})

class UserDataView(APIView):
    @swagger_auto_schema(
        operation_description="Получить данные пользователя",
        responses={
            200: openapi.Response('Успешно', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'client': openapi.Schema(type=openapi.TYPE_OBJECT, description='Данные клиента'),
                    'cars': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT, description='Данные автомобиля')),
                    'contracts': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT, description='Данные контракта')),
                    'orders': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT, description='Данные заказа')),
                    'services': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT, description='Данные услуги')),
                    'spare_parts': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT, description='Данные запчасти')),
                }
            )),
            400: 'Клиент не найден или пользователь не аутентифицирован.'
        }
    )
    def get(self, request):
        """ Получение данных пользователя.

        Если пользователь аутентифицирован, получает данные клиента, связанные с ним,
        включая автомобили, контракты, заказы, услуги и запчасти.
        Если клиент не найден, возвращает сообщение об ошибке.
        Если пользователь не аутентифицирован, возвращает сообщение о необходимости входа в систему.

        Args:
            request: Объект запроса.

        Returns:
            HttpResponse: HTML-страница с данными пользователя или сообщение об ошибке.
        """
        if request.user.is_authenticated:
            # Получаем клиента по имени пользователя
            client = Client.objects.filter(full_name=request.user.username).first()
            if client:
                # Получаем данные, связанные с клиентом
                cars = Car.objects.filter(client=client)
                contracts = Contract.objects.filter(client=client)
                orders = Order.objects.filter(client=client)
                services = Service.objects.all()  # Все услуги, если нужно
                spare_parts = SparePart.objects.all()  # Все запчасти, если нужно

                # Проверяем, является ли запрос API или HTML
                if request.accepted_renderer.format == 'json':
                    return Response({
                        'client': client,
                        'cars': cars,
                        'contracts': contracts,
                        'orders': orders,
                        'services': services,
                        'spare_parts': spare_parts,
                    }, status=stat.HTTP_200_OK)  # Возвращаем данные в формате JSON
                else:
                    return render(request, 'user_data.html', {
                        'client': client,
                        'cars': cars,
                        'contracts': contracts,
                        'orders': orders,
                        'services': services,
                        'spare_parts': spare_parts,
                    })  # Возвращаем HTML-страницу
            else:
                return render(request, 'user_data.html', {'error': 'Клиент не найден.'})
        else:
            return render(request, 'user_data.html', {'error': 'Пожалуйста, войдите в систему.'})

class CarListByClientView(APIView):
    def get(self, request):
        client_id = request.GET.get('client_id')
        cars = Car.objects.filter(client_id=client_id).values('id', 'brand', 'model')
        return Response(list(cars), status=200)