"""Lifecycle contract checks without touching the developer's Docker daemon."""
import json
import subprocess

import pytest

from scripts import runtime


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    monkeypatch.setattr(runtime, 'ROOT', tmp_path)
    monkeypatch.setattr(runtime, 'STATE', tmp_path / '.state')
    runtime.STATE.mkdir()
    return tmp_path


@pytest.mark.parametrize('operation', [('up', '-d', 'prod'), ('stop', 'wud'), ('down',), ('ps',)])
def test_all_compose_operations_preserve_override_and_release_selection(workspace, monkeypatch, operation):
    (workspace / 'compose.override.yaml').touch()
    (runtime.STATE / 'release.env').write_text('PROD_IMAGE=example/app@sha256:selected\n')
    monkeypatch.setenv('PROD_IMAGE', 'example/app:wrong-shell-value')
    calls = []
    monkeypatch.setattr(runtime, 'run', lambda args, **kwargs: calls.append((args, kwargs)))
    runtime.compose(*operation)
    args, kwargs = calls[0]
    assert str(workspace / 'compose.override.yaml') in args
    assert args[-len(operation):] == list(operation)
    assert kwargs['env']['PROD_IMAGE'] == 'example/app@sha256:selected'


def test_initial_image_customization_is_preserved(workspace, monkeypatch):
    monkeypatch.setenv('PROD_IMAGE', 'example/app:initial')
    calls = []
    monkeypatch.setattr(runtime, 'run', lambda args, **kwargs: calls.append(kwargs))
    runtime.compose('config')
    assert calls[0]['env']['PROD_IMAGE'] == 'example/app:initial'


def test_same_commit_in_different_image_is_not_a_verified_rollback(monkeypatch):
    image = {'Id': 'sha256:selected', 'Config': {'Labels': {'org.opencontainers.image.revision': 'a' * 40}}}
    monkeypatch.setattr(runtime, 'compose', lambda *args, **kwargs: subprocess.CompletedProcess([], 0, stdout='container-id\n'))
    monkeypatch.setattr(runtime, 'output', lambda args: json.dumps([image]) if args[1:3] == ['image', 'inspect'] else 'sha256:other')
    with pytest.raises(RuntimeError, match='selected image ID'):
        runtime.verify_production('example/app:old')


def test_paused_production_deploy_never_starts_updater_or_development(workspace, monkeypatch):
    (runtime.STATE / 'updates-paused').touch()
    monkeypatch.setattr(runtime, 'initialize_updater', lambda: None)
    monkeypatch.setattr(runtime, 'verify_production', lambda reference: None)
    monkeypatch.setattr(runtime, 'production_reference', lambda: 'example/app:old')
    calls = []
    monkeypatch.setattr(runtime, 'compose', lambda *args: calls.append(args))
    runtime.deploy()
    assert calls == [('pull', 'prod'), ('up', '-d', '--no-deps', 'prod')]
