# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MediaHost'
        db.create_table(u'multimedias_mediahost', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('host', self.gf('django.db.models.fields.CharField')(default='uolmais', max_length=16)),
            ('status', self.gf('django.db.models.fields.CharField')(default='notuploaded', max_length=16)),
            ('host_id', self.gf('django.db.models.fields.CharField')(max_length=64, null=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=255, null=True)),
            ('celery_task', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['djcelery.TaskMeta'], unique=True, null=True)),
            ('updated', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('status_message', self.gf('django.db.models.fields.CharField')(max_length=64, null=True)),
        ))
        db.send_create_signal(u'multimedias', ['MediaHost'])

        # Adding model 'Video'
        db.create_table(u'multimedias_video', (
            (u'article_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['articles.Article'], unique=True, primary_key=True)),
            ('uolmais', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name=u'uolmais_video', unique=True, null=True, to=orm['multimedias.MediaHost'])),
            ('media_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('youtube', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name=u'youtube_video', unique=True, null=True, to=orm['multimedias.MediaHost'])),
        ))
        db.send_create_signal(u'multimedias', ['Video'])

        # Adding M2M table for field posts on 'Video'
        db.create_table(u'multimedias_video_posts', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('video', models.ForeignKey(orm[u'multimedias.video'], null=False)),
            ('post', models.ForeignKey(orm[u'articles.post'], null=False))
        ))
        db.create_unique(u'multimedias_video_posts', ['video_id', 'post_id'])

        # Adding model 'Audio'
        db.create_table(u'multimedias_audio', (
            (u'article_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['articles.Article'], unique=True, primary_key=True)),
            ('uolmais', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name=u'uolmais_audio', unique=True, null=True, to=orm['multimedias.MediaHost'])),
            ('media_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal(u'multimedias', ['Audio'])

        # Adding M2M table for field posts on 'Audio'
        db.create_table(u'multimedias_audio_posts', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('audio', models.ForeignKey(orm[u'multimedias.audio'], null=False)),
            ('post', models.ForeignKey(orm[u'articles.post'], null=False))
        ))
        db.create_unique(u'multimedias_audio_posts', ['audio_id', 'post_id'])

        # Adding model 'MediaBox'
        db.create_table(u'multimedias_mediabox', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_insert', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_update', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm["%s.%s" % (User._meta.app_label, User._meta.object_name)])),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['sites.Site'])),
            ('date_available', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=140)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=150)),
            ('article', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['articles.Article'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('channel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['channels.Channel'], null=True, on_delete=models.SET_NULL, blank=True)),
        ))
        db.send_create_signal(u'multimedias', ['MediaBox'])

        # Adding model 'MediaBoxAudios'
        db.create_table(u'multimedias_mediaboxaudios', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mediabox', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='mediaboxaudios_mediaboxes', null=True, on_delete=models.SET_NULL, to=orm['multimedias.MediaBox'])),
            ('audio', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='mediaboxaudios_audios', null=True, on_delete=models.SET_NULL, to=orm['multimedias.Audio'])),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal(u'multimedias', ['MediaBoxAudios'])

        # Adding model 'MediaBoxVideos'
        db.create_table(u'multimedias_mediaboxvideos', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mediabox', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='mediaboxvideos_mediaboxes', null=True, on_delete=models.SET_NULL, to=orm['multimedias.MediaBox'])),
            ('video', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='mediaboxvideos_videos', null=True, on_delete=models.SET_NULL, to=orm['multimedias.Video'])),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal(u'multimedias', ['MediaBoxVideos'])

        # Adding model 'MediaConfig'
        db.create_table(u'multimedias_mediaconfig', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_insert', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_update', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm["%s.%s" % (User._meta.app_label, User._meta.object_name)])),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['sites.Site'])),
            ('date_available', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('key_group', self.gf('django.db.models.fields.SlugField')(max_length=150, null=True, blank=True)),
            ('key', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=150)),
            ('format', self.gf('django.db.models.fields.CharField')(default='text', max_length=20)),
            ('value', self.gf('django.db.models.fields.TextField')()),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('article', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['articles.Article'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('channel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['channels.Channel'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('audio', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='mediaconfig_audios', null=True, on_delete=models.SET_NULL, to=orm['multimedias.Audio'])),
            ('video', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='mediaconfig_videos', null=True, on_delete=models.SET_NULL, to=orm['multimedias.Video'])),
        ))
        db.send_create_signal(u'multimedias', ['MediaConfig'])

        # Adding unique constraint on 'MediaConfig', fields ['key_group', 'key', 'site', 'channel', 'article', 'audio', 'video']
        db.create_unique(u'multimedias_mediaconfig', ['key_group', 'key', 'site_id', 'channel_id', 'article_id', 'audio_id', 'video_id'])

    def backwards(self, orm):
        # Removing unique constraint on 'MediaConfig', fields ['key_group', 'key', 'site', 'channel', 'article', 'audio', 'video']
        db.delete_unique(u'multimedias_mediaconfig', ['key_group', 'key', 'site_id', 'channel_id', 'article_id', 'audio_id', 'video_id'])

        # Deleting model 'MediaHost'
        db.delete_table(u'multimedias_mediahost')

        # Deleting model 'Video'
        db.delete_table(u'multimedias_video')

        # Removing M2M table for field posts on 'Video'
        db.delete_table('multimedias_video_posts')

        # Deleting model 'Audio'
        db.delete_table(u'multimedias_audio')

        # Removing M2M table for field posts on 'Audio'
        db.delete_table('multimedias_audio_posts')

        # Deleting model 'MediaBox'
        db.delete_table(u'multimedias_mediabox')

        # Deleting model 'MediaBoxAudios'
        db.delete_table(u'multimedias_mediaboxaudios')

        # Deleting model 'MediaBoxVideos'
        db.delete_table(u'multimedias_mediaboxvideos')

        # Deleting model 'MediaConfig'
        db.delete_table(u'multimedias_mediaconfig')

    models = {
        "%s.%s" % (User._meta.app_label, User._meta.module_name): {
        'Meta': {'object_name': User.__name__},
        },
        u'articles.album': {
            'Meta': {'ordering': "['-date_available']", 'object_name': 'Album', '_ormbases': [u'articles.Article']},
            u'article_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['articles.Article']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'articles.article': {
            'Meta': {'ordering': "['-date_available']", 'object_name': 'Article'},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['channels.Channel']"}),
            'channel_long_slug': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'db_index': 'True'}),
            'channel_name': ('django.db.models.fields.CharField', [], {'max_length': '140', 'null': 'True', 'db_index': 'True'}),
            'child_class': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'db_index': 'True'}),
            'date_available': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'headline': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'article_images'", 'to': u"orm['images.Image']", 'through': u"orm['articles.ArticleImage']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'main_image': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['images.Image']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'short_title': ('django.db.models.fields.CharField', [], {'max_length': '140', 'null': 'True'}),
            'short_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'default': '0', 'to': u"orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '150'}),
            'sources': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['sources.Source']", 'null': 'True', 'through': u"orm['articles.ArticleSource']", 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '140', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['%s.%s']" % (User._meta.app_label, User._meta.object_name)})
        },
        u'articles.articleimage': {
            'Meta': {'object_name': 'ArticleImage'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'articleimage_articles'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['articles.Article']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['images.Image']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        u'articles.articlesource': {
            'Meta': {'object_name': 'ArticleSource'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'articlesource_articles'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['articles.Article']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'articlesource_sources'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['sources.Source']"})
        },
        u'articles.post': {
            'Meta': {'ordering': "['-date_available']", 'object_name': 'Post', '_ormbases': [u'articles.Article']},
            'albums': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'post_albums'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['articles.Album']"}),
            u'article_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['articles.Article']", 'unique': 'True', 'primary_key': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'channels.channel': {
            'Meta': {'object_name': 'Channel'},
            'date_available': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'homepage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'long_slug': ('django.db.models.fields.SlugField', [], {'max_length': '250'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'subchannel'", 'null': 'True', 'to': u"orm['channels.Channel']"}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'show_in_menu': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'default': '0', 'to': u"orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '150'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['%s.%s']" % (User._meta.app_label, User._meta.object_name)})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'djcelery.taskmeta': {
            'Meta': {'object_name': 'TaskMeta', 'db_table': "'celery_taskmeta'"},
            'date_done': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meta': ('djcelery.picklefield.PickledObjectField', [], {'default': 'None', 'null': 'True'}),
            'result': ('djcelery.picklefield.PickledObjectField', [], {'default': 'None', 'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'PENDING'", 'max_length': '50'}),
            'task_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'traceback': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'images.image': {
            'Meta': {'object_name': 'Image'},
            'date_available': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'default': '0', 'to': u"orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '150', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sources.Source']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '140', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['%s.%s']" % (User._meta.app_label, User._meta.object_name)})
        },
        u'multimedias.audio': {
            'Meta': {'object_name': 'Audio'},
            u'article_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['articles.Article']", 'unique': 'True', 'primary_key': 'True'}),
            'media_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'posts': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'audio'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['articles.Post']"}),
            'uolmais': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "u'uolmais_audio'", 'unique': 'True', 'null': 'True', 'to': u"orm['multimedias.MediaHost']"})
        },
        u'multimedias.mediabox': {
            'Meta': {'object_name': 'MediaBox'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['articles.Article']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'audios': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'mediabox_audios'", 'to': u"orm['multimedias.Audio']", 'through': u"orm['multimedias.MediaBoxAudios']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['channels.Channel']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'date_available': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '140'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'default': '0', 'to': u"orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '150'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['%s.%s']" % (User._meta.app_label, User._meta.object_name)}),
            'videos': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'mediabox_videos'", 'to': u"orm['multimedias.Video']", 'through': u"orm['multimedias.MediaBoxVideos']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'})
        },
        u'multimedias.mediaboxaudios': {
            'Meta': {'object_name': 'MediaBoxAudios'},
            'audio': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'mediaboxaudios_audios'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['multimedias.Audio']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mediabox': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'mediaboxaudios_mediaboxes'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['multimedias.MediaBox']"}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        u'multimedias.mediaboxvideos': {
            'Meta': {'object_name': 'MediaBoxVideos'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mediabox': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'mediaboxvideos_mediaboxes'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['multimedias.MediaBox']"}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'mediaboxvideos_videos'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['multimedias.Video']"})
        },
        u'multimedias.mediaconfig': {
            'Meta': {'unique_together': "(('key_group', 'key', 'site', 'channel', 'article', 'audio', 'video'),)", 'object_name': 'MediaConfig'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['articles.Article']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'audio': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'mediaconfig_audios'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['multimedias.Audio']"}),
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['channels.Channel']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'date_available': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'format': ('django.db.models.fields.CharField', [], {'default': "'text'", 'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '150'}),
            'key_group': ('django.db.models.fields.SlugField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'default': '0', 'to': u"orm['sites.Site']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['%s.%s']" % (User._meta.app_label, User._meta.object_name)}),
            'value': ('django.db.models.fields.TextField', [], {}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'mediaconfig_videos'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['multimedias.Video']"})
        },
        u'multimedias.mediahost': {
            'Meta': {'object_name': 'MediaHost'},
            'celery_task': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['djcelery.TaskMeta']", 'unique': 'True', 'null': 'True'}),
            'host': ('django.db.models.fields.CharField', [], {'default': "'uolmais'", 'max_length': '16'}),
            'host_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'notuploaded'", 'max_length': '16'}),
            'status_message': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'}),
            'updated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'null': 'True'})
        },
        u'multimedias.video': {
            'Meta': {'object_name': 'Video'},
            u'article_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['articles.Article']", 'unique': 'True', 'primary_key': 'True'}),
            'media_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'posts': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'video'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['articles.Post']"}),
            'uolmais': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "u'uolmais_video'", 'unique': 'True', 'null': 'True', 'to': u"orm['multimedias.MediaHost']"}),
            'youtube': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "u'youtube_video'", 'unique': 'True', 'null': 'True', 'to': u"orm['multimedias.MediaHost']"})
        },
        u'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'sources.source': {
            'Meta': {'object_name': 'Source'},
            'date_available': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'feed': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'default': '0', 'to': u"orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '140'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['%s.%s']" % (User._meta.app_label, User._meta.object_name)})
        },
        u'taggit.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'taggit.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'taggit_taggeditem_tagged_items'", 'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'taggit_taggeditem_items'", 'to': u"orm['taggit.Tag']"})
        }
    }

    complete_apps = ['multimedias']