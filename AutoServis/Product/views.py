from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import Client, Car, Contract, Service, SparePart, Order
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages

# Главная страница
def home(request):
    return render(request, 'home.html')

# Представления для клиентов
class ClientListView(View):
    def get(self, request):
        clients = Client.objects.all()
        return render(request, 'client_list.html', {'clients': clients})

class ClientCreateView(View):
    def get(self, request):
        # Здесь вы можете передать пустую форму, если используете Django Forms
        return render(request, 'client_form.html')  # Убедитесь, что у вас есть соответствующий шаблон

    def post(self, request):
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        
        if full_name and phone and email and address:
            Client.objects.create(full_name=full_name, phone=phone, email=email, address=address)
            return redirect('client_list')
        return HttpResponse("Invalid data", status=400)

class ClientUpdateView(View):
    def get(self, request, pk):
        client = get_object_or_404(Client, pk=pk)
        return render(request, 'client_form.html', {'client': client})

    def post(self, request, pk):
        client = get_object_or_404(Client, pk=pk)
        client.full_name = request.POST.get('full_name', client.full_name)
        client.phone = request.POST.get('phone', client.phone)
        client.email = request.POST.get('email', client.email)
        client.address = request.POST.get('address', client.address)
        client.save()
        return redirect('client_list')

class ClientDeleteView(View):
    def post(self, request, pk):
        client = get_object_or_404(Client, pk=pk)
        client.delete()
        return redirect('client_list')

# Представления для автомобилей
class CarListView(View):
    def get(self, request):
        cars = Car.objects.all()
        return render(request, 'car_list.html', {'cars': cars})

class CarCreateView(View):
    def get(self, request):
        clients = Client.objects.all()
        return render(request, 'car_form.html', {'clients': clients})

    def post(self, request):
        brand = request.POST.get('brand')
        model = request.POST.get('model')
        year = request.POST.get('year')
        vin = request.POST.get('vin')
        client_id = request.POST.get('client_id')
        
        if len(vin) > 17:
            return HttpResponse("VIN не может превышать 17 символов.", status=400)

        if brand and model and year and vin and client_id:
            client = get_object_or_404(Client, pk=client_id)
            Car.objects.create(brand=brand, model=model, year=year, vin=vin, client=client)
            return redirect('car_list')
        return HttpResponse("Invalid data", status=400)

class CarUpdateView(View):
    def get(self, request, pk):
        car = get_object_or_404(Car, pk=pk)
        clients = Client.objects.all()  # Получаем всех клиентов
        return render(request, 'car_form.html', {'car': car, 'clients': clients})  # Передаем клиентов в контекст

    def post(self, request, pk):
        car = get_object_or_404(Car, pk=pk)
        car.brand = request.POST.get('brand', car.brand)
        car.model = request.POST.get('model', car.model)
        car.year = request.POST.get('year', car.year)
        car.vin = request.POST.get('vin', car.vin)
        client_id = request.POST.get('client_id')
        if client_id:
            client = get_object_or_404(Client, pk=client_id)
            car.client = client
        car.save()
        return redirect('car_list')

class CarDeleteView(View):
    def post(self, request, pk):
        car = get_object_or_404(Car, pk=pk)
        car.delete()
        return redirect('car_list')

# Представления для договоров
class ContractListView(View):
    def get(self, request):
        contracts = Contract.objects.all()
        return render(request, 'contract_list.html', {'contracts': contracts})

class ContractCreateView(View):
    def get(self, request):
        clients = Client.objects.all()  # Получаем список клиентов для выбора
        cars = Car.objects.all()  # Получаем список автомобилей для выбора
        return render(request, 'contract_form.html', {'clients': clients, 'cars': cars})

    def post(self, request):
        client_id = request.POST.get('client_id')
        car_id = request.POST.get('car_id')
        date = request.POST.get('date')
        status = request.POST.get('status')
        total_amount = request.POST.get('total_amount')
        
        if client_id and car_id and date and status and total_amount:
            client = get_object_or_404(Client, pk=client_id)
            car = get_object_or_404(Car, pk=car_id)
            Contract.objects.create(client=client, car=car, date=date, status=status, total_amount=total_amount)
            return redirect('contract_list')
        return HttpResponse("Invalid data", status=400)
        
class ContractUpdateView(View):
    def get(self, request, pk):
        contract = get_object_or_404(Contract, pk=pk)
        clients = Client.objects.all()  # Получаем всех клиентов
        cars = Car.objects.all()  # Получаем всех автомобилей
        return render(request, 'contract_form.html', {
            'contract': contract,
            'clients': clients,
            'cars': cars
        })

    def post(self, request, pk):
        contract = get_object_or_404(Contract, pk=pk)
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
        return redirect('contract_list')

class ContractDeleteView(View):
    def post(self, request, pk):
        contract = get_object_or_404(Contract, pk=pk)
        contract.delete()
        return redirect('contract_list')

# Представления для услуг
class ServiceListView(View):
    def get(self, request):
        services = Service.objects.all()
        return render(request, 'service_list.html', {'services': services})

class ServiceCreateView(View):
    def get(self, request):
        # Отправляем пустую форму для добавления услуги
        return render(request, 'service_form.html')

    def post(self, request):
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        
        if name and description and price:
            Service.objects.create(name=name, description=description, price=price)
            return redirect('service_list')
        return HttpResponse("Invalid data", status=400)

class ServiceUpdateView(View):
    def get(self, request, pk):
        service = get_object_or_404(Service, pk=pk)
        return render(request, 'service_form.html', {'service': service})

    def post(self, request, pk):
        service = get_object_or_404(Service, pk=pk)
        service.name = request.POST.get('name', service.name)
        service.description = request.POST.get('description', service.description)
        service.price = request.POST.get('price', service.price)
        service.save()
        return redirect('service_list')

class ServiceDeleteView(View):
    def post(self, request, pk):
        service = get_object_or_404(Service, pk=pk)
        service.delete()
        return redirect('service_list')

# Представления для запчастей
class SparePartListView(View):
    def get(self, request):
        spare_parts = SparePart.objects.all()
        return render(request, 'sparepart_list.html', {'spare_parts': spare_parts})

class SparePartCreateView(View):
    def get(self, request):
        # Отправляем пустую форму для добавления запчасти
        return render(request, 'sparepart_form.html')

    def post(self, request):
        name = request.POST.get('name')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        
        if name and price and quantity:
            SparePart.objects.create(name=name, price=price, quantity=quantity)
            return redirect('sparepart_list')
        return HttpResponse("Invalid data", status=400)

class SparePartUpdateView(View):
    def get(self, request, pk):
        spare_part = get_object_or_404(SparePart, pk=pk)
        return render(request, 'sparepart_form.html', {'spare_part': spare_part})

    def post(self, request, pk):
        spare_part = get_object_or_404(SparePart, pk=pk)
        spare_part.name = request.POST.get('name', spare_part.name)
        spare_part.price = request.POST.get('price', spare_part.price)
        spare_part.quantity = request.POST.get('quantity', spare_part.quantity)
        spare_part.save()
        return redirect('sparepart_list')

class SparePartDeleteView(View):
    def post(self, request, pk):
        spare_part = get_object_or_404(SparePart, pk=pk)
        spare_part.delete()
        return redirect('sparepart_list')

# Представления для заказов
class OrderListView(View):
    def get(self, request):
        orders = Order.objects.all()
        return render(request, 'order_list.html', {'orders': orders})

class OrderCreateView(View):
    def get(self, request):
        clients = Client.objects.all()  # Получаем список клиентов
        cars = Car.objects.all()  # Получаем список автомобилей
        return render(request, 'order_form.html', {'clients': clients, 'cars': cars})

    def post(self, request):
        client_id = request.POST.get('client_id')
        car_id = request.POST.get('car_id')
        order_date = request.POST.get('order_date')
        
        if client_id and car_id and order_date:
            client = get_object_or_404(Client, pk=client_id)
            car = get_object_or_404(Car, pk=car_id)
            Order.objects.create(client=client, car=car, order_date=order_date)
            return redirect('order_list')
        return HttpResponse("Invalid data", status=400)

class OrderUpdateView(View):
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        clients = Client.objects.all()  # Получаем всех клиентов
        services = Service.objects.all()  # Получаем все услуги
        return render(request, 'order_form.html', {
            'order': order,
            'clients': clients,
            'services': services
        })

    def post(self, request, pk):
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

class OrderDeleteView(View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        order.delete()
        return redirect('order_list')
    
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        if username and password and email:
            user = User.objects.create_user(username=username, password=password, email=email)
            user.save()
            login(request, user)
            messages.success(request, 'Вы успешно зарегистрированы!')
            return redirect('home')
        else:
            messages.error(request, 'Пожалуйста, заполните все поля.')
    
    return render(request, 'registration/register.html')