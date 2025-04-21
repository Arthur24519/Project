from django.db import models
from cryptography.fernet import Fernet

class Client(models.Model):
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    encrypted_email = models.CharField(max_length=255, unique=True)  # Изменено на CharField
    address = models.TextField()

    @staticmethod
    def get_fernet():
        key = b'l29hPxeTtD_l-tXDy9ILDHRh-ucFHX_-ARCNU5mQxDg='
        return Fernet(key)

    def set_email(self, email):
        fernet = self.get_fernet()
        self.encrypted_email = fernet.encrypt(email.encode()).decode()  # Convert to string
        print(f"Email set: {email}")  # Debug message

    def get_email(self):
        if self.encrypted_email is not None:
            fernet = self.get_fernet()
            try:
                print(f"Encrypted email: {self.encrypted_email}")  # Debug message
                decrypted_email = fernet.decrypt(self.encrypted_email.encode()).decode()  # Ensure it's bytes
                print(f"Email decrypted: {decrypted_email}")  # Debug message
                return decrypted_email
            except Exception as e:
                print(f"Error decrypting email: {str(e)}")  # Debug message
                return None
        else:
            print("No email has been set.")  # Debug message
            return None
            
class Car(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    vin = models.CharField(max_length=17)

class Contract(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=50)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

class SparePart(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()

class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    order_date = models.DateField()