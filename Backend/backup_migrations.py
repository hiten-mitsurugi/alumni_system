import os, shutil, datetime
root = os.path.join(os.getcwd())
backend = os.path.join(root, 'Backend')
t = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
dst = os.path.join(backend, 'migrations_backups_' + t)
os.makedirs(dst, exist_ok=True)
for name in os.listdir(backend):
    path = os.path.join(backend, name)
    if os.path.isdir(path):
        m = os.path.join(path, 'migrations')
        if os.path.isdir(m):
            shutil.copytree(m, os.path.join(dst, f'{name}_migrations'))
print('Created backup at:', dst)
