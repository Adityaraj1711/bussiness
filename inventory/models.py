from django.db import models

class Area(models.Model):
    city_name = models.CharField(max_length=15, blank=False, default="Jehanabad")
    area_name = models.CharField(max_length=15, blank=False)

    def __str__(self):
        return self.area_name

class Company(models.Model):
    name = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=255, blank=True)
    loan_amount = models.DecimalField(max_digits=9, decimal_places=2, default=0, blank=False)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    stock_in_kg = models.IntegerField(default=0, blank=False)
    one_bora_in_kg = models.IntegerField(default=1, blank=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    @property
    def stock_in_bora(self):
        if self.one_bora_in_kg == 0:
            self.one_bora_in_kg = 1
        return "{:.2f}".format(self.stock_in_kg / self.one_bora_in_kg)

    def __str__(self):
        return self.name

class Dukandaar(models.Model):
    name = models.CharField(max_length=255, unique=True)
    contact_info = models.CharField(max_length=255, blank=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    pending_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=False)
    address = models.CharField(max_length=50, default="", blank=True, null=True)

    def __str__(self):
        return self.name + " " + self.area.area_name

class Bill(models.Model):
    id = models.AutoField(primary_key=True, blank=False)
    dukandaar = models.ForeignKey(Dukandaar, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    pending_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    paid = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if not self.paid:
            self.dukandaar.pending_amount -= self.pending_amount
            self.dukandaar.save()
        for item in self.items.all():
            item.delete()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.id} - {self.dukandaar} - {self.date} - {self.pending_amount}"

class Item(models.Model):
    bill = models.ForeignKey(Bill, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    bora = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    kg = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=20, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.amount = (self.kg * self.price_per_kg) + (self.bora * self.price_per_kg * self.product.one_bora_in_kg)
        super().save(*args, **kwargs)
        self.bill.total_amount += self.amount
        if not self.bill.paid:
            self.bill.pending_amount += self.amount
            self.bill.dukandaar.pending_amount += self.amount
            self.bill.dukandaar.save()
        self.bill.save()
        self.product.stock_in_kg -= ((self.bora * self.product.one_bora_in_kg) + self.kg)
        self.product.save()

    def delete(self, *args, **kwargs):
        self.product.stock_in_kg += (self.bora * self.product.one_bora_in_kg)
        self.product.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.kg} kg @ {self.price_per_kg} per kg {self.bill} Bill order "


class DailyCollection(models.Model):
    dukandaar = models.ForeignKey(Dukandaar, related_name='dukandaar', on_delete=models.CASCADE)
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, null=True, blank=True)
    collection_time = models.DateTimeField(auto_now_add=True)
    amount_collected = models.DecimalField(max_digits=10, decimal_places=2)
    pending_amount_as_of_today = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)

    def save(self, *args, **kwargs):
        self.pending_amount_as_of_today = self.dukandaar.pending_amount - self.amount_collected

        # Reduce the pending amount of the bill if a bill is associated
        if self.bill:
            self.bill.pending_amount -= self.amount_collected
            self.bill.save()
            if self.bill.pending_amount <= 0:
                self.bill.paid = True
                self.bill.save()

        super().save(*args, **kwargs)
        self.dukandaar.pending_amount -= self.amount_collected
        self.dukandaar.save()

    def __delete__(self,  *args, **kwargs):
        if self.bill:
            self.bill.pending_amount += self.amount_collected
            self.bill.save()
            if self.bill.pending_amount > 0:
                self.bill.paid = False
                self.bill.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Collection by {self.dukandaar} on {self.collection_time}"

class PurchaseOrder(models.Model):
    id = models.AutoField(primary_key=True, blank=False)
    date = models.DateField(auto_now_add=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    disc_percent = models.DecimalField(max_digits=4, decimal_places=2, default=2)

    def delete(self, *args, **kwargs):
        self.company.loan_amount -= self.total_amount
        self.company.save()
        for item in self.purchase_order.all():
            item.delete()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.company} - {self.date} - Purchase Order"

class PurchaseItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, related_name='purchase_order', on_delete=models.CASCADE, default=1)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    bora = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    kg = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.amount = (self.kg * self.price_per_kg) + (self.bora * self.price_per_kg * self.product.one_bora_in_kg)
        super().save(*args, **kwargs)
        self.purchase_order.total_amount += self.amount
        self.purchase_order.company.loan_amount += self.amount
        self.purchase_order.company.save()
        self.product.stock_in_kg += ((self.bora * self.product.one_bora_in_kg) + self.kg)
        self.product.save()

    def delete(self, *args, **kwargs):
        self.purchase_order.total_amount -= self.amount
        self.purchase_order.company.loan_amount -= self.amount
        self.purchase_order.company.save()
        self.purchase_order.save()
        self.product.stock_in_kg -= ((self.bora * self.product.one_bora_in_kg) + self.kg)
        self.product.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.kg} kg @ {self.price_per_kg} per kg {self.purchase_order}"

class CompanyPayment(models.Model):
    company = models.ForeignKey(Company, related_name='company', on_delete=models.CASCADE)
    payment_date = models.DateField(auto_now_add=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.company.loan_amount -= self.amount_paid
        self.company.save()

    def __str__(self):
        return f"Paid to {self.company} on {self.payment_date}"