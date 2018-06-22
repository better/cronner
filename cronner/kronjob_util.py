import yaml


class KronjobValidationException(Exception):
    pass


def format_kronjob_entry(entry):
    return {
        'schedule': entry['schedule'],
        'name': entry['fn_name'],
        'command': [entry['python_executable'], entry['script_path'], 'run', entry['fn_name']]
    }


def validate_kronjob_entry(entry):
    if len(entry['name']) > 52:
        raise KronjobValidationException('entry names must not be longer than 52 chars. ({})'.format(entry['name']))


def serialize_kronjob(base_template, entries):
    kronjob_def = yaml.safe_load(base_template)
    kronjob_entries = [format_kronjob_entry(entry) for entry in entries]
    for kronjob_entry in kronjob_entries:
        validate_kronjob_entry(kronjob_entry)
        kronjob_entry['name'] = kronjob_entry['name'].lower().replace('_', '-').strip('-')  # must be DNS-1123 compliant
    kronjob_def['jobs'] = kronjob_entries
    return yaml.safe_dump(kronjob_def)
