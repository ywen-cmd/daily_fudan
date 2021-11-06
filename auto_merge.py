import subprocess
import traceback

print('success')

def git_push(f):
    ret, val = subprocess.getstatusoutput("git status")
    if ret or "noting to commit" in val:
        print(ret, val)
        return 1
    ret, val = subprocess.getstatusoutput(f"git add {f}")
    if ret:
        print(ret, val)
        return 2
    ret, val = subprocess.getstatusoutput('git commit -m "autocreated by auto_merge.py"')
    if ret:
        print(ret, val)
        return 3
    ret, val = subprocess.getstatusoutput("git push origin master --force")
    if ret:
        print(ret, val)
        return 4
    return 0

def cmd_lines(lines):
    for line in lines:
        ret, val = subprocess.getstatusoutput(line)
        if ret:
            print(ret, val)
            return ret

def git_setIdentity():
    lines = [
            'git config --global user.name  "github-actions"',
            'git config --global user.email "github-actions@github.com"'
            ]
    return cmd_lines(lines)

def git_add_upstream():
    lines = [
            "git config --global pull.rebase true",
            "git config --global merge.ours.driver true",
            "git remote add upstream https://github.com/Limour-dev/daily_fudan.git"
        ]
    return cmd_lines(lines)
            

def git_checkout(f):
    lines = [
            "git fetch upstream",
            "git checkout master",
            f"git checkout upstream/master {f}"
        ]
    return cmd_lines(lines)

def update_f(f):
    if not git_checkout(f):
        return git_push(f)

def try_call(call, *arg, **kw):
    try:
        call(*arg, **kw)
    except:
        print(traceback.format_exc())

try_call(git_setIdentity)
try_call(git_add_upstream)
try_call(update_f, r'random_schedule.py')
