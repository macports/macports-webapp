# Generated by Django 2.2.10 on 2020-04-15 18:32

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UUID',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.CharField(db_index=True, max_length=36)),
            ],
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('os_version', models.CharField(max_length=10)),
                ('xcode_version', models.CharField(max_length=10)),
                ('os_arch', models.CharField(max_length=20)),
                ('build_arch', models.CharField(default='', max_length=20)),
                ('platform', models.CharField(default='', max_length=20)),
                ('macports_version', models.CharField(max_length=10)),
                ('cxx_stdlib', models.CharField(default='', max_length=20)),
                ('clt_version', models.CharField(default='', max_length=100)),
                ('raw_json', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('timestamp', models.DateTimeField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stats.UUID')),
            ],
        ),
        migrations.CreateModel(
            name='PortInstallation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('port', models.CharField(max_length=100)),
                ('version', models.CharField(max_length=100)),
                ('variants', models.CharField(default='', max_length=200)),
                ('requested', models.BooleanField(default=False)),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stats.Submission')),
            ],
        ),
        migrations.AddIndex(
            model_name='submission',
            index=models.Index(fields=['timestamp'], name='stats_submi_timesta_cdcb72_idx'),
        ),
        migrations.AddIndex(
            model_name='submission',
            index=models.Index(fields=['user'], name='stats_submi_user_id_fb754f_idx'),
        ),
        migrations.AddIndex(
            model_name='submission',
            index=models.Index(fields=['user', '-timestamp'], name='stats_submi_user_id_10b8e5_idx'),
        ),
        migrations.AddIndex(
            model_name='submission',
            index=models.Index(fields=['user', 'timestamp'], name='stats_submi_user_id_a349e8_idx'),
        ),
        migrations.AddIndex(
            model_name='submission',
            index=models.Index(fields=['os_version'], name='stats_submi_os_vers_f793f1_idx'),
        ),
        migrations.AddIndex(
            model_name='submission',
            index=models.Index(fields=['os_version', 'os_arch'], name='stats_submi_os_vers_0cb582_idx'),
        ),
        migrations.AddIndex(
            model_name='submission',
            index=models.Index(fields=['os_version', 'xcode_version'], name='stats_submi_os_vers_5997ef_idx'),
        ),
        migrations.AddIndex(
            model_name='submission',
            index=models.Index(fields=['os_arch'], name='stats_submi_os_arch_088fdd_idx'),
        ),
        migrations.AddIndex(
            model_name='submission',
            index=models.Index(fields=['macports_version'], name='stats_submi_macport_1bd1cf_idx'),
        ),
        migrations.AddIndex(
            model_name='submission',
            index=models.Index(fields=['cxx_stdlib'], name='stats_submi_cxx_std_267d24_idx'),
        ),
        migrations.AddIndex(
            model_name='submission',
            index=models.Index(fields=['build_arch'], name='stats_submi_build_a_8093ff_idx'),
        ),
        migrations.AddIndex(
            model_name='submission',
            index=models.Index(fields=['clt_version'], name='stats_submi_clt_ver_1a1b8d_idx'),
        ),
        migrations.AddIndex(
            model_name='portinstallation',
            index=models.Index(fields=['submission'], name='stats_porti_submiss_d2ed90_idx'),
        ),
        migrations.AddIndex(
            model_name='portinstallation',
            index=models.Index(fields=['port'], name='stats_porti_port_7817b7_idx'),
        ),
        migrations.AddIndex(
            model_name='portinstallation',
            index=models.Index(fields=['variants'], name='stats_porti_variant_fec07e_idx'),
        ),
    ]
