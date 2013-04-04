
from django.utils import timezone
from celery import task
from djcelery.models import TaskMeta


@task
def upload_video(videohost):
    video = videohost.video
    video_info = videohost.api.upload(video.video_file.path, video.title,
                                      video.headline, [])#video.tags)
    videohost.host_id = video_info['id']
    videohost.celery_task = TaskMeta.objects.get(task_id=upload_video.request.id)
    videohost.save()


@task.periodic_task(run_every=timezone.timedelta(minutes=1))
def update_videohost():
    tasks = TaskMeta.objects.filter(status='SUCCESS', videohost__isnull=False,
                                    videohost__updated=False)
    for task in tasks:
        videohost = task.videohost
        video_info = videohost.api.get_info(videohost.host_id)
        if video_info.has_key('url'):
            videohost.url = video_info['url']
            videohost.updated = True
            videohost.save()
