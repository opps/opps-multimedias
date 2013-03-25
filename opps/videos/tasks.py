
from celery import task
from celery.signals import task_success


@task()
def upload_video(video):
    try:
        video_entry = video.hostctl.upload()
    except Exception as exc:
        upload_video.retry(exc=exc)

    video.host_url = video_entry.GetSwfUrl()
    video.host_id = video_entry.id.text.split('/')[-1]
    video.celery_task_id = upload_video.request.id
    video.save()
