import functools

import cronner
import kronjob
import yaml


class JobValidationException(Exception):
    pass


def create_job(entry):
    return {
        'schedule': entry['schedule'],
        'name': entry['fn_name'],
        'command': [entry['python_executable'], entry['script_path'], 'run', entry['fn_name']]
    }


def validate_job(job):
    if not set(['schedule', 'name', 'command']).issubset(job):
        raise JobValidationException(
            'job does not contain neccessary fields: schedule, name, command. ({})'.format(job)
        )
    if len(job['name']) > 52:
        raise JobValidationException('job names must not be longer than 52 chars. ({})'.format(job['name']))


def serialize(base_template, job_creator, entries):
    kronjob_def = yaml.safe_load(base_template)
    if job_creator is None:
        job_creator = create_job
    jobs = [job_creator(entry) for entry in entries]
    for job in jobs:
        validate_job(job)
        job['name'] = job['name'].lower().replace('_', '-')  # must be DNS-1123 compliant
    kronjob_def['jobs'] = jobs
    k8s_objects = kronjob.build_k8s_objects(kronjob_def)
    return kronjob.serialize_k8s(k8s_objects)


class Kronner(cronner.Cronner):
    def configure(self, base_template=None, job_creator=None, serializer=None):
        if base_template is not None:
            serializer = functools.partial(serialize, base_template, job_creator)
        super(Kronner, self).configure(serializer=serializer)


_KRONNER = Kronner()
configure = _KRONNER.configure
find_registrations = _KRONNER.find_registrations
register = _KRONNER.register
main = _KRONNER.main
