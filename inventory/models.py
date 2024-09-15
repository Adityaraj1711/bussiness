from django.db import models

class Area(models.Model):
    city_name = models.CharField(max_length=15, blank=False, default="Jehanabad")
    area_name = models.CharField(max_length=15, blank=False)

    def __str__(self):
        return self.area_name

class Company(models.Model):
    name = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    stock_in_kg = models.IntegerField(default=0)
    one_bora_in_kg = models.IntegerField(default=0)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Dukandaar(models.Model):
    name = models.CharField(max_length=255, unique=True)
    contact_info = models.CharField(max_length=255, blank=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    pending_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=False)
    address = models.CharField(max_length=50, default="")

    def __str__(self):
        return self.name + " " + self.area.area_name

class Bill(models.Model):
    id = models.AutoField(primary_key=True, blank=False)
    dukandaar = models.ForeignKey(Dukandaar, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    paid = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.dukandaar.pending_amount -= self.total_amount
        self.dukandaar.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.id} - {self.dukandaar} - {self.date}"

class Item(models.Model):
    bill = models.ForeignKey(Bill, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    kg = models.DecimalField(max_digits=7, decimal_places=2)
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=20, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.amount = self.kg * self.price_per_kg
        super().save(*args, **kwargs)
        # method(self, self.bill)
        if not self.bill.paid:
            self.bill.total_amount += self.amount
            self.bill.dukandaar.pending_amount += self.amount
            self.bill.dukandaar.save()
            self.bill.save()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.bill.total_amount -= self.amount
        self.bill.dukandaar.pending_amount -= self.amount
        self.bill.dukandaar.save()
        self.bill.save()

    def __str__(self):
        return f"{self.product.name} - {self.kg} kg @ {self.price_per_kg} per kg {self.bill}"


class DailyCollection(models.Model):
    dukandaar = models.ForeignKey(Dukandaar, related_name='dukandaar', on_delete=models.CASCADE)
    collection_time = models.DateTimeField(auto_now_add=True)
    amount_collected = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.dukandaar.pending_amount -= self.amount_collected
        self.dukandaar.save()

    def __str__(self):
        return f"Collection by {self.dukandaar} on {self.collection_time}"

class PurchaseOrder(models.Model):
    id = models.AutoField(primary_key=True, blank=False)
    date = models.DateField(auto_now_add=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    disc_percent = models.DecimalField(max_digits=4, decimal_places=2, default=2)

class PurchaseItem(models.Model):
    bill = models.ForeignKey(PurchaseOrder, related_name='purchaseitems', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    kg = models.DecimalField(max_digits=7, decimal_places=2)
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.amount = self.kg * self.price_per_kg
        super().save(*args, **kwargs)
        self.bill.total_amount += self.amount
        self.bill.save()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.bill.total_amount -= self.amount
        self.bill.save()

    def __str__(self):
        return f"{self.product.name} - {self.kg} kg @ {self.price_per_kg} per kg {self.bill}"
