import wget
import os
import re
import json
import shutil
import platform
import sys

sysInfo = platform.uname()

if sysInfo[0] == 'Windows':
    from win10toast import ToastNotifier
elif sysInfo[0] == 'Linux':
    import notify2

if len(sys.argv) > 1 and '-q' in sys.argv:
    t = open(os.devnull, 'w')
    sys.stdout = t

url = ['http://ife.plany.p.lodz.pl/plany/5CS1.pdf']

storedDataPath = 'data.json'
data = {}
workingDir = os.getcwd()
desktop = os.path.expanduser("~/Desktop")


for f in os.listdir():
    if f.endswith('pdf'):
        os.remove(f)

print('Beginning file download with wget module')

for u in url:
    outPDF = u.split('/')[-1]
    groupName = outPDF.split('.')[0]
    outTXT = groupName + '.txt'

    print()
    print('Processing ' + groupName + ' schedule...')

    wget.download(u, outPDF)
    os.system(os.path.join('pdf2txt.py -c utf-8 -o' + workingDir , outTXT + ' ' + workingDir, outPDF))

    with open(outTXT, 'r', encoding='utf8') as f:
        text = f.read()
        match = re.findall('[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9]:[0-5][0-9]', text)

        if len(match) == 0:
            match = re.findall('[0-3][0-9]/[0-1][0-9]/[0-9][0-9][0-9][0-9] [0-2][0-9]:[0-5][0-9]:[0-5][0-9]', text)

        data.update({groupName:match[0]})

    os.remove(outTXT)

newVersionFound = False

if storedDataPath not in os.listdir():
    print()
    print('No previous updates have been found')
    newVersionFound = True    
    for c, t in data.items():
        shutil.move(c + '.pdf', os.path.join(desktop, c + '_' + t.split(' ')[0].replace('/', '.') + '.pdf'))

else:
    print()
    print('Looking for changes...')

    with open(storedDataPath, 'r', encoding='utf8') as f:
        storedData = json.load(f)

    for c, t in data.items():
        if t == storedData[c]:
            os.remove(c + '.pdf')
        else:
            print()
            print(c + ': New schedule found!!!')
            print('Date of publication: ' + t)
            shutil.move(c + '.pdf', os.path.join(desktop, c + '_' + t.split(' ')[0].replace('/', '.') + '.pdf'))
            newVersionFound = True


if newVersionFound:
    with open(storedDataPath, 'w', encoding='utf8') as f:
        json.dump(data, f)
    print()
    print('Schedules updated')

    if sysInfo[0] == 'Windows':
        toaster = ToastNotifier()
        toaster.show_toast(
            "Schedule Manager",
            "New schedule has been found and it's waiting on your desktop",
            threaded=True)
    elif sysInfo[0] == 'Linux':
        notify2.init('Schedule Manager')
        n = notify2.Notification('New schedule', 'Check out your desktop')
        n.show()
else:
    print()
    print('No changes have been found')

if len(sys.argv) < 1 or '-q' not in sys.argv:
    print()
    input('Press key to finish...')
