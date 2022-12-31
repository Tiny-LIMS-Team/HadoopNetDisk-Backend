import jwt
import json
import os.path
import urllib.parse

from Files.utils import *
from django.conf import settings
from django.http import FileResponse, JsonResponse


def upload_files(request):
    pass


def download_files(request):
    token = request.GET.get('token')
    info_dict = jwt.decode(token, 'secret_key', algorithms=['HS256'])
    user_name = info_dict['username']

    file_paths = request.GET.get('file_paths')
    cli = connect_to_hdfs()
    for user_file_path in file_paths:
        file_path = os.path.join('_files', user_file_path)
        temp_path = os.path.join(settings.MEDIA_ROOT, user_file_path)
        download_from_hdfs(cli, file_path, temp_path)

    compress_file_name = user_name + '.zip'
    compress_file_path = os.path.join(settings.MEDIA_ROOT, compress_file_name)
    compress_path = os.path.join(settings.MEDIA_ROOT, user_name)
    zip_ya(compress_path, compress_file_name, settings.MEDIA_ROOT)

    file = open(compress_file_path, 'rb')
    file_response = FileResponse(file)
    file_response['Content-Type'] = 'application/octet-stream'
    file_response[
        "Access-Control-Expose-Headers"] = 'Content-Disposition'
    file_response['Content-Disposition'] = 'attachment;filename={}'.format(urllib.parse.quote(compress_file_name))
    return file_response


def search_for_files(request):
    pass
    # cli = connect_to_hbase()
    # scanner_get_select(cli, 'SBhbase', ['', '', '', '', ''], 0, rows_cnt=100000)


def del_files(request):
    token = request.GET.get('token')
    info_dict = jwt.decode(token, 'secret_key', algorithms=['HS256'])
    user_name = info_dict['username']

    file_paths = request.GET.get('file_paths')
    cli = connect_to_hdfs()
    for file_to_del in file_paths:
        try:
            file_path = os.path.join('_files', user_name, file_to_del)
            hdfs_del_files(cli, file_path)
        except Exception as e:
            print(e)
    return JsonResponse({'code': 200, 'message': '删除操作已完成'})


def get_all_files(request):
    token = request.GET.get('token')
    info_dict = jwt.decode(token, 'secret_key', algorithms=['HS256'])
    user_name = info_dict['username']

    request_path = request.GET.get('require_path')

    cli = connect_to_hdfs()
    user_root_dir = os.path.join('_files', user_name, request_path)
    file_dict = hdfs_list(cli, user_root_dir, verbose=True)
    res_dict = {}
    for item in file_dict:
        res_dict.update({item[0]: item[1]['type']})
    res = json.dumps(res_dict)
    return JsonResponse(res)

