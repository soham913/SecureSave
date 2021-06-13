from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from FileBackupApp.forms import FileForm
import owncloud
import os
import pyAesCrypt


# Create your views here.
bufferSize = 64*1024
fileDict = dict()


oc = owncloud.Client('http://localhost/owncloud')

oc.login('happyghost', 'Admin@123')

#oc.mkdir('File')

mes = "File Uploaded Successfully!"

def handle_uploaded_file(f):
    with open('upload/'+f.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def delete_uploaded_file(f):
    os.remove('./'+f)

def home(request):
    fileForm = FileForm()
    return render( request ,'home.html', {'form': fileForm})

def upload(request):
    if request.method == 'POST':
        fileForm = FileForm(request.POST, request.FILES)
        if fileForm.is_valid():
            handle_uploaded_file(request.FILES['file'])
            name = request.POST['name']
            name = request.FILES['file'].name.split('.')[0]
            desc = request.POST['desc']
            fileDict[request.FILES['file'].name] = [name, desc]

            unEncFile = 'upload/' + request.FILES['file'].name
            encFile = 'upload/' + request.FILES['file'].name + '.aes'
            print(fileDict)
            with open(unEncFile, 'rb') as fIn:
                with open(encFile, 'wb') as fOut:
                    pyAesCrypt.encryptStream(fIn, fOut, '12345', bufferSize)

            oc.put_file('Files/'+request.FILES['file'].name, encFile)
            delete_uploaded_file(encFile)
            delete_uploaded_file(unEncFile)
    return redirect(allFiles)


def allFiles(request):

    ls = oc.list('Files/')
    length = len(ls)
    for i in ls:
        fileDict[str(i).split(',')[0].split('/')[2]] = [str(i).split(',')[0].split('/')[2].split('.')[0], 'Empty']

    return render(request, 'allFiles.html', {'fileDict': fileDict, 'message': mes})

def download(request):

    fileName = request.GET['downloadBtn']
    print(fileName)
    encFile = './Download/{}.{}'.format(fileName, 'aes')
    decFile = './Download/{}'.format(fileName)

    print(oc.get_file('Files/' + fileName, encFile))

    encFileSize = os.stat(encFile).st_size
    with open(encFile, 'rb') as fIn:
        with open(decFile, 'wb') as fOut:
            pyAesCrypt.decryptStream(fIn, fOut, "12345", bufferSize, encFileSize)

    delete_uploaded_file(encFile)

    return FileResponse(open(decFile, 'rb'))

def delete(request):

    fileName = request.POST['deleteBtn']
    print(fileName)
    print(fileDict)
    print(oc.delete('Files/' + fileName))
    del fileDict[fileName]

    return redirect(allFiles)
