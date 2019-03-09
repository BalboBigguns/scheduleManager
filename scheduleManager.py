import wget
import os
import re
import json
import shutil
import platform

sysInfo = platform.uname()

if sysInfo[0] == 'Windows':
    from win10toast import ToastNotifier
elif sysInfo[0] == 'Linux':
    import notify2

url = ['http://ife.plany.p.lodz.pl/plany/4CS1.pdf', 'http://ife.plany.p.lodz.pl/plany/4CS2.pdf',
       'http://ife.plany.p.lodz.pl/plany/2CS1.pdf', 'http://ife.plany.p.lodz.pl/plany/2CS2.pdf']
storedDataPath = 'data.json'
data = {}
workingDir = os.getcwd()
desktop = os.path.expanduser("~/Desktop")


for f in os.listdir():
    if f[-3:] == 'pdf':
        os.remove(f)

print('Beginning file download with wget module')

for u in url:
    outPDF = u[33:]
    outTXT = u[33:37] + '.txt'

    print()
    print('Processing ' + u[33:37] + ' schedule...')

    wget.download(u, outPDF)
    os.system('pdf2txt.py -c utf-8 -o' + workingDir + '/' + outTXT + ' ' + workingDir + '/' + outPDF)

    with open(outTXT, 'r', encoding='utf8') as f:
        data.update({u[33:37]:
                     re.findall('[0-3][0-9]/[0-1][0-9]/[0-9][0-9][0-9][0-9] [0-2][0-9]:[0-5][0-9]:[0-5][0-9]',
                                f.read())[0]})

    os.remove(outTXT)


newVersionFound = False

if storedDataPath not in os.listdir():
    print()
    print('No previous updates have been found')
    newVersionFound = True
    for f in os.listdir():
        if f[-3:] == 'pdf':
            shutil.move(f , desktop + '/' + f)
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
            shutil.move(c + '.pdf', desktop + '/' + c + '.pdf')
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

print()
input('Press key to finish...')
