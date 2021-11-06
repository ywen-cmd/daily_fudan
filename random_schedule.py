from random import randint
from datetime import datetime
import subprocess
import traceback
from sys import argv as sys_argv
from sys import exit as sys_exit

schedule_template = '''name: "Daily Fudan"

on:
  schedule: # scheduled at (UTC+8) everyday
    - cron: "%s"
    - cron: "%s"
  workflow_dispatch:

env:
  # auto merge from y1ndan/genshin-impact-helper, default: false
  ALLOW_MERGE: 'false'
  RUN_ENV: 'prod'
  TZ: 'Asia/Shanghai'
  FUCK_GH_PAT: ${{ secrets.GH_PAT }}

jobs:
  build:
    runs-on: ubuntu-latest
    # if: github.ref == 'refs/heads/master'

    steps:
      - name: Checkout master with GH_PAT
        if: ${{ env.FUCK_GH_PAT }}
        uses: actions/checkout@v2
        with:
          fetch-depth: 2
          ref: master
          token: ${{ secrets.GH_PAT }}

      - name: Checkout master without GH_PAT
        if: ${{ !env.FUCK_GH_PAT }}
        uses: actions/checkout@v2
        with:
          fetch-depth: 0
          ref: master

      - name: Auto merge
        if: ${{ env.ALLOW_MERGE != 'false' }}
        run: |
          git config --global user.name  github-actions
          git config --global user.email github-actions@github.com
          git config --global pull.rebase true
          git remote add upstream https://github.com/Limourli-liu/daily_fudan.git
          git config --global merge.ours.driver true
          git pull upstream master --allow-unrelated-histories
          git push origin master --force
      - name: Set up python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9

      - name: Random_schedule
        if: ${{ env.FUCK_GH_PAT }}
        run: python3 ./random_schedule.py '${{ secrets.SCHEDULE }}'

      - name: Run sign
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          python3 ./dailyFudan.py '${{ secrets.FUDAN }}'
'''
am_inf=19
am_sup=22
pm_inf = 5
pm_sup = 8
t_inf = 4
t_sup = 15

def getRandCron_am():
    mins = randint(0,59)
    hours = randint(am_inf,am_sup) % 24
    return f'{mins} {hours} * * *'

def getRandCron_pm():
    mins = randint(0,59)
    hours = randint(pm_inf,pm_sup) % 24
    return f'{mins} {hours} * * *'

def is_pm():
    uctnow = datetime.utcnow()
    uctnow = uctnow.hour
    if uctnow < t_inf:
        uctnow += 24
    return t_inf < uctnow < t_sup
    
def get_schedule():
    return schedule_template%(getRandCron_am(),getRandCron_pm())

def git_push():
    ret, val = subprocess.getstatusoutput("git status")
    if ret or "noting to commit" in val:
        print(ret, val)
        return 1
    ret, val = subprocess.getstatusoutput("git add .")
    if ret:
        print(ret, val)
        return 2
    ret, val = subprocess.getstatusoutput('git commit -m "autocreated by random_schedule.py"')
    if ret:
        print(ret, val)
        return 3
    ret, val = subprocess.getstatusoutput("git push origin master --force")
    if ret:
        print(ret, val)
        return 4
    return 0

def git_revoke():
    ret, val = subprocess.getstatusoutput(r'git reset --hard "HEAD^"')
    if ret:
        print(ret, val)
        return 1
    ret, val = subprocess.getstatusoutput("git push origin master --force")
    if ret:
        print(ret, val)
        return 2
    return 0

GMT_FORMAT = 'Date:   %a %b %d %H:%M:%S %Y +0800'
def is_today_created(val):
    date = val.split('\n')[2]
    date = datetime.strptime(date, GMT_FORMAT)
    date = (datetime.now()-date).total_seconds()//3600
    print('timedelta', date)
    return date <= 12

def is_autocreated():
    ret, val = subprocess.getstatusoutput("git log -1")
    if ret:
        print(ret, val)
        return False
    if 'autocreated by random_schedule.py' in val:
        if is_today_created(val):
            sys_exit(0)
        return True
    return False

def update_schedule():
    with open(r'./.github/workflows/main.yml','w',encoding='utf-8') as f:
        f.write(get_schedule())

def fuck_windows(std):
    lines = std.readlines()
    try:
        return ''.join(line.decode('utf-8') for line in lines)
    except UnicodeDecodeError:
        return ''.join(line.decode('cp936') for line in lines)

def fuck_cmd(cmd):
    child = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    child.stdin.close()
    ret = child.wait()
    if ret:
        val = fuck_windows(child.stderr)
    else:
        val = fuck_windows(child.stdout)
    return ret, val

subprocess.getstatusoutput = fuck_cmd

def main():
    if is_autocreated():
        if git_revoke():
            return
    update_schedule()
    git_push()

def get_arg():
    print('Please get token from https://github.com/settings/tokens')
    if (len(sys_argv) != 2) or (not sys_argv[1]):
        print('use default SCHEDULE')
        return
    SCHEDULE = sys_argv[1].strip().split(' ')
    global am_inf, am_sup, pm_inf, pm_sup, t_inf, t_sup
    if len(SCHEDULE) == 6:
        am_inf = int(SCHEDULE[0])
        am_sup = int(SCHEDULE[1])
        pm_inf = int(SCHEDULE[2])
        pm_sup = int(SCHEDULE[3])
        t_inf = int(SCHEDULE[4])
        t_sup = int(SCHEDULE[5])
    else:
        print('wrong SCHEDULE. use default SCHEDULE')
    print(am_inf, am_sup, pm_inf, pm_sup, t_inf, t_sup)

def git_setIdentity():
    lines = [
            'git config --global user.name  "github-actions"',
            'git config --global user.email "github-actions@github.com"'
            ]
    for line in lines:
        ret, val = subprocess.getstatusoutput(line)
        if ret:
            print(ret, val)
            return ret

def auto_merge():
    lines = [
            "git config --global pull.rebase true",
            "git config --global merge.ours.driver true",
            "git remote add upstream https://github.com/Limour-dev/daily_fudan.git",
            "git fetch upstream",
            "git checkout master",
            "git checkout upstream/master auto_merge.py"
        ]
    for line in lines:
        ret, val = subprocess.getstatusoutput(line)
        if ret:
            print(ret, val)
            return ret
    ret, val = subprocess.getstatusoutput("python3 ./auto_merge.py")
    print(ret, val)
    if 'success' not in val:
        ret, val = subprocess.getstatusoutput("python ./auto_merge.py")
        print(ret, val)

try:
    if git_setIdentity():
        sys_exit(0)
except:
    print(traceback.format_exc())

try:
    get_arg()
except:
    print(traceback.format_exc())

if is_pm():
    try:
        main()
    except SystemExit:
        pass
    except:
        print(traceback.format_exc())

try:
    if auto_merge():
        sys_exit(0)
except:
    print(traceback.format_exc())
