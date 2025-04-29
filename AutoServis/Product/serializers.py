from rest_framework import serializers
from .models import Client, Car, Contract, Service, SparePart, Order
from hashlib import sha256
from django.shortcuts import get_object_or_404

class ClientSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source='encrypted_email', read_only=True)  # Используем зашифрованный email

    class Meta:
        model = Client
        fields = ['id', 'full_name', 'phone', 'email', 'address']  # Укажите необходимые поля

    def validate_email(self, value):
        """Проверка на корректность email."""
        if not value or '@' not in value:
            raise serializers.ValidationError("Введите корректный email.")
        return value

    def create(self, validated_data):
        """Создание нового клиента."""
        client = Client(**validated_data)
        client.set_email(validated_data['email'])  # Зашифровываем email перед сохранением
        client.save()
        return client

    def update(self, instance, validated_data):
        """Обновление существующего клиента."""
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.address = validated_data.get('address', instance.address)
        if 'email' in validated_data:
            instance.set_email(validated_data['email'])  # Зашифровываем новый email
        instance.save()
        return instance

class ClientCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)  # Добавляем поле email для ввода

    class Meta:
        model = Client
        fields = ['full_name', 'phone', 'email', 'address']  # Указываем поля для сериализации

    def create(self, validated_data):
        email = validated_data.pop('email')  # Извлекаем email из validated_data
        client = Client(**validated_data)  # Создаем объект Client без email
        client.set_email(email)  # Устанавливаем зашифрованный email
        client.save()  # Сохраняем объект
        return client

class ClientUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True, required=False)  # Add email as a write-only field

    class Meta:
        model = Client
        fields = ['full_name', 'phone', 'email', 'address']  # Include email for input
        extra_kwargs = {
            'email': {'required': False},  # Email is optional for updates
        }

    def validate_full_name(self, value):
        # Проверка на наличие пробелов в ФИО
        if ' ' in value:
            raise serializers.ValidationError("ФИО не должно содержать пробелов.")
        return value

    def validate_email(self, value):
        # Проверка на уникальность email, если он был изменен
        if value:
            # Get the current instance of the client being updated
            client = self.instance
            
            # Hash the new email
            hashed_email = sha256(value.encode()).hexdigest()
            
            # Check if the email already exists for another client
            if Client.objects.filter(encrypted_email=hashed_email).exclude(pk=client.pk).exists():
                raise serializers.ValidationError("Клиент с таким email уже существует.")
        return value

    def update(self, instance, validated_data):
        """Обновление существующего клиента."""
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.address = validated_data.get('address', instance.address)
        
        if 'email' in validated_data:
            instance.set_email(validated_data['email'])  # Зашифровываем новый email
        
        instance.save()
        return instance

class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = '__all__'

class CarCreateSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField()  # Add client_name field

    class Meta:
        model = Car
        fields = ['brand', 'model', 'year', 'vin', 'client_name']  # Use client_name instead of client_id

    def create(self, validated_data):
        client_name = validated_data.pop('client_name')  # Extract client_name
        client = get_object_or_404(Client, full_name=client_name)  # Look up the client by name
        car = Car.objects.create(client=client, **validated_data)  # Create the car with the client
        return car

class CarUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ['brand', 'model', 'year', 'vin', 'client_id']

class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = '__all__'

class ContractCreateSerializer(serializers.Serializer):
    client_id = serializers.IntegerField(required=True)
    date = serializers.DateField(required=True)
    status = serializers.CharField(required=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    car_id = serializers.IntegerField(required=True)

class ContractUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = ['client_id', 'date', 'status', 'total_amount', 'car_id']  # Specify the fields you want to include

class SparePartSerializer(serializers.ModelSerializer):
    class Meta:
        model = SparePart
        fields = '__all__'

class ServiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price']  # Specify the fields you want to include

class ServiceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price']  # Укажите поля, которые хотите обновить

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.price = validated_data.get('price', instance.price)
        instance.save()
        return instance

class SparePartCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SparePart
        fields = ['name', 'price', 'quantity']  # Укажите поля, которые хотите включить

class SparePartUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SparePart
        fields = ['name', 'price', 'quantity']  # Укажите поля, которые хотите обновить

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.price = validated_data.get('price', instance.price)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.save()
        return instance

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class OrderCreateSerializer(serializers.Serializer):
    client_id = serializers.IntegerField(required=True, help_text="ID клиента")
    service_id = serializers.IntegerField(required=True, help_text="ID услуги")
    order_date = serializers.DateField(required=True, help_text="Дата заказа в формате YYYY-MM-DD")

class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['client_id', 'service_id', 'order_date']  # Укажите поля, которые хотите обновить

    def update(self, instance, validated_data):
        instance.order_date = validated_data.get('order_date', instance.order_date)
        client_id = validated_data.get('client_id', None)
        service_id = validated_data.get('service_id', None)

        if client_id:
            instance.client = get_object_or_404(Client, pk=client_id)
        if service_id:
            instance.service = get_object_or_404(Service, pk=service_id)

        instance.save()
        return instance