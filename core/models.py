from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import pytesseract
from PIL import Image
import platform

# Smart Tesseract Path
if platform.system() == 'Windows':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
else:
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

# --- 1. POLICE OFFICER MODEL ---
class PoliceOfficer(models.Model):
    RANK_CHOICES = (
        ('CONSTABLE', 'Constable'),
        ('HEAD_CONSTABLE', 'Head Constable'),
        ('ASI', 'Assistant Sub-Inspector (ASI)'),
        ('SI', 'Sub-Inspector (SI)'),
        ('INSPECTOR', 'Inspector'),
        ('SHO', 'SHO'),
        ('PI', 'PI'),
        ('DSP', 'DSP'),
        ('SSP', 'SSP'),
    )
    name = models.CharField(max_length=100)
    rank = models.CharField(max_length=20, choices=RANK_CHOICES, default='SI')
    # Renamed from badge_number to phone_number as per note
    phone_number = models.CharField(max_length=20, unique=True, help_text="Phone No.")

    def __str__(self):
        return f"{self.rank} {self.name} ({self.phone_number})"

# --- 2. ACCUSED MODEL (Renamed from Criminal) ---
class Accused(models.Model):
    name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100, blank=True, verbose_name="Father's Name") # New field
    alias = models.CharField(max_length=100, blank=True, help_text="Urfiyat / Nickname")
    cnic = models.CharField(max_length=15, unique=True, help_text="Format: 12345-1234567-1")
    age = models.PositiveIntegerField(default=0)
    gender_choices = (('M', 'Male'), ('F', 'Female'), ('O', 'Other'))
    gender = models.CharField(max_length=1, choices=gender_choices, default='M')
    photo = models.ImageField(upload_to='accused_photos/', blank=True, null=True)
    address = models.TextField(default="Unknown")
    crime_history = models.TextField(blank=True)

    class Meta:
        verbose_name = "Accused"
        verbose_name_plural = "Accused"

    def __str__(self):
        return f"{self.name} ({self.cnic})"

# --- 3. FIR MODEL ---
STATUS_CHOICES = (
    ('PENDING', 'Pending'),
    ('INTERIM', 'Interim'), # New status (will blink)
    ('CHALLAN', 'Challan'), # New flow
    ('FINAL_REPORT', 'Final Report'), # New flow
    ('A_CLASS', 'A-Class'), # New category
    ('SOLVED', 'Case Solved'),
    ('EXPIRED', 'Expired'),
)

class FIR(models.Model):
    # Renamed case_id to fir_no
    fir_no = models.CharField(max_length=20, unique=True, blank=True, verbose_name="FIR No.")
    police_station = models.CharField(max_length=100, blank=True, verbose_name="Police Station") # New field
    criminal_case_no = models.CharField(max_length=50, blank=True, verbose_name="Criminal Case No.") # New field
    title = models.CharField(max_length=200, blank=True)
    # Label changed to "Enter Data"
    date_reported = models.DateField(default=timezone.now, verbose_name="FIR Date (Enter Data)")
    
    # Renamed fields for Accused
    is_unknown_accused = models.BooleanField(default=False, verbose_name="Unknown Accused")
    accuseds = models.ManyToManyField(Accused, blank=True, verbose_name="Select Accused")
    
    # Evidence renamed to Case Property, added Personal Search Item
    case_property_image = models.ImageField(upload_to='case_property/', null=True, blank=True, verbose_name="Case Property Image (Evidence)")
    description = models.TextField(blank=True, verbose_name="Description / OCR Text")
    personal_search_item = models.TextField(blank=True, verbose_name="Personal Search Item") # New field
    
    officer_assigned = models.ForeignKey(PoliceOfficer, on_delete=models.SET_NULL, null=True, verbose_name="Investigating Officer (I/O)")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "FIR"
        verbose_name_plural = "FIRS" # Capitalized as requested

    def save(self, *args, **kwargs):
        # OCR Auto-Fill using case_property_image
        if self.case_property_image and not self.description:
            try:
                img = Image.open(self.case_property_image)
                extracted_text = pytesseract.image_to_string(img)
                self.description = extracted_text
                if not self.title:
                     self.title = extracted_text.split('\n')[0][:100]
            except Exception as e:
                print(f"OCR Error: {e}")
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.fir_no)

# --- 4. REMAND MODEL (New) ---
class Remand(models.Model):
    fir = models.ForeignKey(FIR, on_delete=models.CASCADE, related_name='remands')
    date = models.DateField(default=timezone.now)
    accused_name = models.CharField(max_length=100)
    io_name = models.CharField(max_length=100, verbose_name="I/O Name")
    section_count = models.CharField(max_length=100, verbose_name="Section (count)")
    order_copy = models.ImageField(upload_to='remand_orders/', blank=True, null=True, verbose_name="Order copy attached")

    REMAND_TYPE_CHOICES = (('POLICE', 'Police'), ('JUDICIAL', 'Judicial'))
    remand_type = models.CharField(max_length=10, choices=REMAND_TYPE_CHOICES, default='POLICE')

    # For Police Remand
    police_remand_details = models.TextField(blank=True, verbose_name="Details")

    # For Judicial Remand
    judicial_remand_image = models.ImageField(upload_to='judicial_remand_images/', blank=True, null=True, verbose_name="Remand Image")

    def __str__(self):
        return f"Remand for {self.fir.fir_no} on {self.date}"

# --- 5. BAIL APPLICATION MODEL (New) ---
class BailApplication(models.Model):
    fir = models.ForeignKey(FIR, on_delete=models.CASCADE, related_name='bail_applications')
    not_alloted_by_self = models.BooleanField(default=False, verbose_name="Not alloted by self")
    date = models.DateField(default=timezone.now)
    section = models.CharField(max_length=100)
    advocate_name = models.CharField(max_length=100)
    order_with_picture = models.ImageField(upload_to='bail_orders/', blank=True, null=True, verbose_name="Order with picture attached")

    def __str__(self):
        return f"Bail Application for {self.fir.fir_no}"

# --- 6. BAIL SURETY MODEL (New) ---
class BailSurety(models.Model):
    bail_application = models.ForeignKey(BailApplication, on_delete=models.CASCADE, related_name='sureties')
    name = models.CharField(max_length=100, verbose_name="Surety Name")
    picture = models.ImageField(upload_to='bail_surety_photos/', blank=True, null=True)

    def __str__(self):
        return f"Surety {self.name} for {self.bail_application}"

# --- 7. ACTION LOG MODEL ---
class ActionLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action}"