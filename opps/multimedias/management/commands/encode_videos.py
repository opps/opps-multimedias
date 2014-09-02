#!/usr/bin/env python
# -*- coding: utf-8 -*-
from optparse import make_option
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from django.conf import settings
from opps.multimedias.models import Video


LOCAL_FORMATS = settings.OPPS_MULTIMEDIAS_LOCAL_FORMATS


class Command(BaseCommand):
    args = '<video_id video_id ...>'
    help = 'Re-encode opps.multimedias local videos'

    option_list = BaseCommand.option_list + (
        make_option('--limit',
                    type='int',
                    dest='limit',
                    default=100,
                    help='Limit of videos to processing'),
        make_option('--from',
                    type='int',
                    dest='start',
                    help='ID to start'),
        make_option('--to',
                    type='int',
                    dest='end',
                    help='ID to end'),
        make_option('--format',
                    type='choice',
                    action="append",
                    choices=LOCAL_FORMATS.keys(),
                    dest='format',
                    help='Formats to (re)encode'),
        make_option('--rebuild',
                    action='store_true',
                    dest='rebuild',
                    default=False,
                    help='Force rebuild existent videos'),
    )

    def handle(self, *args, **options):
        f = Q()

        videos = Video.objects.filter(local__isnull=False).order_by('-id')

        if args:
            id_from = id_to = None
            videos = videos.filter(pk__in=map(int, args))
        else:
            if options.get('from'):
                videos = videos.filter(pk__gt=options.get('from'))
            if options.get('to'):
                videos = videos.filter(pk__lt=options.get('to'))

        if not options.get('rebuild'):
            tpl = "ffmpeg_file_{}"
            for i in options.get('format') or LOCAL_FORMATS.keys():
                f |= Q(**{tpl.format(i) + '__isnull': True})
            videos = videos.filter(f)

        msg = {
            "prefix": "\n[{datetime}][{v.id}] {v}",
            "init": " Start update...\n",
            "ok": " OK!\n",
            "error": " {e}\n"
        }

        for v in videos[:options.get('limit')]:
            try:
                m = msg['prefix'] + msg['init']
                self.stdout.write(m.format(v=v, datetime=datetime.now()))

                v.local.api.process(v.local,
                                    formats=options.get('format'),
                                    force=options.get('rebuild'))

                m = msg['prefix'] + msg['ok']
                self.stdout.write(m.format(v=v, datetime=datetime.now()))
            except Exception as e:
                m = msg['prefix'] + msg['error']
                self.stderr.write(m.format(v=v, e=e, datetime=datetime.now()))
            self.stderr.write('')
