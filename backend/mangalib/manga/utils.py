def background_image_upload_path(instance, filename):
    name = instance.subtitle.replace(" ", "-").lower()
    return f"media/manga/{name}/background/{filename}"

def poster_image_upload_path(instance, filename):
    name = instance.subtitle.replace(" ", "-").lower()
    return f"media/manga/{name}/poster/{filename}"

def page_image_upload_path(instance, filename):
    chapter = instance.chapter
    volume = chapter.volume
    manga_name = volume.manga.subtitle
    volume_number = volume.volume_number
    chapter_number = chapter.chapter_number
    return f"media/manga/{manga_name}/volume-{volume_number}/chapter-{chapter_number}/pages/{filename}"