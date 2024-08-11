
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
import uuid
from rest_framework.authtoken.models import Token
from datetime import datetime
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils import timezone
import logging


logger = logging.getLogger(__name__)

def generate_unique_slug(model_class, field_value):
    """
    Generates a unique slug for a given model and field value.
    """
    base_slug = slugify(field_value)
    unique_slug = base_slug
    num = 1
    while model_class.objects.filter(slug=unique_slug).exists():
        unique_slug = f"{base_slug}-{num}"
        num += 1
    return unique_slug



class ClientProfile(models.Model):
    client_first_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Client's First Name")
    client_last_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Client's Last Name")
    client_business = models.CharField(max_length=255, verbose_name="Client's Business")
    client_phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Client's Phone")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Address")
    client_email = models.EmailField(unique=True, verbose_name="Client's Email")
    client_event_space = models.CharField(max_length=255, verbose_name="Client's Event Space")
    client_special_needs = models.TextField(blank=True, null=True, verbose_name="Client's Special Needs")
    slug = models.SlugField(unique=True, blank=True, null=True, verbose_name="Client Slug", editable=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(ClientProfile, f'{self.client_last_name}-{self.client_business}')
        super(ClientProfile, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.client_first_name} {self.client_last_name} - {self.client_business}"

class ContactFormSubmission(models.Model):
    customer_email = models.EmailField(verbose_name="Customer's Email", default="Enter Email Address Here", blank=True)
    subject = models.CharField(max_length=255, blank=True, null=True, verbose_name="Subject")
    client_profile = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name='contact_forms', verbose_name="Client Profile", null=True, blank=True)
    phone = models.CharField(max_length=12, blank=True, null=True, verbose_name="Phone Number")
    first_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="First Name")
    last_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Last Name")
    event_date_request = models.DateTimeField(default=datetime.now(), verbose_name="Event Date")
    message = models.TextField(verbose_name="Message", default='Tell us about your event')
    time_stamp = models.DateTimeField(auto_now_add=True, verbose_name="Timestamp", blank=True, null=True, editable=False)
    slug = models.SlugField(unique=True, blank=True, null=True, verbose_name="Contact Slug", editable=False)
    message_read = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(ContactFormSubmission, f'{self.last_name}-{self.first_name}')

        is_new = self._state.adding
        super(ContactFormSubmission, self).save(*args, **kwargs)

        if is_new and not self.client_profile:
            self.run_after_save()

    def __str__(self):
        return f"Submission by {self.customer_email} on {self.time_stamp}"

    def run_after_save(self):
        if not self.client_profile:
            client_profile, created = ClientProfile.objects.get_or_create(
                client_email=self.customer_email,
                defaults={
                    'client_first_name': self.first_name,
                    'client_last_name': self.last_name,
                    'client_phone': self.phone
                }
            )
            if created:
                self.client_profile = client_profile
                # Save again if a new ClientProfile was created
                self.save()


@receiver(post_save, sender=ContactFormSubmission)
def execute_after_save(sender, instance, created, **kwargs):
    if created:
        instance.run_after_save()




class EventData(models.Model):
    class EventTypeChoices(models.TextChoices):
        MUSIC = 'Music', 'Music'
        THEATRE = 'Theatre', 'Theatre'
        WRESTLING = 'Wrestling', 'Wrestling'
        MARKET = 'Market', 'Market'
        PRIVATE_PARTY = 'Private Party', 'Private Party'




    event_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Event Name")
    event_venue = models.CharField(max_length=30, blank=True, null=True, verbose_name="Event Venue")
    event_date = models.DateField(default=timezone.now, verbose_name="Event Date")
    event_type = models.CharField(max_length=20, choices=EventTypeChoices, blank=True, null=True, verbose_name="Event Type")
    event_genre = models.CharField(max_length=30, blank=True, null=True, verbose_name='Event Genre')
    event_time = models.TimeField(default=datetime.now(), verbose_name="Event Time")
    event_host = models.CharField(max_length=255, blank=True, null=True, verbose_name="Event Host")
    client_profile = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name='events', verbose_name="Client Profile")
    event_image = models.ImageField(upload_to='frost', blank=True, verbose_name='Image Upload')
    event_description = models.TextField(blank=True, null=True, verbose_name="Event Description")
    slug = models.SlugField(unique=True, blank=True, null=True, verbose_name="Event Slug", editable=False)
    time_stamp = models.DateTimeField(auto_now_add=True, verbose_name="Timestamp", blank=True, null=True, editable=False)
    artist_name = models.CharField(max_length=255, blank=True)
    artist_instagram = models.URLField(validators=[URLValidator()], blank=True, null=True, verbose_name='Instagram')
    artist_spotify = models.URLField(validators=[URLValidator()], blank=True, null=True, verbose_name='spotify')
    artist_youtube = models.URLField(validators=[URLValidator()], blank=True, null=True, verbose_name='youtube')
    artist_facebook = models.URLField(validators=[URLValidator()], blank=True, null=True, verbose_name='Facebook')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(EventData, self.event_name)
        super(EventData, self).save(*args, **kwargs)

    def __str__(self):
        return self.event_name

    class Meta:
        ordering = ['event_date']
        verbose_name_plural = 'Event Data'
        verbose_name = 'Event Data'

class FAQData(models.Model):
    faq_title = models.CharField(max_length=100, blank=True, null=True, verbose_name='FAQ Title')
    faq_descrip = models.TextField(blank=True, null=True, verbose_name='FAQ Description')

    class Meta:
        verbose_name_plural = 'FAQ Data'


class PolicyData(models.Model):
    Policy_title = models.CharField(max_length=100, blank=True, null=True, verbose_name='Policy Title')
    Policy_descrip = models.TextField(blank=True, null=True, verbose_name='Policy Description')

    class Meta:
        verbose_name_plural = 'Policy Data'

class GalleryData(models.Model):

    class MediaChoices(models.TextChoices):
        IMAGE = 'image', 'image'
        VIDEO = 'video', 'video'

    class EventChoices(models.TextChoices):
        MUSIC = 'music', 'music'
        ENTERTAINMENT = 'entertainment', 'entertainment'

    gallery_media_title = models.CharField(max_length=100, blank=True, null=True, verbose_name='Image/Video Title')
    gallery_media_description = models.TextField(blank=True, null=True, verbose_name='Image/Video Description')
    gallery_media_image = models.ImageField(upload_to='gallery', blank=True, null=True, verbose_name='Image Upload')
    gallery_media_video = models.URLField(validators=[URLValidator()], blank=True, null=True, verbose_name='Video Link')
    gallery_media_date = models.DateTimeField(default=timezone.now, verbose_name="Image/Video Date")
    gallery_media_type = models.CharField(max_length=100, choices=MediaChoices, blank=True, null=True, verbose_name='Media Type')
    gallery_event_type = models.CharField(max_length=100, choices=EventChoices, blank=True, null=True, verbose_name='Event Type')
    slug = models.SlugField(unique=True, blank=True, null=True, verbose_name="gallery Slug", editable=False)
    class Meta:
        verbose_name = 'Gallery Data'
        verbose_name_plural = 'Gallery Data'



    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = generate_unique_slug(GalleryData, self.gallery_media_title)

        try:
            if self.gallery_media_image:
                # Open the image using Pillow
                img = Image.open(self.gallery_media_image)
                logger.debug(f"Opened image: {self.gallery_media_image.name}, mode: {img.mode}, format: {img.format}")

                # Define the desired height and calculate the corresponding width to maintain aspect ratio
                desired_height = 500  # Target height
                aspect_ratio = img.width / img.height
                new_width = int(desired_height * aspect_ratio)

                # Resize the image
                img = img.resize((new_width, desired_height), Image.Resampling.LANCZOS)
                logger.debug(f"Resized image to: {new_width}x{desired_height}")

                # Ensure the image is saved as PNG regardless of the original format
                img_io = BytesIO()

                # If the image is not a PNG, convert it to PNG
                if img.format != "PNG":
                    if img.mode != "RGBA":
                        img = img.convert("RGBA")
                        logger.debug(f"Converted image to RGBA mode")
                    img.save(img_io, format='PNG', optimize=True)
                    logger.debug(f"Image converted to PNG and optimized")
                    img_name = f"{self.gallery_media_image.name.split('.')[0]}.png"
                else:
                    # Save the PNG image directly after resizing
                    img.save(img_io, format='PNG', optimize=True)
                    logger.debug(f"PNG image resized and optimized")
                    img_name = self.gallery_media_image.name

                # Create a new Django file-like object to save to the model
                img_content = ContentFile(img_io.getvalue(), img_name)

                # Save the image back to the image field
                self.gallery_media_image.save(img_name, img_content, save=False)

        except Exception as e:
            logger.error(f"Error processing image {self.gallery_media_image.name}: {e}")
            raise

            # Call the parent class's save method to save other changes
        super(GalleryData, self).save(*args, **kwargs)



class TextSliderTop(models.Model):
    top_slider_title = models.CharField(max_length=20, blank=True, null=False, primary_key=True)
    top_slider_text = models.CharField(max_length=100, blank=True, null=True, verbose_name='Slider Top Text')
    active_text = models.BooleanField(default=False, null=True, verbose_name='Active Text')

class TextSliderBottom(models.Model):
    bottom_slider_title = models.CharField(max_length=20, blank=True, null=False, primary_key=True)
    bottom_slider_text = models.CharField(max_length=100, blank=True, null=True, verbose_name='Slider Bottom Text')
    active_text = models.BooleanField(default=False, null=True, verbose_name='Active Text')