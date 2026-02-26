from django.core.files.storage import FileSystemStorage

class MediaStorage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('location', 'media')
        kwargs.setdefault('base_url', '/media/')
        super().__init__(*args, **kwargs)