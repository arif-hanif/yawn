from yawn.worker.models import Worker
# to make the fixture available:
from yawn.task.tests.test_models import run


def test_get_task(client, run):
    task = run.task_set.first()
    worker = Worker.objects.create(name='worker1')
    task.start_execution(worker)
    url = '/api/tasks/%s/' % task.id
    response = client.get(url)
    assert response.status_code == 200, response.data
    assert response.data['name'] == task.template.name
    assert response.data['status'] == task.status
    assert response.data['executions'][0]['worker']['name'] == worker.name
    assert response.data['messages'][0]['queue'] == task.message_set.first().queue.name


def test_patch_task_terminate(client, run):
    task = run.task_set.first()
    url = '/api/tasks/%s/' % task.id
    worker = Worker.objects.create(name='worker1')
    execution = task.start_execution(worker)
    response = client.patch(url, {'terminate': execution.id})
    execution.refresh_from_db()
    assert response.status_code == 200, response.data
    assert response.data['executions'][0]['id'] == execution.id
    assert response.data['executions'][0]['status'] == execution.status
    assert response.data['executions'][0]['status'] == execution.KILLED


def test_patch_task_enqueue(client, run):
    task = run.task_set.first()
    assert task.message_set.count() == 1
    url = '/api/tasks/%s/' % task.id
    response = client.patch(url, {'enqueue': True})
    assert response.status_code == 200, response.data
    assert len(response.data['messages']) == 2
