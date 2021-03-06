import logging

import boto3
from PIL import Image
from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.dispatch import receiver
from django.utils.text import slugify
from markdownx.utils import markdownify
from martor.models import MartorField

from risingofminds import settings


def thumbnail_name(instance, filename):
    import os
    from django.utils.timezone import now
    filename_base, filename_ext = os.path.splitext(filename)
    return 'thumbnail/%s%s' % (
        now().strftime("%Y%m%d%H%M%S"),
        filename_ext.lower(),
    )


class Author(AbstractUser):
    username = models.CharField(max_length=100, db_index=True, unique=True)
    description = models.TextField(max_length=500)
    thumbnail = models.ImageField(upload_to=thumbnail_name, blank=True)
    linkedin = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)

    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    def get_slug(self):
        return self.first_name.lower() + '-' + self.last_name.lower()

    def get_title(self):
        return self.first_name + ' ' + self.last_name + ' - Rising Of Minds'

    def save(self, *args, **kwargs):
        super(Author, self).save(*args, **kwargs)
        create_thumbnail(self)

    def get_thumbnail_url(self):
        from django.core.files.storage import default_storage as storage
        if not self.thumbnail:
            return ""
        thumb_file_path = "%s" % self.thumbnail.name
        if storage.exists(thumb_file_path):
            return storage.url(thumb_file_path)
        return ""


class Blog(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False, null=True,
                               blank=True)
    title = models.CharField(max_length=100, unique=True)
    tags = models.CharField(max_length=100, default='')
    thumbnail = models.ImageField(upload_to=thumbnail_name, blank=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.CharField(max_length=100, default="New Post")
    body = MartorField()
    posted_on = models.DateField(db_index=True, auto_now_add=True)
    views = models.IntegerField(default=0)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    active = models.BooleanField(default=False)

    @property
    def formatted_markdown(self):
        return markdownify(self.body)

    def __str__(self):
        return self.title

    def get_seo_title(self):
        return self.title + ' - ' + self.author.first_name + ' ' + self.author.last_name + ' - Rising Of Minds'

    def save(self, *args, **kwargs):
        super(Blog, self).save(*args, **kwargs)
        create_thumbnail(self)

    def get_thumbnail_url(self):
        from django.core.files.storage import default_storage as storage
        if not self.thumbnail:
            return ""
        thumb_file_path = "%s" % self.thumbnail.name
        if storage.exists(thumb_file_path):
            return storage.url(thumb_file_path)
        return ""

    @classmethod
    def increment_view(cls, pk):
        with transaction.atomic():
            blog = (
                cls.objects
                    .select_for_update()
                    .get(id=pk)
            )

            blog.views += 1
            blog.save()

        return blog


def get_image_filename(instance, filename):
    title = instance.post.title
    slug = slugify(title)
    return "blog_images/%s-%s" % (slug, filename)


class Images(models.Model):
    post = models.ForeignKey(Blog, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=get_image_filename, blank=True)

    def __str__(self):
        if self.image.name is not None:
            return self.post.title + ': ' + self.image.name
        else:
            return self.post.title + ': null'

    def get_image_url(self):
        from django.core.files.storage import default_storage as storage
        if not self.image:
            return ""
        thumb_file_path = "%s" % self.image.name
        if storage.exists(thumb_file_path):
            return storage.url(thumb_file_path)
        return ""

    def save(self, **kwargs):
        from django.core.files.storage import default_storage as storage
        import io
        import os
        from risingofminds import settings

        if not self.id and not self.image:
            return
        super(Images, self).save()
        filename = str(self.image.name)
        filename_base, filename_ext = os.path.splitext(filename)
        existing_file = storage.open(filename, 'r')
        image = Image.open(existing_file)
        size_in_kb = int(len(image.fp.read()) / 1024)
        width, height = image.size
        if size_in_kb > 50 and width >= 750:
            image = image.resize((750, int(750 * height / width)), Image.ANTIALIAS)
        sfile = io.BytesIO()
        image.save(sfile, filename_ext.replace('.', ''), quality=100)
        sfile.seek(0)
        s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        s3.upload_fileobj(sfile, settings.AWS_STORAGE_BUCKET_NAME, settings.AWS_LOCATION + '/' + filename,
                          ExtraArgs={'ACL': 'public-read'})
        existing_file.close()


@receiver(models.signals.post_delete, sender=Images)
def remove_file_from_s3(sender, instance, using, **kwargs):
    instance.image.delete(save=False)


class Category(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, db_index=True)

    def __str__(self):
        return self.title


def create_thumbnail(self):
    import os
    from PIL import Image
    from django.core.files.storage import default_storage as storage
    if not self.thumbnail:
        return ""
    file_path = self.thumbnail.name
    filename_base, filename_ext = os.path.splitext(file_path)
    thumb_file_path = "%s%s" % (filename_base, filename_ext)
    if storage.exists(thumb_file_path):
        return "exists"
    try:
        # resize the original image and return url path of the thumbnail
        f = storage.open(file_path, 'r')
        image = Image.open(f.name)
        width, height = image.size

        if width > height:
            delta = width - height
            left = int(delta / 2)
            upper = 0
            right = height + left
            lower = height
        else:
            delta = height - width
            left = 0
            upper = int(delta / 2)
            right = width
            lower = width + upper

        image = image.crop((left, upper, right, lower))
        image = image.resize((50, 50), Image.ANTIALIAS)

        f_thumb = storage.open(thumb_file_path, "w")
        image.save(f_thumb)
        f_thumb.close()
        return "success"
    except:
        logging.exception('Exception while Image processing')
        return "error"
